import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
import os

def train_anomaly_model():
    data_path = 'data/simulated_smart_dataset.csv'
    if not os.path.exists(data_path):
        print("Dataset not found. Run synthetic_generator.py first.")
        return

    df = pd.read_csv(data_path)
    
    features = [
        'Power_On_Hours', 'Wear_Leveling_Count', 'Temperature', 
        'Reallocated_Sector_Ct', 'Media_Errors', 'Host_Writes', 
        'Write_Amplification', 'Bad_Block_Count'
    ]
    X = df[features]
    
    # IsolationForest is unsupervised
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X)
    
    model_path = 'models/anomaly_model.pkl'
    joblib.dump(model, model_path)
    print(f"Anomaly detection model saved to {model_path}")

if __name__ == "__main__":
    train_anomaly_model()
