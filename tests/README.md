# PC Builder Project Tests

This directory contains test scripts for various components of the PC Builder project.

## Directory Structure

- **api/** - Tests for API Gateway and FastAPI endpoints
- **aws/** - Tests for AWS services and connectivity
- **unit/** - Unit tests for project components

## Important Test Scripts

### API Tests
- `test-api-gateway.sh` - Basic API Gateway endpoint tests
- `test-api-gateway-enhanced.sh` - Advanced endpoint tests with diagnostics

### AWS Tests
- `test-aws-credentials.py` - Test AWS credential configuration
- `test-new-credentials.py` - Test newly generated AWS credentials
- `test-image-retrieval.py` - Test image retrieval from S3

### Unit Tests
- `test_scan_staged.py` - Test staged file scanning
- `test-hooks.py` - Test Git hooks configuration

## Running Tests

To run a specific test:

```bash
# For Python tests
python tests/aws/test-aws-credentials.py

# For shell scripts
./tests/api/test-api-gateway.sh
```

To run all tests, use:

```bash
# From the workflow directory
cd workflow && python test-all.py
```

## Writing New Tests

When adding new tests:

1. Place them in the appropriate subdirectory
2. Follow the existing naming conventions
3. Add documentation in the test file and update this README
4. Update the [Script Index](../docs/SCRIPT_INDEX.md) document
