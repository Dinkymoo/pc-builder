#!/usr/bin/env python3
"""
AWS Permission Check Script

This script checks if your current AWS credentials have the necessary permissions
for ECR operations and other services needed by the PC Builder project.

Usage:
  python check_aws_permissions.py
"""

import boto3
import sys
import json
from botocore.exceptions import ClientError, NoCredentialsError
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_aws_credentials():
    """Check if AWS credentials are properly configured."""
    try:
        # Try to get caller identity as a basic authentication check
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        user_arn = identity['Arn']
        account_id = identity['Account']
        logger.info(f"✅ AWS credentials found. Logged in as: {user_arn}")
        logger.info(f"Account ID: {account_id}")
        return True, user_arn, account_id
    except NoCredentialsError:
        logger.error("❌ AWS credentials not found. Set up your credentials by:")
        logger.error("   - Using environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        logger.error("   - Or configure ~/.aws/credentials file")
        return False, None, None
    except ClientError as e:
        logger.error(f"❌ AWS credentials error: {e}")
        return False, None, None
    except Exception as e:
        logger.error(f"❌ Error checking credentials: {type(e).__name__}")
        return False, None, None

def check_permission(service_client, action, resource_arn=None, verbose=True):
    """Check if user has a specific permission using dry run."""
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        user_arn = identity['Arn']
        
        iam = boto3.client('iam')
        
        # Parameters for the simulation
        params = {
            'ActionNames': [action],
            'PolicySourceArn': user_arn
        }
        if resource_arn:
            params['ResourceArns'] = [resource_arn]
            
        response = iam.simulate_principal_policy(**params)
        result = response['EvaluationResults'][0]['EvalDecision']
        
        if result == 'allowed':
            if verbose:
                logger.info(f"✅ Permission check passed: {action}")
            return True
        else:
            if verbose:
                logger.warning(f"⚠️ Permission denied: {action}")
            return False
    except ClientError as e:
        if 'SimulatePrincipalPolicy' in str(e):
            # User doesn't have permission to check their own permissions
            logger.warning(f"⚠️ Cannot simulate policy for {action}. Try the operation directly.")
            return "unknown"
        logger.error(f"❌ Error checking permission {action}: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error checking permission {action}: {type(e).__name__}")
        return False

def test_ecr_permissions(account_id, region="eu-west-3"):
    """Test ECR permissions by trying actual operations."""
    logger.info("\nTesting ECR Permissions:")
    
    # Create a unique repository name for testing
    test_repo = "pc-builder-test-repo"
    
    # Test permissions needed for the workflow
    permissions = [
        ("ecr:CreateRepository", f"arn:aws:ecr:{region}:{account_id}:repository/{test_repo}"),
        ("ecr:DescribeRepositories", f"arn:aws:ecr:{region}:{account_id}:repository/*"),
        ("ecr:GetAuthorizationToken", f"arn:aws:ecr:{region}:{account_id}:*"),
        ("ecr:InitiateLayerUpload", f"arn:aws:ecr:{region}:{account_id}:repository/{test_repo}"),
        ("ecr:PutImage", f"arn:aws:ecr:{region}:{account_id}:repository/{test_repo}")
    ]
    
    results = {}
    for action, resource in permissions:
        result = check_permission(None, action, resource)
        results[action] = result
    
    # Summarize results
    logger.info("\nECR Permission Summary:")
    for action, result in results.items():
        status = "✅ Allowed" if result is True else "❌ Denied" if result is False else "⚠️ Unknown"
        logger.info(f"{status}: {action}")
    
    missing_perms = [action for action, result in results.items() if result is not True]
    if missing_perms:
        logger.warning("\n⚠️ You're missing these ECR permissions:")
        logger.warning("\n".join(missing_perms))
        logger.warning("\nYou'll need these permissions to use the ECR workflow.")
    else:
        logger.info("\n✅ All required ECR permissions are available!")

def suggest_next_steps(account_id):
    """Suggest next steps based on permission check results."""
    logger.info("\n--- Next Steps ---")
    logger.info(f"1. Update the .aws/task-definition.json file:")
    logger.info(f"   Replace YOUR_ACCOUNT_ID with: {account_id}")
    logger.info(f"2. Update the GitHub repository secrets with your AWS credentials")
    logger.info(f"3. Consider using an IAM user with limited permissions for GitHub Actions")
    logger.info(f"4. Follow the instructions in AWS_DEPLOYMENT.md to complete the setup")

def main():
    """Main function."""
    logger.info("=== AWS Permission Check for PC Builder Project ===")
    
    success, user_arn, account_id = check_aws_credentials()
    if not success:
        return 1
    
    # Check ECR permissions
    test_ecr_permissions(account_id)
    
    # Suggest next steps
    suggest_next_steps(account_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
