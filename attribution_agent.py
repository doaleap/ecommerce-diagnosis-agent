
import pandas as pd
import numpy as np

class AttributionAgent:
    def __init__(self):
        self.dimensions = ["category", "region"]
    
    def analyze_dimension(self, df, dimension, metric, date_range=None):
        if date_range is not None:
            df = df[(df["date"] >= date_range[0]) & (df["date"] <= date_range[1])]
        
        dim_data = df.groupby(dimension).agg({
            metric: "sum" if metric in ["gmv", "order_count", "uv", "pv"] else "mean"
        }).reset_index()
        
        total = dim_data[metric].sum() if metric in ["gmv", "order_count", "uv", "pv"] else dim_data[metric].mean()
        dim_data["contribution"] = dim_data[metric] / total
        
        return dim_data.sort_values("contribution", ascending=False)
    
    def drill_down(self, df, metric, target_date):
        results = {}
        
        df_latest = df[df["date"] == target_date]
        
        if len(df_latest) == 0:
            return results
        
        prev_date = df[df["date"] < target_date]["date"].max()
        df_prev = df[df["date"] == prev_date]
        
        for dimension in self.dimensions:
            dim_latest = self.analyze_dimension(df_latest, dimension, metric)
            dim_prev = self.analyze_dimension(df_prev, dimension, metric)
            
            merged = pd.merge(
                dim_latest,
                dim_prev,
                on=dimension,
                suffixes=("_latest", "_prev"),
                how="left"
            )
            
            merged["change"] = merged[f"{metric}_latest"] - merged[f"{metric}_prev"]
            merged["change_rate"] = merged["change"] / merged[f"{metric}_prev"].replace(0, np.nan)
            
            results[dimension] = merged.sort_values("change", ascending=True)
        
        return results
    
    def find_root_cause(self, drill_down_results, top_n=3):
        root_causes = []
        
        for dimension, data in drill_down_results.items():
            if data is None or len(data) == 0:
                continue
            
            top_neg = data[data["change"] < 0].head(top_n)
            
            for _, row in top_neg.iterrows():
                root_causes.append({
                    "dimension": dimension,
                    "value": row[dimension],
                    "metric_latest": row.iloc[1],
                    "metric_prev": row.iloc[3],
                    "change": row["change"],
                    "change_rate": row["change_rate"],
                    "contribution": row["contribution_latest"]
                })
        
        return sorted(root_causes, key=lambda x: x["change"])
    
    def get_attribution_report(self, df, metric, target_date):
        drill_down = self.drill_down(df, metric, target_date)
        root_causes = self.find_root_cause(drill_down)
        
        return {
            "target_date": target_date,
            "metric": metric,
            "drill_down": drill_down,
            "root_causes": root_causes
        }

