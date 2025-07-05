# PC Builder Project Organization Guide

This document explains the reorganization of the PC Builder project structure and provides guidelines for maintaining this organization.

## Organization Rationale

The PC Builder project was reorganized in July 2025 to address several issues:

1. **Scattered Documentation**: Documentation files were spread throughout the repository
2. **Unclear Script Purposes**: Many scripts existed without clear documentation
3. **Inconsistent Naming**: Various scripts used different naming conventions
4. **Limited Structure**: The flat structure made navigation difficult

## Reorganization Changes

### Directory Structure

The repository now follows this organized structure:

```
.
├── docs/               # Documentation files
├── scripts/            # Utility and diagnostic scripts
├── workflow/           # Data workflow automation
├── pc-builder/         # Main project components
│   ├── pc-builder-app/       # Angular frontend
│   ├── pc-builder-backend/   # FastAPI backend with AWS Lambda support
│   └── pc-builder-scraper/   # Web scraping components
├── cdn-images/        # Local image storage (dev only)
└── data-results/      # Scraped data files
```

### Documentation Centralization

All documentation files are now in the `docs/` directory:

- **index.md**: Main documentation index
- **DEVELOPER_GUIDE.md**: Comprehensive setup and development guide
- **SCRIPT_INDEX.md**: Reference for all scripts
- **AWS_*.md**: All AWS-related documentation

### Script Organization

Utility and diagnostic scripts are now organized in the `scripts/` directory:

- **Test Scripts**: Scripts for testing API, AWS services
- **Diagnostic Tools**: Tools for troubleshooting issues
- **Recovery Scripts**: Scripts for recovering from failure states

Component-specific scripts remain in their component directories.

## Maintenance Guidelines

### Adding New Features

When adding new features to the PC Builder project:

1. **Documentation**:
   - Add/update documentation in the `docs/` directory
   - Update the Script Index if adding new scripts
   - Keep the main README.md concise and focused on quick start

2. **Component Organization**:
   - Keep component-specific code within its directory
   - Use consistent naming conventions for files and functions
   - Follow the established project structure

3. **Scripts**:
   - Place utility scripts in the `scripts/` directory
   - Place component-specific scripts in their component directory
   - Document script purpose at the top of each script
   - Make shell scripts executable (`chmod +x script.sh`)

### Best Practices for Organization

1. **File Naming**:
   - Use kebab-case for script names (e.g., `deploy-lambda.sh`)
   - Use snake_case for Python files (e.g., `check_s3_data.py`)
   - Use PascalCase for TypeScript/Angular components

2. **Documentation**:
   - Use Markdown for all documentation
   - Include code examples where helpful
   - Document environment variables and configuration options
   - Keep documentation updated when making changes

3. **Directory Structure**:
   - Maintain separation of concerns between directories
   - Don't mix utility scripts with component code
   - Keep related files together in the same directory

## Git Practices

When committing changes:

1. **Organize Commits**:
   - Group related changes in a single commit
   - Use clear commit messages that describe the change

2. **Documentation Updates**:
   - Update documentation alongside code changes
   - Include documentation changes in the same PR as code changes

3. **.gitignore Management**:
   - The .gitignore file now includes entries for Lambda layers and build artifacts
   - Add new entries when introducing new build processes or dependencies

## Future Improvements

Areas identified for potential future organization improvements:

1. **Component Modularization**: Further modularize the Angular components
2. **Test Organization**: Create a dedicated structure for tests
3. **CI/CD Integration**: Add GitHub Actions workflows for testing and deployment
4. **Environment Management**: Improve handling of different environments

## Conclusion

This organization structure balances flexibility with clarity. By following these guidelines, we can maintain a clean and understandable project structure as the PC Builder project evolves.
