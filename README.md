
# 电商运营异常诊断系统

一个基于多 Agent 协作的智能电商运营异常诊断系统，自动监控核心指标、检测异常、归因分析并提供业务建议。

## 功能特性

- 📊 **数据监控**：自动拉取 GMV、订单量、退款率等核心指标
- 🔍 **异常检测**：采用 3σ、同比、环比等统计学方法识别异常
- 📈 **归因分析**：自动下钻定位问题根因（按品类、区域维度）
- 💡 **智能建议**：基于 LLM 生成可落地的业务策略建议
- 🖥️ **可视化大屏**：实时展示运营数据和诊断结果

## 系统架构

系统由 4 个核心 Agent 组成：

1. **DataMonitorAgent**：负责数据加载、聚合和样本数据生成
2. **AnomalyDetectionAgent**：负责异常检测（3σ、YoY、QoQ）
3. **AttributionAgent**：负责多维度归因分析和根因定位
4. **SuggestionAgent**：基于 LLM 生成业务建议

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `config.py`，填入你的 OpenAI 兼容 API 配置：

```python
API_KEY = "your-api-key-here"
API_BASE = "https://api.siliconflow.cn/v1"
MODEL = "Qwen/Qwen2.5-7B-Instruct"
```

### 3. 启动服务

```bash
python app.py
```

或使用启动脚本（Windows）：

```bash
start.bat
```

### 4. 访问系统

打开浏览器访问：`http://localhost:8000`

## 项目结构

```
ecommerce-diagnosis-agent/
├── config.py              # 配置文件
├── app.py                 # Flask 主程序
├── data_monitor_agent.py  # 数据监控 Agent
├── anomaly_detection_agent.py  # 异常检测 Agent
├── attribution_agent.py   # 归因分析 Agent
├── suggestion_agent.py    # 建议生成 Agent
├── requirements.txt       # Python 依赖
├── frontend/
│   └── index.html        # 可视化大屏前端
├── data/                  # 数据目录（自动生成）
└── README.md
```

## API 接口

- `GET /api/data` - 获取时序数据和最新指标
- `GET /api/anomalies` - 获取异常检测结果
- `GET /api/attribution/&lt;metric&gt;/&lt;date&gt;` - 获取指定指标的归因分析
- `POST /api/suggestions` - 获取智能建议
- `GET /api/run-diagnosis` - 运行完整诊断流程

## 技术栈

- **后端**：Python + Flask
- **数据处理**：Pandas + NumPy + SciPy
- **前端**：HTML + Tailwind CSS + Chart.js
- **AI**：OpenAI API 兼容接口

## 自定义数据源

可以替换 `data_monitor_agent.py` 中的数据加载逻辑，连接真实的电商数据库或数据仓库。

