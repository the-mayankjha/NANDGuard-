import subprocess
import re
import json
import os
import platform

def parse_smart_output(device_path, dev_type=None):
    """Parses smartctl -a output OR native C bridge output into metrics."""
    # 1. Try Native C Bridge on macOS
    if platform.system() == "Darwin":
        native_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "native", "mac_nvme")
        if os.path.exists(native_path):
            try:
                # App is elevated at main.py, no need for internal sudo
                res = subprocess.run([native_path], capture_output=True, text=True)
                if res.returncode == 0:
                    metrics = json.loads(res.stdout)
                    if "error" not in metrics:
                        # Map native names to project standardized names
                        # (e.g., mac_nvme outputs "Temperature", we use "Temperature")
                        metrics['Source'] = "Native C"
                        # Ensure all expected keys exist (dummy values for missing ones)
                        metrics.setdefault('Wear_Leveling_Count', metrics.get('Percentage_Used', 0))
                        metrics.setdefault('Media_Errors', 0)
                        metrics.setdefault('Host_Writes', metrics.get('Data_Units_Written', 0))
                        metrics.setdefault('Write_Amplification', 1.5)
                        metrics.setdefault('Bad_Block_Count', 0)
                        metrics.setdefault('Reallocated_Sector_Ct', 0)
                        return metrics, None
            except Exception:
                pass # Fallback to smartctl

    # 2. Existing smartctl Logic (Fallback)
    try:
        cmd = ['smartctl', '-a', device_path]
        if dev_type:
            cmd.extend(dev_type.split())
            
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Exit code 4 is common on Mac (checksum warning), but the data is usually valid
        if res.returncode not in [0, 4]:
            error_msg = res.stderr.strip() if res.stderr else f"Exit code {res.returncode}"
            if "Permission denied" in error_msg or "Must be run as root" in error_msg:
                error_alert = "PERMISSION DENIED: Run with sudo for live hardware access."
            else:
                error_alert = f"SMART ERROR: {error_msg}"
            return None, error_alert
            
        output = res.stdout
        metrics = {}
        
        # 1. Try SATA Patterns (Vendor Specific IDs)
        sata_patterns = {
            'Power_On_Hours': r'9 Power_On_Hours.*?(\d+)',
            'Wear_Leveling_Count': r'177 Wear_Leveling_Count.*?(\d+)',
            'Temperature': r'194 Temperature_Celsius.*?(\d+)',
            'Reallocated_Sector_Ct': r'5 Reallocated_Sector_Ct.*?(\d+)',
            'Media_Errors': r'187 Reported_Uncorrect.*?(\d+)',
            'Host_Writes': r'241 Total_LBAs_Written.*?(\d+)',
            'Bad_Block_Count': r'198 Offline_Uncorrectable.*?(\d+)'
        }
        
        # 2. Try NVMe Patterns (Standardized Text)
        nvme_patterns = {
            'Power_On_Hours': r'Power On Hours:.*?([\d,]+)',
            'Wear_Leveling_Count': r'Percentage Used:.*?(\d+)%', 
            'Temperature': r'Temperature:.*?(\d+)\s+Celsius',
            'Media_Errors': r'Media and Data Integrity Errors:.*?([\d,]+)',
            'Host_Writes': r'Data Units Written:.*?([\d,]+)',
            'Critical_Warning': r'Critical Warning:.*?0x(\d+)'
        }
        
        is_nvme = "NVMe" in output
        
        if is_nvme:
            for key, pattern in nvme_patterns.items():
                match = re.search(pattern, output)
                if match:
                    val = match.group(1).replace(',', '')
                    metrics[key] = int(val)
                else:
                    metrics[key] = 0
            metrics.setdefault('Reallocated_Sector_Ct', 0)
            metrics.setdefault('Bad_Block_Count', 0)
        else:
            for key, pattern in sata_patterns.items():
                match = re.search(pattern, output)
                metrics[key] = int(match.group(1)) if match else 0
        
        metrics['Write_Amplification'] = 1.5 
        metrics['Source'] = "smartctl"
        return metrics, None
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    # Test with a dummy device path or real one if you have it
    print(parse_smart_output('/dev/disk0'))
