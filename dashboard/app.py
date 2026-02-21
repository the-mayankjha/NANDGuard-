try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False

import threading
import time
import os
import joblib
import sys
import argparse

# Import core modules
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from telemetry.device_detector import detect_devices
from telemetry.smart_reader import parse_smart_output
from telemetry.performance_fallback import collect_performance_metrics
from core.feature_engineering import engineer_features
from core.health_score import calculate_health_score
from core.recommendation_engine import generate_recommendations

class FlashSentinelApp:
    def __init__(self, root):
        if not HAS_TKINTER:
            raise ImportError("Tkinter not available for GUI mode.")
        self.root = root
        # ... (rest of GUI initialization remains same, but I'll provide truncated version for brevity in this tool call)
        self.root.title("NANDGuard – Smart Storage Health Monitor")
        self.root.geometry("900x700")
        self.style = ttk.Style()
        self.models = self.load_models()
        self.monitoring = False
        self.device_list = []
        self.setup_ui()
        self.refresh_devices()

    def load_models(self):
        models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
        try:
            models = {
                'rul': joblib.load(os.path.join(models_dir, "rul_model.pkl")),
                'classifier': joblib.load(os.path.join(models_dir, "classifier_model.pkl")),
                'anomaly': joblib.load(os.path.join(models_dir, "anomaly_model.pkl"))
            }
            print(f"Successfully loaded models from {models_dir}")
            return models
        except Exception as e:
            print(f"CRITICAL: Failed to load models: {e}")
            return None

    def setup_ui(self):
        try:
            self.root.configure(bg="#222222")
            
            # Style Configuration
            style = ttk.Style()
            # 'clam' is often more consistent across Linux distributions
            try:
                if 'clam' in style.theme_names():
                    style.theme_use('clam')
                else:
                    style.theme_use('default')
            except Exception:
                pass

            font_main = ("Inter", 12) if "Inter" in self.root.tk.call("font", "families") else ("Helvetica", 12)
            font_header = ("Inter", 32, "bold") if "Inter" in self.root.tk.call("font", "families") else ("Helvetica", 32, "bold")
            
            style.configure("TFrame", background="#222222")
            style.configure("TLabel", background="#222222", foreground="white", font=font_main)
            style.configure("Header.TLabel", font=font_header)
            style.configure("Horizontal.TProgressbar", thickness=10, background="#007bff")
        except Exception as e:
            print(f"Warning: GUI Styling error: {e}")
        
        # Header / Dropdown
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", padx=40, pady=(20, 0))
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(header_frame, textvariable=self.device_var, state="readonly", width=40)
        self.device_combo.pack(side="right")
        self.device_combo.bind("<<ComboboxSelected>>", lambda e: self.update_dashboard())

        # Score Display
        self.score_label = ttk.Label(self.root, text="--%", font=("Inter", 48, "bold"), foreground="white")
        self.score_label.pack(pady=(40, 10))
        
        # Progress Bar
        self.score_bar = ttk.Progressbar(self.root, length=400, mode='determinate', style="Horizontal.TProgressbar")
        self.score_bar.pack(pady=10)

        # Recommendations Box
        self.recs_frame = tk.Frame(self.root, bg="#1a1a1a", bd=1, relief="flat")
        self.recs_frame.pack(fill="x", padx=40, pady=10)
        
        self.recs_text = tk.Text(self.recs_frame, bg="#1a1a1a", fg="white", font=("Inter", 11), 
                                relief="flat", borderwidth=0, padx=20, pady=20, height=6)
        self.recs_text.pack(fill="x")

        # Stats Grid
        stats_frame = ttk.Frame(self.root)
        stats_frame.pack(pady=20)
        
        self.risk_label = ttk.Label(stats_frame, text="Risk Level: --")
        self.risk_label.grid(row=0, column=0, pady=5)
        
        self.rul_label = ttk.Label(stats_frame, text="RUL: --")
        self.rul_label.grid(row=1, column=0, pady=5)
        
        self.status_label = ttk.Label(stats_frame, text="Status: --")
        self.status_label.grid(row=2, column=0, pady=5)
        
        self.anomaly_label = ttk.Label(stats_frame, text="Anomaly: --")
        self.anomaly_label.grid(row=3, column=0, pady=5)
        
        self.source_label = ttk.Label(stats_frame, text="Source: --", font=("Inter", 10, "bold"))
        self.source_label.grid(row=4, column=0, pady=5)

        self.error_log_label = ttk.Label(self.root, text="", font=("Inter", 9, "italic"), foreground="#ff4444")
        self.error_log_label.pack(pady=5)
        
        self.last_update_label = ttk.Label(stats_frame, text="Update: --", font=("Inter", 10, "italic"), foreground="#888888")
        self.last_update_label.grid(row=5, column=0, pady=10)

        # Start continuous monitoring thread
        self.monitoring = True
        threading.Thread(target=self.monitor_loop, daemon=True).start()

    def monitor_loop(self):
        while self.monitoring:
            self.root.after(0, self.update_dashboard)
            time.sleep(30) # Refresh every 30s

    def refresh_devices(self):
        devices = detect_devices()
        self.device_list = devices
        self.device_combo['values'] = [f"{d['path']} ({d['mountpoint']})" for d in devices]
        if devices:
            self.device_combo.current(0)
            self.update_dashboard()

    def update_dashboard(self):
        idx = self.device_combo.current()
        if idx < 0: return
        device = self.device_list[idx]
        
        metrics = None
        error_msg = None
        source_text = "SIMULATED (Built-in)"
        source_color = "#ffaa00"

        if device['has_smart']:
            metrics, error_msg = parse_smart_output(device['path'])
            if metrics:
                source_text = "LIVE (Hardware)"
                source_color = "#00ff00"
                self.error_log_label.config(text="")
            else:
                self.error_log_label.config(text=f"LOG: {error_msg}")
        else:
            self.error_log_label.config(text="LOG: Device lacks SMART support. Using synthetic simulator.")

        if not metrics:
            metrics = self.get_dummy_metrics()
        
        if not self.models: return
        
        results = self.get_results(metrics)
        
        # Update Health Score & Bar
        self.score_label.config(text=f"{results['health']['score']}%")
        self.score_bar['value'] = results['health']['score']
        
        # Update Info Labels
        self.risk_label.config(text=f"Risk Level: {results['health']['risk_level']}")
        self.rul_label.config(text=f"RUL: {int(results['health']['estimated_days'])} days")
        self.status_label.config(text=f"Status: {results['status']}")
        self.anomaly_label.config(text=f"Anomaly: {'DETECTED' if results['anomaly'] == -1 else 'No'}")
        self.source_label.config(text=f"Source: {source_text}", foreground=source_color)
        self.last_update_label.config(text=f"Update: {time.strftime('%H:%M:%S')}")
        
        # Update Recommendations
        self.recs_text.config(state="normal")
        self.recs_text.delete(1.0, tk.END)
        for r in results['recs']: 
            self.recs_text.insert(tk.END, f"• {r}\n")
        self.recs_text.config(state="disabled")

    def get_dummy_metrics(self):
        return {'Power_On_Hours': 5000, 'Wear_Leveling_Count': 20, 'Temperature': 40, 'Reallocated_Sector_Ct': 0, 'Media_Errors': 0, 'Host_Writes': 10000, 'Write_Amplification': 1.5, 'Bad_Block_Count': 0}

    def get_results(self, metrics):
        features = engineer_features(metrics)
        rul_pred = self.models['rul'].predict(features)[0]
        status_pred = self.models['classifier'].predict(features)[0]
        anomaly_pred = self.models['anomaly'].predict(features)[0]
        probas = self.models['classifier'].predict_proba(features)[0]
        classes = self.models['classifier'].classes_
        failure_prob = sum(probas[i] for i, c in enumerate(classes) if c in ['Critical', 'Degrading'])
        health = calculate_health_score(rul_pred, failure_prob, metrics.get('Wear_Leveling_Count', 0), anomaly_pred)
        recs = generate_recommendations(metrics, health)
        return {'health': health, 'status': status_pred, 'anomaly': anomaly_pred, 'recs': recs}

def run_cli_mode():
    print("\n--- NANDGuard (CLI Mode) ---")
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    try:
        models = {
            'rul': joblib.load(os.path.join(models_dir, "rul_model.pkl")),
            'classifier': joblib.load(os.path.join(models_dir, "classifier_model.pkl")),
            'anomaly': joblib.load(os.path.join(models_dir, "anomaly_model.pkl"))
        }
    except Exception as e:
        print(f"Error loading models for CLI: {e}")
        return

    devices = detect_devices()
    if not devices:
        print("No devices detected.")
        return

    for d in devices:
        print(f"\nAnalyzing: {d['path']} ({d['mountpoint']})")
        metrics = parse_smart_output(d['path']) if d['has_smart'] else {'Power_On_Hours': 5000, 'Wear_Leveling_Count': 20, 'Temperature': 40, 'Reallocated_Sector_Ct': 0, 'Media_Errors': 0, 'Host_Writes': 10000, 'Write_Amplification': 1.5, 'Bad_Block_Count': 0}
        
        features = engineer_features(metrics)
        rul_pred = models['rul'].predict(features)[0]
        status_pred = models['classifier'].predict(features)[0]
        anomaly_pred = models['anomaly'].predict(features)[0]
        
        probas = models['classifier'].predict_proba(features)[0]
        classes = models['classifier'].classes_
        failure_prob = sum(probas[i] for i, c in enumerate(classes) if c in ['Critical', 'Degrading'])
        
        health = calculate_health_score(rul_pred, failure_prob, metrics.get('Wear_Leveling_Count', 0), anomaly_pred)
        recs = generate_recommendations(metrics, health)
        
        print(f"Health Score: {health['score']}% ({health['risk_level']})")
        print(f"Est. Life: {health['estimated_days']} days")
        print(f"Status: {status_pred} | Anomaly: {'DETECTED' if anomaly_pred == -1 else 'No'}")
        print("Recommendations:")
        for r in recs: print(f" - {r}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli or not HAS_TKINTER:
        if not HAS_TKINTER:
            print("Tkinter not found. Falling back to CLI mode...")
        run_cli_mode()
    else:
        root = tk.Tk()
        app = FlashSentinelApp(root)
        root.mainloop()
