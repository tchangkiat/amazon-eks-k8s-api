# Trusted Entities

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::<Account-2-Id>:role/check-eks-cluster-LambdaExecutionRole"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

# Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "eksPermissions",
      "Effect": "Allow",
      "Action": [
        "eks:ListNodegroups",
        "eks:DescribeFargateProfile",
        "eks:DescribeAddonConfiguration",
        "eks:ListTagsForResource",
        "eks:ListAddons",
        "eks:DescribeAddon",
        "eks:ListFargateProfiles",
        "eks:DescribeNodegroup",
        "eks:DescribeIdentityProviderConfig",
        "eks:ListUpdates",
        "eks:DescribeUpdate",
        "eks:AccessKubernetesApi",
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:DescribeAddonVersions",
        "eks:ListIdentityProviderConfigs"
      ],
      "Resource": "*"
    }
  ]
}
```
