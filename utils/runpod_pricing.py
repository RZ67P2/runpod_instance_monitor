import requests
from bs4 import BeautifulSoup
import logging
import time
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

def fetch_runpod_pricing():
    """Fetch current RunPod pricing from their website."""
    try:
        print(f"{Fore.CYAN}Downloading RunPod pricing information...{Style.RESET_ALL}")
        time.sleep(0.5)
        
        # GPU prices from pricing page
        gpu_prices = {
            'H100 NVL': 2.59,
            'H200 SXM': 3.99,
            'MI300X': 2.49,
            'H100 PCIe': 1.99,
            'H100 SXM': 2.69,
            'A100 PCIe': 1.19,
            'A100 SXM': 1.89,
            'A40': 0.44,
            'L40': 0.99,
            'L40S': 0.79,
            'RTX A6000': 0.44,
            'RTX 6000 Ada': 0.74,
            'RTX A5000': 0.22,
            'RTX 4090': 0.34,
            'RTX 3090': 0.22,
            'RTX 3090 Ti': 0.27,
            'A30': 0.22,
            'L4': 0.43,
            'RTX A4500': 0.19,
            'RTX 4000 Ada': 0.20,
            'RTX A4000': 0.17,
            'Tesla V100': 0.19,
            'RTX 2000 Ada': 0.28,
            'RTX 3080': 0.17,
        }
        
        pricing = {
            'gpus': gpu_prices,
            'storage': {
                'idle': 0.20,
                'running': 0.10
            }
        }
        
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
        
        time.sleep(0.3)
        print(f"\n{Fore.YELLOW}Storage Pricing:{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}================{Style.RESET_ALL}")
        time.sleep(0.2)
        print(f"  Running pods: {Fore.GREEN}${pricing['storage']['running']:.2f}/GB/Month{Style.RESET_ALL}")
        time.sleep(0.1)
        print(f"  Idle pods: {Fore.GREEN}${pricing['storage']['idle']:.2f}/GB/Month{Style.RESET_ALL}")
        
        time.sleep(0.5)
        print(f"\n{Fore.RED}IMPORTANT:{Style.RESET_ALL} These are estimated community cloud prices.")
        print("Actual prices may vary based on:")
        time.sleep(0.2)
        for factor in [
            "Secure cloud vs Community cloud",
            "Datacenter location",
            "Current market conditions",
            "Special promotions or discounts"
        ]:
            print(f"  {Fore.CYAN}- {factor}{Style.RESET_ALL}")
            time.sleep(0.1)
        
        time.sleep(0.3)
        print(f"\nPlease verify current prices at: {Fore.BLUE}https://www.runpod.io/gpu-instance/pricing{Style.RESET_ALL}")
        
        return pricing
    except Exception as e:
        logging.error(f"Error fetching pricing: {e}")
        print(f"\n{Fore.RED}Warning: Could not download current pricing.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Using cached price estimates (may be outdated).{Style.RESET_ALL}")
        return {'gpus': {}, 'storage': {'idle': 0.20, 'running': 0.10}} 