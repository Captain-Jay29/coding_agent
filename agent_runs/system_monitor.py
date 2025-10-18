import psutil
import os
from tabulate import tabulate

def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent

def get_python_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes

def main():
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()
    python_processes = get_python_processes()

    table = [
        ['CPU Usage (%)', cpu],
        ['Memory Usage (%)', memory],
        ['Disk Usage (%)', disk],
    ]

    print(tabulate(table, headers=['Metric', 'Value'], tablefmt='grid'))
    print("\nAll Running Python Processes:")
    if python_processes:
        proc_table = [[p['pid'], p['name'], p['cmdline']] for p in python_processes]
        print(tabulate(proc_table, headers=['PID', 'Name', 'Cmdline'], tablefmt='grid'))
    else:
        print("No running Python processes found.")

if __name__ == "__main__":
    main()
