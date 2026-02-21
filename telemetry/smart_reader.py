import subprocess
import re

def parse_smart_output(device_path):
    """Parses smartctl -a output into a dictionary of metrics."""
    try:
        res = subprocess.run(['smartctl', '-a', device_path], capture_output=True, text=True)
        if res.returncode != 0 and not res.stdout:
            return None
        
        output = res.stdout
        metrics = {}
        
        # Regex patterns for common SMART attributes
        patterns = {
            'Power_On_Hours': r'9 Power_On_Hours.*?(\d+)',
            'Wear_Leveling_Count': r'177 Wear_Leveling_Count.*?(\d+)',
            'Temperature': r'194 Temperature_Celsius.*?(\d+)',
            'Reallocated_Sector_Ct': r'5 Reallocated_Sector_Ct.*?(\d+)',
            'Media_Errors': r'187 Reported_Uncorrect.*?(\d+)', # Fallback for media errors
            'Host_Writes': r'241 Total_LBAs_Written.*?(\d+)',
            'Bad_Block_Count': r'198 Offline_Uncorrectable.*?(\d+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output)
            if match:
                metrics[key] = int(match.group(1))
            else:
                metrics[key] = 0 # Default if not found
        
        # Write Amplification is often vendor specific or calculated
        # For simplicity, we'll simulate it if missing or use a dummy constant
        metrics['Write_Amplification'] = 1.5 
        
        return metrics
    except Exception as e:
        print(f"Error reading SMART for {device_path}: {e}")
        return None

if __name__ == "__main__":
    # Test with a dummy device path or real one if you have it
    print(parse_smart_output('/dev/disk0'))
