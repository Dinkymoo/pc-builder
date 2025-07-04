# PC Builder Project

This project implements a PC Builder application with:
- FastAPI backend (Python)
- Angular frontend (TypeScript)
- Web scraper using Playwright (Python)
- AWS S3 integration for image and data storage
- AWS Lambda/SAM deployment

## Quick Start

To get started with the PC Builder project, use the following commands:

```bash
# Development environment (hot reload)
./workflow/dev-all.sh

# Production-like environment (Docker + built frontend)
./workflow/start-all.sh

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
├── workflow/              # Workflow automation scripts
├── data-results/          # Generated CSV data (gitignored)
└── cdn-images/            # Downloaded images (gitignored)
```

## Documentation

- [Developer Setup Guide](DEVELOPER_SETUP.md) - Complete setup instructions
- [Workflow Scripts](workflow/README.md) - Details on automation scripts
- Individual component READMEs in their respective directories

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
# Run tests
./workflow/test-all.py

# Test AWS credentials
./workflow/test-aws-credentials.py
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
