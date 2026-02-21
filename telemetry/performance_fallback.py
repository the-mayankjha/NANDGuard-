import time
import os
import psutil

def collect_performance_metrics(device_path, mountpoint):
    """Collects behavioral metrics when SMART is unavailable."""
    metrics = {}
    
    try:
        # 1. Disk usage %
        usage = psutil.disk_usage(mountpoint)
        metrics['Disk_Usage_Percent'] = usage.percent
        
        # 2. Sequential Write Speed (Small test)
        test_file = os.path.join(mountpoint, '.flash_sentinel_test')
        data = b'0' * 1024 * 1024 * 10 # 10MB
        
        start_time = time.time()
        with open(test_file, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        end_time = time.time()
        
        write_speed = 10 / (end_time - start_time) # MB/s
        metrics['Sequential_Write_Speed'] = write_speed
        
        # 3. Random Read Speed (Simulated)
        start_time = time.time()
        with open(test_file, 'rb') as f:
            for _ in range(100):
                f.seek(int(time.time() * 1000) % (10 * 1024 * 1024))
                f.read(4096)
        end_time = time.time()
        
        read_speed = (100 * 4096 / 1024 / 1024) / (end_time - start_time) # MB/s
        metrics['Random_Read_Speed'] = read_speed
        
        # Cleanup
        os.remove(test_file)
        
        # 4. Latency (Approximate)
        metrics['IO_Latency'] = (end_time - start_time) / 100 # s
        
        # For fallback mode, we want to map these to SMART-like features or placeholders
        # since our ML model expects specific features.
        # We can use heuristics to map performance degradation to "virtual" SMART values.
        
        return metrics
    except Exception as e:
        print(f"Error collecting performance metrics: {e}")
        return None

if __name__ == "__main__":
    # Test on current directory
    print(collect_performance_metrics('/dev/disk1', '/'))
