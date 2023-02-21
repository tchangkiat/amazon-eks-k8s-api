#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

STACK=amazon-eks-k8s-api
BUCKET_NAME=$(cat bucket-name.txt)
FUNCTION=check-eks-cluster
aws cloudformation delete-stack --stack-name $STACK
echo "Deleted stack $STACK"
rm out.yml
aws s3 rb --force s3://$ARTIFACT_BUCKET
echo "Deleted bucket $BUCKET_NAME"
rm bucket-name.txt
aws logs delete-log-group --log-group-name /aws/lambda/$FUNCTION
echo "Deleted log group '/aws/lambda/$FUNCTION'"