# Developer Setup Guide

This guide provides instructions for setting up multiple Git profiles and customizing your terminal experience for a more efficient development workflow.

## Setting Up Multiple Git Profiles

If you need to maintain separate Git identities for personal and work projects, follow these steps:

### 1. Create SSH Keys for Each Profile

```sh
# For your work profile
ssh-keygen -t ed25519 -C "your-work-email@example.com" -f ~/.ssh/id_work

# For your personal profile
ssh-keygen -t ed25519 -C "your-personal-email@example.com" -f ~/.ssh/id_personal
```

### 2. Add Keys to SSH Agent

```sh
# Start SSH agent
eval "$(ssh-agent -s)"

# Add keys to agent
ssh-add ~/.ssh/id_work
ssh-add ~/.ssh/id_personal
```

For persistence, add these commands to your `~/.zshrc` or `~/.bash_profile`.

### 3. Configure SSH Config File

Create or edit `~/.ssh/config`:

```
# Work profile
Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_work
  IdentitiesOnly yes

# Personal profile
Host github-personal
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_personal
  IdentitiesOnly yes
```

### 4. Add Your SSH Keys to GitHub

1. Copy your public keys:
   ```sh
   cat ~/.ssh/id_work.pub
   cat ~/.ssh/id_personal.pub
   ```

2. Add each key to the corresponding GitHub account:
   - Go to GitHub → Settings → SSH and GPG keys → New SSH key

### 5. Configure Git to Use Different Profiles per Repository

```sh
# In your personal repo
git config user.name "Your Personal Name"
git config user.email "your-personal-email@example.com"

# In your work repo
git config user.name "Your Work Name"
git config user.email "your-work-email@example.com"
```

For global defaults:
```sh
git config --global user.name "Default Name"
git config --global user.email "default-email@example.com"
```

### 6. Clone Repositories Using the Right Profile

```sh
# Work repository
git clone git@github-work:organization/repo.git

# Personal repository
git clone git@github-personal:username/repo.git
```

### 7. Change Remote URLs for Existing Repositories

```sh
# Check current remote
git remote -v

# Update to use SSH with the proper host
git remote set-url origin git@github-work:organization/repo.git
# OR
git remote set-url origin git@github-personal:username/repo.git
```

## Shortening Your Terminal Prompt

If your terminal prompt is too long (e.g., `.venvdaniellevangraan@macbookpro`), you can customize it:

### Method 1: Customize ZSH Prompt

Edit your `~/.zshrc` file:

```sh
# Add this to your ~/.zshrc
# Disable default virtual environment prompt
export VIRTUAL_ENV_DISABLE_PROMPT=1

# Create a function to show a minimal venv indicator
function virtualenv_info {
  if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "($(basename $VIRTUAL_ENV)) "
  fi
}

# Set a minimal prompt with current directory and virtualenv indicator
PROMPT='$(virtualenv_info)%1~ $ '
```

Apply the changes:
```sh
source ~/.zshrc
```

### Method 2: Use a ZSH Theme

If you use Oh My Zsh:

1. Edit `~/.zshrc`
2. Set a minimal theme: `ZSH_THEME="robbyrussell"` or `ZSH_THEME="avit"`

### Method 3: Rename the Virtual Environment

```sh
# Deactivate your current environment
deactivate

# Rename the .venv folder to something shorter
mv .venv venv

# Reactivate with the new name
source venv/bin/activate
```

### Method 4: Better Virtual Environment Tools

Consider using:
- [direnv](https://direnv.net/) - Automatically activates environments
- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/) - Better venv management

### Method 5: Project-Local .zshrc

For quick setup without modifying your global profile, this project includes a local `.zshrc-pc-builder` file:

```sh
# From the project directory
source .zshrc-pc-builder
```

Benefits of this approach:
- Works instantly without creating any files outside the project
- Automatically sets project-specific environment variables
- Provides useful aliases for common project tasks
- Shows helpful information about available commands
- References GitHub Copilot instructions
- Auto-activates virtual environment if available

To use this method:
1. Navigate to the project root
2. Run `source .zshrc-pc-builder`
3. Enjoy your project-specific environment

This is ideal for quickly switching between different projects without permanently changing your global settings.

## Setting Up Pre-Commit Hooks

This project uses pre-commit hooks to automatically check code for security issues, secrets, and other potential problems before commits are made.

### 1. Installation

```sh
# Install pre-commit
pip install pre-commit

# Install the hooks defined in .pre-commit-config.yaml
pre-commit install
```

### 2. Updating Hooks

When the hooks in `.pre-commit-config.yaml` need to be updated, use the autoupdate command:

```sh
# Update hooks to their latest versions
pre-commit autoupdate
```

This ensures hooks use immutable references (like specific version tags) rather than mutable branch references (like `main`), providing better stability and consistency across the team.

#### Understanding Hook Updates

The `autoupdate` command:
- Finds the latest stable version tags for each hook repository
- Updates the `rev:` field in `.pre-commit-config.yaml` to use these immutable references 
- Replaces branch references (like `main` or `master`) with specific version tags

For example, it might change:
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: main  # mutable branch reference
  hooks:
    - id: bandit
```

To:
```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.7.5  # immutable version tag
  hooks:
    - id: bandit
```

This ensures that:
1. All developers use the exact same version of each hook
2. Updates are intentional, not automatic when a branch changes
3. Breaking changes in hooks don't unexpectedly affect your workflow

#### When to Run Autoupdate

Run `pre-commit autoupdate`:
- When setting up a new project
- Periodically (e.g., monthly) to get security updates
- When you encounter hook-related issues
- Before major releases to ensure you have the latest security checks

After running autoupdate, it's good practice to:
1. Test the updated hooks: `pre-commit run --all-files`
2. Commit the updated `.pre-commit-config.yaml` file
3. Notify team members to run `pre-commit install` to get the updates

### 3. Running Hooks Manually

You can run the hooks manually on all files:

```sh
# Run on all files
pre-commit run --all-files

# Run a specific hook
pre-commit run detect-secrets --all-files
```

### 4. Current Hooks

- **Bandit**: Scans Python code for security issues
- **detect-secrets**: Checks for accidentally committed secrets/credentials

## Setting Up a Custom Profile with Its Own .zshrc

If you want to maintain separate shell configurations for different projects or roles, you can set up a custom profile with its own `.zshrc` file:

### 1. Create a Custom .zshrc File

```sh
# Create a directory for your custom profile
mkdir -p ~/.zsh_profiles/pc-builder

# Create a custom .zshrc for this profile
touch ~/.zsh_profiles/pc-builder/zshrc
```

### 2. Configure Your Custom .zshrc

Add your project-specific configurations to `~/.zsh_profiles/pc-builder/zshrc`:

```sh
# Source the main .zshrc for common settings
if [ -f "$HOME/.zshrc" ]; then
  source "$HOME/.zshrc"
fi

# Custom prompt for this profile
PROMPT="%F{green}pc-builder%f %1~ $ "

# Project-specific environment variables
export S3_BUCKET="pc-builder-bucket-dvg-2025"
export MY_AWS_REGION="eu-west-3"

# Project-specific aliases
alias pcb=DataScrapingBeautifulSoup
alias pcb-backend="cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/pc-builder-backend"
alias pcb-frontend="cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/pc-builder-app"
alias pcb-run-all="cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup && ./start-all.sh"

# Auto-activate virtual environment
if [ -d "$HOME/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/.venv" ]; then
  source "$HOME/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/.venv/bin/activate"
  echo "PC Builder virtual environment activated"
fi
```

### 3. Create a Launcher Script

Create a script to easily switch to this profile:

```sh
cat > ~/bin/pc-builder-profile <<'EOL'
#!/bin/zsh
export ZDOTDIR=~/.zsh_profiles/pc-builder
exec zsh
EOL

chmod +x ~/bin/pc-builder-profile
```

Ensure `~/bin` is in your PATH. If not, add `export PATH="$HOME/bin:$PATH"` to your main `~/.zshrc`.

### 4. Using Your Custom Profile

Now you can switch to your custom profile by running:

```sh
pc-builder-profile
```

This will:
- Start a new zsh instance with your custom configuration
- Set up your project-specific aliases and environment variables
- Apply your custom prompt
- Automatically navigate to and activate your project's environment

### 5. Switching Between Profiles

You can use multiple custom profiles and switch between them:
- Type `exit` to go back to your default shell
- Run a different profile script to switch to another profile

This approach keeps your project configurations separate and allows you to maintain different environments for different projects or clients

## Project-Specific Setup

For this project, we recommend:

1. Using a dedicated virtual environment
2. Setting up the Git profile appropriate for this codebase
3. Customizing your terminal prompt for better readability

## Managing Generated Data and S3 Storage

This project uses AWS S3 to store generated data files and scraped images, keeping them out of Git. This approach provides several benefits:

- **Keeps Repository Clean**: Large generated files don't bloat the Git repository
- **Consistent Environments**: All deployments use the same data from S3
- **Reduced Merge Conflicts**: Generated files won't cause Git conflicts
- **Flexible Updates**: Data can be updated independently of code

### Data Workflow Overview

![S3 Data Workflow](https://i.imgur.com/xVjpWQO.png)

1. **Generate**: Run the scraper to create CSV files and download images
2. **Upload**: Send the generated files to S3 storage
3. **Clean**: Remove local copies to avoid committing to Git
4. **Access**: Backend automatically retrieves files from S3 when needed

### Step 1: Running the Scraper

Generate the data files by running the scraper:

```sh
# Navigate to the scraper directory
cd pc-builder/pc-builder-scraper

# Run the scraper
python scraper.py
```

This will create CSV files in the `data-results/` directory and download images to `cdn-images/`.

### Step 2: Uploading Generated Data to S3

After running the scraper, use the upload script to send CSV files and images to S3:

```sh
# Upload all data and images
./upload_to_s3.py

# Upload only CSV files
./upload_to_s3.py --data

# Upload only images
./upload_to_s3.py --images

# Upload a specific file
./upload_to_s3.py --file data-results/graphics-cards.csv
```

The script will:
- Check AWS credentials are valid
- Upload files to the configured S3 bucket
- Skip files that already exist in S3 (unless --force is used)
- Set proper content types for different file formats
- Make images publicly accessible (if configured)

### Step 3: Cleaning Up Generated Files

To remove generated files locally after uploading to S3:

```sh
# Preview what would be deleted (safe dry-run mode)
./delete_generated_files.py --dry-run

# Delete all generated files
./delete_generated_files.py

# Delete only CSV data files
./delete_generated_files.py --data

# Delete only images
./delete_generated_files.py --images
```

This helps ensure we don't accidentally commit generated files to Git.

## Automated Workflow with pc-builder-workflow.py

For convenience, we've created an all-in-one workflow script that automates the entire data pipeline:

```sh
# Run the complete workflow (scrape → upload → cleanup)
python pc-builder-workflow.py

# Run with dry-run to see what would happen without making changes
python pc-builder-workflow.py --dry-run

# Run only specific steps
python pc-builder-workflow.py --scrape-only
python pc-builder-workflow.py --upload-only
python pc-builder-workflow.py --cleanup-only

# Skip specific steps
python pc-builder-workflow.py --skip-cleanup
python pc-builder-workflow.py --skip-upload

# Include tests after workflow completion
python pc-builder-workflow.py --test-backend --test-frontend
```

The workflow script handles:

1. Setting up the Python virtual environment automatically
2. Running the scraper to generate CSV data and download images
3. Uploading all generated files to S3
4. Cleaning up local files (optional)
5. Running backend/frontend tests (optional)

This is the recommended approach for maintaining the data pipeline, especially for new developers or automated environments.

## AWS S3 Setup

For this project, you'll need AWS S3 access to store and retrieve images and data. Follow these steps to create an S3-only user with limited permissions.

### Creating an AWS S3-Only User

#### Step 1: Go to AWS IAM Console
- Visit: https://console.aws.amazon.com/iam/

#### Step 2: Create New User
1. Click 'Users' in left sidebar
2. Click 'Create user'
3. User name: 'pc-builder-s3-user'
4. Check ✅ 'Programmatic access'
5. Click 'Next: Permissions'

#### Step 3: Add S3 Permissions ONLY
1. Select 'Attach existing policies directly'
2. Search: 'AmazonS3FullAccess'
3. Check ✅ 'AmazonS3FullAccess' (and ONLY this)
4. Click 'Next: Tags' → 'Next: Review' → 'Create user'

#### Step 4: Copy Credentials
🚨 **CRITICAL**: This is the ONLY time you'll see the secret key!
- Copy 'Access key ID' (starts with AKIA...)
- Click 'Show' and copy 'Secret access key'

#### Step 5: Test Before Updating
Run the test script with your new credentials:
```sh
python test-new-credentials.py ACCESS_KEY SECRET_KEY
```

#### Step 6: Update .env File
If the test passes, update these lines in your `.env` file:
```
AWS_ACCESS_KEY_ID=your_new_access_key
AWS_SECRET_ACCESS_KEY=your_new_secret_key
```

#### Expected Result
- User can only access S3 (no CloudFormation, no other services)
- Perfect for our PC Builder project
- No permission errors

## Using GitHub Copilot with Project-Specific Instructions

This project includes a `COPILOT_INSTRUCTIONS.md` file that contains guidelines for GitHub Copilot to follow when assisting with development tasks. The file includes:

- Project structure overview
- Coding standards for Python and TypeScript
- Security best practices
- Guidelines for common development tasks
- Testing and deployment instructions

### Benefits of Copilot Instructions

- Ensures consistent code quality across the team
- Helps new developers understand project standards
- Makes Copilot's suggestions more relevant to the project
- Reduces the need for extensive code reviews

### Using the Instructions

Simply having the `COPILOT_INSTRUCTIONS.md` file in your repository helps GitHub Copilot understand the project context. Additionally:

1. Reference specific sections when working with Copilot:
   ```
   // @copilot: Please follow the Python coding standards from COPILOT_INSTRUCTIONS.md
   ```

2. For complex features, describe what you need with reference to the instructions:
   ```
   // @copilot: Create a new API endpoint following the pattern in COPILOT_INSTRUCTIONS.md
   ```

3. Keep the instructions updated as project standards evolve

---

*Note: Adjust all example commands and configurations according to your specific needs.*
