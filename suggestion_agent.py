
from openai import OpenAI
import config

class SuggestionAgent:
    def __init__(self):
        self.client = OpenAI(
            api_key=config.API_KEY,
            base_url=config.API_BASE
        )
        self.model = config.MODEL
    
    def generate_suggestions(self, anomaly_summary, attribution_report):
        prompt = self._build_prompt(anomaly_summary, attribution_report)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional e-commerce operations analyst, good at providing actionable business suggestions based on data anomalies and attribution analysis results."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Suggestion generation failed: {e}\n\nRecommended default strategy: Conduct targeted optimization for anomalous dimensions, increase traffic investment and promotional activities."
    
    def _build_prompt(self, anomaly_summary, attribution_report):
        prompt = """Please provide professional business suggestions based on the following e-commerce anomaly diagnosis information:

[Anomaly Overview]
"""
        for item in anomaly_summary:
            prompt += f"- {item['metric']}: "
            for anom in item['anomalies']:
                prompt += f"{anom['method']} detected {anom['count']} anomalies; "
            prompt += "\n"
        
        prompt += "\n[Attribution Analysis]\n"
        if attribution_report and "root_causes" in attribution_report:
            for cause in attribution_report["root_causes"][:3]:
                prompt += f"- {cause['dimension']}: {cause['value']}, Change: {cause['change']:.2f}, Change Rate: {cause['change_rate']:.2%}\n"
        
        prompt += """

Please provide the following:
1. Problem diagnosis summary
2. Targeted business optimization suggestions (listed in points, actionable)
3. Long-term operation strategy suggestions
"""
        return prompt

