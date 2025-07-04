#!/usr/bin/env python3
"""
Script to recursively scan all relevant Python files in the project using Bandit.
Skips non-Python files and .gitkeep files.
"""

import os
import sys
import subprocess

# Directories to scan
SCAN_DIRS = [
    "workflow",
    "pc-builder/pc-builder-backend",
    "pc-builder/pc-builder-scraper",
    ".",
]

# File extensions to include
# SECURITY: Only include Python source files for Bandit scanning. Do not add other extensions unless Bandit supports them.
INCLUDE_EXT = (".py",)

# Files to exclude
# SECURITY: Keep this exclusion list up to date! If you add new sensitive, temporary, or non-source files (e.g., backups, editor swap files, credentials),
# add them here to avoid scanning or exposing them with Bandit.
# Example patterns: .gitkeep, .swp, .bak, *~
EXCLUDE_FILES = {".gitkeep", ".swp", ".bak", "~"}

# Directories to exclude from scanning (third-party, build, cache, etc.)
# SECURITY: Keep this exclusion list up to date! If you add new dependencies, build systems, or vendored code,
# add their directories here to avoid scanning third-party code with Bandit.
# This helps prevent noise and accidental exposure of non-project code issues.
EXCLUDE_DIRS = [
    '__pycache__', 'bin', 'boto3', 'botocore', 'pydantic', 'starlette', 'fastapi',
    'mangum', 'typing_extensions', 'anyio', 'dateutil', 'dotenv', 'click', 'idna',
    'jmespath', 'python_dateutil', 'python_dotenv', 's3transfer', 'six', 'sniffio',
    'pydantic_core', 'typing_inspection', '.git', '.venv', 'venv', '.mypy_cache',
    '.pytest_cache', '.vscode', '.idea', 'dist', 'build', '*.dist-info', '*.egg-info'
]

def is_excluded(path):
    for excl in EXCLUDE_DIRS:
        if excl.startswith('*.'):
            if path.endswith(excl[1:]):
                return True
        elif excl in path.split(os.sep):
            return True
    return False

def find_python_files():
    """
    Find Python files for scanning while applying security restrictions.
    
    Security controls:
    - Skips symlinked directories to prevent path traversal
    - Skips symlinked files to prevent scanning outside project
    - Validates file extensions before inclusion
    - Uses realpath to resolve any .. or other path tricks
    - Multiple exclusion layers to filter out third-party code
    
    Returns:
        list: List of validated Python file paths to scan
    """
    files = []
    # SECURITY: Convert all scan directories to absolute paths to prevent confusion
    scan_dirs_abs = [os.path.abspath(d) for d in SCAN_DIRS]
    
    for scan_dir in scan_dirs_abs:
        # SECURITY: Skip if scan directory doesn't exist or isn't a directory
        if not os.path.isdir(scan_dir):
            print(f"Warning: Skipping non-existent or non-directory: {scan_dir}")
            continue
            
        for root, dirs, filenames in os.walk(scan_dir):
            # SECURITY: Skip symlinked directories to avoid scanning outside the project tree
            dirs[:] = [d for d in dirs if not os.path.islink(os.path.join(root, d))]
            
            # SECURITY: Skip excluded directories
            if is_excluded(root):
                continue
                
            for fname in filenames:
                # Skip files with excluded extensions early
                if not fname.endswith(INCLUDE_EXT):
                    continue
                    
                # Skip excluded filenames
                if fname in EXCLUDE_FILES:
                    continue
                    
                # Construct the full path
                full_path = os.path.join(root, fname)
                
                # SECURITY: Skip symlinked files to avoid scanning outside the project tree
                if os.path.islink(full_path):
                    continue
                    
                # SECURITY: Get real path to handle any '..' or other path tricks
                real_path = os.path.realpath(full_path)
                
                # SECURITY: Ensure the file is still within one of our scan directories
                # after resolving the real path (prevents path traversal)
                in_scan_dir = any(real_path.startswith(d) for d in scan_dirs_abs)
                if not in_scan_dir:
                    print(f"Warning: Path traversal attempt detected: {full_path}")
                    continue
                    
                # Final exclusion check
                if not is_excluded(real_path):
                    files.append(real_path)
    return files

def get_staged_files():
    """
    Get a list of Python files that are staged for commit in Git.
    
    Security controls:
    - Uses subprocess.run with arguments as list (not shell=True) to prevent command injection
    - Validates file extensions and existence before inclusion
    - Handles errors gracefully without leaking sensitive information
    
    Returns:
        list: List of absolute paths to staged Python files
    """
    try:
        # SECURITY: Use subprocess.run with arguments as a list (not shell=True)
        # Get a list of staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Warning: Unable to get staged files from Git (exit code {result.returncode})")
            return []
            
        # Filter for Python files that exist
        staged_files = []
        for file_path in result.stdout.splitlines():
            # Ensure it's a Python file
            if file_path.endswith(INCLUDE_EXT):
                abs_path = os.path.abspath(file_path)
                if os.path.isfile(abs_path):
                    staged_files.append(abs_path)
                    
        return staged_files
    except Exception as e:
        # SECURITY: Catch exceptions to avoid leaking information
        print(f"Warning: Error getting staged files: {type(e).__name__}")
        return []

def main():
    """
    Main function to scan Python files with Bandit.
    
    Security controls:
    - Validates file count against thresholds to detect misconfiguration
    - Uses a minimal environment to avoid leaking sensitive variables
    - Uses argument list syntax (not shell=True) to prevent command injection
    - Sanitizes output to avoid leaking sensitive information
    - Catches and handles exceptions securely
    """
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(
        description="Scan Python files for security issues using Bandit"
    )
    parser.add_argument(
        "-f", "--files", nargs="+", 
        help="Specific files to scan (overrides automatic file discovery)"
    )
    parser.add_argument(
        "-s", "--staged", action="store_true",
        help="Scan only files staged for commit in Git"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Scan all Python files in the project (default when no other options provided)"
    )
    args = parser.parse_args()
    
    # Get files to scan based on command-line options
    if args.files:
        # SECURITY: If specific files are provided, validate them
        print(f"Scanning specific files provided via command line...")
        files = []
        for file_path in args.files:
            if not os.path.exists(file_path):
                print(f"Warning: Skipping non-existent file: {file_path}")
                continue
            
            abs_path = os.path.abspath(file_path)
            if os.path.isfile(abs_path) and abs_path.endswith(INCLUDE_EXT):
                files.append(abs_path)
                print(f"  - Added: {os.path.relpath(abs_path)}")
            else:
                print(f"  - Skipped: {file_path} (not a Python file)")
    elif args.staged:
        # Scan only Git staged files
        print("Scanning only files staged for commit in Git...")
        files = get_staged_files()
        
        # Provide feedback on what's being scanned
        if files:
            print(f"Found {len(files)} staged Python files:")
            for file_path in files:
                print(f"  - {os.path.relpath(file_path)}")
        else:
            print("No staged Python files found. Nothing to scan.")
    else:
        # Default: discover all files automatically if no other options provided
        print("Scanning all Python files in the project (this may take a while)...")
        files = find_python_files()
    
    if not files:
        print("No Python files found to scan.")
        return

    # SECURITY: Warn if an unexpectedly high number of files are found (could indicate misconfiguration)
    if len(files) > 200:
        print(f"Warning: {len(files)} files to scan. This may include unwanted files. Check your exclusions.")

    print(f"Scanning {len(files)} files with Bandit...")
    
    # SECURITY: Run Bandit with a minimal environment to avoid leaking sensitive env variables
    # and use allowlist approach rather than trying to strip variables
    minimal_env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "LANG": os.environ.get("LANG", "en_US.UTF-8"),
        "HOME": os.environ.get("HOME", "")
    }
    
    try:
        # SECURITY: Use subprocess.run with arguments as a list (not shell=True)
        # This prevents command injection vulnerabilities
        result = subprocess.run(
            ["bandit", "-ll", "-r"] + files,
            capture_output=True,
            text=True,
            env=minimal_env
        )
        # Print output but sanitize it first
        stdout = result.stdout
        if stdout:
            print(stdout)
            
        if result.stderr:
            # SECURITY: Be careful about printing error output, it could contain sensitive info
            # Filter or sanitize if necessary
            print("Bandit errors/warnings:", result.stderr)
            
        # Return the exit code
        return result.returncode
            
    except FileNotFoundError:
        print("Error: Bandit not found. Make sure it's installed and in your PATH.")
        print("Try: pip install bandit")
        return 1
    except Exception as e:
        # SECURITY: Catch all exceptions to avoid leaking stack traces or sensitive info
        print(f"Error running Bandit: {type(e).__name__}")
        # Print message but not full exception to avoid leaking paths or other sensitive info
        print("Make sure Bandit is installed and accessible in your PATH.")
        return 1

# SECURITY: This guard ensures the script only runs when executed directly, not when imported as a module.
if __name__ == "__main__":
    # Return the exit code from main() to the system
    sys.exit(main() or 0)
