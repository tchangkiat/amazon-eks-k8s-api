# amazon-eks-k8s-api

## Setup

### Account 1 - contains the EKS cluster(s) and role to be assumed by Lambda function in account 2

1. Create an IAM role based on the configuration in "account-1-iam-role.md". Role name should be "gameday-quest-TeamRole" if you do not want to change the role name in check-eks-cluster.py.

2. Create an EKS cluster and ensure that the cluster's API server endpoint access is set to "Public and Private".

3. Create IAM identity mapping using eksctl:

```bash
eksctl create iamidentitymapping --cluster <EKS_CLUSTER_NAME> --group system:masters --arn <ROLE_ARN_CREATED_IN_1>
```

### Account 2 - contains the Lambda function

2. To set up, execute:

```bash
sh 1-setup.sh
sh 2-deploy.sh
```

3. To cleanup, execute:

```bash
sh 3-cleanup.sh
```
