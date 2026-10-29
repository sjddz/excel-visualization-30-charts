# -*- coding: utf-8 -*-
"""
第1章 数据分析思维
- sale.csv 销售数据可视化
- 关系模型演示：银行数据多表连接（accounts/clients/disp/card/loans）
- 维度模型演示：商场销售数据（星型模型）
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第1章 数据分析思维")
print("=" * 60)

# ============================================================
# 一、sale.csv 销售数据可视化
# ============================================================
print("\n--- 1.1 sale.csv 销售数据可视化 ---")
sale = read_csv(ch("第1章 数据分析思维/sale.csv"))
print(sale)

# 1) 各市场年度销售额对比柱形图
fig, ax = new_fig((8, 5))
years = sale["year"].unique()
markets = sale["market"].unique()
x = np.arange(len(years))
w = 0.18
for i, m in enumerate(markets):
    vals = [sale[(sale.year == y) & (sale.market == m)].sale.values[0] for y in years]
    ax.bar(x + i * w, vals, w, label=m, color=PALETTE[i], zorder=3)
ax.set_xticks(x + w * 1.5)
ax.set_xticklabels(years)
ax.set_ylabel("销售额")
ax.legend(title="市场")
style_ax(ax, "各市场年度销售额对比")
save(fig, "ch01_01_市场销售额对比")

# 2) 各市场利润率对比
fig, ax = new_fig((8, 5))
for i, m in enumerate(markets):
    vals = [sale[(sale.year == y) & (sale.market == m)].profit.values[0] /
            sale[(sale.year == y) & (sale.market == m)].sale.values[0] for y in years]
    ax.bar(x + i * w, vals, w, label=m, color=PALETTE[i], zorder=3)
ax.set_xticks(x + w * 1.5)
ax.set_xticklabels(years)
ax.set_ylabel("利润率")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.1%}"))
ax.legend(title="市场")
style_ax(ax, "各市场年度利润率对比")
save(fig, "ch01_02_市场利润率对比")

# 3) 销售额与利润散点图
fig, ax = new_fig((7, 5))
for i, m in enumerate(markets):
    sub = sale[sale.market == m]
    ax.scatter(sub.sale, sub.profit, s=120, color=PALETTE[i], label=m, zorder=3, edgecolor="white")
ax.set_xlabel("销售额")
ax.set_ylabel("利润")
ax.legend(title="市场")
style_ax(ax, "销售额与利润关系")
save(fig, "ch01_03_销售利润散点")

# ============================================================
# 二、关系模型演示：银行数据多表连接
# ============================================================
print("\n--- 1.2 关系模型演示（银行数据）---")
d = ch("第1章 数据分析思维/关系模型演示-不建议用poweBI操作关系型数据模型")
accounts = read_csv(os.path.join(d, "accounts.csv"))
clients = read_csv(os.path.join(d, "clients.csv"))
disp = read_csv(os.path.join(d, "disp.csv"))
card = read_csv(os.path.join(d, "card.csv"))
loans = read_csv(os.path.join(d, "loans.csv"))
district = read_csv(os.path.join(d, "district.csv"))

print(f"accounts: {accounts.shape}, clients: {clients.shape}, disp: {disp.shape}")
print(f"card: {card.shape}, loans: {loans.shape}, district: {district.shape}")

# 关系模型：card → disp → clients → district 的连接链
merged = card.merge(disp, on="disp_id", how="left") \
             .merge(clients, on="client_id", how="left") \
             .merge(district, left_on="district_id", right_on="A1", how="left")
print(f"连接后: {merged.shape}")

# 1) 信用卡类型分布
fig, ax = new_fig((6, 4.5))
counts = card["type"].value_counts()
ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", colors=[C_BLUE, C_ORANGE, C_GREEN],
       wedgeprops=dict(edgecolor="white", linewidth=2))
ax.set_title("信用卡类型分布", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch01_04_信用卡类型分布")

# 2) 发卡年份趋势
card["issued_year"] = pd.to_datetime(card["issued"]).dt.year
fig, ax = new_fig((8, 4.5))
yc = card.groupby("issued_year").size()
ax.bar(yc.index, yc.values, color=C_BLUE, zorder=3)
ax.set_xlabel("年份")
ax.set_ylabel("发卡数量")
style_ax(ax, "信用卡年度发卡数量趋势")
save(fig, "ch01_05_发卡年度趋势")

# 3) 贷款状态分布
fig, ax = new_fig((6, 4.5))
sc = loans["status"].value_counts()
status_map = {"A": "已还清", "B": "违约", "C": "还款中", "D": "不良"}
labels = [status_map.get(s, s) for s in sc.index]
ax.pie(sc.values, labels=labels, autopct="%1.1f%%", colors=[C_GREEN, C_RED, C_BLUE, C_ORANGE],
       wedgeprops=dict(edgecolor="white", linewidth=2))
ax.set_title("贷款状态分布", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch01_06_贷款状态分布")

# 4) 客户性别分布
fig, ax = new_fig((6, 4.5))
gc = clients["sex"].value_counts()
ax.bar(gc.index, gc.values, color=[C_BLUE, C_ORANGE], width=0.5, zorder=3)
for i, v in enumerate(gc.values):
    ax.text(i, v + 50, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("人数")
style_ax(ax, "客户性别分布")
save(fig, "ch01_07_客户性别分布")

# ============================================================
# 三、维度模型演示：商场销售数据
# ============================================================
print("\n--- 1.3 维度模型演示（商场销售数据）---")
dim_path = ch("第1章 数据分析思维/维度模型演示/商场销售数据表.xlsx")
dim_xls = pd.ExcelFile(dim_path)
print(f"工作表: {dim_xls.sheet_names}")
dim_data = {s: dim_xls.parse(s) for s in dim_xls.sheet_names}

# 找到事实表和维度表
for name, df in dim_data.items():
    print(f"  {name}: {df.shape}, 列={list(df.columns)[:6]}")

# 尝试找含金额/数量的事实表
fact_candidates = [n for n, df in dim_data.items() if any(k in str(df.columns).lower() for k in ["金额", "数量", "销售", "amount"])]
print(f"事实表候选: {fact_candidates}")

# 可视化第一个有数据的表
for name, df in dim_data.items():
    if len(df) > 0 and df.select_dtypes(include=[np.number]).shape[1] >= 2:
        nums = df.select_dtypes(include=[np.number]).columns[:2]
        fig, ax = new_fig((7, 5))
        ax.scatter(df[nums[0]], df[nums[1]], s=30, alpha=0.5, color=C_BLUE, zorder=3)
        ax.set_xlabel(nums[0])
        ax.set_ylabel(nums[1])
        style_ax(ax, f"维度模型演示 - {name}")
        save(fig, f"ch01_08_维度模型_{name}")
        break

print("\n第1章完成！生成图表: ch01_01 ~ ch01_08")