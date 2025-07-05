# PC Builder Project Configuration

This directory contains configuration files for the PC Builder project.

## Important Files

- `.env` - Environment variables for local development
- `ecr-policy.json` - AWS ECR repository policy

## Environment Configuration

The `.env` file is used for local development and contains configuration such as:

- AWS credentials
- S3 bucket names
- API endpoints
- Backend URLs
- Other environment-specific settings

**Note:** The `.env` file is excluded from Git by default. Use `.env.example` as a template.

## AWS Configuration

AWS-related configuration files:

- `ecr-policy.json` - Policy for ECR repositories

## Usage

These configuration files are used by various scripts in the project. The environment variables from the `.env` file are automatically loaded by:

- The FastAPI backend
- Deployment scripts
- AWS CLI scripts
- The workflow automation scripts

## Adding New Configuration

When adding new configuration:

1. Update both the `.env` and `.env.example` files
2. Document the new configuration in this README
3. Ensure the configuration is properly loaded in scripts that need it
