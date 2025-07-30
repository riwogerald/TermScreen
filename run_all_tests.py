#!/usr/bin/env python3
"""
Master test runner that executes all test suites
Compatible with WebContainer Python environment
"""

import sys
import os
import time
from utils import preserve_sys_state


def run_test_suite(test_file, description):
    """Run a single test suite and return success status"""
    print(f"\n{'='*80}")
    print(f"Running {description}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        with preserve_sys_state():
            # Set up environment for test
            sys.argv = [test_file]
            
            # Import the test module
            test_module_name = test_file.replace('.py', '')
            
            # Remove from sys.modules if already imported to force reload
            if test_module_name in sys.modules:
                del sys.modules[test_module_name]
            
            # Import and run the test
            test_module = __import__(test_module_name)
            
            # Look for main function or run tests directly
            if hasattr(test_module, 'main'):
                result = test_module.main()
                success = result == 0 if result is not None else True
            elif hasattr(test_module, 'run_tests'):
                success = test_module.run_tests()
            elif hasattr(test_module, 'run_performance_tests'):
                success = test_module.run_performance_tests()
            elif hasattr(test_module, 'run_integration_tests'):
                success = test_module.run_integration_tests()
            else:
                # Try to run unittest if no specific function found
                import unittest
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromModule(test_module)
                runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
                result = runner.run(suite)
                success = result.wasSuccessful()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n{description} {'PASSED' if success else 'FAILED'} in {duration:.2f}s")
        
        return success, duration
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"\n{description} ERROR: {e}")
        
        return False, duration


def main():
    """Run all test suites"""
    print("Terminal Screen Renderer - Complete Test Suite")
    print("=" * 80)
    
    # Test suites to run
    test_suites = [
        ("test_renderer.py", "Core Functionality Tests"),
        ("test_performance.py", "Performance & Stress Tests"),
        ("test_integration.py", "Integration Tests"),
    ]
    
    total_start_time = time.time()
    results = []
    
    # Run each test suite
    for test_file, description in test_suites:
        if not os.path.exists(test_file):
            print(f"WARNING: {test_file} not found, skipping {description}")
            results.append((description, False, 0))
            continue
        
        success, duration = run_test_suite(test_file, description)
        results.append((description, success, duration))
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print final summary
    print(f"\n{'='*80}")
    print("FINAL TEST SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    
    for description, success, duration in results:
        status = "PASSED" if success else "FAILED"
        print(f"{description:<40} {status:<8} ({duration:.2f}s)")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*80}")
    print(f"Total Test Suites: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed / len(results) * 100):.1f}%")
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"{'='*80}")
    
    # Additional checks
    print("\nAdditional Checks:")
    
    # Check if all required files exist
    required_files = [
        "renderer.py",
        "demo.py",
        "test_renderer.py",
        "README.md",
        "package.json"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            missing_files.append(file)
    
    # Check if demos can be generated
    print("\nDemo Generation Check:")
    try:
        import demo
        demo1_data = demo.create_demo_1()
        demo2_data = demo.create_demo_2()
        print(f"✓ Demo 1 generated ({len(demo1_data)} bytes)")
        print(f"✓ Demo 2 generated ({len(demo2_data)} bytes)")
    except Exception as e:
        print(f"✗ Demo generation failed: {e}")
        failed += 1
    
    # Check if renderer can be imported
    print("\nRenderer Import Check:")
    try:
        import renderer
        print("✓ Renderer module imports successfully")
        
        # Check key classes exist
        if hasattr(renderer, 'ScreenRenderer'):
            print("✓ ScreenRenderer class available")
        else:
            print("✗ ScreenRenderer class missing")
            
        if hasattr(renderer, 'process_binary_stream'):
            print("✓ process_binary_stream function available")
        else:
            print("✗ process_binary_stream function missing")
            
    except Exception as e:
        print(f"✗ Renderer import failed: {e}")
        failed += 1
    
    # Final verdict
    print(f"\n{'='*80}")
    if failed == 0 and not missing_files:
        print("🎉 ALL TESTS PASSED - Project is ready for use!")
        exit_code = 0
    else:
        print("❌ SOME TESTS FAILED - Please review the issues above")
        exit_code = 1
    
    print(f"{'='*80}")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)