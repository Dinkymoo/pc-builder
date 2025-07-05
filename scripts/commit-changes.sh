#!/bin/bash

# Script to commit the reorganized project structure to Git

echo "Preparing to commit the reorganized project structure..."

# Add all changes to the staging area
git add .

# Commit the changes with a descriptive message
git commit -m "Project reorganization: Implemented clean directory structure

- Created organized directory structure (scripts/, tests/, config/)
- Moved scripts to appropriate directories by function
- Updated documentation with new file locations
- Added README files for each major directory
- Created .env.example template
- Removed duplicate files from root directory
- Cleaned up temporary reorganization files

This commit improves project maintainability and follows best practices
for project organization."

echo "Changes have been committed!"
echo "You can now push the changes to your remote repository with 'git push'"

# Self-remove this script after running
echo "Removing this script..."
rm -f "$0"
