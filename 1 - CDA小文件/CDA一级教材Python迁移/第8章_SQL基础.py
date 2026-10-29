# -*- coding: utf-8 -*-
"""
第8章 SQL语言基础与Mysql入门
用pandas实现SQL基础语法的对应操作：
  SQL2 数据过滤与排序 → df[df[...] == ...].sort_values()
  SQL3 表达式创建新列 → df.assign(new = df.a / df.b)
  SQL4 列重编码 → np.select / np.where
  SQL5 分组汇总 → df.groupby().agg()
  SQL6 横向连接 → pd.merge()
  SQL7 子查询 → df[df.col.isin(df2.col)]
  SQL8 集合操作 → pd.concat / intersect / diff
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第8章 SQL语言基础与Mysql入门")
print("=" * 60)

# 使用第1章的sale.csv和银行数据
sale = read_csv(ch("第1章 数据分析思维/sale.csv"))
print("sale.csv:")
print(sale)

d = ch("第1章 数据分析思维/关系模型演示-不建议用poweBI操作关系型数据模型")
trans = read_csv(os.path.join(d, "trans.csv"))
trans["date"] = pd.to_datetime(trans["date"])
# 清洗金额
for c in ["amount", "balance"]:
    if c in trans.columns:
        trans[c] = trans[c].apply(clean_money)

loans = read_csv(os.path.join(d, "loans.csv"))
loans["date"] = pd.to_datetime(loans["date"])

# ============================================================
# SQL2 数据过滤与排序
# ============================================================
print("\n--- SQL2: 数据过滤与排序 ---")
# SELECT * FROM sale WHERE year=2012
r1 = sale[sale["year"] == 2012]
print("WHERE year=2012:\n", r1)

# SELECT DISTINCT year FROM sale
r2 = sale["year"].unique()
print("DISTINCT year:", r2)

# ORDER BY year
r3 = sale.sort_values("year")
print("ORDER BY year (前3行):\n", r3.head(3))

# 可视化：过滤+排序结果
fig, ax = new_fig((7, 5))
r1_sorted = r1.sort_values("sale", ascending=True)
ax.barh(r1_sorted["market"], r1_sorted["sale"], color=PALETTE[:len(r1_sorted)], zorder=3)
ax.set_xlabel("销售额")
style_ax(ax, "SQL: SELECT * FROM sale WHERE year=2012 ORDER BY sale")
for i, v in enumerate(r1_sorted["sale"]):
    ax.text(v + 200, i, str(v), va="center", fontsize=11)
save(fig, "ch08_01_过滤排序")

# ============================================================
# SQL3 表达式创建新列
# ============================================================
print("\n--- SQL3: 表达式创建新列 ---")
# SELECT profit/sale AS rate FROM sale
sale["rate"] = sale["profit"] / sale["sale"]
print("profit/sale AS rate:\n", sale[["year", "market", "rate"]])

# WHERE profit/sale < 0.07
r4 = sale[sale["rate"] < 0.07]
print("rate < 0.07:\n", r4)

fig, ax = new_fig((8, 5))
colors = [C_RED if r < 0.07 else C_BLUE for r in sale["rate"]]
ax.bar(range(len(sale)), sale["rate"], color=colors, zorder=3)
ax.set_xticks(range(len(sale)))
ax.set_xticklabels([f"{r.year}-{r.market}" for r in sale.itertuples()], rotation=45, ha="right", fontsize=8)
ax.axhline(0.07, color=C_RED, linestyle="--", linewidth=1.5, label="rate=0.07")
ax.set_ylabel("利润率")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f"{v:.1%}"))
ax.legend()
style_ax(ax, "SQL: profit/sale AS rate（红色=rate<0.07）")
save(fig, "ch08_02_表达式新列")

# ============================================================
# SQL4 列重编码
# ============================================================
print("\n--- SQL4: 列重编码 ---")
# CASE WHEN weekday=5 THEN '周末' WHEN weekday=6 THEN '周末' ELSE '工作日'
trans_sample = trans.head(1000).copy()
trans_sample["weekday"] = trans_sample["date"].dt.weekday
trans_sample["weekday_2"] = np.where(trans_sample["weekday"] >= 5, "周末", "工作日")
print(trans_sample[["date", "weekday", "weekday_2"]].head())

fig, ax = new_fig((7, 5))
wd = trans_sample["weekday_2"].value_counts()
ax.bar(wd.index, wd.values, color=[C_BLUE, C_ORANGE], width=0.5, zorder=3)
for i, v in enumerate(wd.values):
    ax.text(i, v + max(wd.values) * 0.01, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("交易笔数")
style_ax(ax, "SQL: CASE WHEN weekday>=5 THEN '周末' ELSE '工作日'")
save(fig, "ch08_03_列重编码")

# ============================================================
# SQL5 分组汇总
# ============================================================
print("\n--- SQL5: 分组汇总 ---")
# SELECT year, COUNT(*), AVG(sale), SUM(sale) FROM sale GROUP BY year
r5 = sale.groupby("year").agg(
    COUNT=("market", "count"),
    AVG_sale=("sale", "mean"),
    SUM_sale=("sale", "sum")
).reset_index()
print(r5)

fig, ax = new_fig((8, 5))
x = np.arange(len(r5))
w = 0.35
ax.bar(x - w/2, r5["AVG_sale"], w, label="平均销售额", color=C_BLUE, zorder=3)
ax.bar(x + w/2, r5["SUM_sale"], w, label="总销售额", color=C_ORANGE, zorder=3)
ax.set_xticks(x)
ax.set_xticklabels(r5["year"])
ax.legend()
style_ax(ax, "SQL: GROUP BY year → COUNT/AVG/SUM")
save(fig, "ch08_04_分组汇总")

# ============================================================
# SQL6 横向连接
# ============================================================
print("\n--- SQL6: 横向连接 ---")
accounts = read_csv(os.path.join(d, "accounts.csv"))
clients = read_csv(os.path.join(d, "clients.csv"))
disp = read_csv(os.path.join(d, "disp.csv"))
card = read_csv(os.path.join(d, "card.csv"))

# LEFT JOIN: card → disp → clients
joined = card.merge(disp, on="disp_id", how="left").merge(clients, on="client_id", how="left")
print(f"LEFT JOIN结果: {joined.shape}")
print(joined[["card_id", "issued", "type_x", "sex", "birth_date"]].head())

fig, ax = new_fig((7, 5))
js = joined.groupby("sex").size()
ax.bar(js.index, js.values, color=[C_BLUE, C_ORANGE], width=0.4, zorder=3)
for i, v in enumerate(js.values):
    ax.text(i, v + 10, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("信用卡数")
style_ax(ax, "SQL: card LEFT JOIN disp LEFT JOIN clients → 按性别统计")
save(fig, "ch08_05_横向连接")

# ============================================================
# SQL7 子查询
# ============================================================
print("\n--- SQL7: 子查询 ---")
# 获取贷款违约客户(status=B)的所有交易数据
# SELECT * FROM trans WHERE account_id IN (SELECT account_id FROM loans WHERE status='B')
default_accounts = loans[loans["status"] == "B"]["account_id"]
default_trans = trans[trans["account_id"].isin(default_accounts)]
print(f"违约客户数: {len(default_accounts)}, 违约客户交易数: {len(default_trans)}")

fig, ax = new_fig((8, 5))
ls = loans.groupby("status").size()
status_map = {"A": "已还清", "B": "违约", "C": "还款中", "D": "不良"}
labels = [status_map.get(s, s) for s in ls.index]
colors = [C_GREEN if s == "A" else C_RED if s == "B" else C_BLUE if s == "C" else C_ORANGE for s in ls.index]
ax.bar(labels, ls.values, color=colors, zorder=3, width=0.5)
for i, v in enumerate(ls.values):
    ax.text(i, v + 2, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_ylabel("贷款数")
style_ax(ax, "SQL: 子查询 - 贷款状态分布")
save(fig, "ch08_06_子查询")

# ============================================================
# SQL8 集合操作 (UNION)
# ============================================================
print("\n--- SQL8: 集合操作 ---")
# UNION: 2010年数据 ∪ 2011年数据
s2010 = sale[sale["year"] == 2010]
s2011 = sale[sale["year"] == 2011]
union = pd.concat([s2010, s2011])
print(f"UNION(2010, 2011): {len(union)}行")

fig, ax = new_fig((7, 5))
uc = union.groupby("year").size()
ax.bar(uc.index, uc.values, color=[C_BLUE, C_ORANGE], width=0.4, zorder=3)
for i, v in enumerate(uc.values):
    ax.text(uc.index[i], v + 0.1, str(v), ha="center", fontsize=12, fontweight="bold")
ax.set_xlabel("年份")
ax.set_ylabel("记录数")
style_ax(ax, "SQL: UNION(2010, 2011)")
save(fig, "ch08_07_集合操作")

print("\n第8章完成！生成图表: ch08_01 ~ ch08_07")