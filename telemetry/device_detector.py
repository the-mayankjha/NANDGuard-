import psutil
import subprocess
import shutil
import platform
import re

import platform

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
            if 'disk' in device_path:
                base_device = device_path.split('s')[0] if 's' in device_path else device_path
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
        if shutil.which('smartctl'):
            try:
                # On Windows, smartctl C: works. On Unix, /dev/diskN works.
                res = subprocess.run(['smartctl', '-i', base_device], capture_output=True, text=True)
                if "SMART support is: Enabled" in res.stdout:
                    has_smart = True
            except Exception:
                pass
        
        devices.append({
            'path': base_device,
            'mountpoint': p.mountpoint,
            'fstype': p.fstype,
            'has_smart': has_smart
        })
            
    return devices

if __name__ == "__main__":
    found = detect_devices()
    print(f"Detected {len(found)} devices:")
    for d in found:
        print(f"- {d['path']} (SMART: {d['has_smart']})")
