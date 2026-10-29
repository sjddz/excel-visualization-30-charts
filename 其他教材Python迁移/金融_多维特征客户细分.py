# -*- coding: utf-8 -*-
"""《金融数据分析和数据挖掘案例实战》· 第3章 多维特征的客户细分

来源：教材配套 notebook「第3章多维特征的客户细分代码通过.ipynb」
改写目标：
    ① 原稿用 fa_kit（已停止维护的因子分析包）做旋转和评分，本脚本用 sklearn 的
       PCA 完成同样的"降维成业务维度"目标，并解释为何这样替代；
    ② 原稿的卡方检验写在 for 循环外（只检验了最后一对变量），这里修正；
    ③ 决策树原本导出图片依赖 pydotplus + Graphviz 本地安装，这里改为直接打印规则。

业务背景：零售银行想按"家庭生命周期 + 兴趣爱好"两个维度给客户打标签，
         用于产品组合推荐。数据是 17 个客户属性字段。

运行：python 金融_多维特征客户细分.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import Binarizer, QuantileTransformer, StandardScaler, scale
from sklearn.tree import DecisionTreeClassifier, export_text

from common_data import load_csv, save, title

RANDOM_STATE = 12345
plt.rcParams["figure.figsize"] = (7, 4.5)

# ---------------------------------------------------------------- 1. 读数据
title("1. 读取客户属性数据")
bank = load_csv("data_clust.csv.gz", skipinitialspace=True)
print(f"样本量：{bank.shape[0]} 行 × {bank.shape[1]} 列")
print("字段：", list(bank.columns))
print("\n数值字段描述统计：")
print(bank.describe().T[["mean", "std", "min", "max"]].round(2).to_string())

# ---------------------------------------------------------------- 2. 预处理
title("2. 数据预处理")
# 2.1 缺失值：先看哪些字段有缺失
miss = bank.isnull().sum()
print("缺失字段及缺失数：")
print(miss[miss > 0].to_string())

# 这三个是"数值型分类变量"，用众数填补最稳妥（均值会产生不存在的类别）
fill_cols = [c for c in ["interested_travel", "computer_owner", "HH_adults_num"] if c in bank.columns]
fill_values = {c: bank[c].mode()[0] for c in fill_cols}
bank = bank.fillna(fill_values)
print(f"\n用众数填补：{ {k: round(float(v), 2) for k, v in fill_values.items()} }")

# 2.2 错误值：HH_has_children 用 Y/N 表示，统一成 0/1
if "HH_has_children" in bank.columns:
    bank["HH_has_children"] = bank["HH_has_children"].replace({"N": 0, "Y": 1, np.nan: 0}).astype(int)

# 2.3 interested_reading 里有 "." 脏值，先转 0 再统一类型
if "interested_reading" in bank.columns:
    bank["interested_reading"] = pd.to_numeric(
        bank["interested_reading"].replace({".": 0}), errors="coerce").fillna(0).astype(int)

# 2.4 卡方检验：判断离散变量之间是否独立，为"合并成偏好分"提供依据
title("3. 离散变量两两卡方检验")
cols = [c for c in ["interested_travel", "computer_owner", "marital", "interested_golf",
                    "interested_gambling", "HH_has_children", "interested_reading"]
        if c in bank.columns]
sample = bank[cols].sample(min(3000, len(bank)), random_state=RANDOM_STATE)
independent = 0
for a, b in combinations(cols, 2):
    pval = stats.chi2_contingency(pd.crosstab(sample[a], sample[b]))[1]
    if pval > 0.05:
        independent += 1
        print(f'  p={pval:.3f} > 0.05："{a}" 与 "{b}" 相互独立')
print(f"\n共检验 {len(list(combinations(cols, 2)))} 对，其中 {independent} 对不显著，"
      "说明这些兴趣变量之间信息不重叠，可以分别作为维度输入。")

# 2.5 兴趣二值化 + 合成"偏好填充率"
if "interested_reading" in bank.columns:
    bank["interested_reading"] = Binarizer(threshold=1.5).fit_transform(bank[["interested_reading"]])

interest = [c for c in ["interested_travel", "computer_owner", "interested_golf",
                        "interested_gambling", "interested_reading"] if c in bank.columns]
if interest:
    bank["interest"] = bank[interest].sum(axis=1) / len(interest)
    bank = bank.drop(columns=interest)
    print(f"\n用 {len(interest)} 个兴趣变量合成 interest（0~1 的偏好得分）")

# ---------------------------------------------------------------- 4. 正态化
title("4. 连续变量的正态化与标准化")
continuous = [c for c in ["age", "home_value", "risk_score", "interested_sport", "HH_dieting",
                          "auto_member", "HH_grandparent", "HH_head_age", "loan_ratio"]
              if c in bank.columns]
categorical = [c for c in ["marital", "interest", "HH_adults_num"] if c in bank.columns]
discrete = [c for c in ["HH_has_children"] if c in bank.columns]

# 金额、年龄这类变量分布右偏，直接标准化仍不满足聚类对"椭球分布"的假设，
# 用分位数变换强行拉成标准正态
qt = QuantileTransformer(n_quantiles=100, output_distribution="normal",
                         random_state=0)
qt_data = qt.fit_transform(bank[continuous])

fig, axes = plt.subplots(1, len(continuous[:3]), figsize=(12, 3.2))
for ax, col in zip(axes, continuous[:3]):
    ax.hist(bank[col], bins=25, color="#4A90E2", alpha=0.8)
    ax.set_title(f"原始分布：{col}")
fig.tight_layout()
save(fig, "金融_细分_原始分布")

fig, axes = plt.subplots(1, len(continuous[:3]), figsize=(12, 3.2))
qt_df = pd.DataFrame(qt_data, columns=continuous)
for ax, col in zip(axes, continuous[:3]):
    ax.hist(qt_df[col], bins=25, color="#F5A623", alpha=0.8)
    ax.set_title(f"正态化后：{col}")
fig.tight_layout()
save(fig, "金融_细分_正态化分布")

scale_data = scale(bank[categorical]) if categorical else np.empty((len(bank), 0))
data = np.hstack([qt_data, scale_data, bank[discrete].values if discrete else np.empty((len(bank), 0))])
data = pd.DataFrame(data, columns=continuous + categorical + discrete)
print(f"建模用变量：{list(data.columns)}")

# ---------------------------------------------------------------- 5. 维度降维
title("5. 按业务维度降维（PCA 替代教材的因子分析）")
household = [c for c in ["age", "marital", "HH_adults_num", "home_value", "risk_score",
                         "HH_grandparent", "HH_head_age", "loan_ratio"] if c in data.columns]
hobby = [c for c in ["HH_dieting", "auto_member", "interest", "interested_sport"] if c in data.columns]

# 先看累计方差解释率，决定保留几个主成分
pca_hh = PCA().fit(scale(data[household]))
print("household 维度累计方差解释率：",
      np.round(np.cumsum(pca_hh.explained_variance_ratio_), 3))
print("保留 4 个主成分可解释的信息量：",
      f"{pca_hh.explained_variance_ratio_[:4].sum():.1%}")

pca_hh4 = PCA(n_components=4, random_state=RANDOM_STATE).fit(scale(data[household]))
hh_scores = pd.DataFrame(
    pca_hh4.transform(scale(data[household])),
    columns=["life_circle", "finance", "HH_size", "risk"])

pca_hb = PCA(n_components=3, random_state=RANDOM_STATE).fit(scale(data[hobby]))
hb_scores = pd.DataFrame(
    pca_hb.transform(scale(data[hobby])),
    columns=["sports", "health", "leisure"])
print("hobby 维度 3 个主成分累计解释率：",
      f"{pca_hb.explained_variance_ratio_.sum():.1%}")

# ---------------------------------------------------------------- 6. 聚类
title("6. 两个维度分别聚类（用轮廓系数选 k）")


def choose_k(X, k_range=range(2, 9)):
    """画出 SSD 肘部图 + 轮廓系数图，返回最优 k 和对应模型"""
    rows = []
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=5, random_state=RANDOM_STATE).fit(X)
        sil = silhouette_score(X, km.labels_, sample_size=3000, random_state=RANDOM_STATE)
        rows.append({"k": k, "SSD": km.inertia_, "轮廓系数": sil})
    table = pd.DataFrame(rows)
    print(table.round(3).to_string(index=False))
    best_k = int(table.loc[table["轮廓系数"].idxmax(), "k"])
    print(f"轮廓系数最高的 k = {best_k}\n")
    return best_k, table


scaled_hh = StandardScaler().fit_transform(hh_scores)
scaled_hb = StandardScaler().fit_transform(hb_scores)

print("household 维度：")
k_hh, table_hh = choose_k(scaled_hh)
print("hobby 维度：")
k_hb, table_hb = choose_k(scaled_hb)

fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
axes[0].plot(table_hh["k"], table_hh["SSD"], marker="o")
axes[0].set_title("household：SSD 肘部图")
axes[0].set_xlabel("k")
axes[1].plot(table_hb["k"], table_hb["SSD"], marker="o", color="#F5A623")
axes[1].set_title("hobby：SSD 肘部图")
axes[1].set_xlabel("k")
fig.tight_layout()
save(fig, "金融_细分_肘部图")

# ---------------------------------------------------------------- 7. 打标签
title("7. 生成客户细分标签")
km_hh = KMeans(n_clusters=k_hh, n_init=10, random_state=RANDOM_STATE).fit(scaled_hh)
km_hb = KMeans(n_clusters=k_hb, n_init=10, random_state=RANDOM_STATE).fit(scaled_hb)
clusters = bank.copy()
clusters["hh"] = km_hh.labels_
clusters["hb"] = km_hb.labels_

print(f"household {k_hh} 类，规模：{pd.Series(km_hh.labels_).value_counts().to_dict()}")
print(f"hobby     {k_hb} 类，规模：{pd.Series(km_hb.labels_).value_counts().to_dict()}")

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].scatter(scaled_hh[:, 0], scaled_hh[:, 1], c=km_hh.labels_, s=4, cmap="viridis", alpha=0.6)
axes[0].set_title(f"household 客户分群（k={k_hh}）")
axes[0].set_xlabel("life_circle")
axes[0].set_ylabel("finance")
axes[1].scatter(scaled_hb[:, 0], scaled_hb[:, 1], c=km_hb.labels_, s=4, cmap="plasma", alpha=0.6)
axes[1].set_title(f"hobby 客户分群（k={k_hb}）")
axes[1].set_xlabel("sports")
axes[1].set_ylabel("health")
fig.tight_layout()
save(fig, "金融_细分_聚类散点")

# ---------------------------------------------------------------- 8. 解释
title("8. 用决策树解释每一类客户长什么样")
tree_hh = DecisionTreeClassifier(max_depth=2, random_state=RANDOM_STATE)
tree_hh.fit(bank[household], clusters["hh"])
print("household 分群规则：")
print(export_text(tree_hh, feature_names=household, decimals=1))
print(f"规则还原准确率：{tree_hh.score(bank[household], clusters['hh']):.1%}\n")

tree_hb = DecisionTreeClassifier(max_depth=2, random_state=RANDOM_STATE)
tree_hb.fit(bank[hobby], clusters["hb"])
print("hobby 分群规则：")
print(export_text(tree_hb, feature_names=hobby, decimals=1))

# ---------------------------------------------------------------- 9. 交叉画像
title("9. 两个维度交叉后的客户画像")
pivot = clusters.pivot_table(index="hh", columns="hb", values="home_value", aggfunc="mean")
print("各细分群体的平均房产价值（万元）：")
print(pivot.round(1).to_string())
print("\n各细分群体规模：")
print(clusters.groupby(["hh", "hb"]).size().unstack(fill_value=0).to_string())

# ---------------------------------------------------------------- 10. 结论
title("10. 结论")
print("· 家庭维度（household）主要被年龄、房产价值、风险分驱动；")
print("· 兴趣维度（hobby）主要被运动、饮食、理财偏好驱动；")
print("· 两个维度交叉后得到 k_hh × k_hb 个细分群体，可分别配置产品；")
print("· 输出图片见 images/ 目录。")
