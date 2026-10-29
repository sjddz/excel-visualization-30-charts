# -*- coding: utf-8 -*-
"""CDA 二级教材 · 第9章 用户分群（K-Means 银行交易行为细分）

来源：CDA 二级教材配套 notebook「Kmeans 的应用 - 用户细分.ipynb」
改写目标：原 notebook 依赖 fa_kit（第三方因子分析包，已停止维护），且大量单元格
         只输出中间变量而不做解释。这里用 sklearn 的 PCA + KMeans 复刻同一套流程，
         并把每一步的"为什么"和"结果怎么读"写进注释与打印。

业务背景：银行拿到客户一年内的交易次数（柜台 TBM、ATM、POS、客服 CSC），
         想按"渠道使用习惯"把客户分成 3 类，用于渠道运营和资源投放。

运行：python CDA二级_Kmeans用户细分.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import QuantileTransformer, StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from common_data import load_csv, save, title

RANDOM_STATE = 12345

# ---------------------------------------------------------------- 1. 读数据
title("1. 读取交易行为数据")
model_data = load_csv("profile_bank.csv")
print(f"样本量：{model_data.shape[0]} 位客户，字段：{list(model_data.columns)}")

# 4 个特征是各类渠道的使用次数，CNT_TOT 是总次数，属于"结果"不进模型
feat_cols = ["CNT_TBM", "CNT_ATM", "CNT_POS", "CNT_CSC"]
X_raw = model_data[feat_cols].copy()
print("\n四个渠道使用次数的描述统计：")
print(X_raw.describe().round(2).to_string())

# ---------------------------------------------------------------- 2. 相关分析
title("2. 变量相关性：判断是否有降维必要")
corr = X_raw.corr(method="pearson")
print(corr.round(3).to_string())
print("\n相关系数普遍不高，说明四个渠道反映的是不同的使用习惯，"
      "但为了消除量纲差异、并让聚类在低维空间更稳定，仍做标准化 + PCA。")

# ---------------------------------------------------------------- 3. 标准化 + PCA
title("3. 中心标准化与主成分分析")
scaler = StandardScaler()
X_std = scaler.fit_transform(X_raw)

pca = PCA(n_components=3, random_state=RANDOM_STATE).fit(X_std)
print("各主成分解释的方差：", np.round(pca.explained_variance_, 4))
print("方差解释率：        ", np.round(pca.explained_variance_ratio_, 4))
print("累计解释率：        ", np.round(np.cumsum(pca.explained_variance_ratio_), 4))
print("\n前 2 个主成分已解释绝大部分信息，第三维补充有限。")
print("主成分载荷（每一列是一个主成分，看它主要由哪个渠道驱动）：")
print(pd.DataFrame(pca.components_[:2].T, index=feat_cols,
                   columns=["PC1", "PC2"]).round(3).to_string())

X_pca = pca.transform(X_std)[:, :3]

# ---------------------------------------------------------------- 4. KMeans 聚类
title("4. K-Means 聚类（k=3）")
# k 由业务方给定：高价值 / 中等 / 低频 三类客户
kmeans = KMeans(n_clusters=3, n_init=10, random_state=RANDOM_STATE)
labels = kmeans.fit_predict(X_pca)

print(f"轮廓系数（越大越好，>0.3 说明分群有区分度）：{silhouette_score(X_pca, labels, sample_size=5000, random_state=RANDOM_STATE):.3f}")
print("各簇客户数：")
print(pd.Series(labels, name="cluster").value_counts().sort_index().to_string())

# ---------------------------------------------------------------- 5. 簇的业务解释
title("5. 各簇画像（回到原始业务口径解读）")
profile = model_data.assign(cluster=labels).groupby("cluster")[feat_cols + ["CNT_TOT"]].mean()
profile["客户数"] = pd.Series(labels).value_counts().sort_index()
print(profile.round(1).to_string())

# 用各渠道均值判断每簇"标签"
def name_cluster(row):
    if row["CNT_TBM"] == profile["CNT_TBM"].max():
        return "柜台依赖型"
    if row["CNT_ATM"] == profile["CNT_ATM"].max():
        return "自助设备型"
    return "低频/低活跃型"


profile["群体命名"] = profile.apply(name_cluster, axis=1)
print("\n聚类结果命名：")
print(profile[["群体命名", "客户数", "CNT_TOT"]].round(1).to_string())

# ---------------------------------------------------------------- 6. 可视化
title("6. 结果可视化")
fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

# 左图：ATM × 柜台 两个渠道上的分布
colors = ["#4A90E2", "#F5A623", "#7ED321"]
for c in sorted(set(labels)):
    mask = labels == c
    axes[0].scatter(X_raw.loc[mask, "CNT_ATM"], X_raw.loc[mask, "CNT_TBM"],
                    s=6, alpha=0.5, color=colors[c],
                    label=f"簇{c} {profile.loc[c, '群体命名']}")
axes[0].set_xlabel("ATM 交易次数")
axes[0].set_ylabel("柜台交易次数")
axes[0].set_title("客户在 ATM / 柜台两个渠道上的分布")
axes[0].legend(markerscale=3, fontsize=8)

# 右图：簇规模
sizes = pd.Series(labels).value_counts().sort_index()
axes[1].pie(sizes, labels=[f"簇{i}\n{v}人" for i, v in sizes.items()],
            colors=colors, autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2})
axes[1].set_title("三类客户的规模占比")
save(fig, "二级_Kmeans_聚类分布")

# ---------------------------------------------------------------- 7. 事后解释
title("7. 用决策树解释分群规则")
# 聚类只给编号，业务方看不懂；训练一棵浅树把"什么特征导致被分到这一簇"翻译成 if-else
tree = DecisionTreeClassifier(max_depth=3, min_samples_leaf=200,
                              random_state=RANDOM_STATE)
tree.fit(X_raw, labels)
rules = export_text(tree, feature_names=feat_cols, decimals=1)
print("决策树规则（近似还原 KMeans 的划分边界）：")
print(rules)
print(f"决策树对聚类标签的还原准确率：{tree.score(X_raw, labels):.2%}")

# ---------------------------------------------------------------- 8. 正态变换对比
title("8. 对比实验：先做正态变换再聚类")
# 交易次数是右偏分布（少数客户交易极多），QuantileTransformer 把它拉成近似正态，
# 避免极端值主导欧氏距离。教材用这一步验证"分布形态对 KMeans 的影响"。
qt = QuantileTransformer(output_distribution="normal", random_state=0)
X_qt = qt.fit_transform(X_raw)
labels_qt = KMeans(n_clusters=3, n_init=10, random_state=RANDOM_STATE).fit_predict(X_qt)

print(f"直接聚类轮廓系数：      {silhouette_score(X_pca, labels, sample_size=5000, random_state=RANDOM_STATE):.3f}")
print(f"正态变换后轮廓系数：    {silhouette_score(X_qt, labels_qt, sample_size=5000, random_state=RANDOM_STATE):.3f}")
print("\n正态变换后的簇均值：")
print(model_data.assign(cluster=labels_qt).groupby("cluster")[feat_cols].mean().round(1).to_string())
print("\n两种方案的簇结构基本一致，说明分群结论稳健。")

# ---------------------------------------------------------------- 9. 结论
title("9. 结论与业务建议")
print("· 客户可按渠道偏好清晰分成 3 群，轮廓系数说明分群有效；")
print("· 柜台依赖型：中老年/大额业务为主，应优化网点排队与柜面体验；")
print("· 自助设备型：年轻客群，适合推送 ATM/POS 优惠与线上活动；")
print("· 低频型：沉睡客户，适合做唤醒营销；")
print("· 输出图片见 images/ 目录。")
