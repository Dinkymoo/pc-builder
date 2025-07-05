#!/bin/bash

# Script to remove files that have been moved to the new directory structure
# This script uses full absolute paths to ensure proper removal

ROOT_DIR="/Users/daniellevangraan/Documents/sandbox/python-projects/DataScrapingBeautifulSoup"

echo "Starting cleanup of moved files with absolute paths..."

# Remove documentation files that have been moved to docs/
echo "Removing documentation files..."
rm -fv "${ROOT_DIR}/API_GATEWAY_LAMBDA_TROUBLESHOOTING.md"
rm -fv "${ROOT_DIR}/AWS_DEPLOYMENT.md"
rm -fv "${ROOT_DIR}/AWS_LAMBDA_DEPLOYMENT.md"
rm -fv "${ROOT_DIR}/USING_AWS_LAMBDA_API.md"
rm -fv "${ROOT_DIR}/COPILOT_INSTRUCTIONS.md"
rm -fv "${ROOT_DIR}/DEVELOPER_SETUP.md.new"
rm -fv "${ROOT_DIR}/README.md.new"

# Remove AWS scripts that have been moved to scripts/aws/
echo "Removing AWS scripts..."
rm -fv "${ROOT_DIR}/check_aws_permissions.py"
rm -fv "${ROOT_DIR}/check_lambda_permissions.py"
rm -fv "${ROOT_DIR}/check_s3_data.py"
rm -fv "${ROOT_DIR}/upload_to_s3.py"
rm -fv "${ROOT_DIR}/fix-stack.py"
rm -fv "${ROOT_DIR}/recover-stack.sh"

# Remove diagnostic scripts that have been moved to scripts/diagnostics/
echo "Removing diagnostic scripts..."
rm -fv "${ROOT_DIR}/diagnose-api-issues.sh"

# Remove utility scripts that have been moved to scripts/utils/
echo "Removing utility scripts..."
rm -fv "${ROOT_DIR}/scan_all_with_bandit.py"

# Remove startup scripts that have been moved to scripts/start/
echo "Removing startup scripts..."
rm -fv "${ROOT_DIR}/start-backend.sh"
rm -fv "${ROOT_DIR}/start-frontend.sh"
rm -fv "${ROOT_DIR}/start-frontend-with-lambda.sh"

# Remove deployment scripts that have been moved to scripts/deploy/
echo "Removing deployment scripts..."
rm -fv "${ROOT_DIR}/build-lambda-layer.sh"

# Remove setup scripts that have been moved to scripts/setup/
echo "Removing setup scripts..."
rm -fv "${ROOT_DIR}/setup-workflow.py"

# Remove testing scripts that have been moved to tests/
echo "Removing testing scripts..."
rm -fv "${ROOT_DIR}/test-api-gateway.sh"
rm -fv "${ROOT_DIR}/test-api-gateway-enhanced.sh"
rm -fv "${ROOT_DIR}/test_scan_staged.py"
rm -fv "${ROOT_DIR}/test-hooks.py"

# Remove configuration files that have been moved to config/
echo "Removing configuration files..."
rm -fv "${ROOT_DIR}/ecr-policy.json"

# Remove miscellaneous files
echo "Removing miscellaneous files..."
rm -fv "${ROOT_DIR}/aws-upload-images-cli.txt"

echo "Cleanup complete!"
echo "You can now commit your changes."

# List the root directory to verify files are gone
echo "Current directory listing:"
ls -la ${ROOT_DIR}
