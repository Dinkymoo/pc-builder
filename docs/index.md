# PC Builder Documentation Index

Welcome to the PC Builder documentation. This index will help you find the specific information you need.

## Repository Organization Notes

> **New in July 2025**: The repository has been reorganized to improve structure and maintainability.

### What Changed

1. **Directory Structure**:
   - Created `docs/` directory for all documentation
   - Created `scripts/` directory for utility scripts
   - Preserved existing `workflow/` and `pc-builder/` directories

2. **Documentation Improvements**:
   - Centralized all guides in `docs/` directory
   - Created this index for easier navigation
   - Added Script Index (`SCRIPT_INDEX.md`) documenting all scripts
   - Updated Developer Guide with comprehensive instructions

3. **Script Organization**:
   - Lambda-related scripts are now in both the backend directory and scripts directory
   - All scripts are properly documented and made executable
   - Build and deployment scripts now have consistent naming

### Maintaining This Structure

When adding new components to the project:

1. Place documentation in the `docs/` directory
2. Place utility scripts in the `scripts/` directory
3. Update the Script Index (`SCRIPT_INDEX.md`) when adding new scripts
4. Follow the existing naming conventions for consistency

## Getting Started

- [Developer Guide](DEVELOPER_GUIDE.md) - Setting up the development environment and best practices
- [Project Organization](PROJECT_ORGANIZATION.md) - Detailed explanation of repository structure and maintenance

## Scripts and Tools

- [Script Index](SCRIPT_INDEX.md) - Complete reference of all scripts in the project

## AWS Deployment

- [AWS Deployment Guide](AWS_DEPLOYMENT.md) - General AWS deployment instructions
- [AWS Lambda Deployment](AWS_LAMBDA_DEPLOYMENT.md) - Specific Lambda deployment steps
- [Lambda Troubleshooting](API_GATEWAY_LAMBDA_TROUBLESHOOTING.md) - Solutions for common Lambda/API Gateway issues
- [Using AWS Lambda API](USING_AWS_LAMBDA_API.md) - Integrating with the Lambda-deployed API

## Project Structure

The PC Builder project is organized as follows:

```
.
├── docs/               # Documentation files (you are here)
├── scripts/            # Utility and diagnostic scripts
├── workflow/           # Data workflow automation
├── pc-builder/         # Main project components
│   ├── pc-builder-app/       # Angular frontend
│   ├── pc-builder-backend/   # FastAPI backend with AWS Lambda support
│   └── pc-builder-scraper/   # Web scraping components
├── cdn-images/        # Local image storage (dev only)
└── data-results/      # Scraped data files
```

## Quick Reference

### Common Commands

```bash
# Start the backend (local development)
./start-backend.sh

# Start the frontend (local development)
./start-frontend.sh

# Start frontend with Lambda backend
./start-frontend-with-lambda.sh

# Run complete data workflow
python workflow/pc-builder-workflow.py --scrape --upload --cleanup

# Deploy to AWS Lambda
cd pc-builder/pc-builder-backend
./deploy-lambda-enhanced.sh --use-layer

# Test API Gateway endpoints
cd scripts
./test-api-gateway.sh
```

### Environment Variables

Key environment variables used by the project:

- `S3_BUCKET_NAME` - Name of the S3 bucket for storing data and images
- `S3_REGION` - AWS region for S3 bucket (default: eu-west-3)
- `USE_LOCAL_DATA` - Whether to use local data files (true/false)
- `LOCAL_DATA_PATH` - Path to local data file when USE_LOCAL_DATA is true
