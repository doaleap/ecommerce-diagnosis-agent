
import pandas as pd
import numpy as np
import os
import config
from datetime import datetime, timedelta

class DataMonitorAgent:
    def __init__(self):
        self.data_dir = config.DATA_DIR
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def generate_sample_data(self, days=30):
        data = []
        base_date = datetime.now() - timedelta(days=days)
        
        categories = ["Electronics", "Clothing", "Food", "Home", "Beauty"]
        regions = ["East", "North", "South", "West", "Central"]
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            for category in categories:
                for region in regions:
                    base_gmv = np.random.normal(50000, 10000)
                    
                    if date.weekday() >= 5:
                        base_gmv *= 1.3
                    
                    if i >= days - 5:
                        if category == "Electronics" and region == "East":
                            base_gmv *= 0.6
                    
                    gmv = max(0, base_gmv)
                    order_count = int(gmv / np.random.normal(150, 30))
                    refund_rate = np.random.normal(0.03, 0.01)
                    uv = np.random.randint(1000, 5000)
                    pv = uv * np.random.randint(3, 8)
                    conversion_rate = order_count / uv if uv > 0 else 0
                    
                    data.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "category": category,
                        "region": region,
                        "gmv": round(gmv, 2),
                        "order_count": order_count,
                        "refund_rate": round(refund_rate, 4),
                        "conversion_rate": round(conversion_rate, 4),
                        "uv": uv,
                        "pv": pv
                    })
        
        df = pd.DataFrame(data)
        file_path = os.path.join(self.data_dir, "ecommerce_data.csv")
        df.to_csv(file_path, index=False, encoding="utf-8")
        print("Sample data generated:", file_path)
        return df
    
    def load_data(self, file_path=None):
        if file_path is None:
            file_path = os.path.join(self.data_dir, "ecommerce_data.csv")
        
        if not os.path.exists(file_path):
            print("Data file not found, generating sample data...")
            return self.generate_sample_data()
        
        df = pd.read_csv(file_path)
        df["date"] = pd.to_datetime(df["date"])
        print("Data loaded successfully, total records:", len(df))
        return df
    
    def get_aggregated_metrics(self, df, group_by=None):
        if group_by is None:
            grouped = df.groupby("date").agg({
                "gmv": "sum",
                "order_count": "sum",
                "refund_rate": "mean",
                "conversion_rate": "mean",
                "uv": "sum",
                "pv": "sum"
            }).reset_index()
        else:
            grouped = df.groupby(["date"] + group_by).agg({
                "gmv": "sum",
                "order_count": "sum",
                "refund_rate": "mean",
                "conversion_rate": "mean",
                "uv": "sum",
                "pv": "sum"
            }).reset_index()
        
        return grouped
    
    def get_latest_data(self, df):
        latest_date = df["date"].max()
        latest_data = df[df["date"] == latest_date]
        return latest_date, latest_data

