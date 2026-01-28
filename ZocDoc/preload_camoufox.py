#!/usr/bin/env python3
"""Pre-download Camoufox browser binary during Docker build"""
import tempfile
import shutil
from camoufox.sync_api import Camoufox

temp_dir = tempfile.mkdtemp()
try:
    print("Downloading Camoufox browser...")
    with Camoufox(headless=True, user_data_dir=temp_dir) as browser:
        print("Camoufox browser downloaded successfully!")
finally:
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("Cleanup complete")
