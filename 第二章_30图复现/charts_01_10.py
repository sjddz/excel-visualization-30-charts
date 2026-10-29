# -*- coding: utf-8 -*-
"""图表 1-10：柱形图系列 + 蝴蝶图 + 甘特图"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.dates import date2num
import common as C
from common import (read_sheet, save, new_fig, style_ax, gradient_bar,
                    C_BLUE, C_BLUE_D, C_ORANGE, C_ORANGE_D, C_GREEN, C_RED,
                    C_GRAY, C_DARK, GRADIENT_BLUE, GRADIENT_ORANGE, F1)


def chart_01():
    """1 渐变柱形图"""
    df = read_sheet(F1, "1 渐变柱形图")
    fig, ax = new_fig((7, 4.5))
    n = len(df)
    colors = [plt.cm.Blues(0.35 + 0.55 * i / (n - 1)) for i in range(n)]
    bars = ax.bar(df["区域"], df["销售量"], width=0.55, color=colors,
                  edgecolor="white", linewidth=1.5, zorder=3)
    for b, v in zip(bars, df["销售量"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 40, f"{v}",
                ha="center", fontsize=10, color=C_DARK, fontweight="bold")
    style_ax(ax, "图1 渐变柱形图 — 各区域销售量")
    ax.set_ylim(0, df["销售量"].max() * 1.15)
    return save(fig, "01_渐变柱形图")


def chart_02():
    """2 带均值柱形图"""
    df = read_sheet(F1, "2 带均值柱形图")
    fig, ax = new_fig((7, 4.5))
    bars = ax.bar(df["区域"], df["销售量"], width=0.55, color=C_BLUE,
                  edgecolor="white", linewidth=1.5, zorder=3)
    mean_val = df["销售量"].mean()
    ax.axhline(mean_val, color=C_ORANGE, linewidth=2, linestyle="--", zorder=4)
    ax.text(len(df) - 0.5, mean_val + 60, f"均值: {mean_val:.0f}",
            color=C_ORANGE_D, fontsize=10, ha="right", fontweight="bold")
    for b, v in zip(bars, df["销售量"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 40, f"{v}",
                ha="center", fontsize=10, color=C_DARK)
    style_ax(ax, "图2 带均值柱形图 — 销售量与均值参考线")
    ax.set_ylim(0, df["销售量"].max() * 1.18)
    return save(fig, "02_带均值柱形图")


def chart_03():
    """3 渐变圆角柱形图"""
    df = read_sheet(F1, "3 渐变圆角柱形图")
    fig, ax = new_fig((7, 4.5))
    n = len(df)
    colors = [plt.cm.Oranges(0.4 + 0.5 * i / (n - 1)) for i in range(n)]
    # 用FancyBboxPatch绘制圆角柱
    for i, (cat, val) in enumerate(zip(df["商品"], df["销量"])):
        x = i - 0.28
        w = 0.56
        box = FancyBboxPatch((x, 0), w, val,
                             boxstyle="round,pad=0,rounding_size=0.08",
                             mutation_aspect=val / w,
                             linewidth=1.5, edgecolor="white",
                             facecolor=colors[i], zorder=3)
        ax.add_patch(box)
        ax.text(i, val + 15, f"{val}", ha="center", fontsize=10,
                color=C_DARK, fontweight="bold")
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_xticks(range(n))
    ax.set_xticklabels(df["商品"])
    style_ax(ax, "图3 渐变圆角柱形图 — 商品销量")
    ax.set_ylim(0, df["销量"].max() * 1.15)
    return save(fig, "03_渐变圆角柱形图")


def chart_04():
    """4 标注柱形图"""
    df = read_sheet(F1, "4 标注柱形图")
    fig, ax = new_fig((7, 4.5))
    bars = ax.bar(df["月份"], df["销量"], width=0.55, color=C_BLUE,
                  edgecolor="white", linewidth=1.5, zorder=3)
    # 标注最大值
    idx_max = df["销量"].idxmax()
    bars[idx_max].set_color(C_ORANGE)
    for i, (b, v) in enumerate(zip(bars, df["销量"])):
        ax.text(b.get_x() + b.get_width() / 2, v + 60, f"{v}",
                ha="center", fontsize=10, color=C_DARK)
    ax.annotate(f"最高: {df['销量'].iloc[idx_max]}",
                xy=(idx_max, df["销量"].iloc[idx_max]),
                xytext=(idx_max + 0.6, df["销量"].iloc[idx_max] + 800),
                fontsize=10, color=C_ORANGE_D, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_ORANGE_D))
    style_ax(ax, "图4 标注柱形图 — 月份销量（高亮最大值）")
    ax.set_ylim(0, df["销量"].max() * 1.22)
    return save(fig, "04_标注柱形图")


def chart_05():
    """5 层叠柱形图"""
    df = read_sheet(F1, "5 层叠柱形图")
    fig, ax = new_fig((7, 4.5))
    x = range(len(df))
    ax.bar(x, df["销售额"], width=0.55, color=C_BLUE, label="销售额",
           edgecolor="white", linewidth=1.5, zorder=3)
    ax.bar(x, df["利润额"], width=0.55, color=C_ORANGE, label="利润额",
           edgecolor="white", linewidth=1.5, zorder=3)
    for i, (s, p) in enumerate(zip(df["销售额"], df["利润额"])):
        ax.text(i, s + 80, f"{s}", ha="center", fontsize=9, color=C_DARK)
        ax.text(i, p + 80, f"{p}", ha="center", fontsize=9, color=C_ORANGE_D)
    ax.set_xticks(list(x))
    ax.set_xticklabels(df["季度"])
    ax.legend(loc="upper left", frameon=False)
    style_ax(ax, "图5 层叠柱形图 — 季度销售额与利润额")
    ax.set_ylim(0, df["销售额"].max() * 1.15)
    return save(fig, "05_层叠柱形图")


def chart_06():
    """6 蝴蝶图（对比条形图）"""
    df = read_sheet(F1, "6 蝴蝶图")
    fig, ax = new_fig((8, 4.5))
    y = range(len(df))
    ax.barh(y, [-v for v in df["2021年销量"]], color=C_BLUE, label="2021年",
            edgecolor="white", linewidth=1, zorder=3)
    ax.barh(y, df["2022年销量"], color=C_ORANGE, label="2022年",
            edgecolor="white", linewidth=1, zorder=3)
    for i, (v21, v22) in enumerate(zip(df["2021年销量"], df["2022年销量"])):
        ax.text(-v21 - 30, i, f"{v21}", ha="right", va="center", fontsize=9, color=C_DARK)
        ax.text(v22 + 30, i, f"{v22}", ha="left", va="center", fontsize=9, color=C_DARK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["区域"])
    ax.axvline(0, color=C_GRAY, linewidth=0.8)
    ax.legend(loc="upper right", frameon=False)
    style_ax(ax, "图6 蝴蝶图 — 2021 vs 2022 区域销量对比", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    m = max(df["2021年销量"].max(), df["2022年销量"].max())
    ax.set_xlim(-m * 1.2, m * 1.2)
    return save(fig, "06_蝴蝶图")


def chart_07():
    """7 蝴蝶图（百分比版）"""
    df = read_sheet(F1, "7 蝴蝶图")
    fig, ax = new_fig((8, 4.5))
    y = range(len(df))
    ax.barh(y, [-v for v in df["2021年"]], color=C_BLUE, label="2021年",
            edgecolor="white", linewidth=1, zorder=3)
    ax.barh(y, df["2022年"], color=C_ORANGE, label="2022年",
            edgecolor="white", linewidth=1, zorder=3)
    for i, (v21, v22) in enumerate(zip(df["2021年"], df["2022年"])):
        ax.text(-v21 - 0.01, i, f"{v21*100:.0f}%", ha="right", va="center", fontsize=9, color=C_DARK)
        ax.text(v22 + 0.01, i, f"{v22*100:.0f}%", ha="left", va="center", fontsize=9, color=C_DARK)
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["区域"])
    ax.axvline(0, color=C_GRAY, linewidth=0.8)
    ax.legend(loc="upper right", frameon=False)
    style_ax(ax, "图7 蝴蝶图 — 2021 vs 2022 区域销量占比", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    m = max(df["2021年"].max(), df["2022年"].max())
    ax.set_xlim(-m * 1.35, m * 1.35)
    return save(fig, "07_蝴蝶图百分比")


def chart_08():
    """8 数值百分比"""
    df = read_sheet(F1, "8 数值百分比")
    fig, ax = new_fig((7.5, 4.5))
    bars = ax.bar(df["区域"], df["销量"], width=0.55, color=C_BLUE,
                  edgecolor="white", linewidth=1.5, zorder=3)
    for b, v, r in zip(bars, df["销量"], df["同比去年"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 40, f"{v}",
                ha="center", fontsize=10, color=C_DARK, fontweight="bold")
        ax.text(b.get_x() + b.get_width() / 2, v / 2,
                f"{r*100:+.1f}%", ha="center", va="center",
                fontsize=9, color="white", fontweight="bold")
    style_ax(ax, "图8 数值百分比 — 区域销量与同比变化")
    ax.set_ylim(0, df["销量"].max() * 1.18)
    return save(fig, "08_数值百分比")


def chart_09():
    """9 对比柱形图"""
    df = read_sheet(F1, "9 对比柱形图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    w = 0.35
    ax.bar(x - w/2, df["2021销量"], w, color=C_BLUE, label="2021销量",
           edgecolor="white", linewidth=1, zorder=3)
    ax.bar(x + w/2, df["2022销量"], w, color=C_ORANGE, label="2022销量",
           edgecolor="white", linewidth=1, zorder=3)
    for i, (v21, v22, d) in enumerate(zip(df["2021销量"], df["2022销量"], df["差值"])):
        ax.text(i - w/2, v21 + 40, f"{v21}", ha="center", fontsize=8, color=C_DARK)
        ax.text(i + w/2, v22 + 40, f"{v22}", ha="center", fontsize=8, color=C_DARK)
        ax.text(i, max(v21, v22) + 300, f"Δ{d}", ha="center", fontsize=9,
                color=C_RED, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(df["商品"])
    ax.legend(frameon=False)
    style_ax(ax, "图9 对比柱形图 — 商品 2021 vs 2022 销量差值")
    ax.set_ylim(0, df["2021销量"].max() * 1.22)
    return save(fig, "09_对比柱形图")


def chart_10():
    """10 甘特图"""
    df = read_sheet(F1, "10 甘特图", header_row=2)
    df["开始日期"] = pd.to_datetime(df["开始日期"])
    df["结束日期"] = pd.to_datetime(df["结束日期"])
    fig, ax = new_fig((9, 4.5))
    y = range(len(df))
    # 总工期条
    ax.barh(y, [d.days for d in df["结束日期"] - df["开始日期"]],
            left=[date2num(d) for d in df["开始日期"]],
            color=C_GRAY, alpha=0.3, height=0.5, zorder=2)
    # 已完成部分
    for i, row in df.iterrows():
        done_days = row["项目天数"] * row["完成度"]
        ax.barh(i, done_days, left=date2num(row["开始日期"]),
                color=C_BLUE, height=0.5, edgecolor="white", linewidth=1, zorder=3)
        ax.text(date2num(row["结束日期"]) + 1, i,
                f"{row['完成度']*100:.0f}%", va="center", fontsize=9,
                color=C_BLUE_D, fontweight="bold")
    ax.set_yticks(list(y))
    ax.set_yticklabels(df["项目名称"])
    ax.xaxis_date()
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    style_ax(ax, "图10 甘特图 — 项目进度（蓝色为已完成）", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    ax.set_xlim(date2num(df["开始日期"].min()) - 1,
                date2num(df["结束日期"].max()) + 5)
    return save(fig, "10_甘特图")


def run():
    results = []
    for fn in [chart_01, chart_02, chart_03, chart_04, chart_05,
               chart_06, chart_07, chart_08, chart_09, chart_10]:
        try:
            p = fn()
            results.append((fn.__name__, "OK", p))
            print(f"  [OK] {fn.__name__} -> {p}")
        except Exception as e:
            results.append((fn.__name__, "FAIL", str(e)))
            print(f"  [FAIL] {fn.__name__}: {e}")
    return results


if __name__ == "__main__":
    run()