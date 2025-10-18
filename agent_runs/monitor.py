#!/usr/bin/env python3
import time
import psutil
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box
from rich.align import Align
from rich.rule import Rule
from rich.columns import Columns
from rich.measure import Measurement
from rich.style import Style
from rich.traceback import install
from rich.markdown import Markdown
from rich.progress_bar import ProgressBar
from rich.bar import Bar
from rich.theme import Theme
from rich.plot import Plot
from rich.color import Color

console = Console()

def get_cpu_usage():
    return psutil.cpu_percent(interval=None)

def get_memory_usage():
    mem = psutil.virtual_memory()
    return mem.percent, mem.used, mem.total

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return disk.percent, disk.used, disk.total

def get_network_stats():
    net = psutil.net_io_counters()
    return net.bytes_sent, net.bytes_recv

def format_bytes(size):
    # 2**10 = 1024
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def make_table(cpu, mem, mem_used, mem_total, disk, disk_used, disk_total, net_sent, net_recv):
    table = Table(title="[bold magenta]System Resource Monitor", box=box.ROUNDED, style="bold white")
    table.add_column("Resource", style="cyan", no_wrap=True)
    table.add_column("Usage", style="green")
    table.add_column("Details", style="yellow")
    table.add_row("CPU", f"{cpu}%", "-")
    table.add_row("Memory", f"{mem}%", f"{format_bytes(mem_used)} / {format_bytes(mem_total)}")
    table.add_row("Disk", f"{disk}%", f"{format_bytes(disk_used)} / {format_bytes(disk_total)}")
    table.add_row("Net Sent", "-", f"{format_bytes(net_sent)}")
    table.add_row("Net Recv", "-", f"{format_bytes(net_recv)}")
    return table

def make_progress(cpu, mem, disk):
    progress = Progress(
        TextColumn("[bold blue]CPU"),
        BarColumn(bar_width=None, style="bright_magenta"),
        TextColumn("[bold white]{task.percentage:>3.0f}%"),
        expand=True,
        transient=True
    )
    cpu_task = progress.add_task("CPU", total=100, completed=cpu)
    mem_task = progress.add_task("Memory", total=100, completed=mem)
    disk_task = progress.add_task("Disk", total=100, completed=disk)
    return progress, cpu_task, mem_task, disk_task

def make_chart(data, label, color):
    # Simple bar chart using Rich's Bar
    bars = []
    for value in data:
        bars.append(Bar(size=20, begin=0, end=100, value=value, color=color))
    return Columns(bars, equal=True, expand=True)

def main():
    cpu_history = []
    mem_history = []
    disk_history = []
    net_sent0, net_recv0 = get_network_stats()
    start_time = time.time()
    with Live(console=console, refresh_per_second=4) as live:
        while True:
            cpu = get_cpu_usage()
            mem, mem_used, mem_total = get_memory_usage()
            disk, disk_used, disk_total = get_disk_usage()
            net_sent, net_recv = get_network_stats()
            cpu_history.append(cpu)
            mem_history.append(mem)
            disk_history.append(disk)
            if len(cpu_history) > 30:
                cpu_history.pop(0)
                mem_history.pop(0)
                disk_history.pop(0)
            table = make_table(cpu, mem, mem_used, mem_total, disk, disk_used, disk_total, net_sent-net_sent0, net_recv-net_recv0)
            cpu_chart = make_chart(cpu_history, "CPU", "magenta")
            mem_chart = make_chart(mem_history, "Memory", "green")
            disk_chart = make_chart(disk_history, "Disk", "yellow")
            charts = Columns([
                Panel(cpu_chart, title="CPU Usage", border_style="magenta"),
                Panel(mem_chart, title="Memory Usage", border_style="green"),
                Panel(disk_chart, title="Disk Usage", border_style="yellow")
            ], expand=True)
            layout = Layout()
            layout.split_column(
                Layout(table, name="upper", size=8),
                Layout(charts, name="lower")
            )
            live.update(layout)
            if time.time() - start_time > 30:
                break
            time.sleep(1)
if __name__ == "__main__":
    main()
