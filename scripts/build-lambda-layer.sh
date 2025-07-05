#!/bin/bash
# Script to build Lambda-compatible Python packages for PC Builder backend

set -e

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Building Lambda-compatible Python packages for PC Builder${NC}"
echo "This script will create a Lambda Layer with all required dependencies"
echo "The Layer can be attached to your Lambda function to resolve dependency issues"
echo "---------------------------------------------------------------------"

# Create directories for Lambda Layer
echo -e "${YELLOW}Creating directories for Lambda Layer...${NC}"
mkdir -p lambda-layer/python

# Install packages with platform-specific binaries
echo -e "${YELLOW}Installing packages with Lambda-compatible binaries...${NC}"
pip install --platform manylinux2014_x86_64 \
  --target=lambda-layer/python \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  fastapi==0.103.1 \
  pydantic==1.10.8 \
  mangum==0.17.0 \
  boto3==1.28.40 \
  python-dotenv==1.0.0

if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing packages. Please check your pip setup.${NC}"
    exit 1
fi

# Create a ZIP file of the layer
echo -e "${YELLOW}Creating ZIP archive of Lambda Layer...${NC}"
cd lambda-layer
zip -r ../pc-builder-lambda-layer.zip python/

if [ $? -ne 0 ]; then
    echo -e "${RED}Error creating ZIP file. Please check if zip is installed.${NC}"
    exit 1
fi

cd ..

echo -e "${GREEN}Successfully created pc-builder-lambda-layer.zip${NC}"
echo "---------------------------------------------------------------------"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Upload the layer to AWS Lambda:"
echo "   aws lambda publish-layer-version \\"
echo "     --layer-name pc-builder-dependencies \\"
echo "     --zip-file fileb://pc-builder-lambda-layer.zip \\"
echo "     --compatible-runtimes python3.11"
echo ""
echo "2. Attach the layer to your function:"
echo "   aws lambda update-function-configuration \\"
echo "     --function-name YOUR_FUNCTION_NAME \\"
echo "     --layers \$(aws lambda publish-layer-version ... --query 'LayerVersionArn' --output text)"
echo ""
echo "3. If you're using SAM, add this to your template.yaml:"
echo "   Layers:"
echo "     - !Ref DependenciesLayer"
echo ""
echo "   Resources:"
echo "     DependenciesLayer:"
echo "       Type: AWS::Serverless::LayerVersion"
echo "       Properties:"
echo "         ContentUri: ./pc-builder-lambda-layer.zip"
echo "         CompatibleRuntimes:"
echo "           - python3.11"
echo "---------------------------------------------------------------------"
