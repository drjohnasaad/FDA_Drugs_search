#!/usr/bin/env python3
"""
Quick Start - Verify FDA Medication Search App Setup

Run this script to test that everything is set up correctly and see working examples.
"""

import sys
import subprocess

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT - Command took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║     FDA MEDICATION SEARCH - QUICK START & VERIFICATION     ║
╚════════════════════════════════════════════════════════════╝
""")
    
    tests = [
        ("pip install -r requirements.txt", "Install Python Dependencies"),
        ("python3 test.py", "Run Example Medication Searches"),
    ]
    
    print("\nRunning verification tests...\n")
    
    passed = 0
    failed = 0
    
    for cmd, desc in tests:
        if run_command(cmd, desc):
            print(f"✓ PASSED")
            passed += 1
        else:
            print(f"✗ FAILED")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*60}\n")
    
    if failed == 0:
        print("""
✓ All tests passed! Your medication search app is ready.

NEXT STEPS:
1. Install dependencies:
   pip install -r requirements.txt

2. Run the web app:
   python3 app.py

3. Open your browser:
   http://localhost:5000

4. Try these searches:
   - Generic Name: "aspirin"
   - Brand Name: "tylenol"
   - NDC Code: "00930147"

For help, see TROUBLESHOOTING.md
""")
    else:
        print("""
Some tests failed. Check the output above for details.

Common issues:
- Missing dependencies: pip install -r requirements.txt
- Python not found: use python or python3
- Network issues: check internet connection
- API issues: see TROUBLESHOOTING.md
""")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
