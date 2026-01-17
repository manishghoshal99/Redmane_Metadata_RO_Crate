#!/usr/bin/env python3
"""
Wrapper script for REDMANE Metadata Generator.
This script replaces the old update_local_v1.py logic by calling the
redmane package directly.

Usage:
    python3 update_local.py --dataset <dataset_directory>
"""
import sys
import os

# Ensure the current directory is in sys.path so we can import 'redmane'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from redmane.generator import main
except ImportError as e:
    print(f"Error: Could not import redmane package. {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
