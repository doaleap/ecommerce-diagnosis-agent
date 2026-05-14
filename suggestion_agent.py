from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import config


class SuggestionAgent:
    """基于 LangChain 的智能建议生成 Agent"""

    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=config.API_KEY,
            base_url=config.API_BASE,
            model=config.MODEL,
            temperature=0.7,
            max_tokens=2000,
        )

        self.system_prompt = SystemMessagePromptTemplate.from_template(
            "你是专业的电商运营分析师，擅长基于数据异常和归因分析结果提供可落地的业务建议。请始终用中文回复。"
        )

        self.human_prompt = HumanMessagePromptTemplate.from_template(
            """请基于以下电商异常诊断信息，提供专业的业务建议：

[异常概要]
{anomaly_summary}

[归因分析]
{attribution_report}

请提供以下内容：
1. 问题诊断总结
2. 针对性的业务优化建议（分点列出，可落地）
3. 长期运营策略建议"""
        )

        self.chat_prompt = ChatPromptTemplate.from_messages(
            [self.system_prompt, self.human_prompt]
        )

        self.chain = self.chat_prompt | self.llm | StrOutputParser()

    def generate_suggestions(self, anomaly_summary, attribution_report):
        summary_text = self._format_anomaly_summary(anomaly_summary)
        report_text = self._format_attribution_report(attribution_report)

        try:
            result = self.chain.invoke({
                "anomaly_summary": summary_text,
                "attribution_report": report_text,
            })
            return result
        except Exception as e:
            return (
                f"建议生成失败: {e}\n\n"
                "推荐默认策略：针对异常维度进行定向优化，加大流量投入和促销活动力度。"
            )

    def _format_anomaly_summary(self, anomaly_summary):
        if not anomaly_summary:
            return "无异常数据"

        lines = []
        for item in anomaly_summary:
            metric = item.get("metric", "未知指标")
            anomalies = item.get("anomalies", [])
            for anom in anomalies:
                method = anom.get("method", "")
                count = anom.get("count", 0)
                lines.append(f"- {metric}: {method} 检测到 {count} 个异常")
        return "\n".join(lines) if lines else "无异常数据"

    def _format_attribution_report(self, attribution_report):
        if not attribution_report:
            return "无归因分析数据"

        lines = []
        root_causes = attribution_report.get("root_causes", [])
        if root_causes:
            for cause in root_causes[:3]:
                dim = cause.get("dimension", "")
                val = cause.get("value", "")
                change = cause.get("change", 0)
                rate = cause.get("change_rate", 0)
                lines.append(
                    f"- {dim}: {val}, 变化量: {change:.2f}, 变化率: {rate:.2%}"
                )
        return "\n".join(lines) if lines else "无归因分析数据"
