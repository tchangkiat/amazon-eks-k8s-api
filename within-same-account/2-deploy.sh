#!/bin/bash
if ! hash aws 2>/dev/null || ! hash pip3 2>/dev/null; then
    echo "This script requires the AWS cli, and pip3 installed"
    exit 2
fi

set -eo pipefail
BUCKET_NAME=check-eks-cluster-assets
rm -rf build ; mkdir build ; cd build
cp -r ../functions/* .
pip3 install --target . -r requirements.txt
cd ../
aws cloudformation package --template-file cfn-template.yml --s3-bucket $BUCKET_NAME --output-template-file out.yml
aws cloudformation deploy --template-file out.yml \
  --stack-name amazon-eks-k8s-api \
  --capabilities CAPABILITY_NAMED_IAM
