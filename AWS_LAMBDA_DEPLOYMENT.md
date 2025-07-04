# AWS Lambda Deployment Guide for PC Builder Backend

This guide shows you how to deploy your PC Builder backend as an AWS Lambda function using the Serverless Application Model (SAM). This approach requires fewer AWS permissions than the ECS deployment method.

## Prerequisites

1. [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed
2. AWS credentials configured (`~/.aws/credentials` or environment variables)
3. An S3 bucket for deployment artifacts (or permissions to create one)

## Step 1: Prepare the Backend for SAM Deployment

Your FastAPI application is already properly configured with Mangum for AWS Lambda deployment:

```python
from mangum import Mangum
# ...existing app code...
app = FastAPI()
# ...middleware, routes, etc...
handler = Mangum(app)
```

This `handler` function is what Lambda will call to process API requests.

## Step 2: Verify the SAM Template

Make sure your `template.yaml` is properly configured. It should look something like this:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: FastAPI backend for PC Builder running on AWS Lambda
Resources:
  FastApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: .
      Handler: app.main.handler
      Runtime: python3.11
      Timeout: 30
      MemorySize: 512
      Environment:
        Variables:
          MY_AWS_REGION: eu-west-3
          S3_BUCKET: pc-builder-bucket-dvg-2025
          S3_CSV_KEY: graphics-cards.csv
      Events:
        Api:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

## Step 3: Add an Output Section to the Template

Update your template.yaml to include outputs that will show your API URL:

```yaml
# Add this at the end of template.yaml
Outputs:
  FastApiFunction:
    Description: "Lambda Function ARN"
    Value: !GetAtt FastApiFunction.Arn
  ApiURL:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
  ApiARN:
    Description: "API Gateway ARN"
    Value: !Ref ServerlessRestApi
```

## Step 4: Install Required Dependencies

Ensure all dependencies are in your requirements.txt file:

```bash
cd pc-builder/pc-builder-backend
pip install -r requirements.txt
```

Make sure 'mangum' is included in the requirements.txt file.

## Step 5: Build and Package Your Application

Use the SAM CLI to build and package your application:

```bash
# Navigate to the backend directory
cd pc-builder/pc-builder-backend

# Build the application using SAM
sam build

# If the build succeeds, you'll see a .aws-sam directory created
```

## Step 6: Deploy to AWS

There are two ways to deploy your application:

### Option 1: SAM Deploy (Guided)

```bash
# Run a guided deployment
sam deploy --guided
```

Follow the prompts to deploy your application:
- Stack Name: `pc-builder-backend`
- AWS Region: `eu-west-3` (or your preferred region)
- Parameter overrides: Press Enter to use defaults
- Confirm changes: `y`
- Allow SAM to create roles: `y`
- Disable rollback: `n`

### Option 2: SAM Package and Deploy (Manual)

```bash
# Package the application
sam package --template-file template.yaml --s3-bucket YOUR_S3_BUCKET --output-template-file packaged.yaml

# Deploy the packaged application
sam deploy --template-file packaged.yaml --stack-name pc-builder-backend --capabilities CAPABILITY_IAM
```

## Step 7: Verify Deployment

After deployment completes, SAM will display outputs including your API URL. You can also check the AWS Console:

1. Open the AWS Lambda Console
2. Find your `pc-builder-backend` function
3. Test the function or use the provided API Gateway URL

You can also retrieve the API URL at any time with:

```bash
aws cloudformation describe-stacks --stack-name pc-builder-backend --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text
```

## Step 8: Update Your Frontend

Update your Angular application to use the new API URL:

```typescript
// In your environment.ts or service files
apiBaseUrl: 'https://your-api-id.execute-api.eu-west-3.amazonaws.com/Prod'
```

## Testing the Lambda Deployment

Test your API with curl:

```bash
# Get the API URL
API_URL=$(aws cloudformation describe-stacks --stack-name pc-builder-backend --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text)

# Test the health endpoint
curl "${API_URL}health"

# Test the graphics cards endpoint
curl "${API_URL}graphics-cards"
```

## Additional Resources

- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [FastAPI + Lambda with Mangum](https://github.com/jordaneremieff/mangum)
- [API Gateway Lambda Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-create-api-as-simple-proxy-for-lambda.html)

## Troubleshooting

### Common Issues

1. **Deployment Permission Errors**:
   - Ensure your AWS user has the permissions: `cloudformation:*`, `lambda:*`, `apigateway:*`, `iam:CreateRole`, `iam:AttachRolePolicy`
   - Use `--capabilities CAPABILITY_IAM` with deployment commands

2. **Missing Dependencies**:
   - Make sure all dependencies are listed in `requirements.txt`
   - Some packages may need to be installed using Lambda Layers for size constraints

3. **S3 Access from Lambda**:
   - Make sure your Lambda function has proper permissions to access S3 buckets
   - Add an S3 policy to the function's role in the template.yaml

4. **Timeout Issues**:
   - If you experience timeouts, increase the `Timeout` property in template.yaml

### Debugging Lambda Functions

View CloudWatch logs for your function:

```bash
sam logs -n FastApiFunction --stack-name pc-builder-backend
```

Or through the AWS Console:
1. Go to CloudWatch > Log groups
2. Find the log group for your Lambda function (/aws/lambda/pc-builder-backend-FastApiFunction-XXXX)

### Removing the Deployment

To delete the entire deployment:

```bash
sam delete --stack-name pc-builder-backend
```
