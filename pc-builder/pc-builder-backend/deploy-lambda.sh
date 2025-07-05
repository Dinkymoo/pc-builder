#!/bin/bash
# Deploy FastAPI backend to AWS Lambda using SAM

# Exit on any error
set -e

# Change to the backend directory
cd "$(dirname "$0")"

echo "🛠️ Building the SAM application..."
sam build

echo "🚀 Deploying to AWS Lambda..."
# If the stack is in UPDATE_FAILED state, use --disable-rollback
STACK_STATUS=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].StackStatus" --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_STATUS" == "UPDATE_FAILED" ] || [ "$STACK_STATUS" == "UPDATE_ROLLBACK_FAILED" ]; then
  echo "⚠️ Stack is in $STACK_STATUS state. Using --disable-rollback to recover..."
  sam deploy --stack-name pc-builder --disable-rollback --capabilities CAPABILITY_IAM
else
  sam deploy --guided
fi

if [ $? -eq 0 ]; then
  echo "✅ Deployment completed successfully!"
  
  # Get the API URL
  API_URL=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text)
  
  echo "🌐 Your API is now available at:"
  echo "$API_URL"
  
  echo "🔍 Testing the health endpoint..."
  curl -s "${API_URL}health" | jq

  echo "📋 Testing the graphics cards endpoint..."
  curl -s "${API_URL}graphic-cards" | jq -c '.[0:1]'
  
  echo "🔍 Testing S3 connectivity..."
  curl -s "${API_URL}debug/check-s3" | jq
  
  echo "🔧 To check logs:"
  echo "sam logs -n FastApiFunction --stack-name pc-builder"
else
  echo "❌ Deployment failed. Check the error messages above."
  exit 1
fi
