import pandas as pd
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import os

def train_rul_model():
    data_path = 'smart_storage_monitor/data/simulated_smart_dataset.csv'
    if not os.path.exists(data_path):
        print("Dataset not found. Run synthetic_generator.py first.")
        return

    df = pd.read_csv(data_path)
    
    # Features for RUL
    features = [
        'Power_On_Hours', 'Wear_Leveling_Count', 'Temperature', 
        'Reallocated_Sector_Ct', 'Media_Errors', 'Host_Writes', 
        'Write_Amplification', 'Bad_Block_Count'
    ]
    X = df[features]
    y = df['days_to_failure']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"RUL Model trained. MAE: {mae:.2f} days")
    
    model_path = 'smart_storage_monitor/models/rul_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_rul_model()
