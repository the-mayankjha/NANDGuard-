def calculate_health_score(rul_prediction, failure_prob, wear_percentage, anomaly_score):
    """
    Computes a health score from 0 to 100.
    rul_prediction: predicted days to failure
    failure_prob: probability of being in 'Critical' class
    wear_percentage: wear leveling count (0-100)
    anomaly_score: 1 for normal, -1 for anomaly (IsolationForest output)
    """
    
    # Normalize RUL: 3650 days (10 years) is 100%, 0 days is 0%
    norm_rul = min(100, (rul_prediction / 3650) * 100)
    
    # failure_prob is (1 - healthy_score), we want (1 - failure_prob)
    safety_score = (1 - failure_prob) * 100
    
    # wear_percentage: 0 is healthy, 100 is dead. We want (100 - wear)
    nand_vibrancy = 100 - wear_percentage
    
    # anomaly_score: 1 becomes 100, -1 becomes 0
    anomaly_vibrancy = 100 if anomaly_score == 1 else 0
    
    # Weighted Average
    # 0.4 * RUL + 0.3 * Safety + 0.2 * NAND + 0.1 * Anomaly
    final_score = (0.4 * norm_rul) + (0.3 * safety_score) + (0.2 * nand_vibrancy) + (0.1 * anomaly_vibrancy)
    
    risk_level = "Low"
    if final_score < 40:
        risk_level = "Critical"
    elif final_score < 75:
        risk_level = "Medium"
        
    return {
        'score': round(final_score, 1),
        'risk_level': risk_level,
        'estimated_days': int(rul_prediction)
    }

if __name__ == "__main__":
    print(calculate_health_score(2000, 0.1, 10, 1))
