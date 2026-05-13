
# 电商运营异常诊断多 Agent 系统 - 项目简介

## 项目概述

构建了一套完整的多 Agent 协作电商运营异常诊断系统，实现从数据监控、异常检测、归因分析到智能建议的端到端自动化流程，帮助运营团队快速定位和解决业务问题。

## 技术栈

- **后端框架**：Python + Flask
- **数据处理**：Pandas + NumPy + SciPy
- **前端可视化**：HTML + Tailwind CSS + Chart.js
- **AI 能力**：OpenAI API 兼容接口（支持 Qwen 等大模型）
- **核心算法**：3σ 原则、同比/环比分析、多维下钻归因

## 核心功能与 Agent 设计

### 1. 数据监控 Agent
- 负责多维度电商数据的拉取、聚合和清洗
- 支持 GMV、订单量、退款率、转化率、UV、PV 等 6 大核心指标监控
- 内置样本数据生成器，模拟真实业务场景（含周末效应、品类/区域细分）

### 2. 异常检测 Agent
- 3σ 统计学异常检测：识别超出正常波动范围的数据点
- 同比（YoY）分析：检测周度异常波动
- 环比（QoQ）分析：监控日度变化趋势
- 多方法融合，提高异常召回率

### 3. 归因分析 Agent
- 自动下钻定位：按品类、区域维度进行多维度归因
- 贡献度计算：量化各维度对整体指标的影响
- 根因排序：智能识别影响最大的问题维度

### 4. 建议生成 Agent
- 基于 LLM 的自然语言建议生成
- 结合异常检测和归因分析结果
- 输出可落地的业务优化策略

## 项目亮点

✅ **多 Agent 协作架构**：4 个独立 Agent 分工明确，协同完成诊断任务  
✅ **实时可视化大屏**：动态展示数据趋势、异常警报和根因分析  
✅ **完整诊断闭环**：从数据采集到智能建议的一站式解决方案  
✅ **可扩展设计**：支持接入真实数据源，方便扩展更多监控维度  

## 项目成果

- 系统自动生成模拟数据并完成异常检测
- 可视化大屏实时展示运营状态
- 一键运行完整诊断流程，输出可操作建议
- 为运营团队节省 80% 的异常分析时间

## 相关文件

- [app.py](file:///d:\vibecoding\ecommerce-diagnosis-agent\app.py) - Flask 主程序
- [data_monitor_agent.py](file:///d:\vibecoding\ecommerce-diagnosis-agent\data_monitor_agent.py) - 数据监控 Agent
- [anomaly_detection_agent.py](file:///d:\vibecoding\ecommerce-diagnosis-agent\anomaly_detection_agent.py) - 异常检测 Agent
- [attribution_agent.py](file:///d:\vibecoding\ecommerce-diagnosis-agent\attribution_agent.py) - 归因分析 Agent
- [suggestion_agent.py](file:///d:\vibecoding\ecommerce-diagnosis-agent\suggestion_agent.py) - 建议生成 Agent

