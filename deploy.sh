#!/bin/bash
if ! hash aws 2>/dev/null || ! hash pip3 2>/dev/null; then
    echo "This script requires the AWS cli, and pip3 installed"
    exit 2
fi

set -eo pipefail
rm -rf build ; mkdir build ; cd build
cp -r ../functions/* .
pip3 install --target . -r requirements.txt
cd ../
aws cloudformation deploy --template-file cfn-template.yml \
  --stack-name check-eks-cluster \
  --capabilities CAPABILITY_NAMED_IAM
