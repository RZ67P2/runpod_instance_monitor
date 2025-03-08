# RunPod Monitor

A Python script to monitor RunPod instances, track costs, and automatically manage cloud GPU resources to prevent unnecessary expenses.

## 🎯 Purpose

When working with RunPod, especially if using mostly serverless workers, sometimes I spin up an on-demand pods for testing purposes and forget about them 😅 This script helps prevent incurring unnecessary costs by:

- Monitoring all your active and exited pods and their GPU types
- Tracking real-time costs using current RunPod pricing
- Sending notifications when pods have been running for a configurable amount of time
- Automatically terminating long-running active pods that exceed a specified runtime threshold
- Maintaining a cost history for better resource management
- Storage cost warning for exited pods
- Running automatically at system startup (optional)
- Interactive configuration for personalized settings

## 📦 Installation & Setup

### Prerequisites

- Windows OS (required for notifications)
- Python 3.6 or higher
- RunPod CLI (runpodctl)

First, install and configure the RunPod CLI:
> Note: This script has been tested with runpodctl v1.14.4. Other versions may work but are not guaranteed.
> Note: The `amd64` version works on both Intel and AMD 64-bit processors.

```bash
wget https://github.com/runpod/runpodctl/releases/download/v1.14.4/runpodctl-windows-amd64.exe -O runpodctl.exe
runpodctl config --apiKey your-api-key
```

> 📝 Get your API key from your RunPod account settings



### Quick Start
1. Clone this repository
```bash
git clone https://github.com/RZ67P2/runpod_instance_monitor.git
cd runpod_instance_monitor
```

2. Install required packages:
```bash
pip install -r requirements.txt
```
3. Run the monitor to create initial configuration:
```bash
python pod_monitor.py
```
4. (Optional) Set up automatic startup:
```bash
python config/setup_startup.py
```

### Troubleshooting

Common issues:
1. "runpodctl not found" - Ensure RunPod CLI is in your PATH or in the same directory as the script
2. "No module named win10toast" - Run `pip install -r requirements.txt`
3. "Permission denied" - Run with appropriate permissions for startup configuration

## 📊 Features

### Notifications
Windows notifications are sent when:
- Active pods exceed the notification threshold
- Pods exceed the shutdown threshold
- Pods are automatically terminated (with final runtime and cost)
- Exited pods remain unused (daily reminders)

### Data Storage
- Logs: `logs/pod_monitor_YYYYMMDD.log`
- History: `data/pod_history.json`
- All directories are created automatically

### Pricing Notes
Prices shown are estimated community cloud prices and may vary based on:
- Secure cloud vs Community cloud
- Datacenter location
- Current market conditions
- Special promotions or discounts

Always verify current prices at https://www.runpod.io/gpu-instance/pricing

## ⚙️ Configuration

The script uses these configurable settings:
- Check interval: 300 seconds (5 minutes)
- Notification threshold: 60 minutes
- Notification cooldown: 60 minutes
- Shutdown threshold: 3 hours

You can modify these settings by:
1. Running the configuration script:
```bash
python config/setup_config.py
```
2. Or directly editing `data/config.json`

## 🤝 Contributing

Feel free to open issues or submit pull requests if you have suggestions for improvements!

## 📜 License

MIT License





