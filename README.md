# PC Builder Project

This project implements a PC Builder application with:
- FastAPI backend (Python)
- Angular frontend (TypeScript)
- Web scraper using Playwright (Python)
- AWS S3 integration for image and data storage
- AWS Lambda/SAM deployment

> **Note (July 2025)**: The repository has been reorganized for better structure and maintainability.
> See [Project Organization](docs/PROJECT_ORGANIZATION.md) for details on the new structure.

## Quick Start

To get started with the PC Builder project, use the following commands:

```bash
# Install development dependencies (first time setup)
./scripts/setup/install-dev-dependencies.sh

# Development environment (hot reload)
./workflow/dev-all.sh

# Production-like environment (Docker + built frontend)
./workflow/start-all.sh

# Start just the backend service
./scripts/start/start-backend.sh

# Start just the frontend service
./scripts/start/start-frontend.sh

# Automated data workflow (scrape → upload → cleanup)
./workflow/pc-builder-workflow.py
```

## Directory Structure

```
.
├── pc-builder/            # Main project code
│   ├── pc-builder-app/    # Angular frontend
│   ├── pc-builder-backend/# FastAPI backend with AWS integration
│   └── pc-builder-scraper/# Web scraper components
├── docs/                  # Project documentation
├── scripts/               # Organized script directories
│   ├── aws/               # AWS-related scripts
│   ├── deploy/            # Deployment scripts
│   ├── diagnostics/       # Diagnostic tools
│   ├── setup/             # Setup and configuration scripts
│   ├── start/             # Application startup scripts
│   └── utils/             # Utility scripts
├── tests/                 # Test scripts
│   ├── api/               # API tests
│   ├── aws/               # AWS service tests
│   └── unit/              # Unit tests
├── config/                # Configuration files
├── workflow/              # Workflow automation scripts
├── data-results/          # Generated CSV data (gitignored)
└── cdn-images/            # Downloaded images (gitignored)
```

## Documentation

- [Developer Setup Guide](docs/DEVELOPER_GUIDE.md) - Setting up the development environment
- [Project Organization](docs/PROJECT_ORGANIZATION.md) - Project structure and organization principles
- [Script Index](docs/SCRIPT_INDEX.md) - Complete list of all project scripts and utilities
- [AWS Deployment Guide](docs/AWS_DEPLOYMENT.md) - Deploying to AWS ECS
- [AWS Lambda Deployment](docs/AWS_LAMBDA_DEPLOYMENT.md) - Deploying the API to AWS Lambda
- [API Gateway & Lambda Troubleshooting](docs/API_GATEWAY_LAMBDA_TROUBLESHOOTING.md) - Common issues and solutions
- [Using AWS Lambda API](docs/USING_AWS_LAMBDA_API.md) - Using the deployed Lambda API

## Workflow Automation

The project includes several workflow scripts to automate common tasks:

### Data Pipeline

```bash
# Run the complete data workflow
./workflow/pc-builder-workflow.py

# Options
./workflow/pc-builder-workflow.py --skip-cleanup  # Don't delete local files
./workflow/pc-builder-workflow.py --scrape-only   # Only run scraper
./workflow/pc-builder-workflow.py --dry-run       # Show what would happen
```

### Development

```bash
# Start all components for development
./workflow/dev-all.sh

# Start components individually
./workflow/start-backend.sh
```

### Testing

```bash
# Run all tests
./workflow/test-all.py

# Test AWS credentials
python tests/aws/test-aws-credentials.py

# Test API Gateway endpoints
./tests/api/test-api-gateway.sh

# Advanced API diagnostics
./tests/api/test-api-gateway-enhanced.sh

# Test S3 data access
python scripts/aws/check_s3_data.py
```

## Environment Setup

The project uses environment variables for configuration. Create a `.env` file with:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-west-3
S3_BUCKET=your-bucket-name
```

See [Developer Setup Guide](DEVELOPER_SETUP.md) for complete environment setup instructions.

## AWS Deployment

This project supports automated deployment to AWS ECS using GitHub Actions:

```bash
# View deployment status
aws ecs describe-services --cluster pc-builder-cluster --services pc-builder-service --region eu-west-3

# Monitor logs
aws logs get-log-events --log-group-name "/ecs/pc-builder-backend" --log-stream-name "latest" --region eu-west-3
```

For detailed deployment instructions, see [AWS Deployment Guide](AWS_DEPLOYMENT.md).

## Security Controls

This project uses several security controls:

- Pre-commit hooks with bandit for Python security scanning
- detect-secrets to prevent accidental credential commits
- Environment variables for sensitive configuration
- Input validation in API endpoints and scripts
- AWS IAM policies with least privilege
- Timeouts on all HTTP requests

When making changes:
- Run `pre-commit run --all-files` to check for security issues
- Use appropriate `# nosec` annotations only when necessary with explanation
- Never hardcode credentials or sensitive information

## Contributing

1. Follow the [Developer Setup Guide](DEVELOPER_SETUP.md)
2. Use the pre-commit hooks to ensure code quality
3. Run tests before submitting changes
4. Follow the coding standards in [GitHub Copilot Instructions](COPILOT_INSTRUCTIONS.md)
