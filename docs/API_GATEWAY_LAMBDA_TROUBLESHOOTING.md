# AWS Lambda and API Gateway Troubleshooting Guide

## Automated Diagnostics and Solutions

The PC Builder project includes an enhanced Lambda deployment script with comprehensive diagnostics:

```bash
cd pc-builder/pc-builder-backend
./deploy-lambda-enhanced.sh
```

This script provides:
- Automatic diagnosis of common deployment issues
- Lambda log analysis for specific errors
- JSON response validation
- S3 data integration verification
- Workflow data freshness checks

**Options:**
- `--fix-deps`: Use Lambda-compatible dependencies
- `--use-layer`: Create a Lambda Layer for complex dependencies
- `--downgrade`: Use Pydantic v1 (for Lambda compatibility)

For specific issues, see the detailed troubleshooting steps below.

## Common Lambda Deployment Issues

### 1. CloudFormation Stack in UPDATE_FAILED State

**Symptoms:**
- Error: `An error occurred (ValidationError) when calling the ExecuteChangeSet operation: This stack is currently in a non-terminal [UPDATE_FAILED] state`

**Solution:**
```bash
# Option 1: Update with rollback disabled
aws cloudformation update-stack --stack-name <stack-name> --use-previous-template --disable-rollback

# Option 2: Use the enhanced deploy script (recommended)
./deploy-lambda-enhanced.sh

# Option 3: Use the basic deploy script
./deploy-lambda.sh
```

### 2. Mangum Handler Not Found

**Symptoms:**
- Error: `The adapter was unable to infer a handler to use for the event`

**Causes & Solutions:**

a) **Incorrect handler path in template.yaml**
   - Check for path format: `app/main.handler` NOT `app.main.handler`
   - The Lambda handler path uses `/` for directories in your code but `.` in the handler config

b) **Invalid test event format**
   - Make sure to use an API Gateway HTTP API (v2) format test event
   - Include all required fields: version, routeKey, rawPath, headers, requestContext

c) **Missing Mangum configuration**
   - Ensure Mangum is properly configured in your FastAPI app:
   ```python
   from mangum import Mangum
   app = FastAPI()
   # Your routes here...
   handler = Mangum(app, lifespan="off")
   ```

### 3. Endpoint Not Found (404)

**Symptoms:**
- 404 "Not Found" response when testing the endpoint

**Solutions:**

a) **Check path matching**
   - Ensure the path in the test event matches exactly what's in your FastAPI app
   - Watch for plural vs singular: `/graphic-cards` vs `/graphics-cards`

b) **Check stage prefix**
   - For API Gateway v2 HTTP APIs, the stage is included in the path
   - Try updating Mangum config: `Mangum(app, lifespan="off", api_gateway_base_path="/Prod")`
   - Or update the test event to include stage: `"rawPath": "/Prod/health"`

c) **Check proxy configuration**
   - Verify your template.yaml has the right path configuration:
   ```yaml
   Events:
     ApiEvents:
       Type: Api
       Properties:
         Path: /{proxy+}
         Method: ANY
   ```

### 4. S3 Access Issues

**Symptoms:**
- Lambda deploys but fails when trying to read from S3
- API returns 200 OK but with empty data array `[]`
- Backend loads correctly but no data appears in frontend

**Solutions:**
- Verify S3 bucket policy and Lambda execution role permissions:
  ```bash
  # Check Lambda execution role
  aws lambda get-function --function-name pc-builder-FastApiFunction-XXXX --query 'Configuration.Role'
  
  # Check if the role has S3 read access
  aws iam get-policy-version --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess --version-id v1
  ```

- Check that environment variables are set correctly:
  ```bash
  # View Lambda environment variables
  aws lambda get-function-configuration --function-name pc-builder-FastApiFunction-XXXX --query 'Environment'
  
  # Required environment variables:
  # - S3_BUCKET: pc-builder-bucket-dvg-2025
  # - S3_CSV_KEY: graphics-cards.csv
  # - MY_AWS_REGION: eu-west-3
  ```

- Use diagnostic endpoints to troubleshoot:
  ```bash
  # Test S3 connectivity and CSV presence
  curl https://your-api-id.execute-api.region.amazonaws.com/Prod/debug/check-s3
  
  # Get comprehensive system diagnostics
  curl https://your-api-id.execute-api.region.amazonaws.com/Prod/debug/diagnostics
  ```

- Check CloudWatch logs for S3 access errors
- Ensure region consistency across all services
- Try uploading the CSV file again to S3:
  ```bash
  aws s3 cp graphics-cards.csv s3://pc-builder-bucket-dvg-2025/graphics-cards.csv
  ```

## Creating Proper API Gateway Test Events

### Health Endpoint Test Event
```json
{
  "version": "2.0",
  "routeKey": "GET /health",
  "rawPath": "/health",
  "requestContext": {
    "http": {
      "method": "GET",
      "path": "/health"
    }
  }
}
```

### Graphic Cards Endpoint Test Event
```json
{
  "version": "2.0",
  "routeKey": "GET /graphic-cards",
  "rawPath": "/graphic-cards",
  "requestContext": {
    "http": {
      "method": "GET",
      "path": "/graphic-cards"
    }
  }
}
```

### 5. Empty Data Responses (200 OK but No Data)

**Symptoms:**
- API returns HTTP 200 status code but with empty array `[]`
- The frontend loads without errors but shows no products
- S3 bucket appears to have the necessary files

**Solutions:**

a) **Use diagnostic endpoints**
   - We've added two special diagnostic endpoints to help troubleshoot:
   ```bash
   # Check S3 connectivity and verify CSV file exists
   curl https://your-api-id.execute-api.region.amazonaws.com/Prod/debug/check-s3
   
   # Get comprehensive system diagnostics including environment info and file paths
   curl https://your-api-id.execute-api.region.amazonaws.com/Prod/debug/diagnostics
   
   # Manually trigger data reload
   curl https://your-api-id.execute-api.region.amazonaws.com/Prod/debug/reload
   ```

b) **Check S3 bucket permissions**
   - Ensure the Lambda execution role has S3 read permissions
   - Check both bucket and object permissions (ACLs)
   - Try making the CSV file public-read for testing

c) **Verify CSV format**
   - Ensure the CSV has the expected column names: Product Name, Brand, Price, Specs, Image Path
   - Check for BOM or encoding issues that might affect parsing
   - Upload a fresh copy of the CSV using the workflow script:
   ```bash
   python workflow/pc-builder-workflow.py --upload-only
   ```

d) **Check Cold Start Issues**
   - Lambda functions have a "cold start" period where initialization happens
   - The first request might time out or fail to load data
   - Try hitting the endpoint multiple times or implement warming

e) **Review CloudWatch Logs**
   - The enhanced logging we've added will help identify issues
   - Check for S3 access denied errors or file not found messages
   - Look for JSON parsing errors in the CSV loading code

## Best Practices for FastAPI with Lambda/API Gateway

1. Always use Mangum adapter for FastAPI applications
2. Set explicit environment variables in template.yaml
3. Include proper IAM policies in template.yaml
4. Test locally before deploying (use `uvicorn app.main:app --reload`)
5. Use minimal test events when testing in the AWS Console
6. Avoid AWS reserved environment variable names (e.g., use `MY_AWS_REGION` not `AWS_REGION`)
7. Add comprehensive diagnostic endpoints for troubleshooting
8. Implement graceful fallbacks for missing data sources
