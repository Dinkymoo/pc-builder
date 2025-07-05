#!/usr/bin/env python3
"""
AWS Lambda Permission Check Script

This script checks if your current AWS credentials have the necessary permissions
for AWS Lambda and SAM deployments.

Usage:
  python check_lambda_permissions.py
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

def check_sam_permissions(account_id, region="eu-west-3"):
    """Test permissions needed for SAM deployments."""
    logger.info("\nTesting AWS SAM Deployment Permissions:")
    
    # Services and actions required for SAM deployment
    services = {
        "CloudFormation": [
            "cloudformation:CreateStack",
            "cloudformation:DescribeStacks",
            "cloudformation:UpdateStack",
            "cloudformation:DeleteStack",
            "cloudformation:CreateChangeSet",
            "cloudformation:ExecuteChangeSet",
            "cloudformation:DescribeChangeSet"
        ],
        "Lambda": [
            "lambda:CreateFunction",
            "lambda:GetFunction",
            "lambda:DeleteFunction",
            "lambda:UpdateFunctionCode",
            "lambda:UpdateFunctionConfiguration",
            "lambda:AddPermission"
        ],
        "IAM": [
            "iam:CreateRole",
            "iam:GetRole",
            "iam:DeleteRole",
            "iam:AttachRolePolicy",
            "iam:DetachRolePolicy",
            "iam:PutRolePolicy"
        ],
        "API Gateway": [
            "apigateway:POST",
            "apigateway:GET",
            "apigateway:DELETE",
            "apigateway:PUT"
        ],
        "S3": [
            "s3:CreateBucket",
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject",
            "s3:ListBucket"
        ]
    }
    
    results = {}
    for service, actions in services.items():
        logger.info(f"\nChecking {service} permissions:")
        service_results = {}
        for action in actions:
            resource = "*"  # General check, would need specific ARNs for detailed check
            result = check_permission(action, resource, verbose=True)
            service_results[action] = result
        
        results[service] = service_results
    
    # Calculate permissions summary
    service_summary = {}
    for service, actions in results.items():
        allowed = sum(1 for action, result in actions.items() if result is True)
        total = len(actions)
        service_summary[service] = {
            "allowed": allowed,
            "total": total,
            "percentage": round((allowed / total) * 100)
        }
    
    # Display summary
    logger.info("\n=== PERMISSIONS SUMMARY ===")
    total_allowed = sum(summary["allowed"] for summary in service_summary.values())
    total_permissions = sum(summary["total"] for summary in service_summary.values())
    overall_percentage = round((total_allowed / total_permissions) * 100) if total_permissions > 0 else 0
    
    logger.info(f"Overall: {total_allowed}/{total_permissions} permissions ({overall_percentage}%)")
    
    for service, summary in service_summary.items():
        bar_length = 20
        filled_length = int(summary["percentage"] / 100 * bar_length)
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        logger.info(f"{service}: {summary['allowed']}/{summary['total']} [{bar}] {summary['percentage']}%")
    
    # Provide deployment feasibility assessment
    if overall_percentage >= 80:
        logger.info("\n✅ You have sufficient permissions for AWS SAM deployment!")
    elif overall_percentage >= 50:
        logger.warning("\n⚠️ You have some permissions for SAM deployment but may encounter issues.")
        logger.warning("   Consider requesting additional permissions or using the --guided flag.")
    else:
        logger.error("\n❌ You don't have enough permissions for SAM deployment.")
        logger.error("   Please contact your AWS administrator for the necessary permissions.")

def check_permission(action, resource="*", verbose=True):
    """Check if user has a specific permission by simulating the policy."""
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
        if resource and resource != "*":
            params['ResourceArns'] = [resource]
            
        response = iam.simulate_principal_policy(**params)
        result = response['EvaluationResults'][0]['EvalDecision']
        
        if result == 'allowed':
            if verbose:
                logger.info(f"✅ {action}")
            return True
        else:
            if verbose:
                logger.warning(f"❌ {action}")
            return False
    except ClientError as e:
        if 'SimulatePrincipalPolicy' in str(e):
            # User doesn't have permission to check their own permissions
            if verbose:
                logger.warning(f"⚠️ {action} - Cannot determine (no permission to simulate policy)")
            return "unknown"
        if verbose:
            logger.error(f"❌ {action} - Error: {str(e)}")
        return False
    except Exception as e:
        if verbose:
            logger.error(f"❌ {action} - Error: {type(e).__name__}")
        return False

def suggest_next_steps():
    """Suggest next steps for SAM deployment."""
    logger.info("\n=== NEXT STEPS ===")
    logger.info("1. Navigate to your backend directory:")
    logger.info("   cd pc-builder/pc-builder-backend")
    logger.info("\n2. Build your SAM application:")
    logger.info("   sam build")
    logger.info("\n3. Deploy with guided setup (easiest option):")
    logger.info("   sam deploy --guided")
    logger.info("\nOr use the deployment script:")
    logger.info("   ./deploy-lambda.sh")

def main():
    """Main function."""
    logger.info("=== AWS Lambda Deployment Permission Check ===")
    
    success, user_arn, account_id = check_aws_credentials()
    if not success:
        return 1
    
    # Check SAM deployment permissions
    check_sam_permissions(account_id)
    
    # Suggest next steps
    suggest_next_steps()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
