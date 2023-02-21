#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

BUCKET_ID=$(dd if=/dev/random bs=8 count=1 2>/dev/null | od -An -tx1 | tr -d ' \t\n')
BUCKET_NAME=check-eks-cluster-assets-$BUCKET_ID
echo $BUCKET_NAME > bucket-name.txt
aws s3 mb s3://$BUCKET_NAME
