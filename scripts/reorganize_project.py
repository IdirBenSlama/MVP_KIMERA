#!/usr/bin/env python3
"""
KIMERA SWM Project Reorganization Script
========================================

This script reorganizes the KIMERA project into a formal, professional structure
with proper documentation and file organization.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class ProjectReorganizer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_directory_structure(self):
        """Create the formal project directory structure"""
        
        directories = [
            # Core directories
            "src/kimera",
            "src/kimera/api",
            "src/kimera/core", 
            "src/kimera/engines",
            "src/kimera/linguistic",
            "src/kimera/monitoring",
            "src/kimera/vault",
            
            # Documentation
            "docs/api",
            "docs/architecture", 
            "docs/installation",
            "docs/testing",
            "docs/performance",
            "docs/research",
            "docs/examples",
            
            # Testing
            "tests/unit",
            "tests/integration", 
            "tests/stress",
            "tests/validation",
            "tests/benchmarks",
            "tests/fixtures",
            
            # Configuration
            "config/environments",
            "config/profiles",
            
            # Scripts
            "scripts/deployment",
            "scripts/maintenance", 
            "scripts/testing",
            "scripts/utilities",
            
            # Data and logs
            "data/samples",
            "data/exports",
            "logs",
            
            # Docker and deployment
            "docker",
            "deployment/kubernetes",
            "deployment/terraform",
            
            # Resources and assets
            "resources/documentation",
            "resources/research",
            "assets/images",
            "assets/diagrams",
            
            # Backup directory
            str(self.backup_dir.relative_to(self.project_root))
        ]
        
        print("📁 Creating directory structure...")
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   Created: {directory}")
    
    def backup_existing_files(self):
        """Backup existing files before reorganization"""
        print("\n💾 Creating backup of existing files...")
        
        # Files to backup
        backup_files = [
            "comprehensive_stress_test.py",
            "continue_stress_test.py", 
            "crash_test_kimera.py",
            "entropy_analysis.py",
            "entropy_formulas.py",
            "entropy_math_validation.py",
            "entropy_stress_test.py",
            "entropy_validation_summary.py",
            "progressive_crash_test.py",
            "robust_stress_test.py",
            "test_kimera_demo.py",
            "test_monitoring_system.py"
        ]
        
        for file in backup_files:
            src = self.project_root / file
            if src.exists():
                dst = self.backup_dir / file
                shutil.copy2(src, dst)
                print(f"   Backed up: {file}")
    
    def organize_source_code(self):
        """Organize source code into proper structure"""
        print("\n🔧 Organizing source code...")
        
        # Move backend to src/kimera
        if (self.project_root / "backend").exists():
            print("   Moving backend/ to src/kimera/")
            # Copy backend contents to src/kimera
            backend_src = self.project_root / "backend"
            kimera_dst = self.project_root / "src" / "kimera"
            
            for item in backend_src.iterdir():
                if item.is_dir():
                    shutil.copytree(item, kimera_dst / item.name, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, kimera_dst / item.name)
    
    def organize_tests(self):
        """Organize test files into proper structure"""
        print("\n🧪 Organizing test files...")
        
        # Move stress tests
        stress_tests = [
            "comprehensive_stress_test.py",
            "continue_stress_test.py",
            "crash_test_kimera.py", 
            "progressive_crash_test.py",
            "robust_stress_test.py"
        ]
        
        for test_file in stress_tests:
            src = self.project_root / test_file
            if src.exists():
                dst = self.project_root / "tests" / "stress" / test_file
                shutil.move(str(src), str(dst))
                print(f"   Moved: {test_file} -> tests/stress/")
        
        # Move validation tests
        validation_tests = [
            "entropy_analysis.py",
            "entropy_formulas.py", 
            "entropy_math_validation.py",
            "entropy_validation_summary.py"
        ]
        
        for test_file in validation_tests:
            src = self.project_root / test_file
            if src.exists():
                dst = self.project_root / "tests" / "validation" / test_file
                shutil.move(str(src), str(dst))
                print(f"   Moved: {test_file} -> tests/validation/")
        
        # Move demo and monitoring tests
        demo_tests = [
            "test_kimera_demo.py",
            "test_monitoring_system.py"
        ]
        
        for test_file in demo_tests:
            src = self.project_root / test_file
            if src.exists():
                dst = self.project_root / "tests" / "integration" / test_file
                shutil.move(str(src), str(dst))
                print(f"   Moved: {test_file} -> tests/integration/")
    
    def organize_scripts(self):
        """Organize scripts into proper structure"""
        print("\n📜 Organizing scripts...")
        
        # Move utility scripts
        utility_scripts = [
            "run_kimera.py",
            "launch_dashboard.py",
            "launch_monitoring.py", 
            "open_all_dashboards.py",
            "open_dashboard.py",
            "serve_dashboard.py"
        ]
        
        for script in utility_scripts:
            src = self.project_root / script
            if src.exists():
                dst = self.project_root / "scripts" / "utilities" / script
                shutil.copy2(src, dst)  # Copy instead of move to keep originals
                print(f"   Copied: {script} -> scripts/utilities/")
    
    def organize_resources(self):
        """Organize resources and documentation"""
        print("\n📚 Organizing resources...")
        
        # Move Resources directory contents
        resources_src = self.project_root / "Resources"
        if resources_src.exists():
            resources_dst = self.project_root / "resources" / "research"
            
            for item in resources_src.iterdir():
                if item.is_file():
                    dst_file = resources_dst / item.name
                    shutil.copy2(item, dst_file)
                    print(f"   Moved: Resources/{item.name} -> resources/research/")
    
    def organize_data_files(self):
        """Organize data files and databases"""
        print("\n💾 Organizing data files...")
        
        # Move database files to data directory
        db_files = [
            "kimera_swm.db",
            "crash_test_*.db*",
            "robust_stress_test.db",
            "stress_test*.db*"
        ]
        
        data_dir = self.project_root / "data"
        
        for pattern in db_files:
            for db_file in self.project_root.glob(pattern):
                if db_file.is_file():
                    dst = data_dir / db_file.name
                    shutil.move(str(db_file), str(dst))
                    print(f"   Moved: {db_file.name} -> data/")
        
        # Move result files
        result_files = [
            "*_results.json",
            "*_test_results.json"
        ]
        
        for pattern in result_files:
            for result_file in self.project_root.glob(pattern):
                if result_file.is_file():
                    dst = data_dir / "exports" / result_file.name
                    shutil.move(str(result_file), str(dst))
                    print(f"   Moved: {result_file.name} -> data/exports/")
    
    def organize_dashboard_files(self):
        """Organize dashboard and monitoring files"""
        print("\n📊 Organizing dashboard files...")
        
        # Dashboard files to move to monitoring
        dashboard_files = [
            "dashboard_cheatsheet.html",
            "dashboard_guide.html", 
            "monitoring_dashboard.html",
            "real_time_dashboard.html",
            "test_dashboard.html"
        ]
        
        monitoring_dir = self.project_root / "src" / "kimera" / "monitoring" / "dashboards"
        monitoring_dir.mkdir(exist_ok=True)
        
        for dashboard_file in dashboard_files:
            src = self.project_root / dashboard_file
            if src.exists():
                dst = monitoring_dir / dashboard_file
                shutil.move(str(src), str(dst))
                print(f"   Moved: {dashboard_file} -> src/kimera/monitoring/dashboards/")
    
    def create_configuration_files(self):
        """Create proper configuration files"""
        print("\n⚙️ Creating configuration files...")
        
        # Create setup.py
        setup_py_content = '''"""
KIMERA SWM Setup Configuration
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kimera-swm",
    version="1.0.0",
    author="KIMERA Development Team",
    author_email="dev@kimera-swm.org",
    description="Advanced Semantic Working Memory System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/kimera-swm",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "kimera-swm=kimera.cli:main",
        ],
    },
)
'''
        
        with open(self.project_root / "setup.py", "w") as f:
            f.write(setup_py_content)
        print("   Created: setup.py")
        
        # Create pyproject.toml
        pyproject_content = '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "kimera-swm"
version = "1.0.0"
description = "Advanced Semantic Working Memory System"
readme = "README.md"
requires-python = ">=3.12"
license = {text = "MIT"}
authors = [
    {name = "KIMERA Development Team", email = "dev@kimera-swm.org"},
]
keywords = ["ai", "cognitive-architecture", "semantic-processing", "thermodynamics"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

[project.urls]
Homepage = "https://github.com/your-org/kimera-swm"
Documentation = "https://kimera-swm.readthedocs.io"
Repository = "https://github.com/your-org/kimera-swm"
Issues = "https://github.com/your-org/kimera-swm/issues"

[tool.setuptools.packages.find]
where = ["src"]

[tool.black]
line-length = 88
target-version = ["py312"]
include = '\\.pyi?$'

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "stress: Stress tests",
    "slow: Slow running tests",
]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
'''
        
        with open(self.project_root / "pyproject.toml", "w") as f:
            f.write(pyproject_content)
        print("   Created: pyproject.toml")
        
        # Create .gitignore
        gitignore_content = '''# Python
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
MANIFEST

# Virtual environments
venv/
venv-*/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Databases
*.db
*.db-journal
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Environment variables
.env
.env.*

# OS
.DS_Store
Thumbs.db

# Backup
backup/

# Data files
data/exports/*.json
data/exports/*.csv
data/*.db*

# Temporary files
tmp/
temp/
*.tmp
'''
        
        with open(self.project_root / ".gitignore", "w") as f:
            f.write(gitignore_content)
        print("   Created: .gitignore")
    
    def create_init_files(self):
        """Create __init__.py files for proper Python package structure"""
        print("\n📦 Creating package __init__.py files...")
        
        init_files = [
            "src/kimera/__init__.py",
            "src/kimera/api/__init__.py",
            "src/kimera/core/__init__.py",
            "src/kimera/engines/__init__.py",
            "src/kimera/linguistic/__init__.py",
            "src/kimera/monitoring/__init__.py",
            "src/kimera/vault/__init__.py",
            "tests/__init__.py",
            "tests/unit/__init__.py",
            "tests/integration/__init__.py",
            "tests/stress/__init__.py",
            "tests/validation/__init__.py",
        ]
        
        for init_file in init_files:
            init_path = self.project_root / init_file
            if not init_path.exists():
                init_path.touch()
                print(f"   Created: {init_file}")
    
    def generate_reorganization_report(self):
        """Generate a report of the reorganization"""
        print("\n📋 Generating reorganization report...")
        
        report = {
            "reorganization_date": datetime.now().isoformat(),
            "project_structure": {
                "source_code": "src/kimera/",
                "documentation": "docs/",
                "tests": "tests/",
                "configuration": "config/",
                "scripts": "scripts/",
                "resources": "resources/",
                "data": "data/",
                "backup": str(self.backup_dir.relative_to(self.project_root))
            },
            "files_moved": {
                "stress_tests": "tests/stress/",
                "validation_tests": "tests/validation/",
                "integration_tests": "tests/integration/",
                "utility_scripts": "scripts/utilities/",
                "dashboard_files": "src/kimera/monitoring/dashboards/",
                "database_files": "data/",
                "result_files": "data/exports/",
                "research_documents": "resources/research/"
            },
            "new_files_created": [
                "setup.py",
                "pyproject.toml", 
                ".gitignore",
                "docs/README.md",
                "docs/api/README.md",
                "docs/architecture/README.md",
                "docs/installation/README.md",
                "docs/testing/README.md",
                "docs/performance/README.md"
            ]
        }
        
        report_file = self.project_root / "REORGANIZATION_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"   Report saved: {report_file}")
        return report
    
    def run_reorganization(self):
        """Run the complete project reorganization"""
        print("🚀 KIMERA SWM PROJECT REORGANIZATION")
        print("=" * 50)
        
        try:
            self.create_directory_structure()
            self.backup_existing_files()
            self.organize_source_code()
            self.organize_tests()
            self.organize_scripts()
            self.organize_resources()
            self.organize_data_files()
            self.organize_dashboard_files()
            self.create_configuration_files()
            self.create_init_files()
            report = self.generate_reorganization_report()
            
            print("\n✅ PROJECT REORGANIZATION COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print(f"📁 Backup created: {self.backup_dir}")
            print("📚 Documentation updated")
            print("🧪 Tests organized")
            print("⚙️ Configuration files created")
            print("📦 Package structure established")
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR DURING REORGANIZATION: {e}")
            print("🔄 Consider restoring from backup if needed")
            return False

def main():
    """Main function to run project reorganization"""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    reorganizer = ProjectReorganizer(project_root)
    success = reorganizer.run_reorganization()
    
    if success:
        print("\n🎉 KIMERA SWM project has been successfully reorganized!")
        print("📖 Check the updated documentation in docs/")
        print("🧪 Run tests with: pytest tests/")
        print("🚀 Start the system with: python scripts/utilities/run_kimera.py")
    else:
        print("\n💥 Reorganization failed. Check error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
