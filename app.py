
from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import json
import config
from data_monitor_agent import DataMonitorAgent
from anomaly_detection_agent import AnomalyDetectionAgent
from attribution_agent import AttributionAgent
from suggestion_agent import SuggestionAgent

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.strftime("%Y-%m-%d")
        return super().default(obj)

app.json_encoder = CustomJSONEncoder

data_agent = DataMonitorAgent()
anomaly_agent = AnomalyDetectionAgent()
attribution_agent = AttributionAgent()
suggestion_agent = SuggestionAgent()

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/api/data")
def get_data():
    df = data_agent.load_data()
    aggregated = data_agent.get_aggregated_metrics(df)
    
    latest_date, latest_data = data_agent.get_latest_data(df)
    
    aggregated["date"] = aggregated["date"].astype(str)
    
    return jsonify({
        "timeseries": aggregated.to_dict("records"),
        "latest_date": str(latest_date.date()),
        "latest_summary": {
            "gmv": float(latest_data["gmv"].sum()),
            "order_count": int(latest_data["order_count"].sum()),
            "refund_rate": float(latest_data["refund_rate"].mean()),
            "conversion_rate": float(latest_data["conversion_rate"].mean()),
            "uv": int(latest_data["uv"].sum()),
            "pv": int(latest_data["pv"].sum())
        }
    })

@app.route("/api/anomalies")
def get_anomalies():
    df = data_agent.load_data()
    aggregated = data_agent.get_aggregated_metrics(df)
    
    detection_results = anomaly_agent.detect_all(aggregated)
    summary = anomaly_agent.get_summary(detection_results)
    
    return jsonify({
        "detection_results": detection_results,
        "summary": summary
    })

@app.route("/api/attribution/<metric>/<date>")
def get_attribution(metric, date):
    df = data_agent.load_data()
    
    report = attribution_agent.get_attribution_report(df, metric, pd.to_datetime(date))
    
    def to_dict_func(x): 
        if hasattr(x, "to_dict"):
            return x.to_dict("records")
        return x
    serializable_report = {}
    for k, v in report.items():
        if k == "drill_down":
            serializable_report[k] = {dim: to_dict_func(dv) for dim, dv in v.items()}
        else:
            serializable_report[k] = to_dict_func(v)
    
    return jsonify(serializable_report)

@app.route("/api/suggestions", methods=["POST"])
def get_suggestions():
    from flask import request
    data = request.json
    anomaly_summary = data.get("anomaly_summary", [])
    attribution_report = data.get("attribution_report", {})
    
    suggestions = suggestion_agent.generate_suggestions(anomaly_summary, attribution_report)
    
    return jsonify({"suggestions": suggestions})

@app.route("/api/run-diagnosis")
def run_diagnosis():
    df = data_agent.load_data()
    aggregated = data_agent.get_aggregated_metrics(df)
    latest_date, _ = data_agent.get_latest_data(df)
    
    detection_results = anomaly_agent.detect_all(aggregated)
    summary = anomaly_agent.get_summary(detection_results)
    
    main_metric = "gmv"
    attribution_report = attribution_agent.get_attribution_report(df, main_metric, latest_date)
    
    suggestions = suggestion_agent.generate_suggestions(summary, attribution_report)
    
    def to_dict_func(x): 
        if hasattr(x, "to_dict"):
            return x.to_dict("records")
        return x
    serializable_attribution = {}
    for k, v in attribution_report.items():
        if k == "drill_down":
            serializable_attribution[k] = {dim: to_dict_func(dv) for dim, dv in v.items()}
        else:
            serializable_attribution[k] = to_dict_func(v)
    
    return jsonify({
        "anomaly_summary": summary,
        "attribution": serializable_attribution,
        "suggestions": suggestions
    })

if __name__ == "__main__":
    print("Starting e-commerce anomaly diagnosis system...")
    if not os.path.exists(os.path.join(config.DATA_DIR, "ecommerce_data.csv")):
        data_agent.generate_sample_data()
    app.run(host=config.HOST, port=config.PORT, debug=True)

