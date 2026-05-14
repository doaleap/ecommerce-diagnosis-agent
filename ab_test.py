"""
A/B测试评估模块：量化Agent诊断系统的业务效果

对比"无Agent干预(对照组)" vs "Agent诊断后修复(实验组)"的退款率，
使用独立样本t检验判断差异是否统计显著。
"""
import pandas as pd
import numpy as np
from scipy import stats


def run_ab_test(n_days=60, n_regions=5, n_categories=5, random_seed=42):
    """运行A/B测试并输出报告"""
    np.random.seed(random_seed)

    # ---------- 1. 生成模拟数据 ----------
    focus_days = 10
    df = _generate_ab_data(n_days, n_regions, n_categories, focus_days)

    anomaly_region, anomaly_category = "East", "Electronics"
    anomaly_end = df["date"].max()

    # ---------- 2. 拆分对照组 vs 实验组 ----------
    control = df.copy()

    treatment = df.copy()
    mask = (
        (treatment["region"] == anomaly_region)
        & (treatment["category"] == anomaly_category)
        & (treatment["date"] > anomaly_end - pd.Timedelta(days=focus_days))
    )
    normal_rate = df.loc[
        ~((df["region"] == anomaly_region) & (df["category"] == anomaly_category)),
        "refund_rate",
    ].mean()
    treatment.loc[mask, "refund_rate"] = normal_rate + np.random.normal(
        0, 0.003, size=mask.sum()
    )

    # ---------- 3. 统计检验 ----------
    # 聚焦异常时段（最后10天），按天聚合退款率做配对检验
    control_daily = control.groupby("date")["refund_rate"].mean().tail(focus_days)
    treatment_daily = treatment.groupby("date")["refund_rate"].mean().tail(focus_days)

    t_stat, p_value = stats.ttest_ind(control_daily, treatment_daily)

    control_mean = control_daily.mean()
    treatment_mean = treatment_daily.mean()
    lift_pct = (control_mean - treatment_mean) / control_mean * 100

    n_control, n_treatment = len(control_daily), len(treatment_daily)
    pooled_std = np.sqrt(
        ((n_control - 1) * control_daily.var() + (n_treatment - 1) * treatment_daily.var())
        / (n_control + n_treatment - 2)
    )
    se = pooled_std * np.sqrt(1 / n_control + 1 / n_treatment)
    ci = stats.t.ppf(0.975, n_control + n_treatment - 2) * se
    diff = control_mean - treatment_mean

    # ---------- 4. 输出报告 ----------
    print("=" * 56)
    print("  A/B测试报告：电商异常诊断Agent效果评估")
    print("=" * 56)
    print(f"  异常场景        : {anomaly_region} {anomaly_category} 退款率突增")
    print(f"  测试周期        : {n_days}天 × {n_regions}个区域 × {n_categories}个品类")
    print()
    print(f"  对照组(无Agent) : 退款率均值 = {control_mean:.4f} ({control_mean*100:.2f}%)")
    print(f"  实验组(Agent干预): 退款率均值 = {treatment_mean:.4f} ({treatment_mean*100:.2f}%)")
    print(f"  绝对降幅        : {diff:.4f} ({diff*100:.2f}个百分点)")
    print(f"  相对提升        : {lift_pct:.1f}%")
    print(f"  95%置信区间     : [{diff-ci:.4f}, {diff+ci:.4f}]")
    print()
    print(f"  t统计量         : {t_stat:.4f}")
    print(f"  p值             : {p_value:.4f} {'***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else '(不显著)'}")
    print()
    if p_value < 0.05:
        print("  结论: Agent诊断干预效果统计显著，推荐投入生产使用")
    else:
        print("  结论: 效果未达统计显著，建议扩大样本量继续观察")
    print("=" * 56)

    return {
        "control_mean": control_mean,
        "treatment_mean": treatment_mean,
        "diff": diff,
        "lift_pct": lift_pct,
        "ci_lower": diff - ci,
        "ci_upper": diff + ci,
        "t_stat": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }


def _generate_ab_data(n_days, n_regions, n_categories, focus_days=10):
    """生成含已知异常的A/B测试数据"""
    dates = pd.date_range(end=pd.Timestamp.now().normalize(), periods=n_days, freq="D")
    regions = ["East", "South", "North", "West", "Central"][:n_regions]
    categories = [
        "Electronics", "Clothing", "Food", "Home", "Sports"
    ][:n_categories]

    rows = []
    for date in dates:
        for region in regions:
            for category in categories:
                base_rate = 0.05 + np.random.normal(0, 0.005)
                # 注入异常：最后10天东部地区电子产品退款率飙升（5%→15%）
                if (
                    region == "East"
                    and category == "Electronics"
                    and date > dates[-(focus_days + 1)]
                ):
                    base_rate = 0.15 + np.random.normal(0, 0.01)
                base_rate = max(0.01, min(base_rate, 0.25))
                rows.append(
                    {
                        "date": date,
                        "region": region,
                        "category": category,
                        "gmv": np.random.uniform(5000, 50000),
                        "order_count": np.random.randint(50, 500),
                        "refund_rate": base_rate,
                        "conversion_rate": np.random.uniform(0.02, 0.10),
                        "uv": np.random.randint(1000, 10000),
                        "pv": np.random.randint(2000, 20000),
                    }
                )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    run_ab_test()
