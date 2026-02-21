def generate_recommendations(metrics, health_results):
    """Generates actionable insights based on health data."""
    recs = []
    
    score = health_results['score']
    risk = health_results['risk_level']
    
    if score < 30 or risk == "Critical":
        recs.append("CRITICAL: Immediate backup recommended. Device showing signs of imminent failure.")
        recs.append("Plan device replacement immediately.")
    elif score < 70:
        recs.append("Moderate wear detected. Ensure regular backups are active.")
        recs.append("Monitor write-intensive workloads.")
    
    # Specific metric alerts
    if metrics.get('Temperature', 0) > 60:
        recs.append("High Temperature: Improve airflow or reduce workload to prevent NAND throttling.")
    
    if metrics.get('Write_Amplification', 1.0) > 5.0:
        recs.append("High Write Amplification: Consider disabling unnecessary logging or indexing on this drive.")
        
    if metrics.get('Reallocated_Sector_Ct', 0) > 50:
        recs.append("Reallocated Sectors detected: Hardware-level degradation is progressing.")
 
    if not recs:
        recs.append("Device is healthy. No action required.")
        recs.append("Normal operating conditions.")
        
    return recs

if __name__ == "__main__":
    dummy_metrics = {'Temperature': 65, 'Reallocated_Sector_Ct': 100}
    dummy_health = {'score': 45, 'risk_level': 'Medium'}
    print(generate_recommendations(dummy_metrics, dummy_health))
