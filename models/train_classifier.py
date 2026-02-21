import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

def train_classifier_model():
    data_path = 'smart_storage_monitor/data/simulated_smart_dataset.csv'
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
    y = df['health_status']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    print("Health Classifier Report:")
    print(classification_report(y_test, predictions))
    
    model_path = 'smart_storage_monitor/models/classifier_model.pkl'
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train_classifier_model()
