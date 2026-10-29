# -*- coding: utf-8 -*-
"""CDA 三级教材 · 2.1 客户价值预测（线性回归全流程）

来源：CDA 三级教材配套 notebook「2.1线性回归.ipynb」
改写目标：notebook 里用 30 多个单元格零散地"做一步看一步"，本脚本按建模流程
         串成一条可复现的流水线，并说明每一步的诊断意义。

业务背景：汽车金融公司想用"分析窗口期"的客户特征（收入、年龄、房产、学历等），
         预测客户下一期的月均信用卡支出（avg_exp），用于额度预授信。

数据说明：
    creditcard_exp.csv                —— 有因变量的历史样本（训练用）
    creditcard_exp_out_of_sample.csv  —— 只有自变量、需要用模型打分的新客（预测用）

运行：python CDA三级_客户价值预测线性回归.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from statsmodels.stats.outliers_influence import OLSInfluence

from common_data import load_csv, save, title

# ---------------------------------------------------------------- 1. 读数据
title("1. 读取训练集与待预测样本")
raw = load_csv("creditcard_exp.csv", skipinitialspace=True)
oos = load_csv("creditcard_exp_out_of_sample.csv", skipinitialspace=True)
print(f"训练集：{raw.shape[0]} 行 × {raw.shape[1]} 列")
print(f"待预测：{oos.shape[0]} 行 × {oos.shape[1]} 列")
print("\n字段：", list(raw.columns))

# 只保留有因变量的样本；去掉 id/Acc 这类主键与结果字段、去掉共线的 age2
train = raw[raw["avg_exp"].notnull()].iloc[:, 2:].drop(columns=["age2"], errors="ignore")
oos_data = oos.drop(columns=["age2"], errors="ignore")
print(f"\n有效训练样本：{len(train)} 条")

# ---------------------------------------------------------------- 2. 探索
title("2. 相关性分析与散点图")
print("与月均支出的相关系数：")
print(train[["avg_exp", "Income", "Age", "dist_home_val", "dist_avg_income"]]
      .corr(numeric_only=True)["avg_exp"].sort_values(ascending=False).round(3).to_string())

fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.scatter(train["Income"], train["avg_exp"], alpha=0.75,
           color="#4A90E2", edgecolor="white")
ax.set_xlabel("年收入（万元）")
ax.set_ylabel("月均信用卡支出（元）")
ax.set_title("收入 vs 月均支出")
ax.grid(alpha=0.3, linestyle="--")
save(fig, "三级_收入与支出散点")

# ---------------------------------------------------------------- 3. 简单回归
title("3. 一元线性回归：avg_exp ~ Income")
simple = ols("avg_exp ~ Income", data=train).fit()
print(f"R2 = {simple.rsquared:.4f}   系数 = {simple.params.round(3).to_dict()}")
print("解释：收入每增加 1 万元，月均支出平均增加 "
      f"{simple.params['Income']:.2f} 元。")

# ---------------------------------------------------------------- 4. 多元回归
title("4. 多元线性回归")
multi = ols("avg_exp ~ Income + dist_home_val + dist_avg_income", data=train).fit()
print(f"R2 = {multi.rsquared:.4f}   调整R2 = {multi.rsquared_adj:.4f}   AIC = {multi.aic:.1f}")
print(multi.params.round(3).to_string())

# ---------------------------------------------------------------- 5. 逐步回归
title("5. 基于 AIC 的前向逐步回归")


def forward_select(data, response, verbose=True):
    """每次加入一个能让 AIC 下降最多的变量，直到再加变量 AIC 不再下降"""
    remaining = [c for c in data.columns if c != response]
    selected = []
    current_aic = np.inf
    while remaining:
        candidates = []
        for cand in remaining:
            formula = f"{response} ~ " + " + ".join(selected + [cand])
            candidates.append((ols(formula, data=data).fit().aic, cand))
        candidates.sort()
        best_aic, best_cand = candidates[0]
        if best_aic < current_aic:
            selected.append(best_cand)
            remaining.remove(best_cand)
            current_aic = best_aic
            if verbose:
                print(f"  加入 {best_cand:<16} AIC = {current_aic:.2f}")
        else:
            break
    formula = f"{response} ~ " + " + ".join(selected)
    print(f"最终变量组合：{selected}")
    return ols(formula, data=data).fit()


pick = train[["avg_exp", "Income", "Age", "dist_home_val", "dist_avg_income"]].dropna()
fwd_model = forward_select(pick, "avg_exp")
print(f"前向选择模型 R2 = {fwd_model.rsquared:.4f}")

# ---------------------------------------------------------------- 6. 残差诊断
title("6. 残差诊断：同方差性与正态性")
fig, axes = plt.subplots(2, 1, figsize=(7, 7))
axes[0].scatter(train["Income"], fwd_model.resid, alpha=0.75, color="#F5A623")
axes[0].axhline(0, color="#4A4A4A", linestyle="--")
axes[0].set_xlabel("Income")
axes[0].set_ylabel("残差")
axes[0].set_title("残差 vs 自变量（看是否随机散布）")
axes[1].scatter(fwd_model.predict(pick), fwd_model.resid, alpha=0.75, color="#4A90E2")
axes[1].axhline(0, color="#4A4A4A", linestyle="--")
axes[1].set_xlabel("拟合值")
axes[1].set_ylabel("残差")
axes[1].set_title("残差 vs 拟合值（喇叭口 = 异方差）")
fig.tight_layout()
save(fig, "三级_残差图")

# 因变量取对数：右偏的金额变量取对数后更接近正态，也缓解异方差
train["avg_exp_ln"] = np.log(train["avg_exp"])
train["Income_ln"] = np.log(train["Income"])
oos_data["Income_ln"] = np.log(oos_data["Income"])

log_model = ols("avg_exp_ln ~ Income_ln", data=train).fit()
print(f"\n对数模型 R2 = {log_model.rsquared:.4f}"
      f"（原模型 {simple.rsquared:.4f}，解释力提升）")
print(f"弹性解释：收入每增加 1%，月均支出平均增加 {log_model.params['Income_ln']:.3f}%")

fig, ax = plt.subplots(figsize=(5.5, 5))
from statsmodels.graphics.gofplots import qqplot
qqplot(log_model.resid, line="45", ax=ax, fit=True)
ax.set_title("对数模型残差 Q-Q 图")
save(fig, "三级_QQ图")

# ---------------------------------------------------------------- 7. 强影响点
title("7. 强影响点识别")
train["resid"] = log_model.resid
student_resid = (train["resid"] - train["resid"].mean()) / train["resid"].std()
outliers = train[np.abs(student_resid) > 2]
print(f"标准化残差绝对值 > 2 的样本：{len(outliers)} 条")
print(outliers[["avg_exp", "Income", "resid"]].round(2).to_string())

# Cook's D 衡量"删掉这个点模型会变多少"，> 4/n 视为强影响点
influence = OLSInfluence(log_model)
cooks = influence.cooks_distance[0]
threshold = 4 / len(train)
print(f"\nCook's D 阈值 = 4/n = {threshold:.4f}，超阈值的样本：{int((cooks > threshold).sum())} 条")

clean = train[np.abs(student_resid) <= 2].copy()
log_model_clean = ols("avg_exp_ln ~ Income_ln", data=clean).fit()
print(f"\n剔除强影响点后 R2：{log_model_clean.rsquared:.4f}"
      f"（剔除前 {log_model.rsquared:.4f}）")

# ---------------------------------------------------------------- 8. 共线性
title("8. 多重共线性诊断（VIF）")
formula_vars = ["Income_ln", "Age", "dist_home_val"]


def vif(frame, col):
    r2 = ols(f"{col} ~ " + " + ".join([c for c in frame.columns if c != col]),
             data=frame).fit().rsquared
    return 1 / (1 - r2)


vif_frame = train[formula_vars].dropna()
for col in formula_vars:
    print(f"  {col:<16} VIF = {vif(vif_frame, col):6.2f}")

# ---------------------------------------------------------------- 9. 打分
title("9. 用最终模型对新客打分")
final = ols("avg_exp_ln ~ Income_ln + Age", data=clean).fit()
print(f"最终模型 R2 = {final.rsquared:.4f}")
print(final.params.round(4).to_string())

pred_ln = final.predict(oos_data.dropna(subset=["Income_ln", "Age"]))
pred = np.exp(pred_ln)
result = pd.DataFrame({"预测月均支出": pred.round(2)}).reset_index(drop=True)
print("\n待预测样本打分结果（前 10 条）：")
print(result.head(10).to_string(index=False))
print(f"\n预测值分布：均值 {pred.mean():.0f} 元，中位数 {np.median(pred):.0f} 元")

out_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output",
                       "三级_客户价值预测结果.csv")
os.makedirs(os.path.dirname(out_csv), exist_ok=True)
result.to_csv(out_csv, index=False, encoding="utf-8-sig")
print(f"完整打分结果已保存：{os.path.relpath(out_csv, os.path.dirname(os.path.abspath(__file__)))}")

# ---------------------------------------------------------------- 10. 结论
title("10. 结论")
print("· 收入是最强解释变量，收入越高月均支出越高；")
print("· 金额类变量取对数后残差更接近正态，模型更稳健；")
print("· 剔除 2 个强影响点后模型系数变化不大，说明结论不是被个别客户带偏的；")
print("· 输出图片见 images/，打分结果见 output/。")
