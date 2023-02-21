#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

STACK=amazon-eks-k8s-api
BUCKET_NAME=check-eks-cluster-assets
FUNCTION=check-eks-cluster

echo "--- Deleting stack $STACK ---"
aws cloudformation delete-stack --stack-name $STACK
rm out.yml
echo "--- Deleteing bucket $BUCKET_NAME ---"
aws s3 rb --force s3://$BUCKET_NAME
rm bucket-name.txt

echo "--- Deleting log group '/aws/lambda/$FUNCTION' ---"
aws logs delete-log-group --log-group-name /aws/lambda/$FUNCTION