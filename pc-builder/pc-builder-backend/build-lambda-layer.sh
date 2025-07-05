#!/bin/bash
# Build Lambda Layer with Compatible Dependencies for PC Builder Backend

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}     BUILDING AWS LAMBDA LAYER FOR PC BUILDER     ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Create directories for Lambda Layer
mkdir -p lambda-layer/python

# Copy the requirements file for Lambda
cp requirements-lambda.txt lambda-layer/requirements.txt

cd lambda-layer

echo -e "${YELLOW}Installing packages with platform-specific binaries for Lambda...${NC}"

# Install packages for Lambda
pip install --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --target=python \
  -r requirements.txt

if [ $? -ne 0 ]; then
  echo -e "${RED}Error installing packages for Lambda Layer. Trying alternative approach...${NC}"
  
  # Alternative approach: use docker container to build packages
  echo -e "${YELLOW}Using Docker container to build compatible dependencies...${NC}"
  
  # Check if Docker is available
  if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install Docker to build Lambda Layer.${NC}"
    exit 1
  fi
  
  # Create a Dockerfile for building Lambda dependencies
  cat > Dockerfile << EOL
FROM amazon/aws-lambda-python:3.11

WORKDIR /var/task
COPY requirements.txt .
RUN pip install -r requirements.txt -t /python
CMD cp -r /python/* /output/
EOL
  
  # Build the Docker image
  docker build -t lambda-layer-builder .
  
  # Run the container to extract the dependencies
  mkdir -p output
  docker run --rm -v $(pwd)/output:/output lambda-layer-builder
  
  # Move the packages to the python directory
  mv output/* python/
  
  if [ $? -ne 0 ]; then
    echo -e "${RED}Error building packages with Docker. Aborting.${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}✓ Installed packages successfully${NC}"
echo -e "${YELLOW}Creating ZIP file for Lambda Layer...${NC}"

# Create a ZIP file of the layer
zip -r ../pc-builder-lambda-layer.zip python/

cd ..

echo -e "${GREEN}✓ Created Lambda Layer: pc-builder-lambda-layer.zip${NC}"
echo -e "${YELLOW}Updating template.yaml with Lambda Layer reference...${NC}"

# Check if template.yaml already has the layer definition
if grep -q "DependenciesLayer" template.yaml; then
  echo -e "${YELLOW}Lambda Layer already defined in template.yaml${NC}"
else
  # Add the layer to the template
  echo -e "${YELLOW}Adding Lambda Layer to template.yaml...${NC}"
  
  # Create a temporary file
  TEMP_FILE=$(mktemp)
  
  # Add the layer to the template
  awk '/Resources:/{print;print "  DependenciesLayer:";print "    Type: AWS::Serverless::LayerVersion";print "    Properties:";print "      ContentUri: ./pc-builder-lambda-layer.zip";print "      CompatibleRuntimes:";print "        - python3.11";next}1' template.yaml > $TEMP_FILE
  
  # Add the layer to the function
  awk '/FastApiFunction:/{layer_added=0} /Properties:/ && !layer_added && layer_section{print;print "      Layers:";print "        - !Ref DependenciesLayer";layer_added=1;next} layer_section{layer_section=0} /FastApiFunction:/{layer_section=1} 1' $TEMP_FILE > template.yaml
  
  rm $TEMP_FILE
  
  echo -e "${GREEN}✓ Updated template.yaml with Lambda Layer${NC}"
fi

echo -e "${BLUE}==================================================${NC}"
echo -e "${GREEN}Lambda Layer created successfully!${NC}"
echo -e "${BLUE}==================================================${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Deploy using: ./deploy-lambda-enhanced.sh --use-layer"
echo "2. If issues persist, check CloudWatch logs for detailed errors"
echo "3. Verify Lambda execution role has required permissions"
echo -e "${BLUE}==================================================${NC}"
