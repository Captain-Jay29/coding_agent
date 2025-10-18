import time
import threading
import system_monitor

def run_monitor_for_duration(duration_sec):
    monitor_thread = threading.Thread(target=system_monitor.main)
    monitor_thread.start()
    time.sleep(duration_sec)
    # Attempt to stop the monitor gracefully if possible
    # If system_monitor.main() is a loop, consider setting a flag or using another mechanism
    # For now, we assume the process will be killed after 30 seconds
    print(f"Test complete: ran system_monitor for {duration_sec} seconds.")

if __name__ == "__main__":
    run_monitor_for_duration(30)
