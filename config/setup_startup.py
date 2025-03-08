#!/usr/bin/env python3
import os
import sys
import winreg
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def add_to_startup():
    """Add pod_monitor.py to Windows startup."""
    try:
        # Get the full path to pod_monitor.py
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        monitor_path = os.path.join(script_dir, 'pod_monitor.py')
        pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        
        # Create the command to run the script
        command = f'"{pythonw_path}" "{monitor_path}"'
        
        # Open the registry key for startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Add the script to startup
        winreg.SetValueEx(
            key,
            "RunPod Monitor",
            0,
            winreg.REG_SZ,
            command
        )
        
        print(f"{Fore.GREEN}Successfully added RunPod Monitor to startup!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}The monitor will start automatically when you log in.{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error adding to startup: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    add_to_startup()

"""
After setup, the script will run silently in the background when you log into Windows.
You can check the logs in logs/pod_monitor_YYYYMMDD.log
""" 