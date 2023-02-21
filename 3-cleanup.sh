#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

STACK=amazon-eks-k8s-api
BUCKET_NAME=check-eks-cluster-assets
FUNCTION=check-eks-cluster

aws cloudformation delete-stack --stack-name $STACK
rm out.yml
aws s3 rb --force s3://$BUCKET_NAME
aws logs delete-log-group --log-group-name /aws/lambda/$FUNCTION