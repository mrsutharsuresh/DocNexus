import sys
import pytest
from pathlib import Path
import datetime

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
TESTS_DIR = PROJECT_ROOT / 'tests'
OUTPUT_FILE = TESTS_DIR / 'latest_results.log'

def run_tests_with_pytest():
    """
    Runs all tests using pytest and pipes output to tests/latest_results.log.
    """
    print(f"Running tests via Pytest...")
    print(f"Output will be saved to: {OUTPUT_FILE}")

    # Args for pytest
    # -v: Verbose
    # --tb=short: Shorter tracebacks
    # Capture output to file is tricky with pytest.main inside python.
    # We can use the 'Pastebin' plugin or redirect stdout/stderr.
    
    # We will use simple stdout/stderr redirection at the Python level
    # because pytest writes to sys.stdout/sys.stderr
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"Test Run: {datetime.datetime.now()}\n")
        f.write("="*60 + "\n\n")
        f.flush()
        
        # Redirection Context
        class Tee(object):
            def __init__(self, *files):
                self.files = files
            def write(self, obj):
                for f in self.files:
                    f.write(obj)
                    f.flush()
            def flush(self):
                for f in self.files:
                    f.flush()
            def isatty(self):
                return False

        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # We redirect stdout/stderr to both console AND file
        sys.stdout = Tee(sys.stdout, f)
        sys.stderr = Tee(sys.stderr, f)
        
        try:
            # Run Pytest on 'tests' directory
            # We add '-ra' to show summary of (r)easons for (a)ll except passed
            exit_code = pytest.main(["-v", "-ra", str(TESTS_DIR)])
        finally:
            # Restore
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            
        f.write("\n" + "="*60 + "\n")
        f.write(f"Run Completed. Exit Code: {exit_code}\n")
        
    return exit_code == 0

if __name__ == "__main__":
    success = run_tests_with_pytest()
    sys.exit(0 if success else 1)
