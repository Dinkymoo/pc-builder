#!/usr/bin/env python3
"""
PC Builder Project Workflow Script

This script automates the entire PC Builder workflow:
1. Run scrapers to generate data
2. Upload data and images to S3
3. Clean up local files (optional)
4. Test backend and frontend (optional)

Usage:
  python pc-builder-workflow.py [options]

Options:
  --skip-scrape      Skip scraping step
  --skip-upload      Skip uploading to S3
  --skip-cleanup     Skip cleaning up local files
  --test-backend     Test backend after workflow
  --test-frontend    Test frontend after workflow
  --dry-run          Show what would happen without making changes
  --scrape-only      Only run the scraping step
  --upload-only      Only run the upload step
  --cleanup-only     Only run the cleanup step
  --help             Show this help message
"""

import os
import sys
import subprocess  # nosec B404 - Used with validation and security controls
import argparse
import logging
import time
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # One level up from workflow dir
SCRAPER_DIR = os.path.join(BASE_DIR, 'pc-builder', 'pc-builder-scraper')
BACKEND_DIR = os.path.join(BASE_DIR, 'pc-builder', 'pc-builder-backend')
FRONTEND_DIR = os.path.join(BASE_DIR, 'pc-builder', 'pc-builder-app')
DATA_DIR = os.path.join(BASE_DIR, 'data-results')
IMAGES_DIR = os.path.join(BASE_DIR, 'cdn-images')
WORKFLOW_DIR = os.path.join(BASE_DIR, 'workflow')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PC Builder Workflow - Automate scraping, uploading to S3, and cleanup"
    )
    parser.add_argument('--skip-scrape', action='store_true', help='Skip scraping step')
    parser.add_argument('--skip-upload', action='store_true', help='Skip uploading to S3')
    parser.add_argument('--skip-cleanup', action='store_true', help='Skip cleaning up local files')
    parser.add_argument('--test-backend', action='store_true', help='Test backend after workflow')
    parser.add_argument('--test-frontend', action='store_true', help='Test frontend after workflow')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without making changes')
    
    # Exclusive operation modes
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--scrape-only', action='store_true', help='Only run the scraping step')
    group.add_argument('--upload-only', action='store_true', help='Only run the upload step')
    group.add_argument('--cleanup-only', action='store_true', help='Only run the cleanup step')
    
    return parser.parse_args()

def run_command(cmd, cwd=None, env=None, check=True, capture_output=False):
    """Run a command and return the result."""
    if env is None:
        env = os.environ.copy()
    # SECURITY: Never use untrusted input in shell commands. Validate all arguments.
    # Security: Validate cmd is a list and all elements are strings
    if not isinstance(cmd, list):
        raise ValueError("Command must be a list")
    if not all(isinstance(arg, str) for arg in cmd):
        raise ValueError("All command arguments must be strings")
    # SECURITY: Avoid logging secrets, credentials, or sensitive file paths.
    logger.info(f"Running command: {' '.join(cmd)}")
    try:
        result = subprocess.run(  # nosec B603 - Input is validated above
            cmd, 
            cwd=cwd, 
            env=env, 
            check=check,
            capture_output=capture_output,
            text=True,
            shell=False  # Explicitly set shell=False for security
        )
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}")
        if capture_output:
            logger.error(f"STDOUT: {e.stdout}")
            logger.error(f"STDERR: {e.stderr}")
        if check:
            sys.exit(e.returncode)
        return e

def setup_virtual_env():
    """Set up and activate the virtual environment."""
    venv_dir = os.path.join(os.path.dirname(SCRAPER_DIR), '.venv')
    # SECURITY: Ensure no untrusted code is executed in the venv context.
    if not os.path.exists(venv_dir):
        logger.info("Creating virtual environment...")
        # Using the run_command function which has security validation
        run_command([sys.executable, '-m', 'venv', venv_dir], check=True)
    
    # Return the path to the Python executable in the venv
    if sys.platform == 'win32':
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    return python_path

def run_scraper(python_path, dry_run=False):
    """Run the scraper to generate data."""
    logger.info("🔍 Running scraper to generate data...")
    
    if dry_run:
        logger.info("DRY RUN: Would run the graphics cards scraper")
        return True
    
    # Install requirements
    run_command(
        [python_path, '-m', 'pip', 'install', '-r', 'requirements.txt'],
        cwd=SCRAPER_DIR
    )
    
    # Run the scraper
    start_time = time.time()
    result = run_command(
        [python_path, 'product_scraper_graphics_cards.py'],
        cwd=SCRAPER_DIR,
        check=False
    )
    
    if result.returncode != 0:
        logger.error("❌ Scraper failed")
        return False
    
    elapsed_time = time.time() - start_time
    logger.info(f"✅ Scraper completed in {elapsed_time:.1f} seconds")
    
    # Check if data was generated
    csv_path = os.path.join(DATA_DIR, 'graphics-cards.csv')
    if not os.path.exists(csv_path):
        logger.error(f"❌ Expected output file not found: {csv_path}")
        return False
    
    logger.info(f"✅ Generated data file: {csv_path}")
    return True

def upload_to_s3(python_path, dry_run=False):
    """Upload data and images to S3."""
    logger.info("☁️ Uploading data and images to S3...")
    
    if dry_run:
        logger.info("DRY RUN: Would upload data and images to S3")
        return True
    
    cmd = [python_path, os.path.join(WORKFLOW_DIR, 'upload_to_s3.py')]
    # Always run from the project root for consistent path handling
    result = run_command(cmd, cwd=BASE_DIR, check=False)
    
    if result.returncode != 0:
        logger.error("❌ Upload to S3 failed")
        return False
    
    logger.info("✅ Upload to S3 completed")
    return True

def cleanup_local_files(python_path, dry_run=False):
    """Clean up local generated files."""
    logger.info("🧹 Cleaning up local generated files...")
    
    cmd = [python_path, os.path.join(WORKFLOW_DIR, 'delete_generated_files.py')]
    if dry_run:
        cmd.append('--dry-run')
    
    # Always run from the project root for consistent path handling
    result = run_command(cmd, cwd=BASE_DIR, check=False)
    
    if result.returncode != 0:
        logger.error("❌ Cleanup failed")
        return False
    
    if not dry_run:
        logger.info("✅ Local files cleaned up")
    return True

def test_backend():
    """Test the backend API."""
    logger.info("🧪 Testing backend API...")
    # SECURITY: Always use timeouts for network calls to avoid hanging.
    # Use the test script if it exists
    test_script = os.path.join(WORKFLOW_DIR, 'test-all.py')
    if os.path.exists(test_script):
        result = run_command(
            [sys.executable, test_script], 
            cwd=BASE_DIR,  # Run from project root
            check=False,
            capture_output=True
        )
        
        if result.returncode != 0:
            logger.error("❌ Backend tests failed")
            if hasattr(result, 'stdout'):
                logger.error(result.stdout)
            return False
        
        logger.info("✅ Backend tests passed")
        return True
    
    # Fallback to a simple health check
    logger.info("Running simple health check (no test script found)")
    try:
        import requests
        resp = requests.get("http://localhost:8000/health", timeout=5)  # Add timeout
        if resp.status_code == 200:
            logger.info("✅ Backend health check passed")
            return True
        else:
            logger.error(f"❌ Backend returned status code {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Backend health check failed: {str(e)}")
        return False

def test_frontend():
    """Test the frontend."""
    logger.info("🧪 Testing frontend...")
    # SECURITY: Always use timeouts for network calls to avoid hanging.
    # For now, just check if the frontend is accessible
    try:
        import requests
        resp = requests.get("http://localhost:4200", timeout=5)  # Add timeout
        if resp.status_code == 200:
            logger.info("✅ Frontend accessible at http://localhost:4200")
            return True
        else:
            logger.error(f"❌ Frontend returned status code {resp.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Frontend check failed: {str(e)}")
        logger.error("Make sure the frontend is running (npm start)")
        return False

def main():
    """Main workflow function."""
    args = parse_args()
    
    # Create a timestamp for this workflow run
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"======= PC Builder Workflow - {timestamp} =======")
    
    if args.dry_run:
        logger.info("⚠️ DRY RUN MODE - No changes will be made")
    
    # Set up Python environment
    python_path = setup_virtual_env()
    
    # Determine what steps to run based on arguments
    run_scrape = not args.skip_scrape and not args.upload_only and not args.cleanup_only
    run_upload = not args.skip_upload and not args.scrape_only and not args.cleanup_only
    run_cleanup = not args.skip_cleanup and not args.scrape_only and not args.upload_only
    
    # Override with specific-only flags
    if args.scrape_only:
        run_scrape = True
        run_upload = False
        run_cleanup = False
    elif args.upload_only:
        run_scrape = False
        run_upload = True
        run_cleanup = False
    elif args.cleanup_only:
        run_scrape = False
        run_upload = False
        run_cleanup = True
    
    success = True
    
    # Run the selected steps
    if run_scrape:
        if not run_scraper(python_path, args.dry_run):
            success = False
            if not args.dry_run:
                logger.error("❌ Scraping failed, stopping workflow")
                return 1
    
    if run_upload and success:
        if not upload_to_s3(python_path, args.dry_run):
            success = False
            if not args.dry_run:
                logger.error("❌ Upload failed, stopping workflow")
                return 1
    
    if run_cleanup and success:
        if not cleanup_local_files(python_path, args.dry_run):
            success = False
    
    # Run tests if requested
    if args.test_backend and success and not args.dry_run:
        if not test_backend():
            success = False
    
    if args.test_frontend and success and not args.dry_run:
        if not test_frontend():
            success = False
    
    # Final status
    if success:
        if args.dry_run:
            logger.info("✅ Dry run completed successfully")
        else:
            logger.info("✅ All workflow steps completed successfully")
    else:
        logger.error("❌ Workflow completed with errors")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
