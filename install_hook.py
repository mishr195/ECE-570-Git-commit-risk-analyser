import os
import stat
import sys

def install_hook():
    print("--- Git Risk Analyzer Installer ---")
    
    # Check if inside a git repository
    if not os.path.isdir(".git"):
        print("[Error] Not a git repository. Please run 'git init' first.")
        sys.exit(1)
        
    hooks_dir = os.path.join(".git", "hooks")
    hook_file = os.path.join(hooks_dir, "pre-commit")
    
    # Create hooks directory if it doesn't exist
    if not os.path.exists(hooks_dir):
        os.makedirs(hooks_dir)
        
    hook_content = """#!/bin/bash
# Pre-commit hook to run the Risk Analyzer
$(dirname "$0")/../../.venv/bin/python "$(dirname "$0")/../../analyze_commit.py"
exit $?
"""
    
    print("Writing pre-commit hook...")
    with open(hook_file, 'w') as f:
        f.write(hook_content)
        
    print("Making hook executable...")
    st = os.stat(hook_file)
    os.chmod(hook_file, st.st_mode | stat.S_IEXEC)
    
    print("\nSuccess! The Git Commit Risk Analyzer has been installed.")
    print("It will automatically scan your code every time you run 'git commit'.")
    print("To uninstall, simply delete '.git/hooks/pre-commit'.")

if __name__ == "__main__":
    install_hook()
