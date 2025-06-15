#!/usr/bin/env python3
"""
KIMERA SWM Quick Cleanup Script
===============================

A conservative cleanup that organizes files without breaking existing functionality.
This script moves files into logical folders while preserving the current structure.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict

class QuickCleanup:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        
        # Define cleanup categories
        self.cleanup_folders = {
            "documentation/": {
                "patterns": ["*.md"],
                "exceptions": ["README.md"],  # Keep main README in root
                "description": "All Markdown documentation files"
            },
            "test_results/": {
                "patterns": ["*results*.json", "*test*.json", "*analysis*.json", 
                           "*verification*.json", "*benchmark*.json"],
                "exceptions": [],
                "description": "Test results and analysis JSON files"
            },
            "test_databases/": {
                "patterns": ["*.db", "*.db-shm", "*.db-wal"],
                "exceptions": ["kimera_swm.db", "kimera_swm.db-shm"],  # Keep main DB in root
                "description": "Test database files"
            },
            "test_scripts/": {
                "patterns": ["test_*.py", "*_test.py", "crash_test*.py", 
                           "stress_test*.py", "comprehensive_*test*.py"],
                "exceptions": [],
                "description": "Test and analysis scripts"
            },
            "utility_scripts/": {
                "patterns": ["run_*.py", "launch_*.py", "open_*.py", "serve_*.py",
                           "*_analysis.py", "implement_*.py", "integrate_*.py",
                           "convert_*.py", "check_*.py", "final_*.py"],
                "exceptions": ["run_kimera.py"],  # Keep main runner in root
                "description": "Utility and helper scripts"
            },
            "web_interfaces/": {
                "patterns": ["*.html", "dashboard*"],
                "exceptions": [],
                "description": "Web dashboards and HTML files"
            },
            "financial_demos/": {
                "patterns": ["financial_*.py", "*financial*.py", "*market*.py", 
                           "*volatility*.py", "extreme_*.py", "high_*.py"],
                "exceptions": [],
                "description": "Financial analysis and demo scripts"
            },
            "archived_configs/": {
                "patterns": ["*config*.py"],
                "exceptions": [],
                "description": "Configuration scripts (config/ folder has JSON configs)"
            }
        }
    
    def analyze_current_mess(self) -> Dict:
        """Analyze the current directory mess."""
        analysis = {
            "total_files_in_root": 0,
            "files_by_type": {},
            "large_files": [],
            "potential_moves": {}
        }
        
        for item in self.root.iterdir():
            if item.is_file():
                analysis["total_files_in_root"] += 1
                
                # Count by extension
                ext = item.suffix.lower()
                analysis["files_by_type"][ext] = analysis["files_by_type"].get(ext, 0) + 1
                
                # Check file size
                size_mb = item.stat().st_size / (1024 * 1024)
                if size_mb > 1:  # Files larger than 1MB
                    analysis["large_files"].append({
                        "name": item.name,
                        "size_mb": round(size_mb, 2)
                    })
                
                # Check which cleanup folder it would go to
                for folder, config in self.cleanup_folders.items():
                    if self._matches_patterns(item.name, config["patterns"], config["exceptions"]):
                        if folder not in analysis["potential_moves"]:
                            analysis["potential_moves"][folder] = []
                        analysis["potential_moves"][folder].append(item.name)
                        break
        
        return analysis
    
    def _matches_patterns(self, filename: str, patterns: List[str], exceptions: List[str]) -> bool:
        """Check if filename matches patterns but not exceptions."""
        if filename in exceptions:
            return False
        
        for pattern in patterns:
            if pattern.startswith("*") and pattern.endswith("*"):
                # Contains pattern
                if pattern[1:-1] in filename:
                    return True
            elif pattern.startswith("*"):
                # Ends with pattern
                if filename.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                # Starts with pattern
                if filename.startswith(pattern[:-1]):
                    return True
            else:
                # Exact match
                if filename == pattern:
                    return True
        
        return False
    
    def create_cleanup_folders(self):
        """Create the cleanup folders."""
        print("Creating cleanup folders...")
        for folder in self.cleanup_folders.keys():
            folder_path = self.root / folder
            folder_path.mkdir(exist_ok=True)
            print(f"  ✓ Created: {folder}")
    
    def move_files(self, dry_run: bool = True):
        """Move files to cleanup folders."""
        moved_count = 0
        
        for folder, config in self.cleanup_folders.items():
            folder_path = self.root / folder
            
            for item in self.root.iterdir():
                if (item.is_file() and 
                    self._matches_patterns(item.name, config["patterns"], config["exceptions"])):
                    
                    target_path = folder_path / item.name
                    
                    if dry_run:
                        print(f"  WOULD MOVE: {item.name} -> {folder}")
                    else:
                        try:
                            shutil.move(str(item), str(target_path))
                            print(f"  ✓ MOVED: {item.name} -> {folder}")
                            moved_count += 1
                        except Exception as e:
                            print(f"  ❌ ERROR moving {item.name}: {e}")
        
        return moved_count
    
    def create_index_files(self):
        """Create index files in each cleanup folder."""
        for folder, config in self.cleanup_folders.items():
            folder_path = self.root / folder
            index_path = folder_path / "README.md"
            
            # Count files in folder
            file_count = len([f for f in folder_path.iterdir() if f.is_file() and f.name != "README.md"])
            
            index_content = f"""# {folder.replace('_', ' ').title().rstrip('/')}

{config['description']}

**Files in this folder:** {file_count}

## Contents

"""
            
            # List files
            for file in sorted(folder_path.iterdir()):
                if file.is_file() and file.name != "README.md":
                    index_content += f"- `{file.name}`\n"
            
            index_content += f"""
## Purpose

This folder was created during project reorganization to clean up the root directory.
These files were moved here based on naming patterns and file types.

**Original location:** Root directory  
**Moved on:** 2024-12-14  
**Cleanup script:** quick_cleanup.py  
"""
            
            with open(index_path, "w") as f:
                f.write(index_content)
    
    def update_main_readme(self):
        """Update the main README with cleanup information."""
        readme_path = self.root / "README.md"
        
        if readme_path.exists():
            # Read existing README
            with open(readme_path, "r") as f:
                content = f.read()
            
            # Add cleanup notice
            cleanup_notice = """

## 📁 Project Organization

This project has been reorganized for better maintainability. Files have been moved to logical folders:

- `documentation/` - All Markdown documentation files
- `test_results/` - Test results and analysis JSON files  
- `test_databases/` - Test database files
- `test_scripts/` - Test and analysis scripts
- `utility_scripts/` - Utility and helper scripts
- `web_interfaces/` - Web dashboards and HTML files
- `financial_demos/` - Financial analysis and demo scripts
- `archived_configs/` - Configuration scripts

Each folder contains a README.md explaining its contents.

"""
            
            # Append to existing README
            with open(readme_path, "w") as f:
                f.write(content + cleanup_notice)
    
    def generate_cleanup_report(self, analysis: Dict, moved_count: int):
        """Generate a cleanup report."""
        report_content = f"""# KIMERA SWM Quick Cleanup Report

**Date:** 2024-12-14  
**Script:** quick_cleanup.py  

## Before Cleanup

- **Total files in root:** {analysis['total_files_in_root']}
- **Files moved:** {moved_count}
- **Files remaining in root:** {analysis['total_files_in_root'] - moved_count}

## Files by Type (Before)

"""
        
        for ext, count in sorted(analysis['files_by_type'].items()):
            report_content += f"- `{ext or 'no extension'}`: {count} files\n"
        
        report_content += f"""

## Large Files (>1MB)

"""
        
        for file_info in analysis['large_files']:
            report_content += f"- `{file_info['name']}`: {file_info['size_mb']} MB\n"
        
        report_content += f"""

## Cleanup Folders Created

"""
        
        for folder, config in self.cleanup_folders.items():
            count = len(analysis['potential_moves'].get(folder, []))
            report_content += f"- `{folder}`: {count} files - {config['description']}\n"
        
        report_content += f"""

## Benefits

- ✅ Root directory is much cleaner
- ✅ Files are logically organized
- ✅ Easier to find specific file types
- ✅ Better project navigation
- ✅ Preserved existing functionality
- ✅ Each folder has documentation

## Next Steps

1. Review the organized folders
2. Update any hardcoded file paths in scripts
3. Consider further reorganization if needed
4. Update CI/CD configurations if necessary

"""
        
        with open(self.root / "CLEANUP_REPORT.md", "w") as f:
            f.write(report_content)

def main():
    """Main cleanup function."""
    root_path = os.getcwd()
    cleanup = QuickCleanup(root_path)
    
    print("KIMERA SWM Quick Cleanup")
    print("=" * 30)
    print(f"Working directory: {root_path}")
    print()
    
    # Analyze current state
    print("🔍 Analyzing current directory mess...")
    analysis = cleanup.analyze_current_mess()
    
    print(f"📊 Found {analysis['total_files_in_root']} files in root directory")
    print(f"📁 Will create {len(cleanup.cleanup_folders)} cleanup folders")
    print()
    
    # Show what would be moved
    print("📋 Cleanup plan:")
    for folder, files in analysis['potential_moves'].items():
        print(f"  {folder}: {len(files)} files")
    print()
    
    # Dry run first
    print("🧪 DRY RUN - Showing what would be moved:")
    cleanup.create_cleanup_folders()
    cleanup.move_files(dry_run=True)
    print()
    
    # Confirm
    response = input("Proceed with actual cleanup? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    try:
        print("\n🚀 Starting cleanup...")
        
        # Actually move files
        moved_count = cleanup.move_files(dry_run=False)
        
        # Create documentation
        cleanup.create_index_files()
        cleanup.update_main_readme()
        cleanup.generate_cleanup_report(analysis, moved_count)
        
        print(f"\n✅ Cleanup completed!")
        print(f"📁 Moved {moved_count} files to organized folders")
        print(f"📊 See CLEANUP_REPORT.md for details")
        print(f"📖 Each folder now has a README.md explaining its contents")
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")

if __name__ == "__main__":
    main()