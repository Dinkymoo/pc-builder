#!/usr/bin/env python3
"""
Helper script to test pre-commit hooks on workflow files.
"""
import subprocess
import glob
import os

def main():
    """Run pre-commit on workflow files."""
    # Get all Python files in the workflow directory
    workflow_py_files = glob.glob("workflow/*.py")
    
    if not workflow_py_files:
        print("No Python files found in workflow directory.")
        return
    
    # Run pre-commit on all files
    print(f"Running pre-commit on {len(workflow_py_files)} files...")
    cmd = ["pre-commit", "run", "bandit", "--files"] + workflow_py_files
    
    # SECURITY: Use subprocess.run with arguments as a list (not shell=True)
    # and with minimal environment to avoid leaking sensitive information
    minimal_env = {"PATH": os.environ.get("PATH", "")}
    try:
        subprocess.run(cmd, check=True, env=minimal_env, text=True)
        print("✅ All checks passed!")
    except subprocess.CalledProcessError:
        print("❌ Some checks failed. See output above.")

if __name__ == "__main__":
    main()
