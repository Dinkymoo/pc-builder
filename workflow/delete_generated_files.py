#!/usr/bin/env python3
"""
Script to clean up generated files after they've been uploaded to S3.
This helps ensure that we don't accidentally commit generated files to Git.

Security Features:
- Path validation to prevent directory traversal
- Strict input validation for custom directories
- Detailed error logging
- Protection against deleting files outside target directories
- Proper exception handling

Usage:
  python delete_generated_files.py [--dry-run] [--images] [--data] [--custom dir:pattern] [-v]

Options:
  --dry-run     Show what would be deleted without actually deleting
  --images      Clean image files in cdn-images/
  --data        Clean data files in data-results/
  --custom      Clean files matching pattern in custom directory (format: dir:pattern)
  -v, --verbose Enable verbose logging
"""

import os
import sys
import argparse
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define directories and file patterns to clean
DATA_DIRS = ['data-results']
DATA_PATTERNS = ['*.csv', '*.log']
IMAGE_DIRS = ['cdn-images']

def is_safe_path(base_dir, path_to_check):
    """
    Validate that the path is contained within the base directory to prevent directory traversal.
    
    Args:
        base_dir (str): The base directory that should contain the path
        path_to_check (Path): The path to validate
        
    Returns:
        bool: True if the path is safe (within base_dir), False otherwise
    """
    # Security: Prevent path traversal by ensuring the path is contained within the base directory
    try:
        # Get the real paths (resolving symlinks) and make absolute
        base_path = os.path.abspath(os.path.realpath(base_dir))
        check_path = os.path.abspath(os.path.realpath(str(path_to_check)))
        
        # Check if the path is within the base directory
        common_prefix = os.path.commonpath([base_path, check_path])
        return common_prefix == base_path
    except ValueError:
        # commonpath raises ValueError if paths are on different drives (Windows)
        return False
    except Exception as e:
        logger.error(f"Path validation error: {str(e)}")
        return False

def clean_data_files(dry_run=False):
    """Clean generated data files."""
    deleted_count = 0
    
    for dir_path in DATA_DIRS:
        for pattern in DATA_PATTERNS:
            # Use the clean_directory function for each pattern
            deleted_count += clean_directory(
                base_dir=dir_path, 
                file_pattern=pattern, 
                recursive=True,  # Include subdirectories
                exclude_names=['.gitkeep'],
                dry_run=dry_run
            )
    
    return deleted_count

def clean_image_files(dry_run=False):
    """Clean downloaded images."""
    deleted_count = 0
    
    for dir_path in IMAGE_DIRS:
        # Use the clean_directory function for image files
        deleted_count += clean_directory(
            base_dir=dir_path, 
            file_pattern='*',  # Match all files
            recursive=True,  # Include subdirectories
            exclude_names=['.gitkeep'],
            dry_run=dry_run
        )
    
    return deleted_count

def clean_directory(base_dir, file_pattern='*', recursive=False, exclude_names=None, dry_run=False):
    """
    Clean files matching a pattern in a directory, with optional recursion.
    
    Args:
        base_dir (str): Base directory to clean
        file_pattern (str): Glob pattern to match files
        recursive (bool): Whether to recurse into subdirectories
        exclude_names (list): Names to exclude (e.g., ['.gitkeep'])
        dry_run (bool): If True, only show what would be deleted
        
    Returns:
        int: Number of files deleted
    """
    if exclude_names is None:
        exclude_names = ['.gitkeep']
        
    deleted_count = 0
    base_path = Path(base_dir)
    
    if not base_path.exists():
        logger.warning(f"Directory not found: {base_dir}")
        return 0
    
    # Determine glob pattern based on recursion
    glob_pattern = f"**/{file_pattern}" if recursive else file_pattern
    
    try:
        for file_path in base_path.glob(glob_pattern):
            # Skip directories and excluded files
            if file_path.is_dir() or file_path.name in exclude_names:
                continue
            
            # SECURITY: Validate the path is within base_dir to prevent directory traversal
            if not is_safe_path(base_dir, file_path):
                logger.warning(f"Skipping potentially unsafe file path: {file_path}")
                continue
                
            if dry_run:
                logger.info(f"Would delete: {file_path}")
            else:
                try:
                    os.remove(file_path)
                    logger.info(f"✅ Deleted: {file_path}")
                    deleted_count += 1
                except PermissionError:
                    logger.error(f"❌ Permission denied: {file_path}")
                except IsADirectoryError:
                    logger.warning(f"Skipping directory: {file_path}")
                except FileNotFoundError:
                    logger.warning(f"File not found: {file_path}")
                except Exception as e:
                    logger.error(f"❌ Failed to delete {file_path}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error while processing directory {base_dir}: {str(e)}")
        
    return deleted_count

def ensure_gitkeep(directory):
    """
    Ensures that a directory has a .gitkeep file to maintain empty directory structure in Git.
    
    Args:
        directory (str): Directory to check/create .gitkeep in
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            logger.debug(f"Directory {directory} doesn't exist, skipping .gitkeep")
            return
            
        gitkeep_path = dir_path / ".gitkeep"
        
        # SECURITY: Validate the path is safe
        if not is_safe_path(directory, gitkeep_path):
            logger.warning(f"Skipping potentially unsafe .gitkeep path: {gitkeep_path}")
            return
            
        # Create .gitkeep if it doesn't exist
        if not gitkeep_path.exists():
            try:
                with open(gitkeep_path, 'w') as f:
                    pass  # Create empty file
                logger.debug(f"Created .gitkeep in {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create .gitkeep in {directory}: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Error ensuring .gitkeep in {directory}: {str(e)}")

def main():
    """Main function to parse arguments and clean files."""
    parser = argparse.ArgumentParser(description="Clean up generated files after S3 upload")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--images', action='store_true', help='Clean image files')
    parser.add_argument('--data', action='store_true', help='Clean data files')
    parser.add_argument('--custom', type=str, help='Clean files in a custom directory (format: dir:pattern, e.g. temp:*.tmp)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    # Default behavior: clean both data and images if no specific flags provided
    if not (args.images or args.data or args.custom):
        args.images = True
        args.data = True
    
    # Print warning for dry run
    if args.dry_run:
        logger.info("⚠️  DRY RUN: No files will be deleted")
    
    deleted_count = 0
    errors = 0
    
    try:
        # Clean data files if requested
        if args.data:
            logger.info(f"{'Would clean' if args.dry_run else 'Cleaning'} data files...")
            try:
                deleted_count += clean_data_files(args.dry_run)
            except Exception as e:
                errors += 1
                logger.error(f"❌ Error cleaning data files: {str(e)}")
        
        # Clean image files if requested
        if args.images:
            logger.info(f"{'Would clean' if args.dry_run else 'Cleaning'} image files...")
            try:
                deleted_count += clean_image_files(args.dry_run)
            except Exception as e:
                errors += 1
                logger.error(f"❌ Error cleaning image files: {str(e)}")
        
        # Handle custom directory cleaning
        if args.custom:
            try:
                dir_pattern = args.custom.split(':')
                if len(dir_pattern) != 2:
                    logger.error("❌ Custom pattern must be in format 'directory:pattern' (e.g. temp:*.tmp)")
                    errors += 1
                else:
                    custom_dir, custom_pattern = dir_pattern
                    # Validate the custom directory path
                    project_root = os.path.dirname(os.path.abspath(__file__))
                    custom_path = os.path.abspath(os.path.join(project_root, custom_dir))
                    
                    # Security: Ensure custom directory is within project
                    if not is_safe_path(project_root, custom_path):
                        logger.error(f"❌ Security error: Custom directory {custom_dir} is outside project root")
                        errors += 1
                    else:
                        logger.info(f"{'Would clean' if args.dry_run else 'Cleaning'} custom files: {custom_dir}/{custom_pattern}...")
                        deleted_count += clean_directory(
                            base_dir=custom_path,
                            file_pattern=custom_pattern,
                            recursive=True,
                            dry_run=args.dry_run
                        )
            except Exception as e:
                errors += 1
                logger.error(f"❌ Error processing custom pattern: {str(e)}")
        
        # Report results
        if args.dry_run:
            logger.info(f"Would delete {deleted_count} files")
        else:
            logger.info(f"Deleted {deleted_count} files")
        
        # Ensure .gitkeep files are present in cleaned directories
        if not args.dry_run:
            for dir_path in DATA_DIRS + IMAGE_DIRS:
                # Ensure main directory has .gitkeep
                ensure_gitkeep(dir_path)
                
                # Also check subdirectories
                try:
                    for subdir in Path(dir_path).glob('**/'):
                        if is_safe_path(dir_path, subdir):
                            ensure_gitkeep(subdir)
                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Error ensuring .gitkeep in subdirectories: {str(e)}")
        
        if errors > 0:
            logger.warning(f"Completed with {errors} errors")
            return 1
        return 0
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
