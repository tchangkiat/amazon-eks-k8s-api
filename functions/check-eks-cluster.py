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
session = boto3.session.Session()
sts = session.client('sts')
service_id = sts.meta.service_model.service_id

def lambda_handler(event, context):
    eks = boto3.client('eks')
    
    response = []
    
    for clusterName in eks.list_clusters()['clusters']:
        cluster = eks.describe_cluster(
            name=clusterName
        )['cluster']
        cluster_response = { 'name': cluster['name'], 'status': cluster['status'], 'version': cluster['version'] }
        
        nodegroup_response = []
        for nodegroupName in eks.list_nodegroups(clusterName=clusterName)['nodegroups']:
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

        # config.load_kube_config_from_dict(config_dict=kubeconfig)
        # print(kubeconfig)
        # v1 = client.CoreV1Api()
        # ret = v1.list_pod_for_all_namespaces(watch=False)
        # print(len(ret.items))

        response.append({ 'cluster': cluster_response, 'nodegroups': nodegroup_response })
    
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