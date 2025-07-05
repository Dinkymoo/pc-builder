#!/usr/bin/env python3
"""
Script to move workflow files to the workflow directory
and create symbolic links for backward compatibility.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.absolute()
WORKFLOW_DIR = BASE_DIR / "workflow"

# Files to move
WORKFLOW_FILES = [
    "pc-builder-workflow.py",
    "upload_to_s3.py",
    "delete_generated_files.py",
    "test-aws-credentials.py",
    "test-image-retrieval.py",
    "test-all.py",
    "test-new-credentials.py",
    "setup-s3.py",
    "start-all.sh",
    "start-backend.sh",
    "start-frontend.sh",
    "dev-all.sh"
]

# Create workflow directory
os.makedirs(WORKFLOW_DIR, exist_ok=True)
print(f"✅ Created workflow directory: {WORKFLOW_DIR}")

# Move files and create symlinks
for filename in WORKFLOW_FILES:
    src_file = BASE_DIR / filename
    dest_file = WORKFLOW_DIR / filename
    
    # Skip if source doesn't exist
    if not src_file.exists():
        print(f"⏭️  Skipping {filename} (not found)")
        continue
    
    # Copy file to workflow directory
    shutil.copy2(src_file, dest_file)
    print(f"📋 Copied {filename} to workflow directory")
    
    # Make executable if it's a shell script or Python script
    if filename.endswith(".sh") or filename.endswith(".py"):
        # SECURITY: Use a more restrictive file mode - 0o700 (rwx------) instead of 0o755
        # This restricts execution to owner only for maximum security
        # nosec B103 - This is a legitimate use case for chmod to make scripts executable
        os.chmod(dest_file, 0o700)  # rwx------
        print(f"🔒 Made {filename} executable with restricted permissions (rwx------)")
    
    # Create symbolic link
    try:
        # Remove original file
        os.remove(src_file)
        # Create symbolic link
        os.symlink(dest_file, src_file)
        print(f"🔗 Created symlink for {filename}")
    except Exception as e:
        print(f"❌ Failed to create symlink for {filename}: {e}")

# Create README.md in the workflow directory
with open(WORKFLOW_DIR / "README.md", "w") as f:
    f.write("""# PC Builder Workflow Scripts

This directory contains all the workflow scripts for the PC Builder project.

## Main Workflow

- `pc-builder-workflow.py` - Main workflow script that automates scraping, uploading to S3, and cleanup

## Data Management

- `upload_to_s3.py` - Upload data files and images to S3
- `delete_generated_files.py` - Clean up local generated files
- `setup-s3.py` - S3 setup script

## Testing

- `test-all.py` - Test all components (backend, frontend, S3)
- `test-aws-credentials.py` - Test AWS credentials
- `test-image-retrieval.py` - Test image retrieval
- `test-new-credentials.py` - Test new AWS credentials

## Service Control

- `start-all.sh` - Start both backend and frontend
- `start-backend.sh` - Start only the backend
- `start-frontend.sh` - Start only the frontend
- `dev-all.sh` - Start services in development mode

## Usage

All scripts can be run from the root directory (using symlinks) or directly from this directory.
""")
print(f"📝 Created README.md in workflow directory")

print("\n✅ Done! Workflow scripts have been moved to the workflow directory.")
print("   Symbolic links have been created for backward compatibility.")
