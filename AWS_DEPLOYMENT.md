# AWS Deployment Guide for PC Builder

This document provides instructions for deploying the PC Builder application to AWS using GitHub Actions and Amazon ECS.

## Prerequisites

1. An AWS account with appropriate permissions
2. GitHub repository with the PC Builder code
3. AWS CLI installed and configured locally (for initial setup)

## Initial AWS Setup

### 1. Set up IAM Permissions for ECR

Before creating repositories, ensure your IAM user has the necessary permissions:

```bash
# Create an IAM policy for ECR access
aws iam create-policy \
    --policy-name pc-builder-ecr-policy \
    --policy-document file://ecr-policy.json

# Attach the policy to your user
aws iam attach-user-policy \
    --user-name YOUR_USERNAME \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/pc-builder-ecr-policy
```

The policy file (`ecr-policy.json`) should contain permissions for all ECR operations needed.

If you don't have permission to create policies, contact your AWS administrator to grant you these ECR permissions.

### 2. Create an ECR Repository

Once you have the correct permissions:

```bash
aws ecr create-repository --repository-name pc-builder-repository --region eu-west-3
```

### 3. Create an ECS Cluster

```bash
aws ecs create-cluster --cluster-name pc-builder-cluster --region eu-west-3
```

### 4. Create IAM Roles

You need two IAM roles:
- `ecsTaskExecutionRole`: Allows ECS to pull container images and publish logs
- `pc-builder-task-role`: Allows the application to access AWS services like S3

Create these roles using the AWS Management Console or CLI:

```bash
# Create the ECS task execution role
aws iam create-role \
    --role-name ecsTaskExecutionRole \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'

# Attach the Amazon managed policy for task execution
aws iam attach-role-policy \
    --role-name ecsTaskExecutionRole \
    --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create the task role for application permissions
aws iam create-role \
    --role-name pc-builder-task-role \
    --assume-role-policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "ecs-tasks.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'

# Create and attach a policy for S3 access
aws iam put-role-policy \
    --role-name pc-builder-task-role \
    --policy-name S3Access \
    --policy-document '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "s3:GetObject",
            "s3:ListBucket"
          ],
          "Resource": [
            "arn:aws:s3:::pc-builder-bucket-dvg-2025",
            "arn:aws:s3:::pc-builder-bucket-dvg-2025/*"
          ]
        }
      ]
    }'
```

If you don't have permission to create these roles, work with your AWS administrator.

### 5. Store Secrets in AWS Secrets Manager

Instead of using hardcoded credentials, store them in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name pc-builder/aws-credentials \
  --secret-string '{"AWS_ACCESS_KEY_ID":"your-key","AWS_SECRET_ACCESS_KEY":"your-secret"}' \
  --region eu-west-3
```

### 6. Update Task Definition

Edit `.aws/task-definition.json` to replace:
- `YOUR_ACCOUNT_ID` with your actual AWS account ID
- Update ARNs for roles and secrets as needed

#### Simplified Task Definition

If you don't have access to AWS Secrets Manager, you can use the simplified task definition:

```bash
# Use the simplified task definition instead
cp .aws/task-definition-simplified.json .aws/task-definition.json
```

The simplified version uses environment variables in GitHub Actions secrets instead of AWS Secrets Manager, which requires fewer AWS permissions to set up.

## GitHub Actions Setup

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository:
- `AWS_ACCESS_KEY_ID`: AWS access key with permissions to deploy
- `AWS_SECRET_ACCESS_KEY`: Corresponding secret key

### 2. Update Environment Variables

In `.github/workflows/aws.yml`, update:
- `AWS_REGION`: Your AWS region
- `ECR_REPOSITORY`: Your ECR repository name
- `ECS_SERVICE`: Your ECS service name
- `ECS_CLUSTER`: Your ECS cluster name

## Deploy Process

1. Push to the main branch triggers the GitHub Action
2. The backend Dockerfile is built and pushed to ECR
3. The ECS task definition is updated with the new image
4. The ECS service is updated with the new task definition

## Manual Deployment

You can also deploy manually:

```bash
# Build and tag the image locally
cd pc-builder/pc-builder-backend
docker build -t your-account-id.dkr.ecr.eu-west-3.amazonaws.com/pc-builder-repository:latest .

# Log in to ECR
aws ecr get-login-password --region eu-west-3 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.eu-west-3.amazonaws.com

# Push the image
docker push your-account-id.dkr.ecr.eu-west-3.amazonaws.com/pc-builder-repository:latest

# Update the ECS service
aws ecs update-service --cluster pc-builder-cluster --service pc-builder-service --force-new-deployment
```

## Testing the Deployment

Once deployed, your API will be available at:
- `http://your-load-balancer-url/`
- Health check: `http://your-load-balancer-url/health`

## Troubleshooting

### Common Issues

1. **Authentication Failures**: Ensure your GitHub secrets are correctly set up
2. **Permission Errors**: Verify IAM roles have proper permissions
3. **Build Failures**: Check your Dockerfile and build context
4. **Task Definition Errors**: Validate your task definition JSON format

### Working with Limited AWS Permissions

If you're encountering permission errors and don't have administrative access to add the necessary permissions, consider these alternatives:

1. **Request specific permissions** from your AWS administrator:
   ```
   ecr:CreateRepository, ecr:DescribeRepositories, ecr:GetRepositoryPolicy,
   ecr:SetRepositoryPolicy, ecr:DeleteRepository, ecr:InitiateLayerUpload,
   ecr:UploadLayerPart, ecr:CompleteLayerUpload, ecr:PutImage,
   ecr:BatchCheckLayerAvailability, ecr:GetDownloadUrlForLayer,
   ecr:BatchGetImage, ecr:GetAuthorizationToken
   ```

2. **Use an existing ECR repository** if available:
   ```bash
   # List available repositories
   aws ecr describe-repositories --region eu-west-3
   ```

3. **Deploy as a Lambda function** instead of ECS (requires less permissions):
   ```bash
   # Package the application
   cd pc-builder/pc-builder-backend
   sam package --template-file template.yaml --s3-bucket YOUR_DEPLOYMENT_BUCKET --output-template-file packaged.yaml
   
   # Deploy using SAM
   sam deploy --template-file packaged.yaml --stack-name pc-builder-stack --capabilities CAPABILITY_IAM
   ```

### Debugging

Check AWS CloudWatch Logs:
```bash
aws logs get-log-events --log-group-name "/ecs/pc-builder-backend" --log-stream-name "latest" --region eu-west-3
```

## Security Best Practices

1. Use IAM roles with least privilege
2. Store sensitive information in AWS Secrets Manager
3. Restrict network access to your ECS services
4. Regularly rotate credentials
5. Use VPC endpoints to access AWS services without traversing the internet
