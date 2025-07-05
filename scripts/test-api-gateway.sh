#!/bin/bash
# API Gateway testing script for PC Builder backend

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# API Gateway URL
API_URL="https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod"

echo -e "${YELLOW}Testing PC Builder API Gateway endpoints${NC}"
echo -e "API URL: ${API_URL}"
echo "----------------------------------------"

# Test health endpoint
echo -e "${YELLOW}Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "${API_URL}/health")
echo $HEALTH_RESPONSE | python3 -m json.tool
echo "----------------------------------------"

# Test /graphic-cards endpoint
echo -e "${YELLOW}Testing /graphic-cards endpoint...${NC}"
CARDS_RESPONSE=$(curl -s "${API_URL}/graphic-cards")

# Check if response looks like JSON and is not empty
if [[ $CARDS_RESPONSE == *"["* && $CARDS_RESPONSE == *"]"* ]]; then
    echo -e "${GREEN}✓ Response is JSON array${NC}"
    
    # Count number of items
    ITEM_COUNT=$(echo $CARDS_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))")
    
    if [ "$ITEM_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $ITEM_COUNT graphic cards${NC}"
        echo "First item sample:"
        echo $CARDS_RESPONSE | python3 -c "import sys, json; data = json.load(sys.stdin); print(json.dumps(data[0], indent=2))" 
    else
        echo -e "${RED}✗ Empty array returned (no graphic cards)${NC}"
        echo $CARDS_RESPONSE
    fi
else
    echo -e "${RED}✗ Invalid or empty response${NC}"
    echo $CARDS_RESPONSE
fi
echo "----------------------------------------"

# Test debug endpoints for diagnostics
echo -e "${YELLOW}Testing /debug/check-s3 endpoint...${NC}"
S3_RESPONSE=$(curl -s "${API_URL}/debug/check-s3")
echo $S3_RESPONSE | python3 -m json.tool
echo "----------------------------------------"

echo -e "${YELLOW}Testing /debug/diagnostics endpoint...${NC}"
DIAG_RESPONSE=$(curl -s "${API_URL}/debug/diagnostics")
echo $DIAG_RESPONSE | python3 -m json.tool
echo "----------------------------------------"

# Check for common issues
echo -e "${YELLOW}Common issues check:${NC}"
if [[ $S3_RESPONSE == *"csv_exists\":false"* ]]; then
    echo -e "${RED}✗ CSV file not found in S3. Check S3 bucket configuration and file upload.${NC}"
fi

if [[ $CARDS_RESPONSE == *"ERROR: No data loaded"* ]]; then
    echo -e "${RED}✗ Error indicator found in data. S3 access likely failing.${NC}"
fi

if [[ $HEALTH_RESPONSE == *"\"data_count\":0"* ]]; then
    echo -e "${RED}✗ No data loaded according to health check.${NC}"
fi

echo "----------------------------------------"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Check AWS credentials and S3 bucket permissions"
echo "2. Verify CSV file is uploaded correctly"
echo "3. Check Lambda execution role permissions"
echo "4. Review CloudWatch logs for detailed errors"
echo "----------------------------------------"
