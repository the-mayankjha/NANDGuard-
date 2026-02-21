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

    # 2. Secondary discovery (psutil) for devices not found by scan (e.g. ones that don't support smartctl well)
    try:
        partitions = psutil.disk_partitions()
        for p in partitions:
            if not p.device or p.device in seen_paths:
                continue
            
            # Basic validation to avoid virtual disks
            if 'loop' in p.device or 'ram' in p.device:
                continue
                
            devices.append({
                'path': p.device,
                'dev_type': "",
                'model': "Generic Disk",
                'has_smart': False,
                'smart_error': "Not found in smartctl scan",
                'mountpoint': p.mountpoint
            })
    except Exception:
        pass
            
    return devices

if __name__ == "__main__":
    found = detect_devices()
    print(f"Detected {len(found)} devices:")
    for d in found:
        print(f"- {d['path']} (SMART: {d['has_smart']})")
