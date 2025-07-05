# Using the AWS Lambda API with Local Frontend

This guide explains how to use the AWS Lambda-deployed API with your local frontend application for testing and development.

## API URL Configuration

The API URL is configured in the environment files:

- `pc-builder/pc-builder-app/src/environments/environment.ts` - Development environment
- `pc-builder/pc-builder-app/src/environments/environment.prod.ts` - Production environment

By default, the development environment is now configured to use the AWS Lambda API endpoint:

```typescript
export const environment = {
  production: false,
  apiUrl: 'https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod',
  // For local development, uncomment the line below and comment out the Lambda URL above
  // apiUrl: 'http://127.0.0.1:8000',
};
```

## Running the Frontend with AWS Lambda Backend

Use the provided script to start the Angular frontend with the AWS Lambda backend:

```bash
./start-frontend-with-lambda.sh
```

This script will:
1. Show the current API URL being used
2. Start the Angular development server
3. Open a browser to the application

## Testing the API Connection

1. Open the browser console (F12 or right-click → Inspect → Console)
2. Check for successful API calls to the graphics cards endpoint
3. You should see data being loaded from the AWS Lambda API

## Using the Diagnostic Endpoints

We've added special diagnostic endpoints to help troubleshoot API issues, especially when you receive a 200 response but with empty data:

### Check S3 Connectivity

To verify that the Lambda function can connect to S3 and find the data file:

```bash
# Replace with your actual API Gateway URL if different
curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/check-s3
```

This will show:
- If the S3 bucket exists and is accessible
- If the CSV file exists in the bucket
- A preview of the CSV content (first few lines)
- A list of objects in the bucket
- Environment variables related to S3 configuration

### Force Data Reload

If the API shows empty data, you can force it to reload from S3:

```bash
curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/reload
```

This will:
- Attempt to reload the data from S3
- Return the number of items loaded
- Update the in-memory data store used by the API endpoints

### Get System Diagnostics

For comprehensive system information:

```bash
curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/diagnostics
```

This provides:
- Request path information (helpful for API Gateway path issues)
- Environment variables (without sensitive values)
- Local file paths and availability
- Lambda context and configuration details

## Switching Between Local and Lambda Backends

To switch between using the local FastAPI backend and the AWS Lambda backend:

### To use the local backend:
1. Edit `pc-builder/pc-builder-app/src/environments/environment.ts`
2. Comment out the Lambda API URL and uncomment the local URL:
   ```typescript
   // apiUrl: 'https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod',
   apiUrl: 'http://127.0.0.1:8000',
   ```
3. Save the file and restart the Angular server

### To use the Lambda backend:
1. Edit `pc-builder/pc-builder-app/src/environments/environment.ts`
2. Uncomment the Lambda API URL and comment out the local URL:
   ```typescript
   apiUrl: 'https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod',
   // apiUrl: 'http://127.0.0.1:8000',
   ```
2. Save the file and restart the Angular server

## Troubleshooting

### Empty Data Response (200 OK but No Data)
If the API returns a 200 status code but with empty data, use these diagnostic endpoints to troubleshoot:

1. Check S3 connectivity and file presence:
   ```bash
   # Replace with your actual API Gateway URL
   curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/check-s3
   ```

2. Force reload data from S3:
   ```bash
   curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/reload
   ```

3. Get comprehensive system diagnostics:
   ```bash
   curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/debug/diagnostics
   ```

4. Check the health endpoint with data count:
   ```bash
   curl https://xifhvni3h7.execute-api.eu-west-3.amazonaws.com/Prod/health
   ```

Common issues and solutions:
- S3 bucket permissions: Verify Lambda execution role has S3 read access
- CSV file missing or malformed: Check if the file exists and has correct columns
- Region mismatch: Ensure S3 bucket and Lambda are in the same AWS region
- Environment variables: Confirm S3_BUCKET and S3_CSV_KEY are set correctly

For more detailed troubleshooting, refer to `API_GATEWAY_LAMBDA_TROUBLESHOOTING.md`.

### Using the API Testing Script

We've created a testing script that checks all the endpoints and helps diagnose issues:

```bash
# Run the comprehensive API testing script
./test-api-gateway.sh
```

This script will:
1. Test the `/health` endpoint to verify the service is running
2. Test the `/graphic-cards` endpoint and display the first item if available
3. Test the `/debug/check-s3` endpoint to check S3 connectivity
4. Test the `/debug/diagnostics` endpoint for system information
5. Provide a summary of any detected issues and suggested fixes

### CORS Issues
If you encounter CORS errors in the console, ensure that the Lambda function's API Gateway has CORS configured correctly. The FastAPI application in your Lambda should have the CORS middleware with appropriate settings.

### API Gateway URL Issues
If the API URL changes (due to redeployment or region changes), update the URL in the environment configuration file.

### Authentication
For endpoints requiring authentication, ensure the appropriate headers are sent with each request.

## Advanced AWS Diagnostics

For deeper investigation into AWS configuration issues, especially when experiencing empty data responses, we've created Python diagnostic scripts:

### Check S3 Data Connectivity

This script performs a comprehensive check of your S3 setup:

```bash
# Run the S3 data connectivity checker
python3 check_s3_data.py
```

Features:
- Tests S3 connectivity and permissions
- Verifies the CSV file exists and has valid content
- Checks image files existence
- Offers automatic fixes for common issues

### Check Lambda Permissions

To verify that your Lambda function has proper permissions to access S3:

```bash
# Run the Lambda permissions checker
python3 check_lambda_permissions.py
```

Features:
- Identifies PC Builder Lambda functions
- Verifies environment variables are correctly set
- Checks IAM roles and policies for S3 read permissions
- Suggests specific fixes for permission issues

These scripts require AWS CLI configured with appropriate credentials.

### All-in-One Diagnostic Utility

For convenience, we've created an all-in-one diagnostic script that combines all the above tools:

```bash
# Run the comprehensive diagnostic utility
./diagnose-api-issues.sh
```

This interactive script provides a menu-driven interface to:
1. Test all API Gateway endpoints
2. Check S3 connectivity and data
3. Verify Lambda permissions
4. Run comprehensive diagnostics (all of the above)

Use this utility when you need to troubleshoot empty data responses or other API issues.

## Lambda Deployment Issues

### Python Package Dependency Errors

If you see errors like the following in your Lambda logs:

```
[ERROR] Runtime.ImportModuleError: Unable to import module 'app.main': No module named 'pydantic_core._pydantic_core'
```

This indicates a problem with Python package dependencies. There are two main approaches to fix this:

#### Option 1: Use a Lambda Layer with Compatible Binaries

1. Create a Lambda Layer with compatible versions of all dependencies:
   ```bash
   # Create a directory for the layer
   mkdir -p lambda-layer/python
   cd lambda-layer
   
   # Install packages with platform-specific binaries
   pip install --platform manylinux2014_x86_64 \
     --target=python \
     --implementation cp \
     --python-version 3.11 \
     --only-binary=:all: \
     fastapi pydantic mangum boto3
   
   # Create a ZIP file of the layer
   zip -r lambda-layer.zip python/
   
   # Upload the layer to Lambda
   aws lambda publish-layer-version \
     --layer-name pc-builder-dependencies \
     --zip-file fileb://lambda-layer.zip \
     --compatible-runtimes python3.11
   ```

2. Attach the layer to your Lambda function in the AWS console or via SAM template.

#### Option 2: Downgrade Pydantic Version

If you're using FastAPI with a recent version of Pydantic, try downgrading to a more stable version:

1. Edit your `requirements.txt` file:
   ```
   fastapi==0.103.1
   pydantic==1.10.8  # Use a version < 2.0
   mangum==0.17.0
   boto3==1.28.40
   ```

2. Redeploy your Lambda function:
   ```bash
   cd pc-builder/pc-builder-backend
   ./deploy-lambda.sh
   ```

Pydantic v1.x is often more stable in AWS Lambda environments than the newer v2.x releases.

### Fixing Pydantic Core Import Error

If you see this specific error in your Lambda logs:
```
[ERROR] Runtime.ImportModuleError: Unable to import module 'app.main': No module named 'pydantic_core._pydantic_core'
```

This is a known issue with newer versions of Pydantic (v2.x) in AWS Lambda. Here's how to fix it:

#### Quick Fix: Use the Enhanced Deployment Script

We've created an enhanced deployment script that handles this issue:

```bash
cd pc-builder/pc-builder-backend
./deploy-lambda-enhanced.sh --fix-deps
```

This script will:
1. Temporarily replace your requirements.txt with Lambda-compatible versions
2. Deploy the function with these compatible dependencies
3. Restore your original requirements.txt after deployment

#### Alternative Approaches

If the quick fix doesn't work, you can try these approaches:

1. **Use a Lambda Layer:**
   ```bash
   ./deploy-lambda-enhanced.sh --use-layer
   ```
   This creates a Layer with pre-compiled binaries compatible with Lambda.

2. **Manually Downgrade Pydantic:**
   ```bash
   pip install pydantic==1.10.8 -t ./
   ```
   Then redeploy your Lambda function.

3. **Package with Docker:**
   ```bash
   # In your SAM template.yaml, add:
   Metadata:
     BuildMethod: makefile
   ```
   Then create a Makefile that builds dependencies in a Lambda-like container.

## Checking Lambda Logs

To investigate issues with your Lambda function, you should check the CloudWatch logs:

### Using AWS CLI

```bash
# Get logs from the last 10 minutes
aws logs filter-log-events \
  --log-group-name "/aws/lambda/pc-builder-FastApiFunction-XXXX" \
  --start-time $(date -v -10M +%s)000

# Using SAM CLI (easier)
cd pc-builder/pc-builder-backend
sam logs -n FastApiFunction --stack-name pc-builder --tail
```

### Common Log Patterns to Look For

1. **Import Errors** (like the pydantic_core error):
   ```
   Runtime.ImportModuleError: Unable to import module 'app.main': No module named 'X'
   ```
   Solution: Fix dependencies using one of the methods described above.

2. **Permission Errors**:
   ```
   botocore.exceptions.ClientError: An error occurred (AccessDenied)
   ```
   Solution: Check the Lambda execution role permissions.

3. **Path Resolution Errors**:
   ```
   File not found: /var/task/app/main.py
   ```
   Solution: Check your handler configuration in template.yaml.

4. **Timeout Errors**:
   ```
   Task timed out after X.XX seconds
   ```
   Solution: Increase the timeout in your Lambda configuration.

5. **Memory Errors**:
   ```
   Runtime exited with error: signal: killed
   ```
   Solution: Increase the memory allocation for your Lambda function.
