#!/bin/bash
# Enhanced Deploy FastAPI backend to AWS Lambda using SAM
# With options to fix common dependency issues

# Exit on any error
set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to the backend directory
cd "$(dirname "$0")"

# Parse command line arguments
USE_LAYER=false
FIX_DEPS=false
DOWNGRADE=false

while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --use-layer)
      USE_LAYER=true
      shift
      ;;
    --fix-deps)
      FIX_DEPS=true
      shift
      ;;
    --downgrade)
      DOWNGRADE=true
      shift
      ;;
    --help)
      echo -e "${BLUE}Enhanced PC Builder Lambda Deployment${NC}"
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --use-layer    Use a Lambda Layer for dependencies"
      echo "  --fix-deps     Fix dependency issues before deployment"
      echo "  --downgrade    Downgrade pydantic to v1.x for Lambda compatibility"
      echo "  --help         Show this help message"
      echo
      echo "Features:"
      echo "  • Enhanced error diagnostics for SAM deployment failures"
      echo "  • Auto-detection and analysis of Lambda logs"
      echo "  • S3 data freshness verification"
      echo "  • JSON response analysis and troubleshooting"
      echo "  • Workflow data integration verification"
      echo
      echo "Typical usage:"
      echo "  1. First attempt: $0"
      echo "  2. If dependencies fail: $0 --fix-deps"
      echo "  3. For complex dependencies: $0 --use-layer"
      exit 0
      ;;
    *)
      shift
      ;;
  esac
done

# Check if we need to fix dependencies
if [ "$FIX_DEPS" = true ] || [ "$DOWNGRADE" = true ]; then
  echo -e "${YELLOW}Fixing dependencies for Lambda compatibility...${NC}"
  
  # Create a backup of the original requirements.txt
  cp requirements.txt requirements.txt.bak
  
  # Use the Lambda-compatible requirements
  cp requirements-lambda.txt requirements.txt
  
  echo -e "${GREEN}✓ Using Lambda-compatible dependencies${NC}"
fi

# Check if we need to create a Lambda Layer
if [ "$USE_LAYER" = true ]; then
  echo -e "${YELLOW}Creating Lambda Layer with compatible dependencies...${NC}"
  
  # Create directories for Lambda Layer
  mkdir -p lambda-layer/python
  
  # Install packages with platform-specific binaries
  pip install --platform manylinux2014_x86_64 \
    --target=lambda-layer/python \
    --implementation cp \
    --python-version 3.11 \
    --only-binary=:all: \
    --requirement requirements.txt
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing packages for Lambda Layer. Aborting.${NC}"
    exit 1
  fi
  
  # Create a ZIP file of the layer
  cd lambda-layer
  zip -r ../lambda-layer.zip python/
  cd ..
  
  echo -e "${GREEN}✓ Created Lambda Layer with compatible dependencies${NC}"
  
  # Update template.yaml to use the Lambda Layer
  if ! grep -q "DependenciesLayer" template.yaml; then
    echo -e "${YELLOW}Adding Lambda Layer to template.yaml...${NC}"
    
    # Create a temporary file
    TEMP_FILE=$(mktemp)
    
    # Add the layer to the template
    awk '/Resources:/{print;print "  DependenciesLayer:";print "    Type: AWS::Serverless::LayerVersion";print "    Properties:";print "      ContentUri: ./lambda-layer.zip";print "      CompatibleRuntimes:";print "        - python3.11";next}1' template.yaml > $TEMP_FILE
    
    # Add the layer to the function
    awk '/FastApiFunction:/{layer_added=0} /Properties:/ && !layer_added && layer_section{print;print "      Layers:";print "        - !Ref DependenciesLayer";layer_added=1;next} layer_section{layer_section=0} /FastApiFunction:/{layer_section=1} 1' $TEMP_FILE > template.yaml
    
    rm $TEMP_FILE
    
    echo -e "${GREEN}✓ Updated template.yaml with Lambda Layer${NC}"
  fi
fi

echo -e "${YELLOW}🛠️ Building the SAM application...${NC}"
sam build

echo -e "${YELLOW}🚀 Deploying to AWS Lambda...${NC}"
# If the stack is in UPDATE_FAILED state, use --disable-rollback
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" == "UPDATE_FAILED" ] || [ "$STACK_STATUS" == "UPDATE_ROLLBACK_FAILED" ]; then
  echo -e "${YELLOW}⚠️ Stack is in $STACK_STATUS state. Using --disable-rollback to recover...${NC}"
  DEPLOY_OUTPUT=$(sam deploy --stack-name pc-builder --disable-rollback --capabilities CAPABILITY_IAM 2>&1)
  DEPLOY_STATUS=$?
else
  DEPLOY_OUTPUT=$(sam deploy --guided 2>&1)
  DEPLOY_STATUS=$?
fi

if [ $DEPLOY_STATUS -eq 0 ]; then
  echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
else
  # If deployment failed, diagnose the issue
  diagnose_sam_failure "$DEPLOY_OUTPUT"
  echo -e "${RED}Deployment failed. Please fix the issues and try again.${NC}"
  exit 1
fi
  
  # Get the API URL
  API_URL=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text)
  
  echo -e "${BLUE}🌐 Your API is now available at:${NC}"
  echo "$API_URL"
  
  echo -e "${YELLOW}🔍 Testing the health endpoint...${NC}"
  HEALTH_RESPONSE=$(curl -s "${API_URL}health")
  
  # Show the raw response first 100 characters
  echo "Raw response first 100 characters:"
  echo "$HEALTH_RESPONSE" | head -c 100
  echo -e "\n"
  
  # Use our analysis function to diagnose issues
  analyze_json_response "$HEALTH_RESPONSE" "health"
  
  # Get HTTP status code to provide more context
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}health")
  echo -e "${BLUE}HTTP Status Code: ${HTTP_STATUS}${NC}"
  
  if [ "$HTTP_STATUS" != "200" ]; then
    echo -e "${RED}Non-success status code received!${NC}"
    echo -e "${YELLOW}This indicates an issue with your API Gateway or Lambda function.${NC}"
  fi
  
  echo -e "${YELLOW}📋 Testing the graphics cards endpoint...${NC}"
  GRAPHICS_RESPONSE=$(curl -s "${API_URL}graphic-cards")
  
  # First show the raw response
  echo "Raw response first 100 characters:"
  echo "$GRAPHICS_RESPONSE" | head -c 100
  echo -e "\n"
  
  # Use our analysis function to diagnose issues
  analyze_json_response "$GRAPHICS_RESPONSE" "graphic-cards"
  
  # If we get a jq error, try diagnosing specific issues
  if ! echo "$GRAPHICS_RESPONSE" | jq '.' &>/dev/null; then
    echo -e "${YELLOW}Attempting to diagnose parsing errors:${NC}"
    
    # Check if response might have a BOM or other special characters
    HEX_DUMP=$(echo "$GRAPHICS_RESPONSE" | hexdump -C | head -1)
    echo -e "${BLUE}Hex dump of first bytes:${NC} $HEX_DUMP"
    
    # Check for specific API Gateway/Lambda error patterns
    if echo "$GRAPHICS_RESPONSE" | grep -q "Internal Server Error"; then
      echo -e "${RED}API Gateway returned a 500 Internal Server Error.${NC}"
      echo -e "${YELLOW}This usually indicates an error in the Lambda function. Check the Lambda logs.${NC}"
    elif echo "$GRAPHICS_RESPONSE" | grep -q "Task timed out"; then
      echo -e "${RED}Lambda function timed out.${NC}"
      echo -e "${YELLOW}Try increasing the Lambda timeout in template.yaml.${NC}"
    fi
  fi
  
  echo -e "${YELLOW}🔍 Testing S3 connectivity...${NC}"
  S3_RESPONSE=$(curl -s "${API_URL}debug/check-s3")
  
  # Show the raw response first
  echo "Raw response first 100 characters:"
  echo "$S3_RESPONSE" | head -c 100
  echo -e "\n"
  
  # Use our analysis function to diagnose issues
  analyze_json_response "$S3_RESPONSE" "debug/check-s3"
  
  # Get HTTP status code
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}debug/check-s3")
  echo -e "${BLUE}HTTP Status Code: ${HTTP_STATUS}${NC}"
  
  # Check for specific S3 connectivity issues in the response
  if echo "$S3_RESPONSE" | jq -e 'has("status")' &>/dev/null && echo "$S3_RESPONSE" | jq -e '.status == "error"' &>/dev/null; then
    echo -e "${RED}S3 connectivity test failed!${NC}"
    echo -e "${YELLOW}This indicates issues with S3 permissions or configuration.${NC}"
    
    # Extract error info if available
    if echo "$S3_RESPONSE" | jq -e 'has("error_type")' &>/dev/null; then
      ERROR_TYPE=$(echo "$S3_RESPONSE" | jq -r '.error_type')
      echo -e "${RED}Error type: ${ERROR_TYPE}${NC}"
      
      case $ERROR_TYPE in
        *"AccessDenied"*)
          echo -e "${YELLOW}This is an S3 permissions issue. Check Lambda execution role permissions.${NC}"
          ;;
        *"NoSuchBucket"*)
          echo -e "${YELLOW}The S3 bucket doesn't exist or is in a different region.${NC}"
          ;;
        *"NoSuchKey"*)
          echo -e "${YELLOW}The CSV file doesn't exist in the bucket.${NC}"
          ;;
        *)
          echo -e "${YELLOW}Check CloudWatch logs for more details.${NC}"
          ;;
      esac
    fi
  fi
  
  # Restore original requirements.txt if we changed it
  if [ "$FIX_DEPS" = true ] || [ "$DOWNGRADE" = true ]; then
    if [ -f requirements.txt.bak ]; then
      mv requirements.txt.bak requirements.txt
    fi
  fi
  
  # Check for common issues in responses
  echo -e "${YELLOW}🔍 Checking for common issues...${NC}"
  
  # Check Lambda logs for errors
  echo -e "${YELLOW}Checking recent Lambda logs for errors...${NC}"
  FUNCTION_NAME=$(aws cloudformation describe-stack-resources --stack-name pc-builder --query "StackResources[?ResourceType=='AWS::Lambda::Function'].PhysicalResourceId" --output text)
  if [ -n "$FUNCTION_NAME" ]; then
    echo -e "${BLUE}Found Lambda function: $FUNCTION_NAME${NC}"
    echo -e "${BLUE}Fetching recent logs...${NC}"
    
    # Get the log group name
    LOG_GROUP="/aws/lambda/$FUNCTION_NAME"
    
    # Check if the aws cli can access logs
    if aws logs describe-log-groups --log-group-name-prefix "$LOG_GROUP" &>/dev/null; then
      # Get the most recent log events
      echo -e "${BLUE}Most recent error logs:${NC}"
      aws logs filter-log-events \
        --log-group-name "$LOG_GROUP" \
        --filter-pattern "ERROR" \
        --limit 5 \
        --query "events[].message" \
        --output text
        
      # Check for specific errors
      if aws logs filter-log-events --log-group-name "$LOG_GROUP" --filter-pattern "pydantic_core" --limit 1 &>/dev/null; then
        echo -e "${RED}❌ Found pydantic_core dependency error in logs!${NC}"
        echo -e "${YELLOW}Fix: Run './deploy-lambda-enhanced.sh --fix-deps --downgrade'${NC}"
      fi
      
      if aws logs filter-log-events --log-group-name "$LOG_GROUP" --filter-pattern "Unable to import module" --limit 1 &>/dev/null; then
        echo -e "${RED}❌ Found Python import error in logs!${NC}"
        echo -e "${YELLOW}Fix: Run './deploy-lambda-enhanced.sh --use-layer'${NC}"
      fi
      
      if aws logs filter-log-events --log-group-name "$LOG_GROUP" --filter-pattern "AccessDenied" --limit 1 &>/dev/null; then
        echo -e "${RED}❌ Found S3 permissions error in logs!${NC}"
        echo -e "${YELLOW}Fix: Check Lambda execution role permissions for S3 access${NC}"
      fi
    else
      echo -e "${RED}Cannot access CloudWatch logs. Check your AWS CLI permissions.${NC}"
    fi
  else
    echo -e "${RED}Could not find Lambda function name from CloudFormation stack.${NC}"
  fi
  
  echo -e "${BLUE}🔧 To check logs:${NC}"
  echo "sam logs -n FastApiFunction --stack-name pc-builder --tail"
  
  echo -e "${BLUE}📋 If you encounter dependency errors, try running:${NC}"
  echo "./deploy-lambda-enhanced.sh --fix-deps"
  echo "or"
  echo "./deploy-lambda-enhanced.sh --use-layer"
else
  echo -e "${RED}❌ Deployment failed. Check the error messages above.${NC}"
  
  echo -e "${YELLOW}🔧 Common issues and fixes:${NC}"
  echo "1. Python dependency errors: Try './deploy-lambda-enhanced.sh --fix-deps'"
  echo "2. Pydantic/FastAPI compatibility issues: Try './deploy-lambda-enhanced.sh --downgrade'"
  echo "3. Binary compatibility issues: Try './deploy-lambda-enhanced.sh --use-layer'"
  
  # Try to get the API URL even if deployment failed
  API_URL=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text 2>/dev/null)
  
  if [ -n "$API_URL" ]; then
    echo -e "${YELLOW}Testing different API path formats to help diagnose issues:${NC}"
    # Test both the health and graphic-cards endpoints with different path formats
    test_api_paths "$API_URL" "health"
    test_api_paths "$API_URL" "graphic-cards"
  else
    echo -e "${RED}Could not retrieve API URL from CloudFormation stack.${NC}"
  fi
  
  # Restore original requirements.txt if we changed it
  if [ "$FIX_DEPS" = true ] || [ "$DOWNGRADE" = true ]; then
    if [ -f requirements.txt.bak ]; then
      mv requirements.txt.bak requirements.txt
    fi
  fi
  
  echo -e "${YELLOW}Checking Lambda deployment status...${NC}"
  aws lambda list-functions --query "Functions[?contains(FunctionName, 'pc-builder')].[FunctionName,LastUpdateStatus,Runtime,State]" --output table
  
  exit 1
fi

# Function to test different API path variations
test_api_paths() {
  local base_url=$1
  local endpoint=$2
  
  echo -e "${YELLOW}Testing different path formats for endpoint: ${endpoint}${NC}"
  
  # Extract the base URL without trailing slash
  base_url=$(echo $base_url | sed 's|/$||')
  
  # Try different path formats
  echo -e "${BLUE}1. Direct path: ${base_url}${endpoint}${NC}"
  curl -s "${base_url}${endpoint}" | head -c 100
  echo -e "\n"
  
  echo -e "${BLUE}2. With slash: ${base_url}/${endpoint}${NC}"
  curl -s "${base_url}/${endpoint}" | head -c 100
  echo -e "\n"
  
  # If URL doesn't end with /Prod, try adding it
  if [[ $base_url != */Prod ]]; then
    echo -e "${BLUE}3. With /Prod prefix: ${base_url}/Prod${endpoint}${NC}"
    curl -s "${base_url}/Prod${endpoint}" | head -c 100
    echo -e "\n"
    
    echo -e "${BLUE}4. With /Prod/ prefix: ${base_url}/Prod/${endpoint}${NC}"
    curl -s "${base_url}/Prod/${endpoint}" | head -c 100
    echo -e "\n"
  fi
  
  # If URL ends with /Prod, try without it
  if [[ $base_url == */Prod ]]; then
    base_without_prod=$(echo $base_url | sed 's|/Prod$||')
    echo -e "${BLUE}3. Without /Prod: ${base_without_prod}${endpoint}${NC}"
    curl -s "${base_without_prod}${endpoint}" | head -c 100
    echo -e "\n"
  fi
}

# Function to analyze JSON response and diagnose issues
analyze_json_response() {
  local response="$1"
  local endpoint="$2"
  
  echo -e "${YELLOW}Analyzing response from ${endpoint}:${NC}"
  
  # Check if it's empty
  if [ -z "$response" ]; then
    echo -e "${RED}Empty response received!${NC}"
    return
  fi
  
  # Check if it looks like HTML (might be an API Gateway error page)
  if echo "$response" | grep -q "<!DOCTYPE html>" || echo "$response" | grep -q "<html>"; then
    echo -e "${RED}Response appears to be HTML, not JSON. Likely an API Gateway error page.${NC}"
    echo -e "${BLUE}First 100 characters:${NC}"
    echo "$response" | head -c 100
    echo -e "\n${YELLOW}This suggests an issue with API Gateway or Lambda integration.${NC}"
    return
  fi
  
  # Check if it's valid JSON
  if ! echo "$response" | jq '.' &>/dev/null; then
    echo -e "${RED}Invalid JSON response!${NC}"
    echo -e "${BLUE}First 100 characters:${NC}"
    echo "$response" | head -c 100
    echo -e "\n${YELLOW}This might indicate a server-side error or malformed response.${NC}"
    return
  fi
  
  # Check JSON structure
  local json_type=$(echo "$response" | jq -r 'type')
  echo -e "${BLUE}JSON response type: ${json_type}${NC}"
  
  case $json_type in
    "array")
      local array_length=$(echo "$response" | jq 'length')
      echo -e "${BLUE}Array length: ${array_length}${NC}"
      if [ "$array_length" -eq 0 ]; then
        echo -e "${YELLOW}Empty array returned. No data found.${NC}"
      else
        echo -e "${GREEN}Array contains data. First item:${NC}"
        echo "$response" | jq '.[0]'
      fi
      ;;
    
    "object")
      echo -e "${BLUE}Object keys:${NC}"
      echo "$response" | jq 'keys'
      
      # Check for error keys
      if echo "$response" | jq -e 'has("error")' &>/dev/null && echo "$response" | jq -e '.error' &>/dev/null; then
        echo -e "${RED}Error message in response:${NC}"
        echo "$response" | jq '.error'
      fi
      ;;
      
    *)
      echo -e "${RED}Unexpected JSON type: ${json_type}${NC}"
      echo "$response"
      ;;
  esac
}

# Function to analyze Lambda logs for common issues
analyze_lambda_logs() {
  local stack_name="$1"
  local function_name="$2"
  
  echo -e "${YELLOW}Analyzing recent Lambda logs for ${function_name}...${NC}"
  
  # Get the Lambda function ARN
  local lambda_arn=$(aws cloudformation describe-stack-resources --stack-name "$stack_name" \
    --logical-resource-id "$function_name" --query "StackResources[0].PhysicalResourceId" --output text)
  
  if [ -z "$lambda_arn" ] || [ "$lambda_arn" == "None" ]; then
    echo -e "${RED}Could not find Lambda ARN for $function_name${NC}"
    return
  fi
  
  # Get log group name
  local log_group_name="/aws/lambda/$(basename "$lambda_arn")"
  
  # Check if log group exists
  if ! aws logs describe-log-groups --log-group-name-prefix "$log_group_name" --query "logGroups[*].logGroupName" --output text | grep -q "$log_group_name"; then
    echo -e "${RED}No logs found for $function_name. The function may not have been executed yet.${NC}"
    return
  fi
  
  echo -e "${BLUE}Fetching recent logs (last 10 minutes)...${NC}"
  
  # Calculate timestamp for 10 minutes ago
  local start_time=$(($(date +%s) - 600))000
  
  # Get log events
  local log_output=$(aws logs get-log-events --log-group-name "$log_group_name" \
    --log-stream-name $(aws logs describe-log-streams --log-group-name "$log_group_name" \
    --order-by LastEventTime --descending --limit 1 --query "logStreams[0].logStreamName" --output text) \
    --start-time $start_time --query "events[*].message" --output text)
  
  if [ -z "$log_output" ]; then
    echo -e "${YELLOW}No recent logs found.${NC}"
    return
  fi
  
  echo -e "${GREEN}Found log entries. Analyzing for common issues...${NC}"
  
  # Check for common error patterns specific to PC Builder project
  
  # 1. Mangum path handling issues
  if echo "$log_output" | grep -q "NotFoundError"; then
    echo -e "${RED}⚠️ API Gateway path handling issue detected!${NC}"
    echo -e "${YELLOW}Suggestion: Check Mangum configuration in main.py - ensure api_gateway_base_path=\"/Prod\" is set.${NC}"
  fi
  
  # 2. S3 access issues
  if echo "$log_output" | grep -q "S3 access denied" || echo "$log_output" | grep -q "AccessDenied"; then
    echo -e "${RED}⚠️ S3 permission issues detected!${NC}"
    echo -e "${YELLOW}Suggestion: Verify Lambda execution role has s3:GetObject and s3:ListBucket permissions.${NC}"
    echo -e "${YELLOW}          Run check_lambda_permissions.py to diagnose specific permission issues.${NC}"
  fi
  
  # 3. Empty data issues
  if echo "$log_output" | grep -q "No data found in"; then
    echo -e "${RED}⚠️ Empty data issue detected!${NC}"
    echo -e "${YELLOW}Suggestion: Check if data exists in S3 bucket or if fallback to local data is working.${NC}"
    echo -e "${YELLOW}          Run check_s3_data.py to verify data in S3.${NC}"
  fi
  
  # 4. Dependency issues
  if echo "$log_output" | grep -q "ModuleNotFoundError" || echo "$log_output" | grep -q "ImportError"; then
    echo -e "${RED}⚠️ Python dependency issues detected!${NC}"
    echo -e "${YELLOW}Suggestion: Try deploying with --use-layer and --fix-deps options.${NC}"
    echo -e "${YELLOW}          Check that requirements-lambda.txt contains compatible package versions.${NC}"
  fi
  
  # 5. Pydantic v2 incompatibility
  if echo "$log_output" | grep -q "AttributeError: module 'pydantic'" || echo "$log_output" | grep -q "has no attribute 'BaseModel'"; then
    echo -e "${RED}⚠️ Pydantic v2 compatibility issue detected!${NC}"
    echo -e "${YELLOW}Suggestion: Deploy with --downgrade option to use Pydantic v1.${NC}"
  fi
  
  # 6. Lambda timeout issues
  if echo "$log_output" | grep -q "Task timed out after"; then
    echo -e "${RED}⚠️ Lambda timeout detected!${NC}"
    echo -e "${YELLOW}Suggestion: Increase Lambda timeout in template.yaml or optimize code.${NC}"
  fi
  
  # 7. Memory issues
  if echo "$log_output" | grep -q "MemoryError"; then
    echo -e "${RED}⚠️ Lambda memory limit issue detected!${NC}"
    echo -e "${YELLOW}Suggestion: Increase Lambda memory allocation in template.yaml.${NC}"
  fi
  
  # Print last 10 log entries for reference
  echo -e "${BLUE}Last 10 log entries:${NC}"
  echo "$log_output" | tail -n 10
}

# Function to diagnose SAM deployment failures
diagnose_sam_failure() {
  local deploy_output="$1"
  
  echo -e "${RED}SAM deployment failed! Diagnosing...${NC}"
  
  # Check for common errors in the output
  if echo "$deploy_output" | grep -q "AccessDenied"; then
    echo -e "${RED}⚠️ AWS permissions error detected.${NC}"
    echo -e "${YELLOW}Suggestion: Check your AWS credentials and IAM permissions.${NC}"
    echo -e "${YELLOW}Run 'check_aws_permissions.py' to verify your permissions.${NC}"
  fi
  
  if echo "$deploy_output" | grep -q "BucketAlreadyExists"; then
    echo -e "${RED}⚠️ SAM deployment bucket conflict.${NC}"
    echo -e "${YELLOW}Suggestion: Try using a different deployment bucket:${NC}"
    echo -e "${YELLOW}sam deploy --stack-name pc-builder --s3-bucket [unique-bucket-name]${NC}"
  fi
  
  if echo "$deploy_output" | grep -q "not authorized to perform: cloudformation"; then
    echo -e "${RED}⚠️ CloudFormation permissions issue.${NC}"
    echo -e "${YELLOW}Suggestion: Verify your IAM user has CloudFormation permissions.${NC}"
  fi
  
  if echo "$deploy_output" | grep -q "executable not found"; then
    echo -e "${RED}⚠️ Python executable issue in Lambda build.${NC}"
    echo -e "${YELLOW}Suggestion: Check your Python environment and PATH.${NC}"
  fi
  
  if echo "$deploy_output" | grep -q "ImportError"; then
    echo -e "${RED}⚠️ Python dependency issue.${NC}"
    echo -e "${YELLOW}Suggestion: Try using --fix-deps or --use-layer options.${NC}"
  fi
  
  if echo "$deploy_output" | grep -q "CREATE_FAILED"; then
    echo -e "${RED}⚠️ CloudFormation stack creation failed.${NC}"
    echo -e "${YELLOW}Checking CloudFormation events for details...${NC}"
    
    # Get the last few CloudFormation events
    aws cloudformation describe-stack-events --stack-name pc-builder \
      --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
      --output text
  fi
  
  echo -e "${BLUE}For more details, check CloudFormation events:${NC}"
  echo "aws cloudformation describe-stack-events --stack-name pc-builder"
  
  echo -e "${BLUE}For recovery options:${NC}"
  echo "1. Try to delete the stack: aws cloudformation delete-stack --stack-name pc-builder"
  echo "2. Run the recovery script: ./recover-stack.sh"
}

# Function to check if workflow script has been run recently
check_workflow_data() {
  echo -e "${BLUE}Checking workflow data freshness...${NC}"
  
  # Check if workflow directory exists
  if [ ! -d "../../workflow" ]; then
    echo -e "${YELLOW}⚠️ Workflow directory not found.${NC}"
    echo -e "${YELLOW}Suggestion: Set up the workflow directory for automated data processing:${NC}"
    echo -e "${YELLOW}python setup-workflow.py${NC}"
    return
  fi
  
  # Check if pc-builder-workflow.py exists
  WORKFLOW_SCRIPT="../../workflow/pc-builder-workflow.py"
  if [ ! -f "$WORKFLOW_SCRIPT" ]; then
    echo -e "${YELLOW}⚠️ Workflow script not found.${NC}"
    echo -e "${YELLOW}Suggestion: Create the workflow script for data processing.${NC}"
    return
  fi
  
  # Check data freshness
  DATA_DIR="../../data-results"
  if [ ! -d "$DATA_DIR" ]; then
    echo -e "${RED}⚠️ No data directory found!${NC}"
    echo -e "${YELLOW}Suggestion: Run the workflow script to generate data:${NC}"
    echo -e "${YELLOW}python3 ../../workflow/pc-builder-workflow.py --scrape --upload --cleanup${NC}"
    return
  fi
  
  # Check if CSV files exist in data-results
  CSV_COUNT=$(find "$DATA_DIR" -name "*.csv" | wc -l)
  if [ "$CSV_COUNT" -eq 0 ]; then
    echo -e "${RED}⚠️ No CSV files found in data directory!${NC}"
    echo -e "${YELLOW}Suggestion: Run the workflow script to generate data:${NC}"
    echo -e "${YELLOW}python3 ../../workflow/pc-builder-workflow.py --scrape --upload --cleanup${NC}"
    return
  fi
  
  # Check how old the data is
  NEWEST_CSV=$(find "$DATA_DIR" -name "*.csv" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
  
  if [ -z "$NEWEST_CSV" ]; then
    echo -e "${YELLOW}⚠️ Could not determine data freshness.${NC}"
    return
  fi
  
  # Get file modification time in seconds since epoch
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    FILE_MOD_TIME=$(stat -f "%m" "$NEWEST_CSV")
  else
    # Linux
    FILE_MOD_TIME=$(stat -c "%Y" "$NEWEST_CSV")
  fi
  
  CURRENT_TIME=$(date +%s)
  TIME_DIFF=$((CURRENT_TIME - FILE_MOD_TIME))
  DAYS_OLD=$((TIME_DIFF / 86400))
  
  if [ "$DAYS_OLD" -gt 7 ]; then
    echo -e "${YELLOW}⚠️ Data is $DAYS_OLD days old. Consider refreshing.${NC}"
    echo -e "${YELLOW}Suggestion: Run the workflow script to update data:${NC}"
    echo -e "${YELLOW}python3 ../../workflow/pc-builder-workflow.py --scrape --upload --cleanup${NC}"
  else
    echo -e "${GREEN}✓ Data is relatively fresh ($DAYS_OLD days old).${NC}"
  fi
}

# Final summary
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}               DEPLOYMENT SUMMARY${NC}"
echo -e "${BLUE}==================================================${NC}"

# Collect issues we've seen
ISSUES_FOUND=false

# Check if we got empty arrays or error responses
if [ -n "$GRAPHICS_RESPONSE" ] && echo "$GRAPHICS_RESPONSE" | jq -e 'length == 0' &>/dev/null; then
  echo -e "${RED}⚠️ Graphics cards endpoint returned an empty array!${NC}"
  ISSUES_FOUND=true
fi

if [ -n "$S3_RESPONSE" ] && echo "$S3_RESPONSE" | jq -e '.status == "error"' &>/dev/null 2>/dev/null; then
  echo -e "${RED}⚠️ S3 connectivity check failed!${NC}"
  ISSUES_FOUND=true
fi

# Check if the workflow script has been run recently
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}               WORKFLOW CHECK${NC}"
echo -e "${BLUE}==================================================${NC}"
check_workflow_data

# Analyze Lambda logs for diagnostic information
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}              LAMBDA LOG ANALYSIS${NC}"
echo -e "${BLUE}==================================================${NC}"

# Call our log analysis function
analyze_lambda_logs "pc-builder" "FastApiFunction"

# Check workflow data freshness
check_workflow_data

# Final recommendations
if [ "$ISSUES_FOUND" = true ]; then
  echo -e "${YELLOW}Some issues were detected during testing. Next steps:${NC}"
  echo "1. Check Lambda logs for detailed error information:"
  echo "   sam logs -n FastApiFunction --stack-name pc-builder --tail"
  echo
  echo "2. If you see dependency errors, try redeploying with:"
  echo "   ./deploy-lambda-enhanced.sh --fix-deps"
  echo
  echo "3. For binary compatibility issues, use Lambda Layer:"
  echo "   ./deploy-lambda-enhanced.sh --use-layer"
  echo
  echo "4. Run the PC Builder workflow script to update data:"
  echo "   python3 workflow/pc-builder-workflow.py --scrape --upload --cleanup"
  echo
  echo "4. For S3 access issues:"
  echo "   - Verify IAM permissions on the Lambda execution role"
  echo "   - Confirm S3 bucket exists and contains the CSV file"
  echo "   - Check that environment variables are set correctly"
  echo
  echo "5. For API Gateway issues:"
  echo "   - Check path mappings and stage configuration"
  echo "   - Verify Mangum configuration with correct api_gateway_base_path"
else
  echo -e "${GREEN}✅ All tests completed successfully!${NC}"
fi
