"Get information from EKS clusters"
import base64
import boto3
import logging
import re

from botocore.signers import RequestSigner
from kubernetes import client, config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = "ap-southeast-1"
TEAM_ACCOUNTS = ["409989946510"]
TEAM_ROLES = ["arn:aws:iam::409989946510:role/gameday-quest-TeamRole"]

def lambda_handler(event, context):
    response = get_clusters_data()

    return {
        'statusCode': 200,
        'body': response
    }

def get_clusters_data():
    sts = boto3.client('sts')
    response = []

    # Loop through all team accounts to get EKS cluster data
    for i in range(len(TEAM_ACCOUNTS)):
        team_response = {"id": TEAM_ACCOUNTS[i], "clusters": []}

        # Assume role in Team account
        team_account = sts.assume_role(
            RoleArn=TEAM_ROLES[i],
            RoleSessionName="assume_team_role"
        )

        # Initiate a boto3 client for EKS with the credentials of the team account
        eks = boto3.client('eks',
            aws_access_key_id = team_account['Credentials']['AccessKeyId'],
            aws_secret_access_key = team_account['Credentials']['SecretAccessKey'],
            aws_session_token = team_account['Credentials']['SessionToken'],
            region_name = REGION
        )
        
        # Loop through the EKS clusters in a team account to get the list of Nodegroups and Pods
        for clusterName in eks.list_clusters()['clusters']:
            # Get EKS cluster data
            cluster = eks.describe_cluster(
                name=clusterName
            )['cluster']
            cluster_response = { 'name': cluster['name'], 'status': cluster['status'], 'version': cluster['version'] }

            # Get nodegroups data
            nodegroup_response = []
            nodegroups = eks.list_nodegroups(clusterName=clusterName)['nodegroups']
            for nodegroupName in nodegroups:
                ng = eks.describe_nodegroup(
                    clusterName=clusterName,
                    nodegroupName=nodegroupName
                )
                nodegroup_response.append({ 'name': ng['nodegroup']['nodegroupName'], 'status': ng['nodegroup']['status'], 'version': ng['nodegroup']['version'] })
            
            # Set up Kubernetes client
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
                'users': [{'name': 'user1', "user" : {'token': 
                    get_bearer_token(clusterName, sts, boto3.session.Session(
                        aws_access_key_id = team_account['Credentials']['AccessKeyId'],
                        aws_secret_access_key = team_account['Credentials']['SecretAccessKey'],
                        aws_session_token = team_account['Credentials']['SessionToken'],
                        region_name = REGION
                    )
                )}}]
            }
            config.load_kube_config_from_dict(config_dict=kubeconfig)
            v1 = client.CoreV1Api()

            # Get Pods from all namespaces
            system_pods = []
            pod_list = v1.list_pod_for_all_namespaces(watch=False).items
            for p in pod_list:
                system_pods.append(
                    {
                        'name': p.metadata.name,
                        'image': p.spec.containers[0].image,
                        'status': {
                            p.status.conditions[0].type: p.status.conditions[0].status,
                            p.status.conditions[1].type: p.status.conditions[1].status,
                            p.status.conditions[2].type: p.status.conditions[2].status,
                            p.status.conditions[3].type: p.status.conditions[3].status
                        }
                    }
                )

            team_response["clusters"].append({ 'cluster': cluster_response, 'nodegroups': nodegroup_response, 'systemPods': system_pods })

        response.append(team_response)
    
    return response

def get_bearer_token(clusterName, sts, session):
    "Create authentication token"
    service_id = sts.meta.service_model.service_id

    signer = RequestSigner(
        service_id,
        session.region_name,
        'sts',
        'v4',
        session.get_credentials(),
        session.events
    )
    print(signer)

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
        expires_in=60,
        operation_name=''
    )
    base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

    # remove any base64 encoding padding:
    return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)