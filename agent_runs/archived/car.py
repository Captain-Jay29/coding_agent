#!/usr/bin/env python3
"""
Red Sports Car ASCII Art
A sleek sports car rendered in the terminal with ANSI color codes
"""

# ANSI color codes
RED = '\033[91m'
BRIGHT_RED = '\033[1;91m'
BLACK = '\033[90m'
WHITE = '\033[97m'
GRAY = '\033[37m'
RESET = '\033[0m'

def print_car():
    """Print a red sports car using ASCII art"""
    
    car = f"""
{RED}                                  __
{RED}                            _.--'  \\__
{RED}                     __..--''--.    \\  `.
{RED}              ___,--'     __  /  `.  \\   `.
{RED}           ,-'   __..--''' /  /     \\  \\    `.
{RED}        ,-'  _-''    __   /  /       \\  \\     \\
{RED}      ,'  ,-' __..--'  `-'  /         \\  \\     \\
{RED}    ,' ,-' ,-'             /     {BLACK}____{RED}  \\  \\     `.
{RED}  ,'  /  ,'        {BLACK}____{RED}    |    {BLACK}|    |{RED}  \\  \\      \\
{RED} /  ,'  /         {BLACK}|    |{RED}   |    {BLACK}|____|{RED}   \\  \\      \\
{RED}|  /   /          {BLACK}|____|{RED}   |              \\  \\      |
{RED}| |   |{BRIGHT_RED}═══════════════════════════════{RED}|  |      |
{RED}| |   |{BRIGHT_RED}════════════════════════════════{RED}|  |      |
{RED}|  \\   \\{BRIGHT_RED}═══════════════════════════════{RED}/  /      |
{RED} \\  `.  \\                            /  /      /
{RED}  \\   \\  `.                        ,'  /      /
{RED}   `.  \\   `--.                 _,'   /     ,'
{RED}     \\  `.     `--..____...--''     ,'    ,'
{RED}      `.  `-._                   _,'    ,'
{BLACK}    (  {WHITE}O{BLACK}  ){RED}    `--..____...--''  {BLACK}(  {WHITE}O{BLACK}  ){RED}
{BLACK}     `--'                            `--'{RESET}
    """
    
    print(car)
    print(f"{BRIGHT_RED}        🏎️  VROOM VROOM!  🏎️{RESET}")

if __name__ == "__main__":
    print_car()