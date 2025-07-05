#!/bin/bash

# Test script for verifying PC Builder project functionality after reorganization
# This script tests each major component to ensure everything works correctly

# Set colors for better output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Keep track of test results
PASSED=0
FAILED=0
TOTAL=0

# Function to run a test and record the result
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_exit_code="${3:-0}"
    
    echo -e "${BLUE}Running test: ${test_name}${NC}"
    echo "Command: $command"
    eval "$command"
    local exit_code=$?
    
    TOTAL=$((TOTAL + 1))
    
    if [ $exit_code -eq $expected_exit_code ]; then
        echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ FAILED: ${test_name} (Exit code: ${exit_code}, Expected: ${expected_exit_code})${NC}"
        FAILED=$((FAILED + 1))
    fi
    echo "--------------------------------------"
}

# Main script
echo -e "${YELLOW}PC Builder Project - Post-Reorganization Test Script${NC}"
echo "This script will test all major components to verify they work correctly"
echo "after the project reorganization."
echo "========================================"

# 1. Test if docs are accessible
echo -e "${YELLOW}Testing Documentation...${NC}"
run_test "Documentation exists" "test -d ./docs && test -f ./docs/DEVELOPER_GUIDE.md"

# 2. Test if scripts are accessible and executable
echo -e "${YELLOW}Testing Scripts...${NC}"
run_test "Scripts directory structure" "test -d ./scripts/aws && test -d ./scripts/deploy && test -d ./scripts/start"
run_test "Script executability" "test -x ./scripts/start/start-backend.sh"

# 3. Test if tests are accessible
echo -e "${YELLOW}Testing Test Scripts...${NC}"
run_test "Tests directory structure" "test -d ./tests/api && test -d ./tests/aws && test -d ./tests/unit"

# 4. Test if config files are accessible
echo -e "${YELLOW}Testing Config Files...${NC}"
run_test "Config directory" "test -d ./config && test -f ./config/.env.example"

# 5. Test if main project structure is correct
echo -e "${YELLOW}Testing Project Structure...${NC}"
run_test "PC Builder app structure" "test -d ./pc-builder && test -d ./pc-builder/pc-builder-app && test -d ./pc-builder/pc-builder-backend"

# 6. Test AWS credentials (if available)
echo -e "${YELLOW}Testing AWS Integration...${NC}"
run_test "AWS credentials test script" "test -f ./tests/aws/test-aws-credentials.py"

# 7. Test API endpoint test script
echo -e "${YELLOW}Testing API Endpoints...${NC}"
run_test "API testing script" "test -f ./tests/api/test-api-gateway.sh"

# 8. Test workflow script
echo -e "${YELLOW}Testing Workflow Script...${NC}"
run_test "PC Builder workflow script" "test -f ./workflow/pc-builder-workflow.py"

# Print test summary
echo "========================================"
echo -e "${BLUE}Test Summary:${NC}"
echo -e "Total Tests: ${TOTAL}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
echo -e "${RED}Failed: ${FAILED}${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! The project structure is correctly organized.${NC}"
else
    echo -e "${RED}❌ Some tests failed. Review the output above for details.${NC}"
fi

echo "========================================"
echo "To run more in-depth functional tests, try the following commands:"
echo "1. Start the backend: ./scripts/start/start-backend.sh"
echo "2. Test S3 connectivity: python scripts/aws/check_s3_data.py"
echo "3. Run API tests: ./tests/api/test-api-gateway.sh"

# Exit with failure if any tests failed
[ $FAILED -eq 0 ]
