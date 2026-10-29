# -*- coding: utf-8 -*-
"""
第3章 商业数据分析框架
案例1：收入趋势分析（省份月度销售趋势）
案例2：财务费用分析（三大期间费用+管理费用）
案例3：电商平台精准营销（客户画像+品类分析）
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第3章 商业数据分析框架")
print("=" * 60)

D3 = ch("第3章 商业数据分析框架")

# ============================================================
# 案例1：收入趋势分析
# ============================================================
print("\n--- 案例1：收入趋势分析 ---")
f = os.path.join(D3, "案例1：收入趋势分析/案例1：收入趋势分析原始数据.xlsx")
df1 = pd.read_excel(f, sheet_name="原始数据")
print(f"数据: {df1.shape}, 列={list(df1.columns)}")
print(df1.head())

# 1) 各省份年度销售额趋势
fig, ax = new_fig((10, 6))
pivot1 = df1.pivot_table(index="订单年份", columns="销售省份", values="销售额", aggfunc="sum")
for i, prov in enumerate(pivot1.columns):
    ax.plot(pivot1.index, pivot1[prov], marker="o", linewidth=2, markersize=6,
            color=PALETTE[i % len(PALETTE)], label=prov, zorder=3)
ax.set_xlabel("年份")
ax.set_ylabel("销售额")
ax.legend(title="省份", ncol=3, fontsize=8)
style_ax(ax, "各省份年度销售额趋势")
save(fig, "ch03_01_省份销售趋势")

# 2) 月度销售额热力图
fig, ax = new_fig((10, 6))
pivot1m = df1.pivot_table(index="订单年份", columns="订单月份", values="销售额", aggfunc="sum")
im = ax.imshow(pivot1m.values, cmap="YlOrRd", aspect="auto")
ax.set_xticks(range(len(pivot1m.columns)))
ax.set_xticklabels([f"{m}月" for m in pivot1m.columns])
ax.set_yticks(range(len(pivot1m.index)))
ax.set_yticklabels(pivot1m.index)
for i in range(len(pivot1m.index)):
    for j in range(len(pivot1m.columns)):
        v = pivot1m.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v/1e4:.0f}", ha="center", va="center", fontsize=7,
                    color="white" if v > np.nanmax(pivot1m.values) * 0.6 else C_DARK)
ax.set_title("月度销售额热力图（万元）", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
fig.colorbar(im, ax=ax, shrink=0.8, label="销售额")
save(fig, "ch03_02_月度销售热力图")

# 3) 省份销售额排名
fig, ax = new_fig((9, 6))
prov_total = df1.groupby("销售省份")["销售额"].sum().sort_values(ascending=True)
gradient_blue = plt.cm.Blues(np.linspace(0.4, 0.9, len(prov_total)))
ax.barh(range(len(prov_total)), prov_total.values, color=gradient_blue, zorder=3)
ax.set_yticks(range(len(prov_total)))
ax.set_yticklabels(prov_total.index)
ax.set_xlabel("总销售额")
style_ax(ax, "各省份销售额排名")
save(fig, "ch03_03_省份销售排名")

# ============================================================
# 案例2：财务费用分析
# ============================================================
print("\n--- 案例2：财务费用分析 ---")
f2 = os.path.join(D3, "案例2：财务费用分析/案例2：财务费用分析-原始数据.xlsx")
total_cost = pd.read_excel(f2, sheet_name="总费用数据")
period_cost = pd.read_excel(f2, sheet_name="财务三大期间费用数据")
mgmt_cost = pd.read_excel(f2, sheet_name="管理费用数据")
print(f"总费用: {total_cost.shape}")
print(f"期间费用: {period_cost.shape}, 项={period_cost['期间费用项'].unique()}")
print(f"管理费用: {mgmt_cost.shape}")

# 1) 三大期间费用对比
fig, ax = new_fig((8, 5))
pc = period_cost.groupby("期间费用项")["金额"].sum().sort_values(ascending=False)
ax.bar(range(len(pc)), pc.values, color=[C_BLUE, C_ORANGE, C_GREEN][:len(pc)], zorder=3)
ax.set_xticks(range(len(pc)))
ax.set_xticklabels(pc.index)
ax.set_ylabel("金额")
for i, v in enumerate(pc.values):
    ax.text(i, v + max(pc.values) * 0.02, f"{v:,.0f}", ha="center", fontsize=11, fontweight="bold")
style_ax(ax, "财务三大期间费用对比")
save(fig, "ch03_04_期间费用对比")

# 2) 管理费用明细
fig, ax = new_fig((10, 6))
mc = mgmt_cost.groupby("管理费用项")["金额"].sum().sort_values(ascending=True)
ax.barh(range(len(mc)), mc.values, color=C_BLUE_D, zorder=3)
ax.set_yticks(range(len(mc)))
ax.set_yticklabels(mc.index, fontsize=9)
ax.set_xlabel("金额")
style_ax(ax, "管理费用明细")
save(fig, "ch03_05_管理费用明细")

# 3) 期间费用饼图
fig, ax = new_fig((7, 6))
ax.pie(pc.values, labels=pc.index, autopct="%1.1f%%", colors=[C_BLUE, C_ORANGE, C_GREEN],
       wedgeprops=dict(edgecolor="white", linewidth=2), textprops=dict(fontsize=11))
ax.set_title("期间费用占比", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch03_06_期间费用饼图")

# ============================================================
# 案例3：电商平台精准营销
# ============================================================
print("\n--- 案例3：电商平台精准营销 ---")
f3 = os.path.join(D3, "案例3：电商平台的精准营销/案例3：电商平台的精准营销-原始数据.xlsx")
df3 = pd.read_excel(f3, sheet_name="原始数据")
print(f"数据: {df3.shape}, 列={list(df3.columns)}")
print(df3.head())

# 1) 性别与品类交叉分析
fig, ax = new_fig((9, 5))
pivot3 = df3.pivot_table(index="品类", columns="性别", values="数量", aggfunc="sum")
pivot3.plot(kind="bar", ax=ax, color=[C_BLUE, C_ORANGE], width=0.6, zorder=3)
ax.set_xlabel("品类")
ax.set_ylabel("数量")
ax.legend(title="性别")
style_ax(ax, "各品类性别消费数量")
save(fig, "ch03_07_品类性别分析")

# 2) 年龄分布
fig, ax = new_fig((8, 4.5))
ax.hist(df3["年龄"].dropna(), bins=20, color=C_BLUE, alpha=0.7, edgecolor="white", zorder=3)
ax.axvline(df3["年龄"].mean(), color=C_RED, linestyle="--", linewidth=2, label=f"均值={df3['年龄'].mean():.1f}")
ax.set_xlabel("年龄")
ax.set_ylabel("人数")
ax.legend()
style_ax(ax, "客户年龄分布")
save(fig, "ch03_08_年龄分布")

# 3) 支付方式分析
fig, ax = new_fig((7, 5))
pay = df3.groupby("支付方式")["数量"].sum().sort_values(ascending=False)
ax.pie(pay.values, labels=pay.index, autopct="%1.1f%%", colors=PALETTE[:len(pay)],
       wedgeprops=dict(edgecolor="white", linewidth=2), textprops=dict(fontsize=10))
ax.set_title("支付方式占比", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch03_09_支付方式")

# 4) 品类销量排名
fig, ax = new_fig((9, 5))
cat = df3.groupby("品类")["数量"].sum().sort_values(ascending=False)
ax.bar(range(len(cat)), cat.values, color=PALETTE[:len(cat)], zorder=3)
ax.set_xticks(range(len(cat)))
ax.set_xticklabels(cat.index, rotation=30, ha="right")
ax.set_ylabel("销量")
for i, v in enumerate(cat.values):
    ax.text(i, v + max(cat.values) * 0.01, str(v), ha="center", fontsize=9)
style_ax(ax, "品类销量排名")
save(fig, "ch03_10_品类销量排名")

# 5) 年龄段与品类热力图
df3["年龄段"] = pd.cut(df3["年龄"], bins=[0, 20, 30, 40, 50, 100], labels=["<20", "20-30", "30-40", "40-50", "50+"])
pivot_age = df3.pivot_table(index="年龄段", columns="品类", values="数量", aggfunc="sum")
fig, ax = new_fig((10, 5))
im = ax.imshow(pivot_age.values, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(pivot_age.columns)))
ax.set_xticklabels(pivot_age.columns, rotation=30, ha="right")
ax.set_yticks(range(len(pivot_age.index)))
ax.set_yticklabels(pivot_age.index)
for i in range(len(pivot_age.index)):
    for j in range(len(pivot_age.columns)):
        v = pivot_age.values[i, j]
        if not np.isnan(v):
            ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=8,
                    color="white" if v > np.nanmax(pivot_age.values) * 0.6 else C_DARK)
ax.set_title("年龄段×品类消费热力图", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
fig.colorbar(im, ax=ax, shrink=0.8)
save(fig, "ch03_11_年龄品类热力图")

print("\n第3章完成！生成图表: ch03_01 ~ ch03_11")