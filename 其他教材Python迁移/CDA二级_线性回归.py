# -*- coding: utf-8 -*-
"""CDA 二级教材 · 第8章 线性回归（信用卡月均支出预测）

来源：CDA 二级教材配套 notebook「线性回归.ipynb」（原文件为 Jupyter 交互式代码）
改写目标：把 notebook 里"逐个单元格执行、靠输出窗口看图"的写法，整理成一个
         从头到尾可独立运行的脚本，并补齐每一步的业务解释。

分析主线（对应教材 8.x 节）：
    读数据 → 清洗（去重/缺失/编码/异常值）→ 相关分析 → 多元回归
    → 共线性诊断 → 残差诊断（同方差/正态性）→ 变量变换（对数/二次项/交互项）
    → 模型对比

运行：python CDA二级_线性回归.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.formula.api import ols

from common_data import load_excel, save, title


# ---------------------------------------------------------------- 1. 读数据
title("1. 读取数据")
df = load_excel("LR_practice.xlsx")
print(f"样本量：{df.shape[0]} 行 × {df.shape[1]} 列")
print(df.head())
print("\n字段类型：")
print(df.dtypes)

# ---------------------------------------------------------------- 2. 清洗
title("2. 数据清洗")
# 2.1 删除无业务含义 / 全空的字段：id 是主键、Acc 是结果变量（开卡与否）、edad2 全空
df = df.drop(columns=["id", "Acc", "edad2"], errors="ignore")
print(f"删除 id/Acc/edad2 后：{df.shape[1]} 列")

# 2.2 重复值
n_dup = df.duplicated().sum()
df = df.drop_duplicates()
print(f"删除重复行 {n_dup} 条，剩余 {len(df)} 条")

# 2.3 缺失值：因变量缺失无法建模，用均值填补（教材做法；样本量小时可接受）
print("\n各字段缺失率：")
print((df.isnull().mean() * 100).round(2).to_string())
if df["avg_exp"].isnull().any():
    fill = df["avg_exp"].mean()
    df["avg_exp"] = df["avg_exp"].fillna(fill)
    print(f"avg_exp 缺失值用均值 {fill:.2f} 填补")

# 2.4 类别编码：gender 二值；edu_class 有序（学历越高数值越大）
df["gender"] = df["gender"].map({"Male": 1, "Female": 0})
edu_order = ["小学及以下", "中学", "大学", "研究生"]
# 学历有 1 条缺失，用众数补齐后再做有序编码
if df["edu_class"].isnull().any():
    mode = df["edu_class"].mode()[0]
    df["edu_class"] = df["edu_class"].fillna(mode)
    print(f"edu_class 缺失 1 条，用众数「{mode}」填补")
df["edu_class"] = df["edu_class"].map({v: i for i, v in enumerate(edu_order)})
print("\n编码后取值分布：")
print(df["gender"].value_counts().rename({1: "男", 0: "女"}).to_string())
print(df["edu_class"].value_counts().sort_index().to_string())

# ---------------------------------------------------------------- 3. 异常值
title("3. 异常值识别")
# 3.1 箱线图看分布（教材用 seaborn.boxplot，这里用 matplotlib 保持依赖最少）
fig, ax = plt.subplots(figsize=(6, 4))
ax.boxplot(df["dist_avg_income"].dropna(), vert=True, widths=0.5)
ax.set_ylabel("当地人均收入")
ax.set_title("dist_avg_income 箱线图")
save(fig, "二级_线性回归_箱线图")

# 3.2 3σ 法则找年龄异常：Age=999 这类"占位值"
z = np.abs(stats.zscore(df["Age"]))
outliers = df.loc[z > 3, "Age"]
print(f"3σ 法则检出 Age 异常值：{list(outliers)}")
if len(outliers):
    normal_mean = df.loc[z <= 3, "Age"].mean()
    df["Age"] = df["Age"].astype(float)
    df.loc[z > 3, "Age"] = normal_mean
    print(f"用正常样本均值 {normal_mean:.2f} 替换")

# 3.3 学历哑变量：无序类别不能直接进回归，转为 k-1 个 0/1 变量
dummy = pd.get_dummies(df["edu_class"], prefix="edu", drop_first=True).astype(int)
data = pd.concat([df, dummy], axis=1)
print(f"\n加入哑变量后字段数：{data.shape[1]}")

# ---------------------------------------------------------------- 4. 相关分析
title("4. 相关分析")
corr = data.corr(numeric_only=True)["avg_exp"].sort_values(ascending=False)
print("与月均支出的相关系数（Pearson）：")
print(corr.round(3).to_string())

fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(data["Income"], data["avg_exp"], alpha=0.7, color="#4A90E2", edgecolor="white")
ax.set_xlabel("年收入（万元）")
ax.set_ylabel("月均信用卡支出（元）")
ax.set_title("收入与月均支出的散点图")
ax.grid(alpha=0.3, linestyle="--")
save(fig, "二级_线性回归_散点图")

# ---------------------------------------------------------------- 5. 多元回归
title("5. 多元线性回归")
features = "gender + Age + Income + Ownrent + Selfempl + dist_home_val + dist_avg_income + edu_1 + edu_2 + edu_3"
model_1 = ols(f"avg_exp ~ {features}", data=data).fit()
print(f"R2 = {model_1.rsquared:.4f}   调整R2 = {model_1.rsquared_adj:.4f}   AIC = {model_1.aic:.1f}")
print("\n回归系数：")
print(model_1.params.round(4).to_string())

# ---------------------------------------------------------------- 6. 共线性
title("6. 共线性诊断（VIF）")
# VIF > 10 一般认为存在严重共线性；用"对其余自变量回归"的 R2 反推
def vif(frame, y_col):
    x_cols = [c for c in frame.columns if c != y_col]
    r2 = ols(f"{y_col} ~ " + " + ".join(x_cols), frame).fit().rsquared
    return 1.0 / (1.0 - r2)


exog = data[["gender", "Age", "Income", "Ownrent", "Selfempl",
             "dist_home_val", "dist_avg_income", "edu_class"]].dropna()
for col in exog.columns:
    print(f"  {col:<16} VIF = {vif(exog, col):6.2f}")

# 收入与当地人均收入高度共线，剔除 dist_avg_income 后重拟合
model_2 = ols("avg_exp ~ gender + Age + Income + Ownrent + Selfempl + dist_home_val + edu_1 + edu_2 + edu_3",
              data=data).fit()
print(f"\n剔除 dist_avg_income 后：R2 = {model_2.rsquared:.4f}   AIC = {model_2.aic:.1f}")

# ---------------------------------------------------------------- 7. 残差诊断
title("7. 残差诊断")
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter(model_2.predict(data), model_2.resid, alpha=0.7, color="#F5A623", edgecolor="white")
ax.axhline(0, color="#4A4A4A", linestyle="--", linewidth=1)
ax.set_xlabel("拟合值")
ax.set_ylabel("残差")
ax.set_title("残差 vs 拟合值（看是否喇叭口 = 异方差）")
save(fig, "二级_线性回归_残差图")

fig, ax = plt.subplots(figsize=(5.5, 5))
stats.probplot(model_2.resid, plot=ax)
ax.set_title("残差 Q-Q 图（看是否贴近对角线 = 正态）")
save(fig, "二级_线性回归_QQ图")

print(f"残差偏度 = {stats.skew(model_2.resid):.3f}（越接近 0 越对称）")

# ---------------------------------------------------------------- 8. 变量变换
title("8. 变量变换与模型对比")
data["ln_avg_exp"] = np.log(data["avg_exp"])
data["Age_sq"] = data["Age"] ** 2
data["Age_gender"] = data["Age"] * data["gender"]

models = {
    "基础线性": "avg_exp ~ gender + Age + Income + Ownrent + Selfempl + dist_home_val + edu_1 + edu_2 + edu_3",
    "对数因变量": "ln_avg_exp ~ gender + Age + Income + Ownrent + Selfempl + dist_home_val + edu_1 + edu_2 + edu_3",
    "加年龄二次项": "ln_avg_exp ~ gender + Age + Income + Ownrent + Selfempl + dist_home_val + edu_1 + edu_2 + edu_3 + Age_sq",
    "加交互项": "ln_avg_exp ~ gender + Age + Income + Ownrent + Selfempl + dist_home_val + edu_1 + edu_2 + edu_3 + Age_sq + Age_gender",
}
rows = []
for name, formula in models.items():
    m = ols(formula, data=data).fit()
    rows.append({"模型": name, "R2": round(m.rsquared, 4),
                 "调整R2": round(m.rsquared_adj, 4), "AIC": round(m.aic, 1)})
compare = pd.DataFrame(rows)
print(compare.to_string(index=False))

best_name = compare.sort_values("AIC").iloc[0]["模型"]
best = ols(models[best_name], data=data).fit()
print(f"\n按 AIC 最优模型：{best_name}")
print(best.summary().tables[1])

# ---------------------------------------------------------------- 9. 结论
title("9. 结论")
print("· 收入（Income）是月均支出的最强正相关因素，系数显著；")
print("· 当地人均收入与个人收入共线（VIF 高），保留其一即可；")
print("· 因变量取对数后残差更接近正态、异方差缓解，模型更稳；")
print("· 输出图片见 images/ 目录。")
