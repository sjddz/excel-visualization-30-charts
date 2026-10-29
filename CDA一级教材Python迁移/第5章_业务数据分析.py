# -*- coding: utf-8 -*-
"""
第5章 业务数据分析
- 银行案例：理财产品销售看板（客户画像+目标达成）
- 归因分析：贷款申请渠道分析
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第5章 业务数据分析")
print("=" * 60)

D5 = ch("第5章 业务数据分析")

# ============================================================
# 一、银行案例：理财产品销售看板
# ============================================================
print("\n--- 5.1 银行理财产品销售看板 ---")
f = os.path.join(D5, "第5章  PowerBI业务看板案例-银行案例/银行案例数据 - 学员用.xlsx")
risk = pd.read_excel(f, sheet_name="风险偏好说明表")
cat = pd.read_excel(f, sheet_name="品类说明表")
edu = pd.read_excel(f, sheet_name="学历说明表")
sales = pd.read_excel(f, sheet_name="销售数据")
print(f"销售数据: {sales.shape}, 列={list(sales.columns)}")
print(sales.head())

# 关联说明表
sales = sales.merge(risk, on="风险编号", how="left").merge(cat, on="品类编号", how="left")
if "学历编号" in sales.columns:
    sales = sales.merge(edu, on="学历编号", how="left")
print(f"关联后: {sales.shape}")

# 1) 品类销售分布
fig, ax = new_fig((9, 5))
if "品类名称" in sales.columns:
    cat_sum = sales.groupby("品类名称")["家庭年收入"].count().sort_values(ascending=False)
else:
    cat_sum = sales.groupby("品类编号").size().sort_values(ascending=False)
ax.bar(range(len(cat_sum)), cat_sum.values, color=PALETTE[:len(cat_sum)], zorder=3)
ax.set_xticks(range(len(cat_sum)))
ax.set_xticklabels(cat_sum.index, rotation=30, ha="right")
ax.set_ylabel("销售笔数")
for i, v in enumerate(cat_sum.values):
    ax.text(i, v + max(cat_sum.values) * 0.01, str(v), ha="center", fontsize=9)
style_ax(ax, "理财产品品类销售分布")
save(fig, "ch05_01_品类销售分布")

# 2) 风险偏好分布
fig, ax = new_fig((7, 5))
if "风险说明" in sales.columns:
    rk = sales.groupby("风险说明").size()
else:
    rk = sales.groupby("风险编号").size()
ax.pie(rk.values, labels=rk.index, autopct="%1.1f%%", colors=PALETTE[:len(rk)],
       wedgeprops=dict(edgecolor="white", linewidth=2), textprops=dict(fontsize=11))
ax.set_title("客户风险偏好分布", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch05_02_风险偏好分布")

# 3) 年龄与年收入散点
fig, ax = new_fig((8, 5))
if "年龄" in sales.columns and "家庭年收入" in sales.columns:
    for i, g in enumerate(sales["性别"].unique() if "性别" in sales.columns else [None]):
        sub = sales[sales["性别"] == g] if g is not None else sales
        lbl = g if g is not None else "全部"
        ax.scatter(sub["年龄"], sub["家庭年收入"], s=40, alpha=0.5,
                   color=PALETTE[i % len(PALETTE)], label=lbl, zorder=3, edgecolor="white")
    ax.set_xlabel("年龄")
    ax.set_ylabel("家庭年收入")
    ax.legend(title="性别")
    style_ax(ax, "客户年龄与家庭年收入关系")
save(fig, "ch05_03_年龄收入散点")

# 4) 购买目的分析
fig, ax = new_fig((9, 5))
if "购买目的" in sales.columns:
    pp = sales.groupby("购买目的").size().sort_values(ascending=True)
    ax.barh(range(len(pp)), pp.values, color=C_BLUE_D, zorder=3)
    ax.set_yticks(range(len(pp)))
    ax.set_yticklabels(pp.index)
    ax.set_xlabel("人数")
    for i, v in enumerate(pp.values):
        ax.text(v + max(pp.values) * 0.01, i, str(v), va="center", fontsize=10)
    style_ax(ax, "客户购买目的分析")
save(fig, "ch05_04_购买目的")

# 5) 性别×品类交叉热力图
if "性别" in sales.columns and "品类名称" in sales.columns:
    cross = sales.pivot_table(index="性别", columns="品类名称", values="家庭年收入", aggfunc="count")
    fig, ax = new_fig((10, 4))
    im = ax.imshow(cross.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(cross.columns)))
    ax.set_xticklabels(cross.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(cross.index)))
    ax.set_yticklabels(cross.index)
    for i in range(len(cross.index)):
        for j in range(len(cross.columns)):
            v = cross.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9,
                        color="white" if v > np.nanmax(cross.values) * 0.6 else C_DARK)
    ax.set_title("性别×品类交叉分析", fontsize=13, fontweight="bold", color=C_DARK, pad=12)
    fig.colorbar(im, ax=ax, shrink=0.8)
    save(fig, "ch05_05_性别品类交叉")

# ============================================================
# 二、归因分析：贷款申请渠道
# ============================================================
print("\n--- 5.2 归因分析：贷款申请渠道 ---")
f2 = os.path.join(D5, "第5章 WPS归因分析案例-银行案例/归因分析数据.xlsx")
loan = pd.read_excel(f2, sheet_name="贷款申请表")
print(f"贷款申请: {loan.shape}, 列={list(loan.columns)}")
print(loan.head())

loan["申请日期"] = pd.to_datetime(loan["申请日期"])
loan["日"] = loan["申请日期"].dt.day
loan["渠道"] = loan["申请渠道"]

# 1) 各渠道申请量对比
fig, ax = new_fig((7, 5))
ch_sum = loan.groupby("渠道").size().sort_values(ascending=False)
ax.bar(range(len(ch_sum)), ch_sum.values, color=PALETTE[:len(ch_sum)], zorder=3)
ax.set_xticks(range(len(ch_sum)))
ax.set_xticklabels(ch_sum.index)
ax.set_ylabel("申请量")
for i, v in enumerate(ch_sum.values):
    ax.text(i, v + max(ch_sum.values) * 0.01, f"{v}\n({v/ch_sum.sum():.1%})", ha="center", fontsize=10)
style_ax(ax, "各渠道贷款申请量对比")
save(fig, "ch05_06_渠道申请量")

# 2) 日度申请趋势（按渠道）
fig, ax = new_fig((12, 5))
daily = loan.groupby(["日", "渠道"]).size().reset_index(name="count")
for i, ch_name in enumerate(daily["渠道"].unique()):
    sub = daily[daily.渠道 == ch_name]
    ax.plot(sub["日"], sub["count"], marker="o", markersize=3, linewidth=1.5,
            color=PALETTE[i % len(PALETTE)], label=ch_name, zorder=3)
ax.set_xlabel("日期（5月）")
ax.set_ylabel("申请量")
ax.legend(title="渠道")
style_ax(ax, "5月日度贷款申请趋势（分渠道）")
save(fig, "ch05_07_日度趋势")

# 3) 渠道占比饼图
fig, ax = new_fig((6, 5))
ax.pie(ch_sum.values, labels=ch_sum.index, autopct="%1.1f%%", colors=PALETTE[:len(ch_sum)],
       wedgeprops=dict(edgecolor="white", linewidth=2), textprops=dict(fontsize=11))
ax.set_title("贷款申请渠道占比", fontsize=13, fontweight="bold", color=C_DARK)
save(fig, "ch05_08_渠道占比")

# 4) 累计申请量
fig, ax = new_fig((10, 5))
daily_total = loan.groupby("日").size().cumsum()
ax.plot(daily_total.index, daily_total.values, color=C_BLUE, linewidth=2.5, zorder=3)
ax.fill_between(daily_total.index, daily_total.values, alpha=0.15, color=C_BLUE)
ax.set_xlabel("日期（5月）")
ax.set_ylabel("累计申请量")
style_ax(ax, "5月累计贷款申请量")
save(fig, "ch05_09_累计申请量")

print("\n第5章完成！生成图表: ch05_01 ~ ch05_09")