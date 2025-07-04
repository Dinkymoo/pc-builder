#!/usr/bin/env python3
"""
Developer Setup Guide - Interactive Script
"""

import os
import sys
import webbrowser

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")

def print_step(number, title):
    """Print a step header"""
    print(f"\n## Step {number}: {title}")

def print_section_header(title):
    """Print a section header"""
    print(f"\n\n{'#' * 3} {title}\n")

def print_aws_s3_setup():
    """Print AWS S3 setup instructions in a markdown-like format"""
    print_header("AWS S3 Setup Guide")
    
    print("\nThis guide will help you set up an AWS S3-only user with limited permissions")
    print("for the PC Builder project. Follow these steps carefully.\n")
    
    print_step(1, "Go to AWS IAM Console")
    print("Visit: https://console.aws.amazon.com/iam/")
    
    print_step(2, "Create New User")
    print("1. Click 'Users' in left sidebar")
    print("2. Click 'Create user'")
    print("3. User name: 'pc-builder-s3-user'")
    print("4. Check ✅ 'Programmatic access'")
    print("5. Click 'Next: Permissions'")
    
    print_step(3, "Add S3 Permissions ONLY")
    print("1. Select 'Attach existing policies directly'")
    print("2. Search: 'AmazonS3FullAccess'")
    print("3. Check ✅ 'AmazonS3FullAccess' (and ONLY this)")
    print("4. Click 'Next: Tags' → 'Next: Review' → 'Create user'")
    
    print_step(4, "Copy Credentials")
    print("🚨 CRITICAL: This is the ONLY time you'll see the secret key!")
    print("- Copy 'Access key ID' (starts with AKIA...)")
    print("- Click 'Show' and copy 'Secret access key'")
    
    print_step(5, "Test Before Updating")
    print("Run the test script with your new credentials:")
    print("```")
    print("python test-new-credentials.py ACCESS_KEY SECRET_KEY")
    print("```")
    
    print_step(6, "Update .env File")
    print("If the test passes, update these lines in your .env file:")
    print("```")
    print("AWS_ACCESS_KEY_ID=your_new_access_key")
    print("AWS_SECRET_ACCESS_KEY=your_new_secret_key")
    print("```")
    
    print("\n## Expected Result")
    print("- User can only access S3 (no CloudFormation, no other services)")
    print("- Perfect for our PC Builder project")
    print("- No permission errors")

def print_git_setup():
    """Print Git setup instructions in a markdown-like format"""
    print_header("Git Setup Guide")
    
    print("\nThis guide will help you set up Git with multiple profiles for different")
    print("projects. This is useful if you're working with both personal and work accounts.\n")
    
    print_section_header("1. Create SSH Keys for Each Profile")
    print("```sh")
    print("# For your work profile")
    print("ssh-keygen -t ed25519 -C \"your-work-email@example.com\" -f ~/.ssh/id_work")
    print("")
    print("# For your personal profile")
    print("ssh-keygen -t ed25519 -C \"your-personal-email@example.com\" -f ~/.ssh/id_personal")
    print("```")
    
    print_section_header("2. Add Keys to SSH Agent")
    print("```sh")
    print("# Start SSH agent")
    print("eval \"$(ssh-agent -s)\"")
    print("")
    print("# Add keys to agent")
    print("ssh-add ~/.ssh/id_work")
    print("ssh-add ~/.ssh/id_personal")
    print("```")
    
    print("\nFor persistence, add these commands to your `~/.zshrc` or `~/.bash_profile`.")
    
    print_section_header("3. Configure SSH Config File")
    print("Create or edit `~/.ssh/config`:")
    print("")
    print("```")
    print("# Work profile")
    print("Host github-work")
    print("  HostName github.com")
    print("  User git")
    print("  IdentityFile ~/.ssh/id_work")
    print("  IdentitiesOnly yes")
    print("")
    print("# Personal profile")
    print("Host github-personal")
    print("  HostName github.com")
    print("  User git")
    print("  IdentityFile ~/.ssh/id_personal")
    print("  IdentitiesOnly yes")
    print("```")
    
    print_section_header("4. Add Your SSH Keys to GitHub")
    print("1. Copy your public keys:")
    print("   ```sh")
    print("   cat ~/.ssh/id_work.pub")
    print("   cat ~/.ssh/id_personal.pub")
    print("   ```")
    print("")
    print("2. Add each key to the corresponding GitHub account:")
    print("   - Go to GitHub → Settings → SSH and GPG keys → New SSH key")
    
    print_section_header("5. Configure Git to Use Different Profiles per Repository")
    print("```sh")
    print("# In your personal repo")
    print("git config user.name \"Your Personal Name\"")
    print("git config user.email \"your-personal-email@example.com\"")
    print("")
    print("# In your work repo")
    print("git config user.name \"Your Work Name\"")
    print("git config user.email \"your-work-email@example.com\"")
    print("```")
    
    print("\nFor global defaults:")
    print("```sh")
    print("git config --global user.name \"Default Name\"")
    print("git config --global user.email \"default-email@example.com\"")
    print("```")
    
    print_section_header("6. Clone Repositories Using the Right Profile")
    print("```sh")
    print("# Work repository")
    print("git clone git@github-work:organization/repo.git")
    print("")
    print("# Personal repository")
    print("git clone git@github-personal:username/repo.git")
    print("```")
    
    print_section_header("7. Change Remote URLs for Existing Repositories")
    print("```sh")
    print("# Check current remote")
    print("git remote -v")
    print("")
    print("# Update to use SSH with the proper host")
    print("git remote set-url origin git@github-work:organization/repo.git")
    print("# OR")
    print("git remote set-url origin git@github-personal:username/repo.git")
    print("```")

def print_terminal_customization():
    """Print terminal customization instructions in a markdown-like format"""
    print_header("Customizing Your Terminal")
    
    print("\nIf your terminal prompt is too long (e.g., `.venvdaniellevangraan@macbookpro`),")
    print("here are several methods to customize it:\n")
    
    print_section_header("Method 1: Customize ZSH Prompt")
    print("Edit your `~/.zshrc` file:")
    print("")
    print("```sh")
    print("# Add this to your ~/.zshrc")
    print("# Disable default virtual environment prompt")
    print("export VIRTUAL_ENV_DISABLE_PROMPT=1")
    print("")
    print("# Create a function to show a minimal venv indicator")
    print("function virtualenv_info {")
    print("  if [[ -n \"$VIRTUAL_ENV\" ]]; then")
    print("    echo \"($(basename $VIRTUAL_ENV)) \"")
    print("  fi")
    print("}")
    print("")
    print("# Set a minimal prompt with current directory and virtualenv indicator")
    print("PROMPT='$(virtualenv_info)%1~ $ '")
    print("```")
    print("")
    print("Apply the changes:")
    print("```sh")
    print("source ~/.zshrc")
    print("```")
    
    print_section_header("Method 2: Use a ZSH Theme")
    print("If you use Oh My Zsh:")
    print("")
    print("1. Edit `~/.zshrc`")
    print("2. Set a minimal theme: `ZSH_THEME=\"robbyrussell\"` or `ZSH_THEME=\"avit\"`")
    
    print_section_header("Method 3: Rename the Virtual Environment")
    print("```sh")
    print("# Deactivate your current environment")
    print("deactivate")
    print("")
    print("# Rename the .venv folder to something shorter")
    print("mv .venv venv")
    print("")
    print("# Reactivate with the new name")
    print("source venv/bin/activate")
    print("```")
    
    print_section_header("Method 4: Better Virtual Environment Tools")
    print("Consider using:")
    print("- [direnv](https://direnv.net/) - Automatically activates environments")
    print("- [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/) - Better venv management")
    
    print_section_header("Method 5: Project-Local .zshrc")
    print("For quick setup without modifying your global profile, this project includes a local `.zshrc-pc-builder` file:")
    print("")
    print("```sh")
    print("# From the project directory")
    print("source .zshrc-pc-builder")
    print("```")
    print("")
    print("Benefits of this approach:")
    print("- Works instantly without creating any files outside the project")
    print("- Automatically sets project-specific environment variables")
    print("- Provides useful aliases for common project tasks")
    print("- Shows helpful information about available commands")
    print("- References GitHub Copilot instructions")
    print("- Auto-activates virtual environment if available")
    print("")
    print("To use this method:")
    print("1. Navigate to the project root")
    print("2. Run `source .zshrc-pc-builder`")
    print("3. Enjoy your project-specific environment")
    print("")
    print("This is ideal for quickly switching between different projects without permanently changing your global settings.")

def print_precommit_setup():
    """Print pre-commit hooks setup instructions"""
    print_header("Setting Up Pre-Commit Hooks")
    
    print("\nThis project uses pre-commit hooks to automatically check code for security issues,")
    print("secrets, and other potential problems before commits are made.\n")
    
    print_section_header("1. Installation")
    print("```sh")
    print("# Install pre-commit")
    print("pip install pre-commit")
    print("")
    print("# Install the hooks defined in .pre-commit-config.yaml")
    print("pre-commit install")
    print("```")
    
    print_section_header("2. Updating Hooks")
    print("When the hooks in `.pre-commit-config.yaml` need to be updated, use the autoupdate command:")
    print("")
    print("```sh")
    print("# Update hooks to their latest versions")
    print("pre-commit autoupdate")
    print("```")
    print("")
    print("This ensures hooks use immutable references (like specific version tags) rather than mutable")
    print("branch references (like `main`), providing better stability and consistency across the team.")
    
    print_section_header("Understanding Hook Updates")
    print("The `autoupdate` command:")
    print("- Finds the latest stable version tags for each hook repository")
    print("- Updates the `rev:` field in `.pre-commit-config.yaml` to use these immutable references")
    print("- Replaces branch references (like `main` or `master`) with specific version tags")
    print("")
    print("For example, it might change:")
    print("```yaml")
    print("- repo: https://github.com/PyCQA/bandit")
    print("  rev: main  # mutable branch reference")
    print("  hooks:")
    print("    - id: bandit")
    print("```")
    print("")
    print("To:")
    print("```yaml")
    print("- repo: https://github.com/PyCQA/bandit")
    print("  rev: 1.7.5  # immutable version tag")
    print("  hooks:")
    print("    - id: bandit")
    print("```")
    print("")
    print("This ensures that:")
    print("1. All developers use the exact same version of each hook")
    print("2. Updates are intentional, not automatic when a branch changes")
    print("3. Breaking changes in hooks don't unexpectedly affect your workflow")
    
    print_section_header("When to Run Autoupdate")
    print("Run `pre-commit autoupdate`:")
    print("- When setting up a new project")
    print("- Periodically (e.g., monthly) to get security updates")
    print("- When you encounter hook-related issues")
    print("- Before major releases to ensure you have the latest security checks")
    print("")
    print("After running autoupdate, it's good practice to:")
    print("1. Test the updated hooks: `pre-commit run --all-files`")
    print("2. Commit the updated `.pre-commit-config.yaml` file")
    print("3. Notify team members to run `pre-commit install` to get the updates")
    
    print_section_header("3. Running Hooks Manually")
    print("You can run the hooks manually on all files:")
    print("")
    print("```sh")
    print("# Run on all files")
    print("pre-commit run --all-files")
    print("")
    print("# Run a specific hook")
    print("pre-commit run detect-secrets --all-files")
    print("```")
    
    print_section_header("4. Current Hooks")
    print("- **Bandit**: Scans Python code for security issues")
    print("- **detect-secrets**: Checks for accidentally committed secrets/credentials")

def print_custom_profile_setup():
    """Print custom profile setup instructions"""
    print_header("Setting Up a Custom Profile with Its Own .zshrc")
    
    print("\nIf you want to maintain separate shell configurations for different projects or roles,")
    print("you can set up a custom profile with its own `.zshrc` file:\n")
    
    print_section_header("1. Create a Custom .zshrc File")
    print("```sh")
    print("# Create a directory for your custom profile")
    print("mkdir -p ~/.zsh_profiles/pc-builder")
    print("")
    print("# Create a custom .zshrc for this profile")
    print("touch ~/.zsh_profiles/pc-builder/zshrc")
    print("```")
    
    print_section_header("2. Configure Your Custom .zshrc")
    print("Add your project-specific configurations to `~/.zsh_profiles/pc-builder/zshrc`:")
    print("")
    print("```sh")
    print("# Source the main .zshrc for common settings")
    print("if [ -f \"$HOME/.zshrc\" ]; then")
    print("  source \"$HOME/.zshrc\"")
    print("fi")
    print("")
    print("# Custom prompt for this profile")
    print("PROMPT=\"%F{green}pc-builder%f %1~ $ \"")
    print("")
    print("# Project-specific environment variables")
    print("export S3_BUCKET=\"pc-builder-bucket-dvg-2025\"")
    print("export MY_AWS_REGION=\"eu-west-3\"")
    print("")
    print("# Project-specific aliases")
    print("alias pcb=\"cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup\"")
    print("alias pcb-backend=\"cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/pc-builder-backend\"")
    print("alias pcb-frontend=\"cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/pc-builder-app\"")
    print("alias pcb-run-all=\"cd ~/Documents/sandbox/python-projects/DataScrapingBeautifulSoup && ./start-all.sh\"")
    print("")
    print("# Auto-activate virtual environment")
    print("if [ -d \"$HOME/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/.venv\" ]; then")
    print("  source \"$HOME/Documents/sandbox/python-projects/DataScrapingBeautifulSoup/pc-builder/.venv/bin/activate\"")
    print("  echo \"PC Builder virtual environment activated\"")
    print("fi")
    print("```")
    
    print_section_header("3. Create a Launcher Script")
    print("Create a script to easily switch to this profile:")
    print("")
    print("```sh")
    print("cat > ~/bin/pc-builder-profile <<'EOL'")
    print("#!/bin/zsh")
    print("export ZDOTDIR=~/.zsh_profiles/pc-builder")
    print("exec zsh")
    print("EOL")
    print("")
    print("chmod +x ~/bin/pc-builder-profile")
    print("```")
    print("")
    print("Ensure `~/bin` is in your PATH. If not, add `export PATH=\"$HOME/bin:$PATH\"` to your main `~/.zshrc`.")
    
    print_section_header("4. Using Your Custom Profile")
    print("Now you can switch to your custom profile by running:")
    print("")
    print("```sh")
    print("pc-builder-profile")
    print("```")
    print("")
    print("This will:")
    print("- Start a new zsh instance with your custom configuration")
    print("- Set up your project-specific aliases and environment variables")
    print("- Apply your custom prompt")
    print("- Automatically navigate to and activate your project's environment")
    
    print_section_header("5. Switching Between Profiles")
    print("You can use multiple custom profiles and switch between them:")
    print("- Type `exit` to go back to your default shell")
    print("- Run a different profile script to switch to another profile")
    print("")
    print("This approach keeps your project configurations separate and allows you to maintain")
    print("different environments for different projects or clients")

def print_github_copilot():
    """Print GitHub Copilot instructions"""
    print_header("Using GitHub Copilot with Project-Specific Instructions")
    
    print("\nThis project includes a `COPILOT_INSTRUCTIONS.md` file that contains guidelines")
    print("for GitHub Copilot to follow when assisting with development tasks. The file includes:\n")
    
    print("- Project structure overview")
    print("- Coding standards for Python and TypeScript")
    print("- Security best practices")
    print("- Guidelines for common development tasks")
    print("- Testing and deployment instructions")
    
    print_section_header("Benefits of Copilot Instructions")
    print("- Ensures consistent code quality across the team")
    print("- Helps new developers understand project standards")
    print("- Makes Copilot's suggestions more relevant to the project")
    print("- Reduces the need for extensive code reviews")
    
    print_section_header("Using the Instructions")
    print("Simply having the `COPILOT_INSTRUCTIONS.md` file in your repository helps GitHub Copilot")
    print("understand the project context. Additionally:")
    print("")
    print("1. Reference specific sections when working with Copilot:")
    print("   ```")
    print("   // @copilot: Please follow the Python coding standards from COPILOT_INSTRUCTIONS.md")
    print("   ```")
    print("")
    print("2. For complex features, describe what you need with reference to the instructions:")
    print("   ```")
    print("   // @copilot: Create a new API endpoint following the pattern in COPILOT_INSTRUCTIONS.md")
    print("   ```")
    print("")
    print("3. Keep the instructions updated as project standards evolve")

def print_project_specific():
    """Print project specific setup recommendations"""
    print_header("Project-Specific Setup")
    
    print("\nFor this project, we recommend:\n")
    print("1. Using a dedicated virtual environment")
    print("2. Setting up the Git profile appropriate for this codebase")
    print("3. Customizing your terminal prompt for better readability")
    print("\n*Note: Adjust all example commands and configurations according to your specific needs.*")
    
def print_menu():
    """Print the main menu"""
    print_header("PC Builder Developer Setup Guide")
    
    print("\nPlease select an option:")
    print("1. AWS S3 User Setup")
    print("2. S3 Data Workflow")
    print("3. Git Profile Setup")
    print("4. Terminal Prompt Customization")
    print("5. Custom Profile Setup")
    print("6. Pre-Commit Hooks Setup")
    print("7. GitHub Copilot Instructions")
    print("8. Project-Specific Setup")
    print("9. View Full Documentation")
    print("0. Exit")
    
    try:
        choice = input("\nEnter your choice (0-9): ")
        return choice
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

def view_full_documentation():
    """Open the full documentation in browser or show path"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    doc_path = os.path.join(current_dir, "DEVELOPER_SETUP.md")
    
    if not os.path.exists(doc_path):
        print(f"\n❌ Error: Could not find {doc_path}")
        print("Please check the repository for the current documentation.")
        return
    
    try:
        webbrowser.open(f"file://{doc_path}")
        print(f"\n✅ Documentation opened in your browser.")
    except Exception as e:
        print(f"\n❌ Could not open documentation automatically: {e}")
    
    print(f"\n📄 Documentation path: {doc_path}")
    print("\nTo view the documentation in the terminal, run:")
    print(f"cat {doc_path}")

def print_all_guides():
    """Print all guides in sequence"""
    print_aws_s3_setup()
    input("\nPress Enter to continue to S3 Data Workflow...")
    print_s3_data_workflow()
    input("\nPress Enter to continue to Git Setup...")
    print_git_setup()
    input("\nPress Enter to continue to Terminal Customization...")
    print_terminal_customization()
    input("\nPress Enter to continue to Custom Profile Setup...")
    print_custom_profile_setup()
    input("\nPress Enter to continue to Pre-Commit Hooks Setup...")
    print_precommit_setup()
    input("\nPress Enter to continue to GitHub Copilot Instructions...")
    print_github_copilot()
    input("\nPress Enter to continue to Project-Specific Setup...")
    print_project_specific()
    input("\nPress Enter to continue to S3 Data Workflow...")
    print_s3_data_workflow()

def print_s3_data_workflow():
    """Print S3 data workflow instructions in a markdown-like format"""
    print_header("S3 Data Workflow")
    
    print("\nThis project uses AWS S3 to store generated data files and scraped images, keeping them")
    print("out of Git. This section explains how to manage these files effectively.\n")
    
    print_section_header("Automated Workflow (Recommended)")
    print("The easiest way to handle the data workflow is with the all-in-one script:")
    print("")
    print("```sh")
    print("# Run the complete workflow (scrape → upload → cleanup)")
    print("python pc-builder-workflow.py")
    print("")
    print("# Run with dry-run to see what would happen without making changes")
    print("python pc-builder-workflow.py --dry-run")
    print("")
    print("# Run only specific steps")
    print("python pc-builder-workflow.py --scrape-only")
    print("python pc-builder-workflow.py --upload-only")
    print("python pc-builder-workflow.py --cleanup-only")
    print("")
    print("# Skip specific steps")
    print("python pc-builder-workflow.py --skip-cleanup")
    print("```")
    print("")
    print("The script handles the entire pipeline automatically, including setting up")
    print("the Python virtual environment and running tests if requested.\n")
    
    print_section_header("1. Uploading Generated Data to S3")
    print("If you prefer manual control, you can use these individual scripts:")
    print("")
    print("```sh")
    print("# Upload all data and images")
    print("./upload_to_s3.py")
    print("")
    print("# Upload only CSV files")
    print("./upload_to_s3.py --data")
    print("")
    print("# Upload only images")
    print("./upload_to_s3.py --images")
    print("")
    print("# Upload a specific file")
    print("./upload_to_s3.py --file data-results/graphics-cards.csv")
    print("```")
    
    print_section_header("2. Cleaning Up Generated Files")
    print("To remove generated files locally after uploading to S3:")
    print("")
    print("```sh")
    print("# Preview what would be deleted")
    print("./delete_generated_files.py --dry-run")
    print("")
    print("# Delete all generated files")
    print("./delete_generated_files.py")
    print("")
    print("# Delete only CSV files")
    print("./delete_generated_files.py --data")
    print("")
    print("# Delete only images")
    print("./delete_generated_files.py --images")
    print("```")
    
    print_section_header("3. Manual Development Workflow")
    print("If not using the automated workflow script, follow these steps:")
    print("")
    print("1. Run the scraper to generate data:")
    print("   ```sh")
    print("   cd pc-builder/pc-builder-scraper")
    print("   python scraper.py")
    print("   ```")
    print("")
    print("2. Upload generated data to S3:")
    print("   ```sh")
    print("   ./upload_to_s3.py")
    print("   ```")
    print("")
    print("3. Clean up local files to avoid committing them to Git:")
    print("   ```sh")
    print("   ./delete_generated_files.py")
    print("   ```")
    print("")
    print("4. The backend will automatically fetch data from S3")
    print("")
    print("This approach ensures that:")
    print("- Generated data isn't stored in Git (reducing repository size)")
    print("- All environments use the same data from S3")
    print("- Local development remains possible")
    print("- Files can be easily regenerated when needed")
    
    print_section_header("4. gitignore Configuration")
    print("The following files are excluded from Git:")
    print("- `data-results/*.csv` - Generated data files")
    print("- `data-results/*.log` - Log files from the scraper")
    print("- `cdn-images/*` - Downloaded product images")

def main():
    """Main function to run the script"""
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            print_all_guides()
            return
            
        while True:
            choice = print_menu()
            
            if choice == '1':
                print_aws_s3_setup()
            elif choice == '2':
                print_s3_data_workflow()
            elif choice == '3':
                print_git_setup()
            elif choice == '4':
                print_terminal_customization()
            elif choice == '5':
                print_custom_profile_setup()
            elif choice == '6':
                print_precommit_setup()
            elif choice == '7':
                print_github_copilot()
            elif choice == '8':
                print_project_specific()
            elif choice == '9':
                view_full_documentation()
            elif choice == '0':
                print("\nExiting. Have a nice day!")
                sys.exit(0)
            elif choice.lower() == 'all':
                print_all_guides()
            else:
                print("\n❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to return to menu...")
    
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
