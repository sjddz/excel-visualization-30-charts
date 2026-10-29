# -*- coding: utf-8 -*-
"""
第9章 用户标签体系与用户画像专题
用pandas实现信用卡客户画像SQL逻辑：
  1) 获取客户性别和发卡时年龄
  2) 截止开卡时最后一次交易间隔和账户余额
  3) 开卡半年内交易统计（笔数/入账/出账/出账比例）
  4) 合并所有变量，构建用户画像
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第9章 用户标签体系与用户画像专题")
print("=" * 60)

d = ch("第9章 用户标签体系与用户画像专题/data")
accounts = read_csv(os.path.join(d, "accounts.csv"))
clients = read_csv(os.path.join(d, "clients.csv"))
disp = read_csv(os.path.join(d, "disp.csv"))
card = read_csv(os.path.join(d, "card.csv"))
loans = read_csv(os.path.join(d, "loans.csv"))
district = read_csv(os.path.join(d, "district.csv"))
trans = read_csv(os.path.join(d, "trans.csv"))

print(f"card: {card.shape}, clients: {clients.shape}, disp: {disp.shape}")
print(f"trans: {trans.shape}")

# 日期转换
card["issued"] = pd.to_datetime(card["issued"])
clients["birth_date"] = pd.to_datetime(clients["birth_date"])
trans["date"] = pd.to_datetime(trans["date"])
loans["date"] = pd.to_datetime(loans["date"])

# 清洗金额
trans["amount"] = trans["amount"].apply(clean_money)
trans["balance"] = trans["balance"].apply(clean_money)

# ============================================================
# 1) 获取客户性别和发卡时年龄
# ============================================================
print("\n--- 9.1 客户性别和发卡时年龄 ---")
var1 = card.merge(disp, on="disp_id", how="left") \
           .merge(clients, on="client_id", how="left")
var1["age"] = (var1["issued"] - var1["birth_date"]).dt.days / 365
var1 = var1.rename(columns={"type_x": "type"})
var1 = var1[["card_id", "disp_id", "issued", "type", "sex", "age", "district_id"]]
print(f"var1: {var1.shape}")
print(var1.head())

# ============================================================
# 2) 截止开卡时最后一次交易间隔和账户余额
# ============================================================
print("\n--- 9.2 开卡前最后一次交易间隔和余额 ---")
# 获取发卡前的交易流水
card_disp = card.merge(disp, on="disp_id", how="left")
var2_1 = card_disp.merge(trans, on="account_id", how="left")
var2_1 = var2_1[var2_1["issued"] > var2_1["date"]].copy()
var2_1["last_days"] = (var2_1["issued"] - var2_1["date"]).dt.days
var2_1 = var2_1[["card_id", "issued", "date", "last_days", "balance"]]

# 每张卡取交易时间最大的记录
var2 = var2_1.sort_values("date", ascending=False).groupby("card_id").first().reset_index()
var2 = var2[["card_id", "last_days", "balance"]]
print(f"var2: {var2.shape}")
print(var2.head())

# ============================================================
# 3) 开卡半年内交易统计
# ============================================================
print("\n--- 9.3 开卡半年内交易统计 ---")
var3_1 = card_disp.merge(trans, on="account_id", how="left")
# 发卡前180天以内
mask = (var3_1["issued"] > var3_1["date"]) & ((var3_1["issued"] - var3_1["date"]).dt.days <= 180)
var3_1 = var3_1[mask].copy()
var3_1["is_in"] = (var3_1["type_y"] == "借").astype(int)
var3_1["is_out"] = (var3_1["type_y"] == "贷").astype(int)
var3_1["in_amount"] = var3_1["is_in"] * var3_1["amount"]
var3_1["out_amount"] = var3_1["is_out"] * var3_1["amount"]

var3 = var3_1.groupby("card_id").agg(
    trans_count=("trans_id", "count"),
    trans_in_amount=("in_amount", "sum"),
    trans_out_amount=("out_amount", "sum"),
    avg_balance=("balance", "mean")
).reset_index()
var3["out_ratio"] = var3["trans_out_amount"] / var3["avg_balance"]
var3["out_in_ratio"] = var3["trans_out_amount"] / var3["trans_in_amount"].replace(0, np.nan)
print(f"var3: {var3.shape}")
print(var3.head())

# ============================================================
# 4) 合并所有变量
# ============================================================
print("\n--- 9.4 合并变量构建用户画像 ---")
creditcard = var1.merge(var2, on="card_id", how="left") \
                 .merge(var3, on="card_id", how="left")
print(f"最终画像数据: {creditcard.shape}")
print(creditcard.head())
print("\n变量统计:")
print(creditcard[["age", "last_days", "balance", "trans_count", "trans_out_amount"]].describe())

# ============================================================
# 可视化
# ============================================================
# 1) 性别分布
fig, ax = new_fig((6, 5))
sc = creditcard["sex"].value_counts()
ax.bar(sc.index, sc.values, color=[C_BLUE, C_ORANGE], width=0.4, zorder=3)
for i, v in enumerate(sc.values):
    ax.text(i, v + 5, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("信用卡数")
style_ax(ax, "信用卡客户性别分布")
save(fig, "ch09_01_性别分布")

# 2) 年龄分布
fig, ax = new_fig((8, 4.5))
ax.hist(creditcard["age"].dropna(), bins=25, color=C_BLUE, alpha=0.7, edgecolor="white", zorder=3)
ax.axvline(creditcard["age"].mean(), color=C_RED, linestyle="--", linewidth=2,
           label=f"均值={creditcard['age'].mean():.1f}岁")
ax.set_xlabel("发卡时年龄")
ax.set_ylabel("人数")
ax.legend()
style_ax(ax, "信用卡客户发卡时年龄分布")
save(fig, "ch09_02_年龄分布")

# 3) 信用卡类型 vs 年龄
fig, ax = new_fig((8, 5))
for i, t in enumerate(creditcard["type"].unique()):
    sub = creditcard[creditcard["type"] == t]["age"].dropna()
    ax.hist(sub, bins=20, alpha=0.5, color=PALETTE[i], label=t, edgecolor="white", zorder=3)
ax.set_xlabel("年龄")
ax.set_ylabel("人数")
ax.legend(title="卡类型")
style_ax(ax, "不同卡类型客户年龄分布")
save(fig, "ch09_03_卡类型年龄")

# 4) 交易频次分布
fig, ax = new_fig((8, 4.5))
tc = creditcard["trans_count"].dropna()
ax.hist(tc, bins=30, color=C_GREEN, alpha=0.7, edgecolor="white", zorder=3)
ax.set_xlabel("半年内交易笔数")
ax.set_ylabel("客户数")
style_ax(ax, "开卡半年内交易频次分布")
save(fig, "ch09_04_交易频次")

# 5) 年龄 vs 交易频次散点
fig, ax = new_fig((8, 5))
valid = creditcard.dropna(subset=["age", "trans_count"])
ax.scatter(valid["age"], valid["trans_count"], s=30, alpha=0.4, color=C_BLUE, zorder=3, edgecolor="white")
ax.set_xlabel("发卡时年龄")
ax.set_ylabel("半年内交易笔数")
style_ax(ax, "年龄与交易频次关系")
save(fig, "ch09_05_年龄交易频次")

# 6) 出账/入账比例分布
fig, ax = new_fig((8, 4.5))
ratio = creditcard["out_in_ratio"].dropna()
ratio = ratio[ratio < ratio.quantile(0.95)]  # 去极端值
ax.hist(ratio, bins=30, color=C_ORANGE, alpha=0.7, edgecolor="white", zorder=3)
ax.set_xlabel("出账/入账比例")
ax.set_ylabel("客户数")
style_ax(ax, "出账/入账比例分布（去极端值）")
save(fig, "ch09_06_出入账比例")

# 7) 用户画像综合雷达图（按卡类型均值）
from sklearn.preprocessing import MinMaxScaler
metrics = ["age", "trans_count", "trans_out_amount", "last_days"]
valid_metrics = [m for m in metrics if m in creditcard.columns]
profile = creditcard.groupby("type")[valid_metrics].mean()
scaler = MinMaxScaler()
profile_norm = pd.DataFrame(scaler.fit_transform(profile), index=profile.index, columns=valid_metrics)

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
fig.patch.set_facecolor("white")
angles = np.linspace(0, 2 * np.pi, len(valid_metrics), endpoint=False).tolist()
angles += angles[:1]
for i, t in enumerate(profile_norm.index):
    vals = profile_norm.loc[t].tolist()
    vals += vals[:1]
    ax.plot(angles, vals, linewidth=2, color=PALETTE[i], label=t)
    ax.fill(angles, vals, alpha=0.15, color=PALETTE[i])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(valid_metrics, fontsize=10)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
ax.set_title("用户画像雷达图（按卡类型）", fontsize=13, fontweight="bold", color=C_DARK, pad=20)
save(fig, "ch09_07_画像雷达图")

# 8) RFM简易画像
creditcard["R_score"] = pd.qcut(creditcard["last_days"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
creditcard["F_score"] = pd.qcut(creditcard["trans_count"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
creditcard["RFM"] = creditcard["R_score"].astype(str) + creditcard["F_score"].astype(str)

fig, ax = new_fig((8, 6))
rfm_pivot = creditcard.pivot_table(index="R_score", columns="F_score", values="card_id", aggfunc="count")
im = ax.imshow(rfm_pivot.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(4))
ax.set_xticklabels([1, 2, 3, 4])
ax.set_yticks(range(4))
ax.set_yticklabels([4, 3, 2, 1])
for i in range(4):
    for j in range(4):
        v = rfm_pivot.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=11,
                    color="white" if v > np.nanmax(rfm_pivot.values) * 0.6 else C_DARK, fontweight="bold")
ax.set_xlabel("F评分（交易频次）")
ax.set_ylabel("R评分（最近交易间隔）")
ax.set_title("信用卡客户RFM分布矩阵", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
save(fig, "ch09_08_RFM矩阵")

print("\n第9章完成！生成图表: ch09_01 ~ ch09_08")