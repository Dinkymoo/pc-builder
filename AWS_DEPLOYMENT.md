# AWS Deployment Guide for PC Builder

This document provides instructions for deploying the PC Builder application to AWS using GitHub Actions and Amazon ECS.

## Prerequisites

1. An AWS account with appropriate permissions
2. GitHub repository with the PC Builder code
3. AWS CLI installed and configured locally (for initial setup)

## Initial AWS Setup

### 1. Create an ECR Repository

```bash
aws ecr create-repository --repository-name pc-builder-repository --region eu-west-3
```

### 2. Create an ECS Cluster

```bash
aws ecs create-cluster --cluster-name pc-builder-cluster --region eu-west-3
```

### 3. Create IAM Roles

You need two IAM roles:
- `ecsTaskExecutionRole`: Allows ECS to pull container images and publish logs
- `pc-builder-task-role`: Allows the application to access AWS services like S3

Follow AWS documentation to create these roles with appropriate permissions.

### 4. Store Secrets in AWS Secrets Manager

Instead of using hardcoded credentials, store them in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name pc-builder/aws-credentials \
  --secret-string '{"AWS_ACCESS_KEY_ID":"your-key","AWS_SECRET_ACCESS_KEY":"your-secret"}' \
  --region eu-west-3
```

### 5. Update Task Definition

Edit `.aws/task-definition.json` to replace:
- `YOUR_ACCOUNT_ID` with your actual AWS account ID
- Update ARNs for roles and secrets as needed

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
