#!/bin/bash

# Script to clean up old files that have been moved to the new directory structure
# This script is designed to be run from the project root directory

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

FORCE=false
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
  FORCE=true
fi

ROOT_DIR="$(pwd)"
echo -e "${BLUE}PC Builder Project - Cleanup Script${NC}"
echo -e "${YELLOW}This script will remove files that have been moved to the new directory structure.${NC}"
echo -e "${YELLOW}Make sure you've already copied all necessary files to their new locations.${NC}"

if [ "$FORCE" = false ]; then
  read -p "Continue? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Cleanup aborted.${NC}"
    exit 1
  fi
else
  echo -e "${YELLOW}Force mode enabled. Proceeding without confirmation.${NC}"
fi

# Function to safely remove a file if it exists
safe_remove() {
  if [ -f "$1" ]; then
    echo -e "${YELLOW}Removing: $1${NC}"
    rm "$1"
    echo -e "${GREEN}✓ Removed${NC}"
  else
    echo -e "${BLUE}File not found, skipping: $1${NC}"
  fi
}

echo -e "\n${BLUE}Removing documentation files moved to docs/ directory...${NC}"
safe_remove "$ROOT_DIR/API_GATEWAY_LAMBDA_TROUBLESHOOTING.md"
safe_remove "$ROOT_DIR/AWS_DEPLOYMENT.md"
safe_remove "$ROOT_DIR/AWS_LAMBDA_DEPLOYMENT.md"
safe_remove "$ROOT_DIR/USING_AWS_LAMBDA_API.md"
safe_remove "$ROOT_DIR/COPILOT_INSTRUCTIONS.md"
safe_remove "$ROOT_DIR/DEVELOPER_SETUP.md.new"

echo -e "\n${BLUE}Removing AWS scripts moved to scripts/aws/ directory...${NC}"
safe_remove "$ROOT_DIR/check_aws_permissions.py"
safe_remove "$ROOT_DIR/check_lambda_permissions.py"
safe_remove "$ROOT_DIR/check_s3_data.py"
safe_remove "$ROOT_DIR/upload_to_s3.py"
safe_remove "$ROOT_DIR/fix-stack.py"
safe_remove "$ROOT_DIR/recover-stack.sh"

echo -e "\n${BLUE}Removing diagnostic scripts moved to scripts/diagnostics/ directory...${NC}"
safe_remove "$ROOT_DIR/diagnose-api-issues.sh"

echo -e "\n${BLUE}Removing utility scripts moved to scripts/utils/ directory...${NC}"
safe_remove "$ROOT_DIR/scan_all_with_bandit.py"

echo -e "\n${BLUE}Removing startup scripts moved to scripts/start/ directory...${NC}"
safe_remove "$ROOT_DIR/start-backend.sh"
safe_remove "$ROOT_DIR/start-frontend.sh"
safe_remove "$ROOT_DIR/start-frontend-with-lambda.sh"

echo -e "\n${BLUE}Removing deployment scripts moved to scripts/deploy/ directory...${NC}"
safe_remove "$ROOT_DIR/build-lambda-layer.sh"

echo -e "\n${BLUE}Removing setup scripts moved to scripts/setup/ directory...${NC}"
safe_remove "$ROOT_DIR/setup-workflow.py"

echo -e "\n${BLUE}Removing testing scripts moved to tests/ directory...${NC}"
safe_remove "$ROOT_DIR/test-api-gateway.sh"
safe_remove "$ROOT_DIR/test-api-gateway-enhanced.sh"
safe_remove "$ROOT_DIR/test_scan_staged.py"
safe_remove "$ROOT_DIR/test-hooks.py"

echo -e "\n${BLUE}Removing configuration files moved to config/ directory...${NC}"
safe_remove "$ROOT_DIR/ecr-policy.json"
# Note: We're not removing .env from root as that may still be needed for some scripts

echo -e "\n${GREEN}Cleanup complete!${NC}"
echo -e "${BLUE}The project structure has been updated according to the new organization.${NC}"
echo -e "${BLUE}Please update any scripts or documentation that reference the old file paths.${NC}"
