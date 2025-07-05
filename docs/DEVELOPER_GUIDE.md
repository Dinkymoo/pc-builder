# PC Builder Project - Developer Guide

This guide provides instructions for setting up, organizing, and working with the PC Builder project.

## Project Organization

The PC Builder project is organized as follows:

```
pc-builder/
├── docs/               # Documentation files
├── scripts/            # Utility and diagnostic scripts
├── workflow/           # Data workflow automation
├── pc-builder/         # Main project components
│   ├── pc-builder-app/       # Angular frontend
│   ├── pc-builder-backend/   # FastAPI backend
│   └── pc-builder-scraper/   # Web scraping components
├── cdn-images/        # Local image storage (dev only)
└── data-results/      # Scraped data files
```

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/pc-builder.git
cd pc-builder
```

### 2. Set Up the Development Environment

```sh
# Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r pc-builder/pc-builder-backend/requirements.txt

# Install development dependencies (including Bandit for security scanning)
./scripts/setup/install-dev-dependencies.sh

# Install frontend dependencies
cd pc-builder/pc-builder-app
npm install
cd ../..
```

### 3. Configure Environment Variables

Create a `.env` file in the `config/` directory with the following settings:

```
# S3 Configuration
S3_BUCKET_NAME=your-s3-bucket-name
S3_REGION=eu-west-3

# Local Development
USE_LOCAL_DATA=true
LOCAL_DATA_PATH=./data-results/graphics-cards.csv
```

## Common Development Tasks

### Running the Application

For local development:
```sh
# Start backend
./scripts/start/start-backend.sh

# In a separate terminal, start frontend
./scripts/start/start-frontend.sh
```

For Lambda integration:
```sh
# Start frontend with Lambda API
./scripts/start/start-frontend-with-lambda.sh
```

### Data Workflow

Use the workflow script to manage data operations:
```sh
# Run the complete workflow
python workflow/pc-builder-workflow.py --scrape --upload --cleanup

# Only scrape data
python workflow/pc-builder-workflow.py --scrape

# Only upload existing data to S3
python workflow/pc-builder-workflow.py --upload
```

### AWS Lambda Deployment

1. Build the Lambda layer:
```sh
cd pc-builder/pc-builder-backend
./build-lambda-layer.sh
```

2. Deploy using the enhanced script:
```sh
./deploy-lambda-enhanced.sh --use-layer
```

3. Verify deployment:
```sh
cd ../../tests/api
./test-api-gateway.sh
```

## Troubleshooting

For detailed troubleshooting information, please refer to the following resources:

- **API Gateway/Lambda Issues**: See `docs/API_GATEWAY_LAMBDA_TROUBLESHOOTING.md`
- **AWS Deployment Guide**: See `docs/AWS_DEPLOYMENT.md`
- **Interactive Diagnostics**: Run `scripts/diagnose-api-issues.sh`

## Script Reference

For a complete list of project scripts and their usage, see `docs/SCRIPT_INDEX.md`.

## Development Best Practices

1. **Environment Management**
   - Always use a virtual environment for Python development
   - Keep frontend and backend dependencies separate and up to date

2. **Code Organization**
   - Follow component separation in the Angular app
   - Use type hints in Python code
   - Document APIs and complex functions

3. **Testing**
   - Test API endpoints before deployment
   - Verify data scraping results before upload

4. **AWS Resources**
   - Check permissions before deployment
   - Use the diagnostic scripts to troubleshoot issues
