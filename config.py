
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
API_BASE = os.getenv("API_BASE", "https://api.deepseek.com/v1")
MODEL = os.getenv("MODEL_NAME", "deepseek-chat")

# LangChain 配置
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "ecommerce-diagnosis-agent")

METRICS = [
    "gmv",
    "order_count",
    "refund_rate",
    "conversion_rate",
    "uv",
    "pv"
]

THRESHOLD_3SIGMA = 3
THRESHOLD_YOY = 0.3
THRESHOLD_QOQ = 0.2

PORT = 8000
HOST = "0.0.0.0"

