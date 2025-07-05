# PC Builder Project Script Index

This document provides an overview of all scripts in the PC Builder project, their purpose, and usage instructions.

## Deployment Scripts

### `build-lambda-layer.sh`
- **Location:** `scripts/deploy/`
- **Purpose:** Creates Lambda-compatible Python packages as a Lambda Layer
- **Usage:** `./scripts/deploy/build-lambda-layer.sh`

### `deploy-lambda-enhanced.sh` (in backend directory)
- **Location:** `pc-builder/pc-builder-backend/`
- **Purpose:** Enhanced deployment script for AWS Lambda with diagnostics
- **Usage:** `cd pc-builder/pc-builder-backend && ./deploy-lambda-enhanced.sh [options]`
- **Options:**
  - `--use-layer`: Use a Lambda Layer for dependencies
  - `--fix-deps`: Fix dependency issues before deployment
  - `--downgrade`: Downgrade pydantic to v1.x for Lambda compatibility

## Startup Scripts

### `start-backend.sh`
- **Location:** `scripts/start/`
- **Purpose:** Starts the FastAPI backend locally
- **Usage:** `./scripts/start/start-backend.sh`

### `start-frontend.sh`
- **Location:** `scripts/start/`
- **Purpose:** Starts the Angular frontend locally
- **Usage:** `./scripts/start/start-frontend.sh`

### `start-frontend-with-lambda.sh`
- **Location:** `scripts/start/`
- **Purpose:** Starts the frontend configured to use Lambda backend
- **Usage:** `./scripts/start/start-frontend-with-lambda.sh`

## Diagnostic and Testing Scripts

### `test-api-gateway.sh`
- **Location:** `tests/api/`
- **Purpose:** Tests API Gateway endpoints and displays responses
- **Usage:** `./tests/api/test-api-gateway.sh`

### `test-api-gateway-enhanced.sh`
- **Location:** `tests/api/`
- **Purpose:** Advanced API Gateway testing with detailed diagnostics
- **Usage:** `./tests/api/test-api-gateway-enhanced.sh [options]`

## AWS Scripts

### `check_lambda_permissions.py`
- **Location:** `scripts/aws/`
- **Purpose:** Verifies AWS permissions required for Lambda deployment
- **Usage:** `python scripts/aws/check_lambda_permissions.py`

### `check_s3_data.py`
- **Location:** `scripts/aws/`
- **Purpose:** Checks S3 bucket for PC Builder data files
- **Usage:** `python scripts/aws/check_s3_data.py`

### `fix-stack.py`
- **Location:** `scripts/aws/`
- **Purpose:** Recovers CloudFormation stack from failed states
- **Usage:** `python scripts/aws/fix-stack.py`

### `recover-stack.sh`
- **Location:** `scripts/aws/`
- **Purpose:** Shell script to recover failed CloudFormation stacks
- **Usage:** `./scripts/aws/recover-stack.sh`

### `upload_to_s3.py`
- **Location:** `scripts/aws/`
- **Purpose:** Uploads CSV and image files to S3
- **Usage:** `python scripts/aws/upload_to_s3.py`

### `check_aws_permissions.py`
- **Location:** `scripts/aws/`
- **Purpose:** Checks AWS user permissions and IAM roles
- **Usage:** `python scripts/aws/check_aws_permissions.py`

## Workflow Scripts

### `pc-builder-workflow.py`
- **Location:** `workflow/`
- **Purpose:** Automates data scraping, S3 upload, and cleanup
- **Usage:** `cd workflow && python pc-builder-workflow.py [options]`
- **Options:**
  - `--scrape`: Run web scraping
  - `--upload`: Upload data to S3
  - `--cleanup`: Remove temporary files

## Test Scripts

### `test_scan_staged.py`
- **Location:** `tests/unit/`
- **Purpose:** Tests scanning of staged code changes
- **Usage:** `python tests/unit/test_scan_staged.py`

### `test-hooks.py`
- **Location:** `tests/unit/`
- **Purpose:** Tests Git hooks and their updates
- **Usage:** `python tests/unit/test-hooks.py`

### `test-aws-credentials.py`
- **Location:** `tests/aws/`
- **Purpose:** Tests AWS credentials configuration and S3 access
- **Usage:** `python tests/aws/test-aws-credentials.py`

### `test-image-retrieval.py`
- **Location:** `tests/aws/`
- **Purpose:** Tests image retrieval from AWS S3
- **Usage:** `python tests/aws/test-image-retrieval.py`

### `verify-structure.sh`
- **Location:** `tests/`
- **Purpose:** Verifies the project's directory structure and organization
- **Usage:** `./tests/verify-structure.sh`

## Utility Scripts

### `scan_all_with_bandit.py`
- **Location:** `scripts/utils/`
- **Purpose:** Security scanning of Python code
- **Usage:** `python scripts/utils/scan_all_with_bandit.py`

### `setup-workflow.py`
- **Location:** `scripts/setup/`
- **Purpose:** Sets up workflow scripts and configurations
- **Usage:** `python scripts/setup/setup-workflow.py`

### `install-dev-dependencies.sh`
- **Location:** `scripts/setup/`
- **Purpose:** Installs development dependencies (Bandit, pre-commit)
- **Usage:** `./scripts/setup/install-dev-dependencies.sh`
