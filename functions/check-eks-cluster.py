import boto3
import json

def lambda_handler(event, context):
    eks = boto3.client('eks')
    
    response = []
    
    for clusterName in eks.list_clusters()['clusters']:
        cluster = eks.describe_cluster(
            name=clusterName
        )
        cluster_response = { 'name': cluster['cluster']['name'], 'status': cluster['cluster']['status'], 'version': cluster['cluster']['version'] }
        
        nodegroup_response = []
        for nodegroupName in eks.list_nodegroups(clusterName=clusterName)['nodegroups']:
            ng = eks.describe_nodegroup(
                clusterName=clusterName,
                nodegroupName=nodegroupName
            )
            nodegroup_response.append({ 'name': ng['nodegroup']['nodegroupName'], 'status': ng['nodegroup']['status'], 'version': ng['nodegroup']['version'] })
            
        response.append({ 'cluster': cluster_response, 'nodegroups': nodegroup_response, })
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }