#!/bin/bash
# Enhanced API Gateway testing script for PC Builder backend
# This script tests all endpoints and provides detailed diagnostics

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default API Gateway URL
DEFAULT_API_URL="https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod"

# Parse command line arguments
API_URL=$DEFAULT_API_URL
TIMEOUT=10
VERBOSE=false
TEST_MALFORMED=false

print_help() {
  echo -e "${BLUE}PC Builder API Gateway Testing Tool${NC}"
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  -u, --url URL       API URL to test (default: $DEFAULT_API_URL)"
  echo "  -t, --timeout SEC   Timeout in seconds for requests (default: 10)"
  echo "  -v, --verbose       Show verbose output"
  echo "  -m, --test-malformed Test with malformed requests to check error handling"
  echo "  -h, --help          Show this help message"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -u|--url)
      API_URL="$2"
      shift 
      shift
      ;;
    -t|--timeout)
      TIMEOUT="$2"
      shift
      shift
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -m|--test-malformed)
      TEST_MALFORMED=true
      shift
      ;;
    -h|--help)
      print_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      print_help
      exit 1
      ;;
  esac
done

# Function to test an endpoint
test_endpoint() {
  local endpoint=$1
  local method=${2:-GET}
  local data=${3:-""}
  local description=${4:-"Testing $endpoint endpoint"}
  
  echo -e "${YELLOW}$description${NC}"
  
  local start_time=$(date +%s.%N)
  
  if [ "$method" == "GET" ]; then
    if [ "$VERBOSE" = true ]; then
      echo -e "${BLUE}curl -s -X $method -m $TIMEOUT \"${API_URL}${endpoint}\"${NC}"
    fi
    RESPONSE=$(curl -s -X $method -m $TIMEOUT "${API_URL}${endpoint}")
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X $method -m $TIMEOUT "${API_URL}${endpoint}")
  else
    if [ "$VERBOSE" = true ]; then
      echo -e "${BLUE}curl -s -X $method -H \"Content-Type: application/json\" -d '$data' -m $TIMEOUT \"${API_URL}${endpoint}\"${NC}"
    fi
    RESPONSE=$(curl -s -X $method -H "Content-Type: application/json" -d "$data" -m $TIMEOUT "${API_URL}${endpoint}")
    STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X $method -H "Content-Type: application/json" -d "$data" -m $TIMEOUT "${API_URL}${endpoint}")
  fi
  
  local end_time=$(date +%s.%N)
  local time_taken=$(echo "$end_time - $start_time" | bc)
  
  echo -e "${BLUE}Status Code: ${STATUS_CODE} (Response time: ${time_taken}s)${NC}"
  
  # Try to format as JSON if possible
  if echo "$RESPONSE" | python3 -m json.tool &>/dev/null; then
    echo "$RESPONSE" | python3 -m json.tool
  else
    # If not valid JSON, show the raw response
    echo -e "${RED}Not valid JSON. Raw response:${NC}"
    echo "$RESPONSE"
  fi
  
  # Analyze status code
  if [[ $STATUS_CODE == 2* ]]; then
    echo -e "${GREEN}✓ Request succeeded${NC}"
  elif [[ $STATUS_CODE == 4* ]]; then
    echo -e "${RED}✗ Client error (HTTP $STATUS_CODE)${NC}"
  elif [[ $STATUS_CODE == 5* ]]; then
    echo -e "${RED}✗ Server error (HTTP $STATUS_CODE)${NC}"
  else
    echo -e "${RED}✗ Unexpected status code: $STATUS_CODE${NC}"
  fi
  
  echo "----------------------------------------"
}

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}       PC Builder API Gateway Test Tool${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "API URL: ${API_URL}"
echo -e "Timeout: ${TIMEOUT}s"
echo "----------------------------------------"

# Test health endpoint
test_endpoint "/health" "GET" "" "Testing /health endpoint"

# Test /graphic-cards endpoint
test_endpoint "/graphic-cards" "GET" "" "Testing /graphic-cards endpoint"

# Test debug endpoints for diagnostics
test_endpoint "/debug/check-s3" "GET" "" "Testing S3 connectivity"
test_endpoint "/debug/diagnostics" "GET" "" "Testing system diagnostics"

# Test malformed requests if specified
if [ "$TEST_MALFORMED" = true ]; then
  echo -e "${YELLOW}Testing error handling with malformed requests${NC}"
  # Test non-existent endpoint
  test_endpoint "/not-found-endpoint" "GET" "" "Testing non-existent endpoint (should return 404)"
  
  # Test malformed JSON body
  test_endpoint "/graphic-cards" "POST" "{malformed-json}" "Testing malformed JSON body"
  
  # Test wrong HTTP method
  test_endpoint "/graphic-cards" "DELETE" "" "Testing wrong HTTP method"
fi

# Analyze results
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}           API Test Summary${NC}"
echo -e "${BLUE}==================================================${NC}"

if [[ $RESPONSE == *"\"status\":\"ok\""* ]]; then
  echo -e "${GREEN}✓ API appears to be working correctly${NC}"
else
  echo -e "${RED}✗ API has issues - see detailed tests above${NC}"
fi

# Check for common issues
if [[ $S3_RESPONSE == *"\"csv_exists\":false"* ]]; then
  echo -e "${RED}✗ CSV file not found in S3. Check S3 bucket configuration and file upload.${NC}"
fi

if [[ $RESPONSE == *"\"error\""* ]]; then
  echo -e "${RED}✗ Error responses detected in API calls.${NC}"
fi

if [[ $RESPONSE == *"\"data_count\":0"* ]]; then
  echo -e "${RED}✗ No data loaded according to responses.${NC}"
fi

echo -e "${YELLOW}Next steps:${NC}"
echo "1. If endpoints are returning errors:"
echo "   - Check AWS credentials and S3 bucket permissions"
echo "   - Verify CSV file is uploaded correctly"
echo "   - Review CloudWatch logs for detailed errors"
echo ""
echo "2. To run the complete workflow:"
echo "   python3 workflow/pc-builder-workflow.py --scrape --upload --cleanup"
echo ""
echo "3. To fix CloudFormation stack issues:"
echo "   python3 fix-stack.py"
echo ""
echo "4. For more detailed diagnostics:"
echo "   ./diagnose-api-issues.sh"
echo "----------------------------------------"
