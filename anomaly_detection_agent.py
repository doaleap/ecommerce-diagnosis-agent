
import numpy as np
import pandas as pd
import config
from scipy import stats

class AnomalyDetectionAgent:
    def __init__(self):
        self.threshold_3sigma = config.THRESHOLD_3SIGMA
        self.threshold_yoy = config.THRESHOLD_YOY
        self.threshold_qoq = config.THRESHOLD_QOQ
    
    def detect_3sigma(self, series):
        mean = series.mean()
        std = series.std()
        threshold_high = mean + self.threshold_3sigma * std
        threshold_low = mean - self.threshold_3sigma * std
        
        anomalies = []
        for idx, value in series.items():
            if value > threshold_high or value < threshold_low:
                anomalies.append({
                    "index": idx,
                    "value": value,
                    "mean": mean,
                    "std": std,
                    "threshold_high": threshold_high,
                    "threshold_low": threshold_low,
                    "type": "high" if value > threshold_high else "low"
                })
        
        return anomalies
    
    def detect_yoy(self, df, metric):
        anomalies = []
        df_sorted = df.sort_values("date")
        
        for i in range(7, len(df_sorted)):
            current = df_sorted.iloc[i]
            prev = df_sorted.iloc[i - 7]
            
            current_val = current[metric]
            prev_val = prev[metric]
            
            if prev_val == 0:
                continue
            
            change_rate = (current_val - prev_val) / prev_val
            
            if abs(change_rate) > self.threshold_yoy:
                anomalies.append({
                    "date": current["date"],
                    "current_value": current_val,
                    "prev_value": prev_val,
                    "change_rate": change_rate,
                    "type": "rise" if change_rate > 0 else "drop"
                })
        
        return anomalies
    
    def detect_qoq(self, df, metric):
        anomalies = []
        df_sorted = df.sort_values("date")
        
        for i in range(1, len(df_sorted)):
            current = df_sorted.iloc[i]
            prev = df_sorted.iloc[i - 1]
            
            current_val = current[metric]
            prev_val = prev[metric]
            
            if prev_val == 0:
                continue
            
            change_rate = (current_val - prev_val) / prev_val
            
            if abs(change_rate) > self.threshold_qoq:
                anomalies.append({
                    "date": current["date"],
                    "current_value": current_val,
                    "prev_value": prev_val,
                    "change_rate": change_rate,
                    "type": "rise" if change_rate > 0 else "drop"
                })
        
        return anomalies
    
    def detect_all(self, df, metrics=None):
        if metrics is None:
            metrics = config.METRICS
        
        results = {}
        
        for metric in metrics:
            results[metric] = {
                "3sigma": self.detect_3sigma(df[metric]),
                "yoy": self.detect_yoy(df, metric),
                "qoq": self.detect_qoq(df, metric)
            }
        
        return results
    
    def get_summary(self, detection_results):
        summary = []
        
        for metric, methods in detection_results.items():
            metric_anomalies = []
            
            for method, anomalies in methods.items():
                if anomalies:
                    metric_anomalies.append({
                        "method": method,
                        "count": len(anomalies),
                        "latest": anomalies[-1] if anomalies else None
                    })
            
            if metric_anomalies:
                summary.append({
                    "metric": metric,
                    "anomalies": metric_anomalies
                })
        
        return summary

