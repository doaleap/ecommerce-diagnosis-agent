# 电商运营异常诊断系统

基于多 Agent 协作的智能电商运营异常诊断系统，自动监控核心指标、检测异常、归因分析并提供业务建议。

## 功能特性

- **数据监控**：自动拉取 GMV、订单量、退款率等核心指标，支持多品类多区域维度
- **异常检测**：采用 3σ、同比、环比等统计学方法识别异常
- **归因分析**：自动下钻定位问题根因（按品类、区域维度），量化贡献度
- **智能建议**：基于 LLM 生成可落地的业务策略建议
- **A/B 测试**：独立模块，量化验证 Agent 系统干预效果
- **可视化大屏**：实时展示运营数据和诊断结果

## 系统架构

系统由 4 个核心 Agent 组成，通过 **LangChain LCEL** 编排为端到端诊断流水线：

```
DataMonitorAgent → AnomalyDetectionAgent → AttributionAgent → SuggestionAgent
      ↓                    ↓                       ↓                  ↓
   数据加载           3σ/同比/环比             多维下钻归因        ChatOpenAI
   指标聚合           异常检测                 根因定位          生成建议
```

## 技术栈

| 层面 | 技术 |
|------|------|
| 任务编排 | LangChain LCEL (`RunnableLambda` + `\|` 管道) |
| LLM 调用 | LangChain ChatOpenAI（对接 DeepSeek API） |
| 后端框架 | Python + Flask |
| 数据处理 | Pandas + NumPy |
| 统计分析 | SciPy（t 检验、3σ 异常检测） |
| 前端 | HTML + Tailwind CSS + Chart.js |
| A/B 测试 | 独立样本 t 检验 + 95% 置信区间 + 效应量 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 DeepSeek API Key

```bash
# Windows
set DEEPSEEK_API_KEY=你的DeepSeek-API-Key

# Mac / Linux
export DEEPSEEK_API_KEY=你的DeepSeek-API-Key
```

API Key 获取地址：[platform.deepseek.com](https://platform.deepseek.com)

### 3. 启动服务

```bash
python app.py
```

浏览器访问 **http://localhost:8000**

### 4. 单独运行 A/B 测试

```bash
python ab_test.py
```

## 项目结构

```
ecommerce-diagnosis-agent/
├── app.py                      # Flask 主程序（LangChain LCEL 编排 Agent 流水线）
├── data_monitor_agent.py       # 数据监控 Agent
├── anomaly_detection_agent.py  # 异常检测 Agent（3σ/同比/环比）
├── attribution_agent.py        # 归因分析 Agent（多维下钻）
├── suggestion_agent.py         # 建议生成 Agent（LangChain ChatOpenAI）
├── ab_test.py                  # A/B 测试模块（独立可运行）
├── config.py                   # 配置文件
├── requirements.txt            # Python 依赖
├── start.bat                   # Windows 一键启动
├── frontend/
│   └── index.html              # 可视化大屏
└── data/                       # 数据目录（自动生成）
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/data` | 获取时序数据和最新指标 |
| GET | `/api/anomalies` | 获取异常检测结果 |
| GET | `/api/attribution/<metric>/<date>` | 指定指标的归因分析 |
| POST | `/api/suggestions` | 获取 LLM 智能建议 |
| GET | `/api/run-diagnosis` | 一键运行 LangChain 诊断流水线 |
| GET | `/api/langchain-diagnosis` | LangChain 编排诊断（含流水线信息） |
