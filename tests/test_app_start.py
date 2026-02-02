#!/usr/bin/env python3
"""
Test that the application can start correctly
"""

import os
import sys
import tempfile
import subprocess
import time
import pytest

def test_app_start():
    """Test that the application can start correctly"""
    print("Testing application startup...")
    
    # Create a temporary config file
    config_content = """
api_key: "test-api-key"
SYNC_INTERVAL_MINUTES: 1
NOTIFY_INTERVAL_SECONDS: 10

calendars:
  "test_user": "https://example.com/test.ics"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp_config:
        tmp_config.write(config_content)
        tmp_config_path = tmp_config.name
    
    # Create a temporary database file
    tmp_db_path = tempfile.mktemp(suffix='.db')
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['CONFIG_PATH'] = tmp_config_path
        env['DB_PATH'] = tmp_db_path
        env['SYNC_INTERVAL_MINUTES'] = '1'
        env['NOTIFY_INTERVAL_SECONDS'] = '10'
        
        # Start the application in a subprocess
        print("Starting application...")
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit to see if it starts
        time.sleep(5)
        
        # Check if the process is still running
        if process.poll() is None:
            print("✓ Application started successfully")
            # Terminate the process
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)  # Wait for kill to complete
        else:
            stdout, stderr = process.communicate()
            print(f"Application failed to start. Exit code: {process.returncode}")
            print(f"Stdout: {stdout.decode()}")
            print(f"Stderr: {stderr.decode()}")
            pytest.fail("Application failed to start")
            
    finally:
        # Clean up temporary files
        # Try multiple times in case of file locking issues
        for _ in range(5):  # Try up to 5 times
            try:
                if os.path.exists(tmp_config_path):
                    os.unlink(tmp_config_path)
                if os.path.exists(tmp_db_path):
                    os.unlink(tmp_db_path)
                break  # Success, exit the loop
            except PermissionError:
                time.sleep(0.1)  # Wait a bit and try again
            except FileNotFoundError:
                # File already deleted, that's fine
                break
        else:
            # If we couldn't delete the files after 5 tries, print a warning
            print(f"Warning: Could not clean up temporary files {tmp_config_path}, {tmp_db_path}")

if __name__ == '__main__':
    try:
        test_app_start()
        print("Application startup test passed! ✓")
    except Exception as e:
        print(f"Application startup test failed! ✗: {e}")
        sys.exit(1)