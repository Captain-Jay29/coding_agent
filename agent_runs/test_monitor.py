#!/usr/bin/env python3
import subprocess
import time

def test_monitor():
    proc = subprocess.Popen(["python", "monitor.py"])
    try:
        proc.wait(timeout=35)
    except subprocess.TimeoutExpired:
        proc.terminate()
        assert False, "Monitor did not exit after 30 seconds"
    assert proc.returncode == 0

if __name__ == "__main__":
    test_monitor()
