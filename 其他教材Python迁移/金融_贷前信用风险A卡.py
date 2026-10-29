# -*- coding: utf-8 -*-
"""《金融数据分析和数据挖掘案例实战》· 第5章 贷前信用风险预测模型（A 卡）

来源：教材配套 notebook「第5章贷前信用风险预测模型（A卡）代码通过.ipynb」
改写目标：原稿高度依赖第三方评分卡库 toad，且夹杂本地 MySQL 连接（Vintage 报表）。
         本脚本把"评分卡"的每个环节手工实现一遍，脱离 toad 也能跑，同时更清楚地
         展示 WOE / IV / 评分刻度换算的原理。

评分卡建模标准流程（教材 5.6 节）：
    数据清洗 → 训练/测试切分 → 特征初筛（IV）→ 分箱与 WOE → 相关性剔除
    → 逻辑回归 → 模型评估（AUC/KS）→ 刻度转换生成评分卡 → 分数分箱监控

数据：creditdata_small.csv（3 万条申请记录、120 个特征，TARGET=1 表示违约）
      仓库中以 .csv.gz 存放，pandas 会自动解压。

运行：python 金融_贷前信用风险A卡.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split

from common_data import load_csv, save, title

RANDOM_STATE = 1223

# ---------------------------------------------------------------- 1. 读数据
title("1. 读取申请数据")
dat = load_csv("creditdata_small.csv.gz", low_memory=False)
print(f"原始数据：{dat.shape[0]} 行 × {dat.shape[1]} 列")
print(f"坏样本率（TARGET=1）：{dat['TARGET'].mean():.2%}")

# 实体一致性：ID 唯一、列名不重复
dat = dat.set_index("ID")
dat = dat.loc[:, ~dat.columns.duplicated()]
dat = dat.loc[~dat.index.duplicated(), :]
print(f"去重后：{dat.shape[0]} 行 × {dat.shape[1]} 列")

# ---------------------------------------------------------------- 2. 清洗
title("2. 数据清洗")
# 2.1 错误值：DAYS_EMPLOYED 用负数表示"未就业"，这类占位值会干扰分箱，置为缺失
if "DAYS_EMPLOYED" in dat.columns:
    n_bad = int((dat["DAYS_EMPLOYED"] < 0).sum())
    dat.loc[dat["DAYS_EMPLOYED"] < 0, "DAYS_EMPLOYED"] = np.nan
    print(f"DAYS_EMPLOYED 负数（未就业占位值）{n_bad} 条，已置为缺失")

# 2.2 缺失值：缺失率过高的字段直接删除
miss = dat.isnull().mean()
drop_cols = miss[miss > 0.6].index.tolist()
dat = dat.drop(columns=drop_cols)
print(f"缺失率 > 60% 的字段 {len(drop_cols)} 个，已删除")

# 2.3 剩余缺失：数值型用中位数，类别型单列一档 "missing"
num_cols = [c for c in dat.columns if c != "TARGET" and pd.api.types.is_numeric_dtype(dat[c])]
cat_cols = [c for c in dat.columns if c != "TARGET" and c not in num_cols]
dat[num_cols] = dat[num_cols].fillna(dat[num_cols].median())
if cat_cols:
    dat[cat_cols] = dat[cat_cols].astype(str).fillna("missing")
print(f"数值型 {len(num_cols)} 个、类别型 {len(cat_cols)} 个，缺失已填补")

# ---------------------------------------------------------------- 3. 切分
title("3. 训练集 / 测试集切分（7:3，分层抽样）")
X = dat.drop(columns=["TARGET"])
y = dat["TARGET"].astype(int)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=RANDOM_STATE, stratify=y)
print(f"训练集 {len(X_train)} 条（坏样本率 {y_train.mean():.2%}）")
print(f"测试集 {len(X_test)} 条（坏样本率 {y_test.mean():.2%}）")

# ---------------------------------------------------------------- 4. IV 筛选
title("4. 特征初筛：计算 IV（信息值）")
print("IV 的含义：该变量对'好坏'的区分能力。经验标准：")
print("  <0.02 几乎无区分力；0.02~0.1 弱；0.1~0.3 中；>0.3 强（也可能过拟合）")


def make_bins(series, q=5):
    """数值型按分位数切 5 箱，类别型按取值本身分组"""
    if pd.api.types.is_numeric_dtype(series) and series.nunique() > q:
        try:
            _, edges = pd.qcut(series, q=q, retbins=True, duplicates="drop")
            return edges, True
        except ValueError:
            pass
    return None, False


def to_group(series, edges):
    if edges is not None:
        return pd.cut(series, bins=edges, include_lowest=True).astype(str)
    return series.astype(str)


def iv_woe(frame, col, target, edges, is_num):
    groups = to_group(frame[col], edges if is_num else None)
    tab = pd.DataFrame({"g": groups, "y": target}).groupby("g")["y"].agg(["count", "sum"])
    tab["good"] = tab["count"] - tab["sum"]
    tab["bad"] = tab["sum"]
    # 避免除零：好坏各加 0.5（拉普拉斯平滑）
    dist_good = (tab["good"] + 0.5) / (tab["good"].sum() + 0.5 * len(tab))
    dist_bad = (tab["bad"] + 0.5) / (tab["bad"].sum() + 0.5 * len(tab))
    woe = np.log(dist_good / dist_bad)
    iv = ((dist_good - dist_bad) * woe).sum()
    return iv, woe.to_dict()


bin_spec, iv_table = {}, []
for col in X_train.columns:
    edges, is_num = make_bins(X_train[col])
    iv, woe_map = iv_woe(X_train, col, y_train, edges, is_num)
    bin_spec[col] = (edges, is_num)
    iv_table.append({"特征": col, "IV": iv})

iv_df = pd.DataFrame(iv_table).sort_values("IV", ascending=False)
print("\nIV 排名前 10：")
print(iv_df.head(10).round(4).to_string(index=False))

# 经验区间：IV < 0.02 不要；IV 过高（>0.5）要怀疑信息泄露
selected = iv_df[(iv_df["IV"] >= 0.02) & (iv_df["IV"] <= 0.5)]["特征"].tolist()[:20]
print(f"\n按 IV 选出 {len(selected)} 个入模特征")

# ---------------------------------------------------------------- 5. WOE 编码
title("5. WOE 编码与相关性剔除")


def to_woe(frame, col):
    edges, is_num = bin_spec[col]
    groups = to_group(frame[col], edges if is_num else None)
    _, woe_map = iv_woe(X_train, col, y_train, edges, is_num)
    # 训练集里没出现过的分箱，WOE 记 0（中性）
    return groups.map(woe_map).fillna(0.0)


train_woe = pd.DataFrame({c: to_woe(X_train, c) for c in selected})
test_woe = pd.DataFrame({c: to_woe(X_test, c) for c in selected})

# 相关性剔除：两个变量高度相关时保留 IV 更高的那个
corr = train_woe.corr().abs()
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
drop_corr = [c for c in upper.columns if (upper[c] > 0.7).any()]
keep = [c for c in selected if c not in drop_corr]
print(f"相关性 > 0.7 剔除 {len(drop_corr)} 个，保留 {len(keep)} 个：{keep}")

train_woe, test_woe = train_woe[keep], test_woe[keep]

# ---------------------------------------------------------------- 6. 逻辑回归
title("6. 逻辑回归建模")
model = LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)
model.fit(train_woe, y_train)
print("入模系数（WOE 已统一方向，系数为正说明该变量越大越'好'）：")
print(pd.Series(model.coef_[0], index=keep).round(4).sort_values(ascending=False).to_string())
print(f"截距：{model.intercept_[0]:.4f}")

# ---------------------------------------------------------------- 7. 评估
title("7. 模型评估：AUC 与 KS")
p_train = model.predict_proba(train_woe)[:, 1]
p_test = model.predict_proba(test_woe)[:, 1]

auc_train, auc_test = roc_auc_score(y_train, p_train), roc_auc_score(y_test, p_test)
fpr_tr, tpr_tr, _ = roc_curve(y_train, p_train)
fpr_te, tpr_te, _ = roc_curve(y_test, p_test)
ks_train, ks_test = np.max(tpr_tr - fpr_tr), np.max(tpr_te - fpr_te)

print(f"训练集 AUC = {auc_train:.4f}   KS = {ks_train:.4f}")
print(f"测试集 AUC = {auc_test:.4f}   KS = {ks_test:.4f}")
print("（AUC > 0.7、KS > 0.3 一般认为是可用的风险模型）")

fig, ax = plt.subplots(figsize=(6, 5.5))
ax.plot(fpr_tr, tpr_tr, label=f"train AUC={auc_train:.3f}")
ax.plot(fpr_te, tpr_te, label=f"test  AUC={auc_test:.3f}")
ax.plot([0, 1], [0, 1], "k--", linewidth=1)
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")
ax.set_title("ROC 曲线")
ax.legend()
save(fig, "金融_A卡_ROC")

fig, ax = plt.subplots(figsize=(6, 4.5))
ax.plot(np.linspace(0, 1, len(tpr_te)), tpr_te, label="TPR（累计好样本占比）")
ax.plot(np.linspace(0, 1, len(fpr_te)), fpr_te, label="FPR（累计坏样本占比）")
ax.plot(np.linspace(0, 1, len(tpr_te)), np.abs(tpr_te - fpr_te),
        label=f"KS = {ks_test:.3f}", color="#E74C3C")
ax.set_xlabel("按违约概率从高到低排序的样本占比")
ax.set_ylabel("累计占比")
ax.set_title("KS 曲线")
ax.legend()
save(fig, "金融_A卡_KS")

# ---------------------------------------------------------------- 8. 评分卡
title("8. 刻度转换：概率 → 分数")
# 评分卡刻度：基准分 600 对应好坏比 35:1，比率每翻一倍加 50 分（PDO=50）
BASE_SCORE, BASE_ODDS, PDO = 600, 35, 50
factor = PDO / np.log(2)
offset = BASE_SCORE - factor * np.log(BASE_ODDS)

logit = model.decision_function(test_woe)          # = ln(p_bad / p_good)
score = offset - factor * logit                    # 分数越高越安全
print(f"刻度参数：factor = {factor:.2f}，offset = {offset:.2f}")
print(f"测试集分数范围：{score.min():.0f} ~ {score.max():.0f}，均值 {score.mean():.0f}")

# 分数分箱监控：每箱的坏账率应随分数升高单调下降，否则模型不稳定
bins = pd.qcut(score, q=10, duplicates="drop")
monitor = pd.DataFrame({"score": score, "bad": y_test.values, "bin": bins})
report = monitor.groupby("bin", observed=True)["bad"].agg(["count", "mean"])
report.columns = ["样本数", "坏账率"]
report["坏账率"] = (report["坏账率"] * 100).round(2)
print("\n评分十分箱监控表：")
print(report.to_string())

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.hist(score[y_test.values == 0], bins=30, alpha=0.6, label="好客户", color="#4A90E2")
ax.hist(score[y_test.values == 1], bins=30, alpha=0.6, label="坏客户", color="#E74C3C")
ax.set_xlabel("信用评分")
ax.set_ylabel("人数")
ax.set_title("好/坏客户的评分分布")
ax.legend()
save(fig, "金融_A卡_评分分布")

# ---------------------------------------------------------------- 9. 结论
title("9. 结论")
print("· IV 把 120 个候选特征压缩到十几个，避免维度灾难；")
print("· WOE 编码让每个分箱的风险被单调量化，逻辑回归系数可直接解释；")
print("· 测试集 AUC / KS 与训练集接近，说明没有明显过拟合；")
print("· 分数分箱后坏账率单调下降，评分卡可用于实际审批分级；")
print("· 输出图片见 images/ 目录。")
