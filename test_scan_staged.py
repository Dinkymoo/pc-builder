#!/usr/bin/env python3
"""
Test script to verify that our scan_all_with_bandit.py script can correctly identify staged files.
"""
import os
import sys
from scan_all_with_bandit import get_staged_files

def main():
    """Test the get_staged_files function"""
    print("Testing the get_staged_files function...")
    staged_files = get_staged_files()
    
    if not staged_files:
        print("No staged Python files found. Try staging some files with 'git add' first.")
        return 1
    
    print(f"Found {len(staged_files)} staged Python files:")
    for file_path in staged_files:
        print(f"  - {os.path.relpath(file_path)}")
    
    print("\nWould scan these files with Bandit...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
