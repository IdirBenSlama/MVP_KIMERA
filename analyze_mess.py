#!/usr/bin/env python3
"""
Directory Mess Analysis
=======================

Analyzes the current chaotic directory structure and shows the problems.
"""

import os
from pathlib import Path
from collections import defaultdict

def analyze_directory_mess():
    """Analyze the current directory structure."""
    root = Path.cwd()
    
    print("KIMERA SWM Directory Mess Analysis")
    print("=" * 50)
    print(f"Root directory: {root}")
    print()
    
    # Count items in root
    files_in_root = []
    dirs_in_root = []
    
    for item in root.iterdir():
        if item.name.startswith('.'):
            continue
        if item.is_file():
            files_in_root.append(item)
        elif item.is_dir():
            dirs_in_root.append(item)
    
    print(f"📁 Directories in root: {len(dirs_in_root)}")
    print(f"📄 Files in root: {len(files_in_root)}")
    print(f"📊 Total items in root: {len(files_in_root) + len(dirs_in_root)}")
    print()
    
    # Analyze file types
    file_types = defaultdict(list)
    for file in files_in_root:
        ext = file.suffix.lower() or 'no_extension'
        file_types[ext].append(file.name)
    
    print("📋 Files by type in root directory:")
    for ext, files in sorted(file_types.items()):
        print(f"  {ext}: {len(files)} files")
        if len(files) <= 5:
            for file in files:
                print(f"    - {file}")
        else:
            for file in files[:3]:
                print(f"    - {file}")
            print(f"    ... and {len(files) - 3} more")
    print()
    
    # Identify problematic patterns
    problems = {
        "Test files in root": [f for f in files_in_root if 'test' in f.name.lower()],
        "Database files in root": [f for f in files_in_root if f.suffix in ['.db', '.db-shm', '.db-wal']],
        "JSON result files": [f for f in files_in_root if f.suffix == '.json' and any(x in f.name.lower() for x in ['result', 'analysis', 'report'])],
        "HTML files in root": [f for f in files_in_root if f.suffix == '.html'],
        "Documentation scattered": [f for f in files_in_root if f.suffix == '.md'],
        "Python scripts everywhere": [f for f in files_in_root if f.suffix == '.py'],
    }
    
    print("🚨 PROBLEMS IDENTIFIED:")
    for problem, files in problems.items():
        if files:
            print(f"  ❌ {problem}: {len(files)} files")
            for file in files[:3]:
                print(f"     - {file.name}")
            if len(files) > 3:
                print(f"     ... and {len(files) - 3} more")
    print()
    
    # Show directory structure issues
    print("📁 DIRECTORY STRUCTURE ISSUES:")
    
    # Check for duplicate/similar directories
    dir_names = [d.name.lower() for d in dirs_in_root]
    if 'docs' in dir_names and any('doc' in name for name in dir_names if name != 'docs'):
        print("  ❌ Multiple documentation directories")
    
    if 'tests' in dir_names and any('test' in name for name in dir_names if name != 'tests'):
        print("  ❌ Multiple test directories")
    
    # Check for scattered configs
    config_files = [f for f in files_in_root if 'config' in f.name.lower()]
    if config_files and 'config' in dir_names:
        print(f"  ❌ Config files both in root ({len(config_files)}) and config/ directory")
    
    # Check for build artifacts
    build_artifacts = [f for f in files_in_root if any(x in f.name.lower() for x in ['build', 'dist', 'egg-info'])]
    if build_artifacts:
        print(f"  ❌ Build artifacts in root: {len(build_artifacts)} files")
    
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("  1. Move all test files to tests/ directory")
    print("  2. Move all documentation to docs/ directory") 
    print("  3. Move database files to data/ directory")
    print("  4. Move JSON results to results/ or data/ directory")
    print("  5. Move HTML files to web/ or dashboard/ directory")
    print("  6. Organize Python scripts by purpose")
    print("  7. Move build artifacts to build/ directory")
    print("  8. Create clear separation between source code and artifacts")
    print()
    
    print("🛠️  AVAILABLE CLEANUP SCRIPTS:")
    print("  - quick_cleanup.py: Conservative cleanup, preserves functionality")
    print("  - reorganize_project.py: Complete restructure to industry standards")
    print()
    
    # Show largest files
    large_files = [(f, f.stat().st_size) for f in files_in_root]
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    print("📊 LARGEST FILES IN ROOT:")
    for file, size in large_files[:10]:
        size_mb = size / (1024 * 1024)
        if size_mb > 0.1:  # Show files > 100KB
            print(f"  {size_mb:6.2f} MB - {file.name}")
    print()
    
    # Summary
    print("📈 MESS SEVERITY: HIGH")
    print(f"  - {len(files_in_root)} files cluttering root directory")
    print(f"  - {len([f for f in files_in_root if f.suffix == '.py'])} Python scripts mixed with data")
    print(f"  - {len([f for f in files_in_root if f.suffix == '.md'])} documentation files scattered")
    print(f"  - {len([f for f in files_in_root if f.suffix in ['.json', '.db', '.html']])} data/result files in wrong location")
    print()
    print("🎯 GOAL: Clean, professional directory structure")
    print("📁 SOLUTION: Run one of the cleanup scripts")

if __name__ == "__main__":
    analyze_directory_mess()