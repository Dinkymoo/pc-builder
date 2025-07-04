# PC Builder Workflow Scripts

This directory contains scripts for automating and managing workflows in the **PC Builder** project.

## Script Overview

| Script                      | Purpose                                         | Environment          | Use Case                           |
|-----------------------------|------------------------------------------------|----------------------|------------------------------------|
| `pc-builder-workflow.py`    | Automated data pipeline (scrape, upload, clean) | Any                  | Data management                    |
| `start-all.sh`              | Build and run all components                    | Production-like      | Testing full production setup      |
| `dev-all.sh`                | Run all components in development mode          | Development          | Active development with hot reload |
| `start-backend.sh`          | Start only the backend component                | Any                  | Testing backend in isolation       |
| `upload_to_s3.py`           | Upload generated files to S3                    | Any                  | Manual data management             |
| `delete_generated_files.py` | Clean up local generated files                  | Any                  | Manual cleanup                     |
| `test-all.py`               | Test all components                             | Any                  | Verify system functionality        |
| `test-aws-credentials.py`   | Test AWS credentials                            | Any                  | Debug AWS connectivity             |
| `test-image-retrieval.py`   | Test image retrieval from S3/backend            | Any                  | Debug image loading                |

## Key Scripts Explained

### `pc-builder-workflow.py`

This is the main workflow script that automates the entire data pipeline:

- Scrapes product data using Playwright-based scrapers
- Uploads results and images to AWS S3
- Cleans up local files as needed
- Handles errors robustly and provides clear feedback

**Usage:**
```sh
# Run the complete workflow
./pc-builder-workflow.py

# Use options for more control
./pc-builder-workflow.py --skip-cleanup
./pc-builder-workflow.py --scrape-only
./pc-builder-workflow.py --dry-run
```
See [DEVELOPER_SETUP.md](../DEVELOPER_SETUP.md) for more details.

### `start-all.sh` vs `dev-all.sh`

Both scripts start all project components, but with different environments:

#### `start-all.sh` (Production-like)

- Uses Docker for the backend
- Builds the frontend for production (`npm run build`)
- Suitable for testing a production-like setup

```sh
./start-all.sh
```

#### `dev-all.sh` (Development)

- Runs backend directly with Python/uvicorn (hot reload)
- Sets up a Python virtual environment
- Runs frontend in development mode (no build step)
- Best for active development

```sh
./dev-all.sh
```

## Other Utility Scripts

### Data Management

- `upload_to_s3.py`: Uploads data and images to S3 (manual use)
- `delete_generated_files.py`: Cleans up local generated files
- `setup-s3.py`: Sets up S3 buckets and permissions

### Testing

- `test-all.py`: Runs integration tests across all components
- `test-aws-credentials.py`: Verifies AWS credentials and connectivity
- `test-image-retrieval.py`: Tests image retrieval from S3/backend
- `test-new-credentials.py`: Tests new AWS credentials

## Using These Scripts

Most scripts support a `--help` flag for usage information:

```sh
./pc-builder-workflow.py --help
./upload_to_s3.py --help
./delete_generated_files.py --help
```

For shell scripts, view usage by reading the script:

```sh
cat start-all.sh
cat dev-all.sh
```

## Best Practices

- **Always use `pc-builder-workflow.py`** for regular data pipeline management (scraping, uploading, cleanup)
- Use `dev-all.sh` for active development
- Use `start-all.sh` to test the production-like setup
- Run utility scripts as needed for specific tasks
- Maintain backward compatibility with existing command-line options

## Directory Structure

Workflow scripts interact with the following project structure:

```
.
├── workflow/                  # Workflow scripts (this directory)
├── pc-builder/                # Main project (use this, not pc-builder-ui)
│   ├── pc-builder-app/        # Angular frontend
│   ├── pc-builder-backend/    # FastAPI backend with AWS integration
│   └── pc-builder-scraper/    # Playwright web scraper
├── data-results/              # Scraped CSV data
└── cdn-images/                # Downloaded images (for development)
```

> **Note:** The `pc-builder-ui/` directory is archived and should not be modified.

## Security Notes

- All scripts use environment variables or `.env` files for credentials
- No hardcoded secrets or credentials are present
- AWS operations are restricted by IAM policies
- Input data is validated and sanitized where applicable

---

*For more details, see the project root README and [DEVELOPER_SETUP.md](../DEVELOPER_SETUP.md).*
