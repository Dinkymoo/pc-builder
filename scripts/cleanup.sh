#!/bin/bash

# Script to remove files that have been moved to the new directory structure
# This script is meant to be run from the project root

echo "Starting cleanup of moved files..."

# Remove documentation files that have been moved to docs/
echo "Removing documentation files..."
rm -f API_GATEWAY_LAMBDA_TROUBLESHOOTING.md
rm -f AWS_DEPLOYMENT.md
rm -f AWS_LAMBDA_DEPLOYMENT.md
rm -f USING_AWS_LAMBDA_API.md
rm -f COPILOT_INSTRUCTIONS.md
rm -f DEVELOPER_SETUP.md.new
rm -f README.md.new

# Remove AWS scripts that have been moved to scripts/aws/
echo "Removing AWS scripts..."
rm -f check_aws_permissions.py
rm -f check_lambda_permissions.py
rm -f check_s3_data.py
rm -f upload_to_s3.py
rm -f fix-stack.py
rm -f recover-stack.sh

# Remove diagnostic scripts that have been moved to scripts/diagnostics/
echo "Removing diagnostic scripts..."
rm -f diagnose-api-issues.sh

# Remove utility scripts that have been moved to scripts/utils/
echo "Removing utility scripts..."
rm -f scan_all_with_bandit.py

# Remove startup scripts that have been moved to scripts/start/
echo "Removing startup scripts..."
rm -f start-backend.sh
rm -f start-frontend.sh
rm -f start-frontend-with-lambda.sh

# Remove deployment scripts that have been moved to scripts/deploy/
echo "Removing deployment scripts..."
rm -f build-lambda-layer.sh

# Remove setup scripts that have been moved to scripts/setup/
echo "Removing setup scripts..."
rm -f setup-workflow.py

# Remove testing scripts that have been moved to tests/
echo "Removing testing scripts..."
rm -f test-api-gateway.sh
rm -f test-api-gateway-enhanced.sh
rm -f test_scan_staged.py
rm -f test-hooks.py

# Remove configuration files that have been moved to config/
echo "Removing configuration files..."
rm -f ecr-policy.json

# Remove miscellaneous files
echo "Removing miscellaneous files..."
rm -f aws-upload-images-cli.txt

echo "Cleanup complete!"
echo "You can now commit your changes."
