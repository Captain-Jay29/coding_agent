# blue_truck.py
# Prints a blue truck in the CLI using ANSI escape codes

BLUE = '\033[94m'
RESET = '\033[0m'

truck = f"""
      {BLUE}________{RESET}
 ____/      \\__
| _          _``-.
'-( o )-----( o )-'
"""

print(truck)
