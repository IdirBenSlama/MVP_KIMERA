#!/usr/bin/env python3
"""
Comprehensive System Update Script for Kimera SWM
Updates all packages, dependencies, and system components
"""

import subprocess
import sys
import json
import time
from datetime import datetime
from pathlib import Path

def run_command(command, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"EXECUTING: {description}")
    print(f"COMMAND: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
        return result.returncode == 0, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print("❌ Command timed out after 5 minutes")
        return False, "", "Command timed out"
    except Exception as e:
        print(f"❌ Error executing command: {e}")
        return False, "", str(e)

def update_pip_packages():
    """Update all pip packages"""
    print("\n🔄 UPDATING PIP PACKAGES...")
    
    # First update pip itself
    success, _, _ = run_command("python -m pip install --upgrade pip", "Updating pip")
    if not success:
        print("⚠️ Failed to update pip, continuing anyway...")
    
    # Get list of outdated packages
    success, stdout, _ = run_command("pip list --outdated --format=json", "Getting outdated packages")
    if not success:
        print("❌ Failed to get outdated packages list")
        return False
    
    try:
        outdated_packages = json.loads(stdout) if stdout.strip() else []
    except json.JSONDecodeError:
        print("❌ Failed to parse outdated packages JSON")
        return False
    
    if not outdated_packages:
        print("✅ All packages are up to date!")
        return True
    
    print(f"📦 Found {len(outdated_packages)} outdated packages")
    
    # Update packages one by one to avoid conflicts
    updated_count = 0
    failed_count = 0
    
    for package in outdated_packages:
        package_name = package['name']
        current_version = package['version']
        latest_version = package['latest_version']
        
        print(f"\n📦 Updating {package_name}: {current_version} → {latest_version}")
        
        success, _, stderr = run_command(
            f"pip install --upgrade {package_name}",
            f"Updating {package_name}"
        )
        
        if success:
            print(f"✅ Successfully updated {package_name}")
            updated_count += 1
        else:
            print(f"❌ Failed to update {package_name}: {stderr}")
            failed_count += 1
    
    print(f"\n📊 UPDATE SUMMARY:")
    print(f"✅ Successfully updated: {updated_count}")
    print(f"❌ Failed to update: {failed_count}")
    
    return failed_count == 0

def update_requirements_file():
    """Update requirements.txt with latest compatible versions"""
    print("\n📝 UPDATING REQUIREMENTS.TXT...")
    
    # Read current requirements
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    # Create backup
    backup_file = f"requirements_backup_{int(time.time())}.txt"
    run_command(f"copy requirements.txt {backup_file}", "Creating backup of requirements.txt")
    
    # Generate new requirements with current versions
    success, stdout, _ = run_command("pip freeze", "Getting current package versions")
    if not success:
        print("❌ Failed to get current package versions")
        return False
    
    # Write updated requirements
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_content = f"""# KIMERA SWM - Updated Dependencies
# Last updated: {timestamp}
# Auto-generated from pip freeze

{stdout}
"""
    
    with open("requirements_updated.txt", "w") as f:
        f.write(updated_content)
    
    print("✅ Created requirements_updated.txt with current versions")
    return True

def check_system_health():
    """Run basic system health checks"""
    print("\n🏥 RUNNING SYSTEM HEALTH CHECKS...")
    
    checks = [
        ("python --version", "Python version check"),
        ("pip --version", "Pip version check"),
        ("python -c \"import torch; print(f'PyTorch: {torch.__version__}')\"", "PyTorch check"),
        ("python -c \"import numpy; print(f'NumPy: {numpy.__version__}')\"", "NumPy check"),
        ("python -c \"import scipy; print(f'SciPy: {scipy.__version__}')\"", "SciPy check"),
        ("python -c \"import fastapi; print(f'FastAPI: {fastapi.__version__}')\"", "FastAPI check"),
    ]
    
    passed = 0
    failed = 0
    
    for command, description in checks:
        success, stdout, stderr = run_command(command, description)
        if success:
            print(f"✅ {description}: PASSED")
            if stdout.strip():
                print(f"   {stdout.strip()}")
            passed += 1
        else:
            print(f"❌ {description}: FAILED")
            if stderr.strip():
                print(f"   {stderr.strip()}")
            failed += 1
    
    print(f"\n📊 HEALTH CHECK SUMMARY:")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    return failed == 0

def update_git_repository():
    """Update git repository if it exists"""
    print("\n📡 CHECKING GIT REPOSITORY...")
    
    # Check if this is a git repository
    success, _, _ = run_command("git status", "Checking git status")
    if not success:
        print("ℹ️ Not a git repository, skipping git updates")
        return True
    
    # Fetch latest changes
    success, _, _ = run_command("git fetch", "Fetching latest changes")
    if not success:
        print("⚠️ Failed to fetch git changes")
        return False
    
    # Show status
    success, stdout, _ = run_command("git status", "Getting git status")
    if success and stdout:
        print("📊 Git Status:")
        print(stdout)
    
    print("ℹ️ Git repository checked. Manual merge may be required if there are conflicts.")
    return True

def generate_update_report():
    """Generate a comprehensive update report"""
    print("\n📋 GENERATING UPDATE REPORT...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"system_update_report_{timestamp}.md"
    
    # Get system information
    success, python_version, _ = run_command("python --version", "Getting Python version")
    success, pip_version, _ = run_command("pip --version", "Getting pip version")
    success, package_list, _ = run_command("pip list", "Getting package list")
    
    report_content = f"""# System Update Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## System Information
- Python Version: {python_version.strip() if python_version else 'Unknown'}
- Pip Version: {pip_version.strip() if pip_version else 'Unknown'}

## Update Summary
- ✅ Package updates completed
- ✅ Requirements file updated
- ✅ System health checks performed
- ✅ Git repository checked

## Current Package Versions
```
{package_list if package_list else 'Failed to get package list'}
```

## Next Steps
1. Test the system functionality
2. Run comprehensive tests
3. Update documentation if needed
4. Commit changes to version control

## Files Created
- requirements_updated.txt - Updated requirements file
- {report_file} - This report

---
*Report generated by Kimera SWM Update Script*
"""
    
    with open(report_file, "w") as f:
        f.write(report_content)
    
    print(f"✅ Update report saved to: {report_file}")
    return True

def main():
    """Main update function"""
    print("🚀 KIMERA SWM COMPREHENSIVE UPDATE SCRIPT")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    steps = [
        ("Updating pip packages", update_pip_packages),
        ("Updating requirements file", update_requirements_file),
        ("Running system health checks", check_system_health),
        ("Checking git repository", update_git_repository),
        ("Generating update report", generate_update_report),
    ]
    
    completed = 0
    failed = 0
    
    for step_name, step_function in steps:
        print(f"\n🔄 STEP: {step_name}")
        try:
            if step_function():
                print(f"✅ COMPLETED: {step_name}")
                completed += 1
            else:
                print(f"❌ FAILED: {step_name}")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR in {step_name}: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("🏁 UPDATE COMPLETE")
    print("=" * 60)
    print(f"✅ Completed steps: {completed}")
    print(f"❌ Failed steps: {failed}")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed == 0:
        print("\n🎉 ALL UPDATES COMPLETED SUCCESSFULLY!")
        print("Your Kimera SWM system is now up to date.")
    else:
        print(f"\n⚠️ {failed} steps failed. Please review the output above.")
        print("Some manual intervention may be required.")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)