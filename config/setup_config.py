#!/usr/bin/env python3
import os
import json
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def create_default_config():
    """Create default config file if it doesn't exist."""
    if not os.path.exists('config.json'):
        default_config = {
            "check_interval_seconds": 300,
            "notification_threshold_hours": 1,
            "shutdown_threshold_hours": 3,
            "notification_cooldown_seconds": 3600
        }
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=4)

def get_user_input(prompt, default_value, value_type=float):
    """Get user input with a default value.
    Press Enter to use default, or enter a number for custom value."""
    while True:
        user_input = input(f"{Fore.CYAN}{prompt} {Fore.GREEN}[{default_value}]{Style.RESET_ALL}: ").strip()
        
        if not user_input:  # User pressed Enter
            return default_value
            
        try:
            return value_type(user_input)
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter a {value_type.__name__} value or press Enter for default.{Style.RESET_ALL}")

def main():
    """Setup configuration file."""
    # Get absolute path to data directory from script location
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(script_dir, 'data', 'config.json')
    
    print(f"\n{Fore.YELLOW}RunPod Monitor Configuration Setup{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}Press Enter to use default values, or enter a number to set custom value{Style.RESET_ALL}")
    time.sleep(0.5)
    
    # Default values
    defaults = {
        'check_interval_seconds': 300,  # 5 minutes
        'notification_threshold_minutes': 60,  # 1 hour
        'notification_cooldown_minutes': 60,  # Changed from seconds to minutes
        'shutdown_threshold_hours': 3  # 3 hours
    }
    
    config = {}
    
    print(f"\n{Fore.MAGENTA}Setting up monitoring intervals:{Style.RESET_ALL}")
    config['check_interval_seconds'] = get_user_input(
        "Check interval in seconds",
        defaults['check_interval_seconds'],
        int
    )
    
    print(f"\n{Fore.MAGENTA}Setting up notifications:{Style.RESET_ALL}")
    config['notification_threshold_minutes'] = get_user_input(
        "Notification threshold in minutes",
        defaults['notification_threshold_minutes'],
        int
    )
    
    config['notification_cooldown_minutes'] = get_user_input(
        "Notification cooldown in minutes",
        defaults['notification_cooldown_minutes'],
        int
    )
    
    print(f"\n{Fore.MAGENTA}Setting up auto-shutdown:{Style.RESET_ALL}")
    config['shutdown_threshold_hours'] = get_user_input(
        "Shutdown threshold in hours",
        defaults['shutdown_threshold_hours']
    )
    
    # Save configuration using absolute path
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)
    
    print(f"\n{Fore.GREEN}Configuration saved to config.json{Style.RESET_ALL}")
    print(f"{Fore.CYAN}You can edit these values later by modifying config.json directly{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 