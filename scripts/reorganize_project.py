#!/usr/bin/env python3
"""
KIMERA SWM Project Reorganization Script
========================================

This script reorganizes the chaotic directory structure into a clean,
professional layout following industry best practices.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List

class ProjectReorganizer:
    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.backup_dir = self.root / "backup_before_reorganization"
        
        # Define the new clean structure
        self.new_structure = {
            # Core application code
            "src/": {
                "kimera/": {
                    "core/": [],
                    "engines/": [],
                    "api/": [],
                    "vault/": [],
                    "monitoring/": [],
                    "linguistic/": [],
                    "governance/": [],
                    "tools/": []
                }
            },
            
            # Documentation
            "docs/": {
                "architecture/": [],
                "api/": [],
                "installation/": [],
                "testing/": [],
                "performance/": [],
                "research/": [],
                "guides/": [],
                "specifications/": []
            },
            
            # Tests
            "tests/": {
                "unit/": [],
                "integration/": [],
                "stress/": [],
                "validation/": [],
                "set_theory/": [],
                "scientific/": []
            },
            
            # Configuration
            "config/": {
                "environments/": [],
                "fine_tuning/": [],
                "optimization/": []
            },
            
            # Scripts and utilities
            "scripts/": {
                "deployment/": [],
                "testing/": [],
                "analysis/": [],
                "utilities/": []
            },
            
            # Web interfaces
            "web/": {
                "dashboard/": [],
                "monitoring/": [],
                "static/": {
                    "css/": [],
                    "js/": [],
                    "images/": []
                }
            },
            
            # Data and results
            "data/": {
                "test_results/": [],
                "benchmarks/": [],
                "analysis/": [],
                "databases/": []
            },
            
            # Research and resources
            "research/": {
                "papers/": [],
                "specifications/": [],
                "theory/": [],
                "case_studies/": []
            },
            
            # Build and deployment
            "build/": [],
            "dist/": [],
            
            # Temporary and backup
            "temp/": [],
            "backups/": []
        }
        
        # File categorization rules
        self.file_rules = {
            # Source code mappings
            "backend/": "src/kimera/",
            
            # Documentation mappings
            r".*\.md$": self._categorize_markdown,
            r".*README.*": "docs/",
            
            # Test mappings
            r"test_.*\.py$": "tests/",
            r".*_test\.py$": "tests/",
            r".*test.*\.py$": "tests/",
            
            # Configuration mappings
            r".*config.*\.json$": "config/",
            r"requirements.*\.txt$": "config/",
            r"setup\.py$": "config/",
            
            # Script mappings
            r"run_.*\.py$": "scripts/",
            r"launch_.*\.py$": "scripts/",
            r".*_analysis\.py$": "scripts/analysis/",
            
            # Web interface mappings
            r".*\.html$": "web/dashboard/",
            r".*\.js$": "web/static/js/",
            r".*\.css$": "web/static/css/",
            
            # Data mappings
            r".*\.db$": "data/databases/",
            r".*\.json$": self._categorize_json,
            r".*results.*": "data/test_results/",
            
            # Research mappings
            r".*\.pdf$": "research/papers/",
            
            # Build artifacts
            r".*\.egg-info/": "build/",
            
            # Temporary files
            r".*\.pyc$": "temp/",
            r"__pycache__/": "temp/"
        }
    
    def _categorize_markdown(self, filepath: Path) -> str:
        """Categorize markdown files based on content and name."""
        name = filepath.name.lower()
        
        if any(x in name for x in ['architecture', 'system']):
            return "docs/architecture/"
        elif any(x in name for x in ['api', 'endpoint']):
            return "docs/api/"
        elif any(x in name for x in ['install', 'setup', 'deploy']):
            return "docs/installation/"
        elif any(x in name for x in ['test', 'validation']):
            return "docs/testing/"
        elif any(x in name for x in ['performance', 'benchmark']):
            return "docs/performance/"
        elif any(x in name for x in ['research', 'theory', 'swm']):
            return "docs/research/"
        elif any(x in name for x in ['guide', 'how', 'tutorial']):
            return "docs/guides/"
        elif any(x in name for x in ['spec', 'specification']):
            return "docs/specifications/"
        else:
            return "docs/"
    
    def _categorize_json(self, filepath: Path) -> str:
        """Categorize JSON files based on content and name."""
        name = filepath.name.lower()
        
        if any(x in name for x in ['config', 'settings']):
            return "config/"
        elif any(x in name for x in ['results', 'test', 'benchmark']):
            return "data/test_results/"
        elif any(x in name for x in ['analysis', 'report']):
            return "data/analysis/"
        else:
            return "data/"
    
    def create_backup(self):
        """Create a backup of the current state."""
        print("Creating backup of current state...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # Copy everything except the backup directory itself
        shutil.copytree(self.root, self.backup_dir, 
                       ignore=shutil.ignore_patterns('backup_*', '.git'))
        print(f"Backup created at: {self.backup_dir}")
    
    def create_directory_structure(self):
        """Create the new directory structure."""
        print("Creating new directory structure...")
        
        def create_dirs(structure: Dict, base_path: Path):
            for name, content in structure.items():
                dir_path = base_path / name
                dir_path.mkdir(parents=True, exist_ok=True)
                
                if isinstance(content, dict):
                    create_dirs(content, dir_path)
        
        create_dirs(self.new_structure, self.root)
        print("Directory structure created.")
    
    def move_files(self):
        """Move files to their new locations."""
        print("Moving files to new structure...")
        
        # Get all files in root directory (excluding new structure)
        files_to_move = []
        for item in self.root.iterdir():
            if (item.is_file() and 
                item.name not in ['reorganize_project.py'] and
                not item.name.startswith('backup_')):
                files_to_move.append(item)
            elif (item.is_dir() and 
                  item.name not in ['src', 'docs', 'tests', 'config', 'scripts', 
                                   'web', 'data', 'research', 'build', 'dist', 
                                   'temp', 'backups', 'backup_before_reorganization']):
                files_to_move.append(item)
        
        moved_count = 0
        for item in files_to_move:
            try:
                new_location = self._determine_new_location(item)
                if new_location:
                    target_path = self.root / new_location / item.name
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if item.is_file():
                        shutil.move(str(item), str(target_path))
                    else:
                        shutil.move(str(item), str(target_path))
                    
                    moved_count += 1
                    print(f"Moved: {item.name} -> {new_location}")
            except Exception as e:
                print(f"Error moving {item.name}: {e}")
        
        print(f"Moved {moved_count} items.")
    
    def _determine_new_location(self, item: Path) -> str:
        """Determine where a file/directory should be moved."""
        name = item.name
        
        # Special directory mappings
        if item.is_dir():
            if name == 'backend':
                return 'src/kimera'
            elif name == 'docs':
                return 'docs'  # Keep existing docs structure
            elif name == 'tests':
                return 'tests'  # Keep existing tests structure
            elif name == 'config':
                return 'config'
            elif name == 'scripts':
                return 'scripts'
            elif name == 'dashboard':
                return 'web'
            elif name == 'static':
                return 'web/static'
            elif name == 'Resources':
                return 'research'
            elif name == 'optimization':
                return 'scripts/optimization'
            elif name == 'scientific':
                return 'tests/scientific'
            elif name == 'verification':
                return 'tests/validation'
            elif name == 'report_kimera':
                return 'data/analysis'
            elif name.endswith('.egg-info'):
                return 'build'
            else:
                return 'temp'
        
        # File mappings
        for pattern, destination in self.file_rules.items():
            if callable(destination):
                result = destination(item)
                if result:
                    return result
            elif item.match(pattern) or pattern in name:
                return destination
        
        # Default location for unmatched files
        return 'temp'
    
    def create_new_structure_files(self):
        """Create essential files for the new structure."""
        print("Creating new structure files...")
        
        # Create main README
        main_readme = """# KIMERA SWM - Semantic Working Memory System

A sophisticated cognitive architecture implementing semantic thermodynamic principles.

## Project Structure

```
kimera-swm/
├── src/kimera/          # Core application code
├── docs/                # Documentation
├── tests/               # Test suites
├── config/              # Configuration files
├── scripts/             # Utility scripts
├── web/                 # Web interfaces
├── data/                # Data and results
├── research/            # Research materials
└── build/               # Build artifacts
```

## Quick Start

```bash
# Install dependencies
pip install -r config/requirements.txt

# Run the system
python scripts/run_kimera.py

# Run tests
python -m pytest tests/
```

## Documentation

See the [docs/](docs/) directory for comprehensive documentation.
"""
        
        with open(self.root / "README.md", "w") as f:
            f.write(main_readme)
        
        # Create .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/databases/*.db
data/databases/*.db-shm
data/databases/*.db-wal
temp/
backups/
*.log

# Test artifacts
.pytest_cache/
.coverage
htmlcov/
"""
        
        with open(self.root / ".gitignore", "w") as f:
            f.write(gitignore)
        
        # Create setup.cfg
        setup_cfg = """[metadata]
name = kimera-swm
version = 2.2.1
description = Semantic Working Memory System
long_description = file: README.md
long_description_content_type = text/markdown
author = KIMERA Development Team
license = MIT
classifiers =
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.12

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.12
install_requires =
    fastapi>=0.115.12
    sqlalchemy>=2.0.41
    transformers>=4.52.4
    sentence-transformers>=4.1.0
    numpy>=2.3.0
    scipy>=1.15.3
    uvicorn>=0.34.3

[options.packages.find]
where = src

[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
"""
        
        with open(self.root / "setup.cfg", "w") as f:
            f.write(setup_cfg)
        
        print("New structure files created.")
    
    def cleanup_empty_directories(self):
        """Remove empty directories."""
        print("Cleaning up empty directories...")
        
        def remove_empty_dirs(path: Path):
            if not path.is_dir():
                return
            
            # First, recursively clean subdirectories
            for subdir in path.iterdir():
                if subdir.is_dir():
                    remove_empty_dirs(subdir)
            
            # Then check if this directory is empty and remove it
            try:
                if not any(path.iterdir()):
                    path.rmdir()
                    print(f"Removed empty directory: {path}")
            except OSError:
                pass  # Directory not empty or permission issue
        
        # Clean up from the root, but preserve our new structure
        for item in self.root.iterdir():
            if item.is_dir() and item.name not in ['src', 'docs', 'tests', 'config', 
                                                  'scripts', 'web', 'data', 'research', 
                                                  'build', 'dist', 'temp', 'backups',
                                                  'backup_before_reorganization', '.git']:
                remove_empty_dirs(item)
    
    def generate_report(self):
        """Generate a reorganization report."""
        print("Generating reorganization report...")
        
        report = {
            "reorganization_date": "2024-12-14",
            "original_structure": "Chaotic - 80+ files in root directory",
            "new_structure": {
                "src/kimera/": "Core application code",
                "docs/": "All documentation organized by type",
                "tests/": "All test suites organized by category",
                "config/": "Configuration files and requirements",
                "scripts/": "Utility and deployment scripts",
                "web/": "Web interfaces and static assets",
                "data/": "Test results, databases, and analysis",
                "research/": "Research papers and theoretical materials",
                "build/": "Build artifacts and distribution files",
                "temp/": "Temporary files and unclassified items"
            },
            "benefits": [
                "Clear separation of concerns",
                "Industry-standard directory structure",
                "Easier navigation and maintenance",
                "Better IDE support",
                "Simplified CI/CD setup",
                "Professional appearance"
            ],
            "backup_location": "backup_before_reorganization/"
        }
        
        with open(self.root / "REORGANIZATION_REPORT.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print("Reorganization complete! Report saved to REORGANIZATION_REPORT.json")

def main():
    """Main reorganization function."""
    root_path = os.getcwd()
    reorganizer = ProjectReorganizer(root_path)
    
    print("KIMERA SWM Project Reorganization")
    print("=" * 40)
    print(f"Working directory: {root_path}")
    print()
    
    # Confirm before proceeding
    response = input("This will reorganize the entire project structure. Continue? (y/N): ")
    if response.lower() != 'y':
        print("Reorganization cancelled.")
        return
    
    try:
        # Step 1: Create backup
        reorganizer.create_backup()
        
        # Step 2: Create new directory structure
        reorganizer.create_directory_structure()
        
        # Step 3: Move files
        reorganizer.move_files()
        
        # Step 4: Create new structure files
        reorganizer.create_new_structure_files()
        
        # Step 5: Cleanup
        reorganizer.cleanup_empty_directories()
        
        # Step 6: Generate report
        reorganizer.generate_report()
        
        print("\n" + "=" * 40)
        print("✅ Reorganization completed successfully!")
        print("📁 Backup created at: backup_before_reorganization/")
        print("📊 See REORGANIZATION_REPORT.json for details")
        print("\nNext steps:")
        print("1. Review the new structure")
        print("2. Update import statements in code")
        print("3. Update CI/CD configurations")
        print("4. Test the reorganized system")
        
    except Exception as e:
        print(f"\n❌ Error during reorganization: {e}")
        print("The backup is available at: backup_before_reorganization/")
        print("You can restore from backup if needed.")

if __name__ == "__main__":
    main()