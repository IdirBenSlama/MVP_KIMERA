#!/usr/bin/env python3
"""
Scientific Tests Runner for Kimera SWM

This script runs all scientific tests with proper Python path configuration
to ensure the backend modules can be imported correctly.
"""

import sys
import os
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import test modules
sys.path.insert(0, str(project_root / "scientific"))

def run_all_scientific_tests():
    """Run all scientific tests and report results."""
    
    print("=" * 60)
    print("KIMERA SWM SCIENTIFIC TESTS")
    print("=" * 60)
    
    # Test results tracking
    results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'error_tests': 0,
        'test_files': []
    }
    
    # List of test files to run
    test_files = [
        'test_draconic_thermodynamic_analysis.py',
        'test_thermodynamics_foundations.py', 
        'test_thermodynamics_system.py'
    ]
    
    scientific_dir = project_root / "scientific"
    
    for test_file in test_files:
        test_path = scientific_dir / test_file
        
        if not test_path.exists():
            print(f"\n❌ Test file not found: {test_file}")
            continue
            
        print(f"\n🧪 Running {test_file}...")
        print("-" * 40)
        
        try:
            # Load and run the test module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(test_file[:-3])  # Remove .py extension
            
            # Run tests with detailed output
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            # Track results
            file_results = {
                'file': test_file,
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'success': result.wasSuccessful()
            }
            
            results['test_files'].append(file_results)
            results['total_tests'] += result.testsRun
            results['passed_tests'] += result.testsRun - len(result.failures) - len(result.errors)
            results['failed_tests'] += len(result.failures)
            results['error_tests'] += len(result.errors)
            
            if result.wasSuccessful():
                print(f"✅ {test_file}: All {result.testsRun} tests passed!")
            else:
                print(f"❌ {test_file}: {len(result.failures)} failures, {len(result.errors)} errors")
                
        except ImportError as e:
            print(f"❌ Import error in {test_file}: {e}")
            results['test_files'].append({
                'file': test_file,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success': False,
                'import_error': str(e)
            })
            results['error_tests'] += 1
            
        except Exception as e:
            print(f"❌ Unexpected error in {test_file}: {e}")
            results['test_files'].append({
                'file': test_file,
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success': False,
                'error': str(e)
            })
            results['error_tests'] += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for file_result in results['test_files']:
        status = "✅ PASS" if file_result['success'] else "❌ FAIL"
        print(f"{status} {file_result['file']}: {file_result['tests_run']} tests")
        
        if not file_result['success']:
            if 'import_error' in file_result:
                print(f"    Import Error: {file_result['import_error']}")
            elif 'error' in file_result:
                print(f"    Error: {file_result['error']}")
            else:
                print(f"    Failures: {file_result['failures']}, Errors: {file_result['errors']}")
    
    print(f"\nOverall Results:")
    print(f"  Total Tests: {results['total_tests']}")
    print(f"  Passed: {results['passed_tests']}")
    print(f"  Failed: {results['failed_tests']}")
    print(f"  Errors: {results['error_tests']}")
    
    success_rate = (results['passed_tests'] / results['total_tests'] * 100) if results['total_tests'] > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")
    
    return results


if __name__ == "__main__":
    # Change to scientific directory for test discovery
    os.chdir(project_root / "scientific")
    
    try:
        results = run_all_scientific_tests()
        
        # Exit with appropriate code
        if results['failed_tests'] > 0 or results['error_tests'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Fatal error running tests: {e}")
        sys.exit(1)