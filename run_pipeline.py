"""
UTF-8 Wrapper for pipeline.py to handle Windows console encoding issues
"""
import sys
import io

# Force UTF-8 encoding for stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Import and run the main pipeline
if __name__ == "__main__":
    import pipeline
    pipeline.main()
