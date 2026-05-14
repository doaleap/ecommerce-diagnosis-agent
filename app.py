from flask import Flask, jsonify, send_from_directory, request
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import config
from data_monitor_agent import DataMonitorAgent
from anomaly_detection_agent import AnomalyDetectionAgent
from attribution_agent import AttributionAgent
from suggestion_agent import SuggestionAgent

# LangChain 任务编排
from langchain_core.runnables import RunnableLambda, RunnablePassthrough


class CustomJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Timestamp):
            return obj.strftime("%Y-%m-%d")
        return super(CustomJSONProvider, CustomJSONProvider).default(obj)


app = Flask(__name__, static_folder="frontend", static_url_path="")
app.json = CustomJSONProvider(app)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


def _serialize_attribution(report):
    """将归因分析报告转为可JSON序列化的字典"""

    def convert(val):
        if isinstance(val, (np.integer,)):
            return int(val)
        if isinstance(val, (np.floating,)):
            return float(val)
        if isinstance(val, np.ndarray):
            return val.tolist()
        if hasattr(val, "to_dict"):
            return val.to_dict("records")
        return val

    out = {}
    for k, v in report.items():
        if k == "drill_down":
            out[k] = {dim: convert(dv) for dim, dv in v.items()}
        else:
            out[k] = convert(v)
    return out


# ---------- 初始化 Agent ----------
data_agent = DataMonitorAgent()
anomaly_agent = AnomalyDetectionAgent()
attribution_agent = AttributionAgent()
suggestion_agent = SuggestionAgent()


# ---------- LangChain LCEL 诊断流水线 ----------
# 将 4 个 Agent 的核心能力封装为 LangChain Runnable，
# 通过 | 操作符串联为端到端诊断链

def _step_load_data(state: dict) -> dict:
    """Step 1: DataMonitorAgent — 加载并聚合数据"""
    df = data_agent.load_data()
    state["df"] = df
    state["aggregated"] = data_agent.get_aggregated_metrics(df)
    latest_date = df["date"].max()
    state["latest_date"] = str(latest_date.date())
    return state


def _step_detect_anomalies(state: dict) -> dict:
    """Step 2: AnomalyDetectionAgent — 多方法异常检测"""
    results = anomaly_agent.detect_all(state["aggregated"])
    state["detection_results"] = results
    state["anomaly_summary"] = anomaly_agent.get_summary(results)
    return state


def _step_attribute(state: dict) -> dict:
    """Step 3: AttributionAgent — 下钻归因定位根因"""
    df = state["df"]
    latest_date = pd.to_datetime(state["latest_date"])
    report = attribution_agent.get_attribution_report(df, "gmv", latest_date)
    state["attribution_report"] = _serialize_attribution(report)
    return state


def _step_suggest(state: dict) -> dict:
    """Step 4: SuggestionAgent — 基于 LangChain LLM 生成业务建议"""
    suggestions = suggestion_agent.generate_suggestions(
        state["anomaly_summary"],
        state.get("attribution_report", {}),
    )
    state["suggestions"] = suggestions
    return state


# LCEL 链：将 4 个步骤用 | 串联，数据在步骤间传递
diagnosis_chain = (
    RunnableLambda(_step_load_data)
    | RunnableLambda(_step_detect_anomalies)
    | RunnableLambda(_step_attribute)
    | RunnableLambda(_step_suggest)
)


# ---------- Flask 路由 ----------

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")


@app.route("/api/data")
def get_data():
    df = data_agent.load_data()
    aggregated = data_agent.get_aggregated_metrics(df)

    latest_date, latest_data = data_agent.get_latest_data(df)

    aggregated["date"] = aggregated["date"].astype(str)

    return jsonify(
        {
            "timeseries": aggregated.to_dict("records"),
            "latest_date": str(latest_date.date()),
            "latest_summary": {
                "gmv": float(latest_data["gmv"].sum()),
                "order_count": int(latest_data["order_count"].sum()),
                "refund_rate": float(latest_data["refund_rate"].mean()),
                "conversion_rate": float(latest_data["conversion_rate"].mean()),
                "uv": int(latest_data["uv"].sum()),
                "pv": int(latest_data["pv"].sum()),
            },
        }
    )


@app.route("/api/anomalies")
def get_anomalies():
    df = data_agent.load_data()
    aggregated = data_agent.get_aggregated_metrics(df)

    detection_results = anomaly_agent.detect_all(aggregated)
    summary = anomaly_agent.get_summary(detection_results)

    return jsonify({"detection_results": detection_results, "summary": summary})


@app.route("/api/attribution/<metric>/<date>")
def get_attribution(metric, date):
    df = data_agent.load_data()

    report = attribution_agent.get_attribution_report(df, metric, pd.to_datetime(date))
    return jsonify(_serialize_attribution(report))


@app.route("/api/suggestions", methods=["POST"])
def get_suggestions():
    data = request.json
    anomaly_summary = data.get("anomaly_summary", [])
    attribution_report = data.get("attribution_report", {})

    suggestions = suggestion_agent.generate_suggestions(
        anomaly_summary, attribution_report
    )

    return jsonify({"suggestions": suggestions})


@app.route("/api/run-diagnosis")
def run_diagnosis():
    """一键诊断：使用 LangChain LCEL 流水线编排 4 个 Agent"""
    try:
        result = diagnosis_chain.invoke({})

        return jsonify(
            {
                "anomaly_summary": result.get("anomaly_summary", []),
                "attribution": result.get("attribution_report", {}),
                "suggestions": result.get("suggestions", ""),
                "pipeline": "LangChain LCEL",
            }
        )
    except Exception as e:
        return jsonify({"error": str(e), "pipeline": "LangChain LCEL"}), 500


@app.route("/api/langchain-diagnosis")
def langchain_diagnosis():
    """LangChain 编排诊断 —— 展示 LCEL 任务编排能力"""
    try:
        result = diagnosis_chain.invoke({})

        return jsonify(
            {
                "orchestration": "LangChain LCEL (LangChain Expression Language)",
                "pipeline_steps": [
                    "DataMonitorAgent → 数据加载与聚合",
                    "AnomalyDetectionAgent → 3σ/同比/环比异常检测",
                    "AttributionAgent → 多维下钻归因分析",
                    "SuggestionAgent → ChatOpenAI 生成业务建议",
                ],
                "result": {
                    "anomaly_summary": result.get("anomaly_summary", []),
                    "attribution": result.get("attribution_report", {}),
                    "suggestions": result.get("suggestions", ""),
                },
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting e-commerce anomaly diagnosis system (LangChain powered)...")
    if not os.path.exists(os.path.join(config.DATA_DIR, "ecommerce_data.csv")):
        data_agent.generate_sample_data()
    app.run(host=config.HOST, port=config.PORT, debug=True)
