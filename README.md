# amazon-eks-k8s-api

## Setup

### In the account which contains the EKS cluster(s) and role to be assumed

1. Create an EKS cluster and ensure that the cluster's API server endpoint access is set to "Public and Private".

### In the account which contains the Lambda function

2. To set up, execute:

```bash
sh 1-setup.sh
sh 2-deploy.sh
```

3. To cleanup, execute:

```bash
sh 3-cleanup.sh
```
