import pandas as pd
import numpy as np

def engineer_features(raw_metrics):
    """
    Transforms raw SMART metrics into features suitable for the ML models.
    Expects a dictionary of raw metrics.
    """
    # In a real system, we might have history to calculate rolling means.
    # For a snapshot inference, we'll return the normalized values.
    
    # Required features for the models:
    # ['Power_On_Hours', 'Wear_Leveling_Count', 'Temperature', 
    #  'Reallocated_Sector_Ct', 'Media_Errors', 'Host_Writes', 
    #  'Write_Amplification', 'Bad_Block_Count']
    
    feature_list = [
        'Power_On_Hours', 'Wear_Leveling_Count', 'Temperature', 
        'Reallocated_Sector_Ct', 'Media_Errors', 'Host_Writes', 
        'Write_Amplification', 'Bad_Block_Count'
    ]
    
    features = {}
    for f in feature_list:
        features[f] = raw_metrics.get(f, 0)
    
    # Normalize or scale if necessary (though RF/XGB are robust)
    # We'll return a DataFrame for easy ingestion by scikit-learn
    return pd.DataFrame([features])

if __name__ == "__main__":
    dummy_metrics = {
        'Power_On_Hours': 1000,
        'Wear_Leveling_Count': 5,
        'Temperature': 35,
        'Reallocated_Sector_Ct': 0,
        'Media_Errors': 0,
        'Host_Writes': 5000,
        'Write_Amplification': 1.5,
        'Bad_Block_Count': 0
    }
    print(engineer_features(dummy_metrics))
