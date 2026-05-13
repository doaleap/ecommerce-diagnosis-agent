
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

API_KEY = "sk-krtluesocapckkinfxtugpnoqtbdycfxlkmehipaiqrwbrgy"
API_BASE = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen2.5-7B-Instruct"

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

