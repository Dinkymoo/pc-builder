#!/bin/bash
# Script to install development dependencies for PC Builder project
# This includes tools like Bandit for security scanning that are needed by pre-commit hooks

echo "Installing development dependencies..."

# Install Bandit for security scanning
pip install bandit

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
fi

# Update pre-commit hooks configuration if needed
pre-commit migrate-config

echo "✅ Development dependencies installed successfully!"
echo "You can now run pre-commit hooks and security scans without errors."
