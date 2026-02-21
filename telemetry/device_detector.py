import platform
import psutil
import subprocess
import shutil
import re

def detect_devices():
    """Detects connected storage devices and checks for SMART support."""
    devices = []
    partitions = psutil.disk_partitions()
    current_os = platform.system()
    
    seen_disks = set()
    
    for p in partitions:
        device_path = p.device
        if not device_path: continue
        
        base_device = device_path
        
        if current_os == "Darwin": # macOS
            if '/dev/disk' in device_path:
                # Correctly strip partition suffixes (e.g., /dev/disk3s1 -> /dev/disk3)
                # We look for 's' followed by digits at the end of the disk name
                base_device = re.sub(r's\d+.*', '', device_path)
        elif current_os == "Linux":
            # For Linux, we want e.g. /dev/sda instead of /dev/sda1
            if '/dev/sd' in device_path or '/dev/nvme' in device_path:
                # Remove partition number (e.g. /dev/sda1 -> /dev/sda, /dev/nvme0n1p1 -> /dev/nvme0n1)
                match = re.search(r'(/dev/(sd[a-z]|nvme[0-9]n[0-9]))', device_path)
                if match:
                    base_device = match.group(1)
        elif current_os == "Windows":
            # Windows is trickier for physical disk mapping. 
            # For the prototype, we can list logical drives and use smartctl on them (it often works)
            # or try to map to PhysicalDrive via wmic if we needed more precision.
            base_device = device_path.split(':')[0] + ":" # e.g. "C:"
            
        if base_device in seen_disks:
            continue
        seen_disks.add(base_device)
        
        has_smart = False
        smart_error = "smartmontools not installed"
        if shutil.which('smartctl'):
            try:
                # Try running smartctl -i to check for support
                res = subprocess.run(['smartctl', '-i', base_device], capture_output=True, text=True)
                if res.returncode == 0:
                    out = res.stdout.lower()
                    # Apple Silicon Macs often don't show "SMART support is: Enabled" 
                    # but they are definitely SMART capable if they are the internal SSD.
                    if "smart support is:" in out or "apple ssd" in out or "nvme" in out or "ans2" in out:
                        has_smart = True
                        smart_error = None
                    else:
                        smart_error = "Drive does not report SMART support in the expected format"
                else:
                    err = res.stderr.strip() or f"Code {res.returncode}"
                    if "Permission denied" in err or "root" in err.lower():
                        smart_error = "PERMISSION DENIED: Run as root/sudo"
                    else:
                        smart_error = f"Probe failed: {err}"
            except Exception as e:
                smart_error = f"Error: {str(e)}"
        
        devices.append({
            'path': base_device,
            'mountpoint': p.mountpoint,
            'fstype': p.fstype,
            'has_smart': has_smart,
            'smart_error': smart_error
        })
            
    return devices

if __name__ == "__main__":
    found = detect_devices()
    print(f"Detected {len(found)} devices:")
    for d in found:
        print(f"- {d['path']} (SMART: {d['has_smart']})")
