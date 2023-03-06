"Get information from EKS clusters"
import base64
import boto3
import json
import logging
import re

from botocore.signers import RequestSigner
from kubernetes import client, config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

STS_TOKEN_EXPIRES_IN = 60
TEAM_MEMBER_ACCOUNTS = ["409989946510"]
TEAM_ROLE = ["arn:aws:iam::409989946510:role/gameday-quest-TeamRole"]

session = boto3.session.Session()
sts = session.client('sts')
service_id = sts.meta.service_model.service_id

def lambda_handler(event, context):
    # Assume role in Team account
    sts_connection = boto3.client('sts')
    team_acct = sts_connection.assume_role(
        RoleArn=TEAM_ROLE[0],
        RoleSessionName="assume_team_role"
    )

    eks = boto3.client('eks',
        aws_access_key_id = team_acct['Credentials']['AccessKeyId'],
        aws_secret_access_key = team_acct['Credentials']['SecretAccessKey'],
        aws_session_token = team_acct['Credentials']['SessionToken']
    )
    
    response = []
    
    for clusterName in eks.list_clusters()['clusters']:
        cluster = eks.describe_cluster(
            name=clusterName
        )['cluster']
        cluster_response = { 'name': cluster['name'], 'status': cluster['status'], 'version': cluster['version'] }

        nodegroup_response = []
        nodegroups = eks.list_nodegroups(clusterName=clusterName)['nodegroups']
        for nodegroupName in nodegroups:
            ng = eks.describe_nodegroup(
                clusterName=clusterName,
                nodegroupName=nodegroupName
            )
            nodegroup_response.append({ 'name': ng['nodegroup']['nodegroupName'], 'status': ng['nodegroup']['status'], 'version': ng['nodegroup']['version'] })
        
        kubeconfig = {
            'apiVersion': 'v1',
            'clusters': [{
            'name': 'cluster1',
            'cluster': {
                'certificate-authority-data': cluster["certificateAuthority"]["data"],
                'server': cluster["endpoint"]}
            }],
            'contexts': [{'name': 'context1', 'context': {'cluster': 'cluster1', "user": "user1"}}],
            'current-context': 'context1',
            'kind': 'Config',
            'preferences': {},
            'users': [{'name': 'user1', "user" : {'token': get_bearer_token(clusterName)}}]
        }

        config.load_kube_config_from_dict(config_dict=kubeconfig)
        v1 = client.CoreV1Api()
        system_pods = []
        for p in v1.list_pod_for_all_namespaces(watch=False).items:
            system_pods.append({ 'name': p.metadata.name, 'image': p.spec.containers[0].image })

        response.append({ 'cluster': cluster_response, 'nodegroups': nodegroup_response, 'systemPods': system_pods })
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }

def get_bearer_token(clusterName):
    "Create authentication token"
    signer = RequestSigner(
        service_id,
        session.region_name,
        'sts',
        'v4',
        session.get_credentials(),
        session.events
    )

    params = {
        'method': 'GET',
        'url': 'https://sts.{}.amazonaws.com/'
               '?Action=GetCallerIdentity&Version=2011-06-15'.format(session.region_name),
        'body': {},
        'headers': {
            'x-k8s-aws-id': clusterName
        },
        'context': {}
    }

    signed_url = signer.generate_presigned_url(
        params,
        region_name=session.region_name,
        expires_in=STS_TOKEN_EXPIRES_IN,
        operation_name=''
    )
    base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

    # remove any base64 encoding padding:
    return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)