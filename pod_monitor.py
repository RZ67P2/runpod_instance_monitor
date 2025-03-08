#!/usr/bin/env python3
import json
import subprocess
import time
from datetime import datetime, timedelta
from win10toast import ToastNotifier
from utils.runpod_pricing import fetch_runpod_pricing
import logging
import os
import sys
from colorama import init, Fore, Style

# Initialize colorama with autoreset=True to handle resets automatically
init(autoreset=True)

def load_config():
    """Load configuration from config.json or run setup if not found."""
    config_path = os.path.join('data', 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config file not found. Running initial setup...")
        try:
            from config import setup_config  # Updated import path
            setup_config.main()
            # After setup, try loading config again
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"{Fore.RED}Error during setup: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please run config/setup_config.py manually to configure the monitor.{Style.RESET_ALL}")
            sys.exit(1)

def parse_pod_output(output):
    """Parse runpodctl pod list output."""
    pods = []
    lines = output.strip().split('\n')
    
    if len(lines) <= 1:
        return []
        
    try:
        # First find the header positions
        header = lines[0].strip()
        id_pos = header.find('ID')
        name_pos = header.find('NAME')
        gpu_pos = header.find('GPU')
        image_pos = header.find('IMAGE')
        status_pos = header.find('STATUS')
        
        for line in lines[1:]:
            if not line.strip():
                continue
            
            # Get each field and clean it thoroughly
            pod_id = line[id_pos:name_pos].strip()
            gpu_info = line[gpu_pos:image_pos].strip()
            # Status might be at the very end
            status = line[status_pos:].strip()
            
            # Clean up GPU info by removing excessive whitespace
            gpu_info = ' '.join(gpu_info.split())
            
            # Handle GPU info (e.g., "1 RTX A4000")
            gpu_parts = gpu_info.split()
            if len(gpu_parts) >= 2 and gpu_parts[0].isdigit():
                gpu = ' '.join(gpu_parts[1:])  # Remove quantity prefix
                quantity = int(gpu_parts[0])
            else:
                gpu = gpu_info
                quantity = 1
            
            pod = {
                'id': pod_id,
                'gpu': gpu.strip(),  # Extra strip to be safe
                'status': status.strip(),  # Extra strip to be safe
                'runtime': '0h',
                'quantity': quantity
            }
            pods.append(pod)
            
    except Exception as e:
        logging.error(f"Error parsing pod output: {e}")
        return []
    
    return pods

def parse_runtime(runtime_str):
    """Convert runtime string (e.g., '2h', '5d') to hours."""
    if not runtime_str:
        return 0
    
    try:
        value = float(runtime_str[:-1])
        unit = runtime_str[-1].lower()
        
        if unit == 'h':
            return value
        elif unit == 'd':
            return value * 24
        elif unit == 'm':
            return value / 60
        else:
            return 0
    except:
        return 0

def get_pod_status():
    """Get status of all pods using runpodctl."""
    try:
        cmd = 'runpodctl.exe' if os.name == 'nt' else 'runpodctl'
        result = subprocess.run([cmd, 'get', 'pod'],
                              capture_output=True, text=True)
        
        logging.debug(f"runpodctl return code: {result.returncode}")
        logging.debug(f"runpodctl stdout: {result.stdout}")
        logging.debug(f"runpodctl stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"runpodctl error: {result.stderr}")
            
        if not result.stdout.strip():
            logging.warning("runpodctl returned empty output")
            return []
            
        return parse_pod_output(result.stdout)
    except FileNotFoundError as e:
        print("\nError: runpodctl not found. Please install it first.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Error getting pod status: {e}")
        return []

def calculate_cost(pod, pricing, runtime_hours):
    """Calculate cost for a pod based on its GPU and runtime."""
    gpu_type = pod['gpu']
    quantity = pod.get('quantity', 1)  # Get GPU quantity, default to 1
    hourly_rate = pricing['gpus'].get(gpu_type, 0)
    return hourly_rate * runtime_hours * quantity  # Multiply by quantity

def notify(title, message):
    """Send Windows notification."""
    try:
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=10)
    except Exception as e:
        print(f"Error sending notification: {e}")

def terminate_pod(pod_id):
    """Terminate a pod using runpodctl."""
    try:
        result = subprocess.run(['runpodctl', 'remove', 'pod', pod_id],  # Changed to 'remove pod'
                              capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"runpodctl error: {result.stderr}")
        logging.info(f"Successfully terminated pod {pod_id}")
        return True
    except Exception as e:
        logging.error(f"Error terminating pod {pod_id}: {e}")
        print(f"Error terminating pod {pod_id}: {e}")
        return False

def load_history():
    """Load pod history from file."""
    history_path = os.path.join('data', 'pod_history.json')
    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
            if 'pods' not in history:  # Ensure the structure exists
                history['pods'] = {}
            return history
    except FileNotFoundError:
        history = {'pods': {}}  # Create initial structure
        save_history(history)  # Create the file
        return history
    except json.JSONDecodeError:  # Handle corrupted file
        print("Warning: History file corrupted, creating new one")
        history = {'pods': {}}
        save_history(history)
        return history

def save_history(history):
    """Save pod history to file."""
    history_path = os.path.join('data', 'pod_history.json')
    with open(history_path, 'w') as f:
        json.dump(history, f, indent=4)

def update_pod_history(pod, runtime_hours, cost, history):
    """Update history for a pod."""
    if not isinstance(history, dict):
        history = {}
    if 'pods' not in history:
        history['pods'] = {}
        
    current_time = datetime.now()
    pod_id = pod['id']
    
    # Initialize pod history if it doesn't exist
    if pod_id not in history['pods']:
        history['pods'][pod_id] = {
            'gpu': pod['gpu'],
            'first_seen': current_time.isoformat(),
            'start_time': current_time.isoformat(),
            'last_seen': current_time.isoformat(),
            'total_runtime': 0,
            'total_cost': 0,
            'status': pod['status']
        }
        return  # Exit early for new pods
    
    # Update existing pod
    pod_history = history['pods'][pod_id]
    
    # Handle status changes
    if pod['status'] != pod_history.get('status'):
        if pod['status'] == 'RUNNING':
            # Only update start time if transitioning to RUNNING
            pod_history['start_time'] = current_time.isoformat()
            pod_history['total_runtime'] = 0
            pod_history['total_cost'] = 0
        pod_history['status'] = pod['status']
    
    # Update runtime and cost for running pods
    if pod['status'] == 'RUNNING':
        pod_history['total_runtime'] = runtime_hours
        pod_history['total_cost'] = cost
    
    # Always update last seen
    pod_history['last_seen'] = current_time.isoformat()

def setup_logging():
    """Setup logging configuration."""
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(
        filename=f'logs/pod_monitor_{datetime.now().strftime("%Y%m%d")}.log',
        level=logging.DEBUG,  # Changed to DEBUG
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def check_long_term_exited(pods, history, last_reminder):
    """Check for pods that have been in EXITED state for a long time."""
    if not pods:  # Skip if no pods
        return
        
    current_time = datetime.now()
    one_day = timedelta(days=1)
    
    # Ensure history structure exists
    if 'pods' not in history:
        history['pods'] = {}
    
    for pod in pods:
        if pod['status'] == 'EXITED':
            pod_id = pod['id']
            
            # Initialize pod history if needed
            if pod_id not in history['pods']:
                history['pods'][pod_id] = {
                    'gpu': pod['gpu'],
                    'first_seen': current_time.isoformat(),
                    'last_seen': current_time.isoformat(),
                    'total_runtime': 0,
                    'total_cost': 0
                }
            
            pod_history = history['pods'][pod_id]
            last_seen = datetime.fromisoformat(pod_history.get('last_seen', current_time.isoformat()))
            days_exited = (current_time - last_seen).days
            
            if (days_exited >= 1 and
                (pod_id not in last_reminder or 
                 current_time - last_reminder[pod_id] >= one_day)):
                
                notify("Exited Pod Reminder", 
                       f"Pod {pod_id} has been in EXITED state for "
                       f"{days_exited} {'day' if days_exited == 1 else 'days'}\n"
                       f"Consider cleaning up to avoid storage costs.")
                last_reminder[pod_id] = current_time
                logging.info(f"Sent daily reminder for exited pod {pod_id}")

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

def main():
    ensure_directories()  # Create directories at startup
    print(f"{Fore.CYAN}RunPod Monitor started. Press Ctrl+C to stop.{Style.RESET_ALL}")
    setup_logging()
    
    try:
        config = load_config()
        print(f"\n{Fore.YELLOW}Current configuration:{Style.RESET_ALL}")
        print(f"  Check interval: {config['check_interval_seconds']} seconds")
        print(f"  Notification threshold: {config['notification_threshold_minutes']} minutes")
        print(f"  Notification cooldown: {config['notification_cooldown_minutes']} minutes")
        print(f"  Shutdown threshold: {config['shutdown_threshold_hours']} hours")
        
        # Add longer pause between config and pricing
        time.sleep(1.5)  # 1.5 second pause
        
        # Get pricing info (this will show colored output from runpod_pricing.py)
        pricing = fetch_runpod_pricing()
        
        get_pod_status()  # Initial test
    except Exception as e:
        print(f"{Fore.RED}Startup error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    last_notification = {}
    last_reminder = {}
    history = load_history()
    
    # Ensure history has the right structure
    if not isinstance(history, dict):
        history = {}
    if 'pods' not in history:
        history['pods'] = {}
    
    logging.info("RunPod Monitor started")
    
    while True:
        try:
            current_time = datetime.now()
            pods = get_pod_status()
            
            # Re-initialize colorama before each status update
            init()
            
            status_msg = f"\n{Fore.CYAN}Status check at {current_time.strftime('%Y-%m-%d %H:%M:%S')}:{Style.RESET_ALL}"
            print(status_msg)
            logging.info(status_msg)
            
            active_pods = [p for p in pods if p['status'] == 'RUNNING']
            exited_pods = [p for p in pods if p['status'] == 'EXITED']
            
            if not pods:
                print("No pods found.")
                time.sleep(config['check_interval_seconds'])
                continue
            
            if active_pods:
                print("\nACTIVE PODS:")
                for pod in active_pods:
                    pod_id = pod['id']
                    
                    # First update history
                    update_pod_history(pod, 0, 0, history)
                    pod_history = history['pods'][pod_id]
                    
                    # Now calculate runtime
                    start_time = datetime.fromisoformat(pod_history['start_time'])
                    runtime_hours = (current_time - start_time).total_seconds() / 3600
                    
                    # Calculate cost
                    cost = calculate_cost(pod, pricing, runtime_hours)
                    
                    # Update history with final values
                    update_pod_history(pod, runtime_hours, cost, history)
                    
                    # Display info
                    print(f"Pod {pod['id']} ({pod['gpu']}):")
                    print(f"  Running for: {runtime_hours:.1f} hours")
                    print(f"  Cost so far: ${cost:.2f} "
                          f"(${pricing['gpus'].get(pod['gpu'], 0):.2f}/hour)")
                    
                    # Check if notification needed
                    if (runtime_hours >= config['notification_threshold_minutes'] / 60 and
                        (pod['id'] not in last_notification or 
                         (current_time - last_notification[pod['id']]).total_seconds() 
                         >= config['notification_cooldown_minutes'] * 60)):  # Convert minutes to seconds
                        
                        notify("Long-running Pod Alert", 
                               f"Pod {pod['id']} has been running for {runtime_hours:.1f} hours\n"
                               f"Cost so far: ${cost:.2f}")
                        last_notification[pod['id']] = current_time
                    
                    # Check if shutdown needed
                    if runtime_hours >= config['shutdown_threshold_hours']:
                        print(f"  WARNING: Pod exceeded shutdown threshold!")
                        if terminate_pod(pod['id']):
                            notify("Pod Terminated", 
                                  f"Pod {pod['id']} was terminated after {runtime_hours:.1f} hours\n"
                                  f"Total cost: ${cost:.2f}")
            
            if exited_pods:
                print("\nEXITED PODS:")
                for pod in exited_pods:
                    pod_id = pod['id']
                    if pod_id not in history['pods']:
                        history['pods'][pod_id] = {
                            'gpu': pod['gpu'],
                            'first_seen': current_time.isoformat(),
                            'status': 'EXITED'
                        }
                    
                    print(f"Pod {pod_id} ({pod['gpu']}):")
                    print(f"  Status: EXITED")
                    print(f"  Storage costs: ${pricing['storage']['idle']:.2f}/GB/Month (idle pod rate)")
                    print("  Note: Check pod storage size for actual costs")
                
                # Add daily reminder checks
                check_long_term_exited(exited_pods, history, last_reminder)
            
            # Save updated history
            save_history(history)
            
            time.sleep(config['check_interval_seconds'])
            
        except KeyboardInterrupt:
            msg = "\nMonitor stopped by user."
            print(msg)
            logging.info(msg)
            break
        except Exception as e:
            msg = f"Critical error in main loop: {e}"
            print(msg)
            logging.error(msg)
            print("Monitor stopped due to critical error. Check the logs for details.")
            break

if __name__ == "__main__":
    main() 