#!/bin/bash

# This script is a comprehensive cleanup for the PC Builder project reorganization
# It removes all duplicate files and temporary files created during the reorganization process

ROOT_DIR="/Users/daniellevangraan/Documents/sandbox/python-projects/DataScrapingBeautifulSoup"
cd "${ROOT_DIR}" || exit 1

echo "=== PC Builder Project Final Cleanup ==="
echo "First, replacing files with their newer versions..."

# Replace README.md with README.md.new
if [ -f README.md.new ]; then
  echo "Replacing README.md with newer version..."
  mv -v README.md.new README.md
fi

# Replace DEVELOPER_SETUP.md with DEVELOPER_SETUP.md.new if needed
if [ -f DEVELOPER_SETUP.md.new ]; then
  echo "Replacing DEVELOPER_SETUP.md with newer version..."
  mv -v DEVELOPER_SETUP.md.new DEVELOPER_SETUP.md
fi

echo "Removing duplicate documentation files..."

# Original files that were moved to docs/ directory
rm -fv API_GATEWAY_LAMBDA_TROUBLESHOOTING.md
rm -fv AWS_DEPLOYMENT.md
rm -fv AWS_LAMBDA_DEPLOYMENT.md
rm -fv USING_AWS_LAMBDA_API.md
rm -fv COPILOT_INSTRUCTIONS.md

echo "Removing duplicate scripts..."

# Scripts that were moved to scripts/ and tests/ directories
rm -fv check_aws_permissions.py
rm -fv check_lambda_permissions.py
rm -fv check_s3_data.py
rm -fv upload_to_s3.py
rm -fv fix-stack.py
rm -fv recover-stack.sh
rm -fv diagnose-api-issues.sh
rm -fv scan_all_with_bandit.py
rm -fv start-backend.sh
rm -fv start-frontend.sh
rm -fv start-frontend-with-lambda.sh
rm -fv build-lambda-layer.sh
rm -fv setup-workflow.py
rm -fv test-api-gateway.sh
rm -fv test-api-gateway-enhanced.sh
rm -fv test_scan_staged.py
rm -fv test-hooks.py
rm -fv ecr-policy.json
rm -fv aws-upload-images-cli.txt

echo "Removing temporary reorganization files..."

# Temporary files created during reorganization
rm -fv REORGANIZATION_SUMMARY.md
rm -fv cleanup.sh
rm -fv cleanup-absolute.sh
rm -fv final-cleanup.sh

echo "=== Cleanup Complete ==="
echo "The repository structure is now clean and organized."
echo "Use the commit-changes.sh script to commit all changes."

# Don't remove this file itself yet - let the user verify first
