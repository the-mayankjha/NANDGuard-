import pandas as pd
import numpy as np
import os

def generate_synthetic_data(num_samples=6000, output_path='smart_storage_monitor/data/simulated_smart_dataset.csv'):
    np.random.seed(42)
    
    # Features
    # Power_On_Hours: 0 to 50,000
    # Wear_Leveling_Count: 0 to 100 (%)
    # Temperature: 25 to 75 (C)
    # Reallocated_Sector_Ct: 0 to 1000
    # Media_Errors: 0 to 500
    # Host_Writes: 0 to 1,000,000 (GB)
    # Write_Amplification: 1.0 to 10.0
    # Bad_Block_Count: 0 to 500
    
    data = []
    
    for i in range(num_samples):
        # Simulate lifespan progression
        # We'll create samples representing different stages of an SSD life
        life_stage = np.random.uniform(0, 1) # 0 = new, 1 = dead
        
        power_on_hours = int(life_stage * 50000 + np.random.normal(0, 1000))
        power_on_hours = max(0, power_on_hours)
        
        wear_leveling_count = int(life_stage * 100 + np.random.normal(0, 2))
        wear_leveling_count = max(0, min(100, wear_leveling_count))
        
        # Temperature fluctuates but might trend slightly higher with wear/usage
        temperature = 30 + (life_stage * 10) + np.random.normal(0, 5)
        
        # Reallocated sectors grow exponentially near end of life
        reallocated_sectors = int(np.exp(life_stage * 7) / 10 + np.random.normal(0, 10))
        reallocated_sectors = max(0, reallocated_sectors)
        
        media_errors = int(np.exp(life_stage * 6) / 20 + np.random.normal(0, 5))
        media_errors = max(0, media_errors)
        
        host_writes = int(life_stage * 500000 + np.random.normal(0, 10000))
        host_writes = max(0, host_writes)
        
        # Write amplification increases as drive fills or NAND degrades
        write_amplification = 1.2 + (life_stage * 2.5) + np.random.normal(0, 0.2)
        
        bad_block_count = int(np.exp(life_stage * 6.5) / 15 + np.random.normal(0, 5))
        bad_block_count = max(0, bad_block_count)
        
        # Labels
        # days_to_failure: roughly 3650 days (10 years) max
        days_to_failure = int((1 - life_stage) * 3650 + np.random.normal(0, 30))
        days_to_failure = max(0, days_to_failure)
        
        # health_status
        if life_stage < 0.6:
            health_status = 'Healthy'
        elif life_stage < 0.85:
            health_status = 'Degrading'
        else:
            health_status = 'Critical'
            
        data.append([
            power_on_hours, wear_leveling_count, temperature, 
            reallocated_sectors, media_errors, host_writes, 
            write_amplification, bad_block_count, 
            days_to_failure, health_status
        ])
    
    columns = [
        'Power_On_Hours', 'Wear_Leveling_Count', 'Temperature', 
        'Reallocated_Sector_Ct', 'Media_Errors', 'Host_Writes', 
        'Write_Amplification', 'Bad_Block_Count', 
        'days_to_failure', 'health_status'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {num_samples} samples at {output_path}")

if __name__ == "__main__":
    generate_synthetic_data()
