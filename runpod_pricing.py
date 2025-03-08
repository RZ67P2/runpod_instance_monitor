import time
from colorama import Fore, Style

def fetch_runpod_pricing():
    """Fetch current RunPod pricing from their website."""
    try:
        print(f"{Fore.CYAN}Downloading RunPod pricing information...{Style.RESET_ALL}")
        time.sleep(0.5)
        
        # ... pricing setup code ...
        
        print(f"\n{Fore.GREEN}Pricing information downloaded successfully!{Style.RESET_ALL}")
        time.sleep(0.5)
        
        print(f"\n{Fore.YELLOW}Current GPU Pricing (Community Cloud):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}====================================={Style.RESET_ALL}")
        time.sleep(0.3)
        
        # Show prices in a compact format
        sorted_gpus = sorted(pricing['gpus'].items())
        # Split into two columns
        for i in range(0, len(sorted_gpus), 2):
            left = f"{sorted_gpus[i][0]}: ${sorted_gpus[i][1]:.2f}/hr"
            # Check if there's a right column
            if i + 1 < len(sorted_gpus):
                right = f"{sorted_gpus[i+1][0]}: ${sorted_gpus[i+1][1]:.2f}/hr"
                print(f"  {Fore.WHITE}{left:<35} | {right}{Style.RESET_ALL}")
            else:
                print(f"  {Fore.WHITE}{left}{Style.RESET_ALL}")
            time.sleep(0.1)
        
        # ... rest of the function ...
    except Exception as e:
        print(f"{Fore.RED}Error fetching RunPod pricing: {e}{Style.RESET_ALL}")

fetch_runpod_pricing() 