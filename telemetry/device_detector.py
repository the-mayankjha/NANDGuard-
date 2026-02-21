import platform
import psutil
import subprocess
import shutil
import re

def detect_devices():
    """Detects physical storage devices using smartctl --scan."""
    devices = []
    seen_paths = set()
    
    # 1. Primary discovery: smartctl --scan
    if shutil.which('smartctl'):
        try:
            res = subprocess.run(['smartctl', '--scan'], capture_output=True, text=True)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if line.startswith('#') or not line.strip():
                        continue
                    
                    # Line format: /dev/sda -d ata # ... or IOService:/... -d nvme
                    match = re.search(r'^(\S+)\s+(-d\s+\S+)', line)
                    if match:
                        path, dev_type = match.groups()
                        
                        # Fix: Split dev_type so it passes as separate args to subprocess
                        scan_cmd = ['smartctl', '-i', path] + dev_type.split()
                        res_i = subprocess.run(scan_cmd, capture_output=True, text=True)
                        
                        has_smart = False
                        smart_error = None
                        model = "Unknown Model"
                        
                        if res_i.returncode in [0, 4]: # 4 is often a checksum error but data is there
                            out = res_i.stdout.lower()
                            has_smart = True if ("smart support is:" in out or "apple ssd" in out or "nvme" in out or "ans2" in out) else False
                            
                            # Extract model
                            model_match = re.search(r'Model Number:\s+(.*)', res_i.stdout)
                            if not model_match:
                                model_match = re.search(r'Device Model:\s+(.*)', res_i.stdout)
                            if model_match:
                                model = model_match.group(1).strip()

                            # Try to find /dev/disk name for consolidation
                            dev_name_match = re.search(r'(/dev/disk\d+)', res_i.stdout)
                            if dev_name_match:
                                seen_paths.add(dev_name_match.group(1))
                        else:
                            smart_error = f"Probe failed (Code {res_i.returncode})"
                            
                        devices.append({
                            'path': path,
                            'dev_type': dev_type,
                            'model': model,
                            'has_smart': has_smart,
                            'smart_error': smart_error,
                            'mountpoint': '/' # Default to root for physical disks
                        })
                        seen_paths.add(path)
        except Exception as e:
            print(f"Error scanning devices: {e}")

    # 2. Secondary discovery (psutil)
    try:
        partitions = psutil.disk_partitions()
        for p in partitions:
            if not p.device:
                continue
                
            # Filter: Avoid virtual/ram disks
            if any(x in p.device.lower() for x in ['loop', 'ram', 'dmg', 'null']):
                continue
            
            # macOS specific: Filter out sub-partitions and consolidate to base disks
            # e.g. /dev/disk3s1 -> /dev/disk3
            clean_path = p.device
            if platform.system() == "Darwin" and "/dev/disk" in p.device:
                base_match = re.search(r'(/dev/disk\d+)', p.device)
                if base_match:
                    clean_path = base_match.group(1)
            
            if clean_path in seen_paths:
                continue
                
            devices.append({
                'path': clean_path,
                'dev_type': "",
                'model': "Generic Disk",
                'has_smart': False,
                'smart_error': "Not found in smartctl scan",
                'mountpoint': p.mountpoint
            })
            seen_paths.add(clean_path)
    except Exception:
        pass
            
    return devices

if __name__ == "__main__":
    found = detect_devices()
    print(f"Detected {len(found)} devices:")
    for d in found:
        print(f"- {d['path']} (SMART: {d['has_smart']})")
