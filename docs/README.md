# PC Builder Project Scripts

This directory contains organized scripts for various aspects of the PC Builder project.

## Directory Structure

- **aws/** - Scripts for AWS services and resources
- **deploy/** - Deployment scripts for Lambda and other services
- **diagnostics/** - Scripts to diagnose and troubleshoot issues
- **setup/** - Setup and initialization scripts
- **start/** - Scripts to start services locally
- **utils/** - Utility scripts for various tasks

## Important Scripts

### AWS Scripts
- `check_aws_permissions.py` - Verify AWS user permissions
- `check_lambda_permissions.py` - Check required Lambda permissions
- `check_s3_data.py` - Verify S3 data accessibility
- `upload_to_s3.py` - Upload data to S3 bucket
- `fix-stack.py` - Fix CloudFormation stack issues

### Deployment Scripts
- `build-lambda-layer.sh` - Build Lambda layer for dependencies

### Diagnostics Scripts
- `diagnose-api-issues.sh` - Diagnose API connectivity issues

### Start Scripts
- `start-backend.sh` - Start the FastAPI backend locally
- `start-frontend.sh` - Start the Angular frontend locally
- `start-frontend-with-lambda.sh` - Start frontend with Lambda backend

### Utility Scripts
- `scan_all_with_bandit.py` - Security scan Python code
- `cleanup-old-files.sh` - Remove files after reorganization

## Usage

To run a script, navigate to the appropriate directory and run:

```bash
# For Python scripts
python scripts/aws/check_aws_permissions.py

# For shell scripts
./scripts/start/start-backend.sh
```

For more detailed information on each script, refer to the [Script Index](../docs/SCRIPT_INDEX.md) document.
