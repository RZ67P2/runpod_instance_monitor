#!/usr/bin/env python3
import winreg
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def remove_from_startup():
    """Remove pod_monitor.py from Windows startup."""
    try:
        # Open the registry key for startup programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        
        # Remove the script from startup
        winreg.DeleteValue(key, "RunPod Monitor")
        
        print(f"{Fore.GREEN}Successfully removed RunPod Monitor from startup!{Style.RESET_ALL}")
        
    except WindowsError as e:
        if e.winerror == 2:  # Value not found
            print(f"{Fore.YELLOW}RunPod Monitor was not in startup.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Error removing from startup: {e}{Style.RESET_ALL}")
            return False
    except Exception as e:
        print(f"{Fore.RED}Error removing from startup: {e}{Style.RESET_ALL}")
        return False
    
    return True

if __name__ == "__main__":
    remove_from_startup() 