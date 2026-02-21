import joblib
import os
import sys
import time
from PyQt6.QtCore import QThread, pyqtSignal

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from telemetry.device_detector import detect_devices
from telemetry.smart_reader import parse_smart_output
from core.feature_engineering import engineer_features
from core.health_score import calculate_health_score
from core.recommendation_engine import generate_recommendations

class TelemetryWorker(QThread):
    """
    Worker thread that periodically polls storage devices for telemetry.
    Emits a signal when new health data is available.
    """
    health_data_ready = pyqtSignal(list)
    notification_triggered = pyqtSignal(str, str) # title, message
    error_occurred = pyqtSignal(str)

    def __init__(self, interval_seconds=300):
        super().__init__()
        self.interval = interval_seconds
        self._running = True
        self._last_notified_risk = {} # path: level
        self.models = self._load_models()

    def _load_models(self):
        models_dir = os.path.join(project_root, "models")
        try:
            return {
                'rul': joblib.load(os.path.join(models_dir, "rul_model.pkl")),
                'classifier': joblib.load(os.path.join(models_dir, "classifier_model.pkl")),
                'anomaly': joblib.load(os.path.join(models_dir, "anomaly_model.pkl"))
            }
        except Exception as e:
            print(f"Error loading models in worker: {e}")
            return None

    def run(self):
        while self._running:
            try:
                devices = detect_devices()
                results = []
                
                for dev in devices:
                    if dev['has_smart']:
                        metrics, err = parse_smart_output(dev['path'], dev['dev_type'])
                        if metrics:
                            # 1. Perform ML Inference if models are loaded
                            if self.models:
                                features = engineer_features(metrics)
                                rul = self.models['rul'].predict(features)[0]
                                status_pred = self.models['classifier'].predict(features)[0]
                                anomaly = self.models['anomaly'].predict(features)[0]
                                
                                # Probability for health score
                                probas = self.models['classifier'].predict_proba(features)[0]
                                classes = self.models['classifier'].classes_
                                fail_prob = sum(probas[i] for i, c in enumerate(classes) if c in ['Critical', 'Degrading'])
                            else:
                                # Fallback to dummy/conservative values if models missing
                                rul = 1000
                                status_pred = "Unknown"
                                anomaly = 1
                                fail_prob = 0.5

                            wear = metrics.get('Wear_Leveling_Count', 0)
                            health = calculate_health_score(rul, fail_prob, wear, anomaly)
                            recs = generate_recommendations(metrics, health)
                            
                            # Notification logic
                            risk = health['risk_level']
                            if risk != "Low":
                                if self._last_notified_risk.get(dev['path']) != risk:
                                    self.notification_triggered.emit(
                                        "NANDGuard+ Alert",
                                        f"{dev['model']} health status is {risk}. Backup recommended."
                                    )
                                    self._last_notified_risk[dev['path']] = risk
                            
                            dev_data = {
                                'path': dev['path'],
                                'model': dev['model'],
                                'metrics': metrics,
                                'health': health,
                                'status': status_pred,
                                'anomaly': anomaly,
                                'recommendations': recs,
                                'source': f"LIVE ({metrics.get('Source', 'Hardware')})"
                            }
                            results.append(dev_data)
                        elif err:
                            # If hardware access fails, we might still have basic info from detector
                            dev['smart_error'] = err
                            dev['source'] = "Fallback (System Logs)"
                            results.append(dev)
                    else:
                        dev['source'] = "Fallback (System Logs)"
                        results.append(dev)
                
                self.health_data_ready.emit(results)
                
            except Exception as e:
                self.error_occurred.emit(str(e))
            
            # Sleep in increments to allow for quick stop
            for _ in range(self.interval):
                if not self._running:
                    break
                time.sleep(1)

    def stop(self):
        self._running = False
        self.wait()
