# GitHub Copilot Instructions for PC Builder Project

This file contains instructions for GitHub Copilot to help maintain consistent code quality and follow project standards when assisting with development tasks.

## Project Overview

This is a PC Builder application consisting of:
- FastAPI backend (Python)
- Angular frontend (TypeScript)
- Web scraper using Playwright (Python)
- AWS S3 integration for image and data storage
- AWS Lambda/SAM deployment
- Automated data workflow script

## Important Note on Project Structure

This project originally had two implementations:
- `pc-builder/` - The primary, most up-to-date implementation (KEEP THIS)
- `pc-builder-ui/` - An older, incomplete implementation (ARCHIVED)

Always work with the code in the `pc-builder/` directory, which contains:
- `pc-builder-app/` - Angular frontend
- `pc-builder-backend/` - FastAPI backend with AWS integration
- `pc-builder-scraper/` - Web scraper components

The `pc-builder-ui/` directory has been backed up and should not be modified.

## Workflow Directory

All automation and workflow scripts are now located in the `workflow/` directory:
- `pc-builder-workflow.py` - Main automation script
- `upload_to_s3.py` - S3 data upload
- `delete_generated_files.py` - Local cleanup
- Test scripts and shell scripts for starting components

When adding new workflow scripts:
- Place them in the `workflow/` directory
- Update paths to work correctly from that location
- Add appropriate security annotations for bandit
- Document in the `workflow/README.md` file

### Pre-commit Configuration

When working with Python files, especially in the workflow directory:
- Ensure they pass bandit security checks: `pre-commit run bandit --files <file_path>`
- Use `# nosec` annotations appropriately and sparingly
- Test all hooks before committing: `./test-hooks.py`
- Remember that hooks run automatically on `git commit`

If you encounter errors with pre-commit hooks:
1. Check the specific error message
2. Run the hook manually on individual files to debug
3. Make minimal necessary changes to configuration

## Data Workflow

This project uses the `workflow/pc-builder-workflow.py` script to automate the data pipeline:

- It handles scraping, uploading to S3, and cleanup in one command
- Always suggest using this script instead of manual steps when possible
- Maintain backward compatibility with existing command-line options
- Keep error handling robust and provide clear feedback
- Respect the virtual environment setup pattern

When making changes to data handling components, ensure they work with this workflow.

## Coding Standards

### Python

- Follow PEP 8 style guidelines
- Use type hints wherever possible
- Log at appropriate levels (debug/info/warning/error)
- Avoid printing sensitive information in logs
- Include docstrings for all functions and classes
- Prefer dependency injection over global state
- Use environment variables for configuration
- Handle exceptions gracefully with appropriate messages

### TypeScript/Angular

- Follow Angular style guide
- Use strong typing with interfaces and types
- Organize code into feature modules
- Use services for data management and API calls
- Follow reactive programming patterns with RxJS
- Use Angular Material components when applicable
- Implement proper error handling and loading states

### Security

- No hardcoded secrets or credentials
- Use environment variables for sensitive information
- Validate input data, especially from external sources
- Sanitize user inputs to prevent XSS attacks
- Follow least privilege principle for AWS resources
- Use HTTPS for all API calls

## Directory Structure

- `pc-builder/pc-builder-backend/`: FastAPI backend application
- `pc-builder/pc-builder-app/`: Angular frontend application
- `pc-builder/pc-builder-scraper/`: Playwright web scraper
- `data-results/`: Scraped CSV data
- `cdn-images/`: Locally stored images (for development)

## Common Tasks

### Adding New API Endpoints

- Create endpoints in `pc-builder-backend/app/`
- Follow RESTful conventions
- Include proper input validation
- Document with FastAPI's automatic documentation
- Add appropriate error handling

### Working with AWS Services

- Use boto3 for AWS interactions
- Configure fallbacks for local development
- Follow AWS best practices for Lambda functions
- Handle S3 operations with proper error checking

### Scraper Enhancements

- Organize scrapers by product category
- Include robust error handling for site changes
- Respect robots.txt and rate limiting
- Save data consistently to CSV format
- Download and process images responsibly

### Frontend Features

- Organize by feature modules
- Use reactive forms with validation
- Implement responsive designs
- Follow component composition patterns
- Use NgRx for complex state management

## Testing

- Write unit tests for all new functionality
- Include integration tests for API endpoints
- Mock external services in tests
- Test error conditions and edge cases
- Run tests before submitting changes

## Deployment

- Follow AWS SAM deployment patterns
- Update CloudFormation templates as needed
- Ensure Lambda compatibility
- Document environment variables

## Resources

- FastAPI documentation: https://fastapi.tiangolo.com/
- Angular documentation: https://angular.io/docs
- AWS SAM documentation: https://docs.aws.amazon.com/serverless-application-model/
- Playwright documentation: https://playwright.dev/python/docs/intro

---

*Note: These instructions should be updated as the project evolves.*
