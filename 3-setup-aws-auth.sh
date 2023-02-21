#!/bin/bash
if ! hash aws 2>/dev/null || ! hash kubectl 2>/dev/null || ! hash eksctl 2>/dev/null; then
    echo "This script requires the AWS cli, kubectl, and eksctl installed"
    exit 2
fi

set -eo pipefail

ROLE_ARN=$(aws cloudformation describe-stacks --stack-name amazon-eks-k8s-api --query "Stacks[0].Outputs[?OutputKey=='Role'].OutputValue" --output text)
CLUSTER_NAME=eks-ca-demo

echo
echo ==========
echo Update aws-auth configmap with a new mapping
echo ==========
echo Cluster: $CLUSTER_NAME
echo RoleArn: $ROLE_ARN
echo
while true; do
    read -p "Do you want to create the aws-auth configmap entry? (y/n)" response
    case $response in
        [Yy]* ) eksctl create iamidentitymapping --cluster $CLUSTER_NAME --group system:masters --arn $ROLE_ARN; break;;
        [Nn]* ) break;;
        * ) echo "Response must start with y or n.";;
    esac
done

