#!/bin/bash
# Deploy FastAPI backend to AWS Lambda using SAM

# Exit on any error
set -e

# Change to the backend directory
cd "$(dirname "$0")"

echo "🛠️ Building the SAM application..."
sam build

echo "🚀 Deploying to AWS Lambda..."
sam deploy --guided

if [ $? -eq 0 ]; then
  echo "✅ Deployment completed successfully!"
  
  # Get the API URL
  API_URL=$(aws cloudformation describe-stacks --stack-name pc-builder --query "Stacks[0].Outputs[?OutputKey=='ApiURL'].OutputValue" --output text)
  
  echo "🌐 Your API is now available at:"
  echo "$API_URL"
  
  echo "🔍 Testing the health endpoint..."
  curl -s "${API_URL}health" | jq

  echo "📋 To test the graphics cards endpoint:"
  echo "curl ${API_URL}graphics-cards"
  
  echo "🔧 To check logs:"
  echo "sam logs -n FastApiFunction --stack-name pc-builder"
else
  echo "❌ Deployment failed. Check the error messages above."
  exit 1
fi
