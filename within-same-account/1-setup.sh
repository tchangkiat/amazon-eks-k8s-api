#!/bin/bash
if ! hash aws 2>/dev/null; then
    echo "This script requires the AWS cli installed"
    exit 2
fi

BUCKET_NAME=check-eks-cluster-assets
aws s3 mb s3://$BUCKET_NAME
