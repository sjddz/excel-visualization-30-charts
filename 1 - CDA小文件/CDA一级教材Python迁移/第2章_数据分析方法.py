# -*- coding: utf-8 -*-
"""
第2章 数据分析方法
复现6种经典分析范式：波士顿矩阵、RFM模型、同期群分析、漏斗图、相关分析、用户忠诚度
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第2章 数据分析方法")
print("=" * 60)

D1 = ch("第2章 数据分析方法/1、分析的基础范式/data-有答案")

# ============================================================
# 1) 波士顿矩阵：按品牌聚合销售额与增长率
# ============================================================
print("\n--- 2.1 波士顿矩阵 ---")
f = os.path.join(D1, "1-1波士顿矩阵-参考.xlsx")
sale_df = pd.read_excel(f, sheet_name="销售表")
sale_df["销售日期"] = pd.to_datetime(sale_df["销售日期"])
sale_df["年月"] = sale_df["销售日期"].dt.to_period("M")

# 按品牌聚合月度销售额
brand_month = sale_df.groupby(["品牌", "年月"])["订单金额"].sum().reset_index()
brand_total = brand_month.groupby("品牌")["订单金额"].sum().reset_index().rename(columns={"订单金额": "总销售额"})
months = brand_month["年月"].nunique()
brand_total["月均销售额"] = brand_total["总销售额"] / months

# 计算环比增长率（最后月 vs 第一月）
first_month = brand_month["年月"].min()
last_month = brand_month["年月"].max()
brand_first = brand_month[brand_month.年月 == first_month].set_index("品牌")["订单金额"]
brand_last = brand_month[brand_month.年月 == last_month].set_index("品牌")["订单金额"]
brand_total = brand_total.set_index("品牌")
brand_total["增长率"] = (brand_last - brand_first) / brand_first
brand_total = brand_total.reset_index()
print(brand_total)

fig, ax = new_fig((8, 6))
x_mean = brand_total["月均销售额"].mean()
y_mean = brand_total["增长率"].mean()
for _, row in brand_total.iterrows():
    xv, yv = row["月均销售额"], row["增长率"]
    if xv >= x_mean and yv >= y_mean:
        c, cat = C_ORANGE, "明星"
    elif xv >= x_mean and yv < y_mean:
        c, cat = C_GREEN, "现金牛"
    elif xv < x_mean and yv >= y_mean:
        c, cat = C_RED, "问题"
    else:
        c, cat = C_GRAY, "瘦狗"
    ax.scatter(xv, yv, s=300, color=c, zorder=3, edgecolor="white", linewidth=2)
    ax.annotate(f"{row['品牌']}\n({cat})", (xv, yv), fontsize=9, ha="center",
                xytext=(0, 15), textcoords="offset points", fontweight="bold")
ax.axvline(x_mean, color=C_GRAY, linestyle="--", alpha=0.5)
ax.axhline(y_mean, color=C_GRAY, linestyle="--", alpha=0.5)
ax.set_xlabel("月均销售额")
ax.set_ylabel("增长率")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.0%}"))
style_ax(ax, "波士顿矩阵（BCG Matrix）- 品牌分析")
save(fig, "ch02_01_波士顿矩阵")

# ============================================================
# 2) RFM模型
# ============================================================
print("\n--- 2.2 RFM模型 ---")
f = os.path.join(D1, "1-2RFM模型-参考.xlsx")
rfm_raw = pd.read_excel(f, sheet_name="原始数据")
print(f"原始数据: {rfm_raw.shape}, 列={list(rfm_raw.columns)}")

# 列：流水号, 用户编号, ..., 消费日期, 消费金额
id_col = "用户编号"
date_col = [c for c in rfm_raw.columns if "日期" in str(c)][0]
amt_col = [c for c in rfm_raw.columns if "金额" in str(c)][0]
print(f"RFM: ID={id_col}, Date={date_col}, Amount={amt_col}")

rfm_raw[date_col] = pd.to_datetime(rfm_raw[date_col])
ref_date = rfm_raw[date_col].max() + pd.Timedelta(days=1)
rfm = rfm_raw.groupby(id_col).agg(
    R=(date_col, lambda x: (ref_date - x.max()).days),
    F=(id_col, "count"),
    M=(amt_col, "sum")
).reset_index()
rfm["R_score"] = pd.qcut(rfm["R"], 5, labels=[5, 4, 3, 2, 1]).astype(int)
rfm["F_score"] = pd.qcut(rfm["F"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
rfm["M_score"] = pd.qcut(rfm["M"], 5, labels=[1, 2, 3, 4, 5]).astype(int)

def seg(row):
    r, f, m = row["R_score"], row["F_score"], row["M_score"]
    if r >= 4 and f >= 4 and m >= 4: return "重要价值客户"
    if r >= 4 and f <= 2: return "重要发展客户"
    if r <= 2 and f >= 4: return "重要保持客户"
    if r <= 2 and f <= 2: return "重要挽留客户"
    return "一般客户"
rfm["segment"] = rfm.apply(seg, axis=1)

fig, ax = new_fig((8, 5))
sc = rfm["segment"].value_counts()
colors = [PALETTE[i % len(PALETTE)] for i in range(len(sc))]
ax.barh(range(len(sc)), sc.values, color=colors, zorder=3)
ax.set_yticks(range(len(sc)))
ax.set_yticklabels(sc.index)
ax.set_xlabel("客户数")
for i, v in enumerate(sc.values):
    ax.text(v + max(sc.values) * 0.01, i, str(v), va="center", fontsize=11)
style_ax(ax, "RFM模型客户分群")
save(fig, "ch02_02_RFM客户分群")

fig, ax = new_fig((8, 6))
for i, s in enumerate(rfm["segment"].unique()):
    sub = rfm[rfm.segment == s]
    ax.scatter(sub["R"], sub["F"], s=sub["M"] / 50, alpha=0.5,
               color=PALETTE[i % len(PALETTE)], label=s, zorder=3)
ax.set_xlabel("R (最近消费间隔/天)")
ax.set_ylabel("F (消费频次)")
ax.legend(fontsize=8, loc="upper left")
style_ax(ax, "RFM分布（气泡大小=消费金额）")
save(fig, "ch02_03_RFM散点")

# ============================================================
# 3) 同期群分析
# ============================================================
print("\n--- 2.3 同期群分析 ---")
f = os.path.join(D1, "1-4同期群分析-参考.xlsx")
login_df = pd.read_excel(f, sheet_name="用户登录明细")
print(f"登录明细: {login_df.shape}, 列={list(login_df.columns)}")

id_col = "用户编号"
date_col = "登录日期"
login_df[date_col] = pd.to_datetime(login_df[date_col])
login_df["month"] = login_df[date_col].dt.to_period("M")
first_login = login_df.groupby(id_col)[date_col].min().dt.to_period("M")
login_df["cohort"] = login_df[id_col].map(first_login)
cc = login_df.groupby(["cohort", "month"])[id_col].nunique().reset_index()
cc["period"] = (cc["month"] - cc["cohort"]).apply(lambda x: x.n)
pivot = cc.pivot_table(index="cohort", columns="period", values=id_col)
sizes = pivot.iloc[:, 0]
retention = pivot.divide(sizes, axis=0).round(3)

fig, ax = new_fig((10, 6))
im = ax.imshow(retention.values, cmap=plt.cm.Blues, aspect="auto", vmin=0, vmax=1)
ax.set_xticks(range(len(retention.columns)))
ax.set_xticklabels(retention.columns)
ax.set_yticks(range(len(retention.index)))
ax.set_yticklabels([str(i) for i in retention.index])
for i in range(len(retention.index)):
    for j in range(len(retention.columns)):
        v = retention.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=8,
                    color="white" if v > 0.5 else C_DARK)
ax.set_xlabel("留存期（月）")
ax.set_ylabel("同期群（首次登录月）")
ax.set_title("同期群留存分析", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
fig.colorbar(im, ax=ax, shrink=0.8, label="留存率")
save(fig, "ch02_04_同期群留存")

# ============================================================
# 4) 漏斗图
# ============================================================
print("\n--- 2.4 漏斗图 ---")
f = os.path.join(D1, "2-1漏斗图-参考.xlsx")
funnel_df = pd.read_excel(f, sheet_name="Sheet1", header=2)
funnel_df = funnel_df.dropna(how="all").dropna(axis=1, how="all")
print(f"漏斗解析: {funnel_df.shape}, 列={list(funnel_df.columns)}")
print(funnel_df)

stage_col = "阶段"
val_col = "用户数"
funnel_data = funnel_df[[stage_col, val_col]].dropna()
funnel_data = funnel_data[funnel_data[val_col] > 0].sort_values(val_col, ascending=False)

fig, ax = new_fig((8, 5))
vals = funnel_data[val_col].values
stages = funnel_data[stage_col].values
max_v = vals[0]
for i, (s, v) in enumerate(zip(stages, vals)):
    w = v / max_v
    left = (1 - w) / 2
    ax.barh(len(stages) - i - 1, w, left=left, height=0.7, color=PALETTE[i % len(PALETTE)], zorder=3)
    ax.text(0.5, len(stages) - i - 1, f"{s}: {v:,.0f} ({v/max_v:.1%})", ha="center", va="center",
            fontsize=10, color="white", fontweight="bold")
ax.set_xlim(0, 1)
ax.set_yticks([])
ax.set_xticks([])
for s in ["top", "right", "left", "bottom"]:
    ax.spines[s].set_visible(False)
ax.set_title("转化漏斗图", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
save(fig, "ch02_05_漏斗图")

# ============================================================
# 5) 相关分析
# ============================================================
print("\n--- 2.5 相关分析 ---")
f = os.path.join(D1, "3-1相关分析-参考.xlsx")
corr_df = pd.read_excel(f, sheet_name="原始数据")
print(f"相关分析: {corr_df.shape}, 列={list(corr_df.columns)}")
print(corr_df.head())

num_cols = corr_df.select_dtypes(include=[np.number]).columns.tolist()
corr_mat = corr_df[num_cols].corr()

fig, ax = new_fig((6, 5))
im = ax.imshow(corr_mat.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
ax.set_xticks(range(len(num_cols)))
ax.set_xticklabels(num_cols, rotation=45, ha="right")
ax.set_yticks(range(len(num_cols)))
ax.set_yticklabels(num_cols)
for i in range(len(num_cols)):
    for j in range(len(num_cols)):
        v = corr_mat.values[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=10,
                color="white" if abs(v) > 0.5 else C_DARK)
ax.set_title("相关系数矩阵", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
fig.colorbar(im, ax=ax, shrink=0.8, label="相关系数")
save(fig, "ch02_06_相关系数矩阵")

# 散点+回归线
if len(num_cols) == 2:
    x, y = num_cols[0], num_cols[1]
    fig, ax = new_fig((7, 5))
    ax.scatter(corr_df[x], corr_df[y], s=40, alpha=0.6, color=C_BLUE, zorder=3, edgecolor="white")
    z = np.polyfit(corr_df[x], corr_df[y], 1)
    xs = np.linspace(corr_df[x].min(), corr_df[x].max(), 100)
    ax.plot(xs, np.polyval(z, xs), color=C_RED, linewidth=2, linestyle="--", zorder=4)
    r = corr_df[[x, y]].corr().iloc[0, 1]
    ax.text(0.05, 0.95, f"r = {r:.4f}", transform=ax.transAxes, fontsize=12,
            verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    style_ax(ax, "相关分析散点图与回归线")
    save(fig, "ch02_07_相关散点回归")

# ============================================================
# 6) 用户忠诚度模型
# ============================================================
print("\n--- 2.6 用户忠诚度模型 ---")
f = os.path.join(D1, "1-3用户忠诚度模型-参考.xlsx")
loyalty_df = pd.read_excel(f, sheet_name="销售流水表")
print(f"销售流水: {loyalty_df.shape}, 列={list(loyalty_df.columns)}")

id_col = "会员编号"
date_col = [c for c in loyalty_df.columns if "日期" in str(c)][0]
amt_col = [c for c in loyalty_df.columns if "金额" in str(c)][0]
loyalty_df[date_col] = pd.to_datetime(loyalty_df[date_col])

# 计算忠诚度指标：消费频次、最近消费、总金额、消费持续天数
loy = loyalty_df.groupby(id_col).agg(
    首次消费=(date_col, "min"),
    末次消费=(date_col, "max"),
    消费频次=(id_col, "count"),
    总金额=(amt_col, "sum")
).reset_index()
loy["活跃天数"] = (loy["末次消费"] - loy["首次消费"]).dt.days
loy["平均消费间隔"] = loy["活跃天数"] / loy["消费频次"]
loy["日均消费"] = loy["总金额"] / (loy["活跃天数"] + 1)

# 忠诚度评分（频次+金额+活跃度归一化）
from sklearn.preprocessing import MinMaxScaler
if "sklearn" in str(type(MinMaxScaler)):
    pass
features = ["消费频次", "总金额", "活跃天数"]
scaler = MinMaxScaler()
loy[[f+"_norm" for f in features]] = scaler.fit_transform(loy[features])
loy["忠诚度评分"] = loy[[f+"_norm" for f in features]].mean(axis=1) * 100

# 忠诚度分群
loy["忠诚度等级"] = pd.cut(loy["忠诚度评分"], bins=[0, 20, 40, 60, 80, 100],
                          labels=["极低", "较低", "中等", "较高", "极高"])

fig, ax = new_fig((8, 5))
lc = loy["忠诚度等级"].value_counts().sort_index()
ax.bar(range(len(lc)), lc.values, color=PALETTE[:len(lc)], zorder=3)
ax.set_xticks(range(len(lc)))
ax.set_xticklabels(lc.index)
ax.set_ylabel("客户数")
for i, v in enumerate(lc.values):
    ax.text(i, v + max(lc.values) * 0.01, str(v), ha="center", fontsize=11, fontweight="bold")
style_ax(ax, "用户忠诚度分群")
save(fig, "ch02_08_忠诚度分群")

# 忠诚度评分分布
fig, ax = new_fig((8, 4.5))
ax.hist(loy["忠诚度评分"], bins=30, color=C_BLUE, alpha=0.7, edgecolor="white", zorder=3)
ax.axvline(loy["忠诚度评分"].mean(), color=C_RED, linestyle="--", linewidth=2, label=f"均值={loy['忠诚度评分'].mean():.1f}")
ax.set_xlabel("忠诚度评分")
ax.set_ylabel("客户数")
ax.legend()
style_ax(ax, "忠诚度评分分布")
save(fig, "ch02_09_忠诚度分布")

print("\n第2章完成！生成图表: ch02_01 ~ ch02_09")