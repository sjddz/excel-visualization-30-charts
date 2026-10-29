# -*- coding: utf-8 -*-
"""图表 21-30：南丁格尔PPT版、仪表盘、柱形折线、目标柱形、子弹图、
    柱形圆、簇状柱形折线、复合柱形、滑珠图、对比滑珠图"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, FancyBboxPatch, Rectangle, FancyArrowPatch
import matplotlib.patches as mpatches
import common as C
from common import (read_sheet, save, new_fig, style_ax,
                    C_BLUE, C_BLUE_D, C_ORANGE, C_ORANGE_D, C_GREEN, C_RED,
                    C_GRAY, C_DARK, F1, F2)


def chart_21():
    """21 南丁格尔玫瑰图（PPT版，纯扇形）"""
    df = read_sheet(F2, "20 南丁格尔（PPT）")
    fig, ax = new_fig((6, 6))
    ax.set_aspect("equal")
    n = len(df)
    colors = [plt.cm.tab10(i / n) for i in range(n)]
    max_ratio = df["人数占比"].max()
    for i, (_, row) in enumerate(df.iterrows()):
        r = row["人数占比"] / max_ratio
        theta1 = 90 - i * (360 / n)
        theta2 = theta1 - (360 / n)
        ax.add_patch(Wedge((0, 0), r, theta2, theta1, facecolor=colors[i],
                            edgecolor="white", linewidth=2))
        angle_mid = np.radians((theta1 + theta2) / 2)
        ax.text(r * 0.65 * np.cos(angle_mid), r * 0.65 * np.sin(angle_mid),
                f"{row['部门']}\n{row['人数占比']*100:.1f}%",
                ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图21 南丁格尔玫瑰图(PPT版) — 部门人数占比", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "21_南丁格尔PPT版")


def chart_22():
    """22 仪表盘图"""
    df = read_sheet(F2, "22 仪表盘图", header_row=1)
    # 指针数值76，刻度50/60/.../100
    pointer_val = 76
    fig, ax = new_fig((6, 5))
    ax.set_aspect("equal")
    # 半圆仪表盘背景 (180度到0度)
    ax.add_patch(Wedge((0, 0), 1, 0, 180, width=0.2, facecolor="#E8E8E8"))
    # 刻度区域: 50-60红, 60-80黄, 80-100绿
    val_min, val_max = 50, 100
    def val_to_angle(v):
        return 180 - (v - val_min) / (val_max - val_min) * 180
    ax.add_patch(Wedge((0, 0), 1, val_to_angle(60), 180, width=0.2, facecolor=C_RED, alpha=0.7))
    ax.add_patch(Wedge((0, 0), 1, val_to_angle(80), val_to_angle(60), width=0.2, facecolor=C_ORANGE, alpha=0.7))
    ax.add_patch(Wedge((0, 0), 1, 0, val_to_angle(80), width=0.2, facecolor=C_GREEN, alpha=0.7))
    # 刻度标签
    for v in [50, 60, 70, 80, 90, 100]:
        ang = np.radians(val_to_angle(v))
        ax.text(1.15 * np.cos(ang), 1.15 * np.sin(ang), str(v),
                ha="center", va="center", fontsize=9, color=C_DARK)
    # 指针
    ptr_ang = np.radians(val_to_angle(pointer_val))
    ax.annotate("", xy=(0.85 * np.cos(ptr_ang), 0.85 * np.sin(ptr_ang)),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle="-|>", color=C_DARK, lw=2.5))
    ax.add_patch(Circle((0, 0), 0.05, facecolor=C_DARK, zorder=5))
    ax.text(0, -0.35, f"{pointer_val}", ha="center", va="center",
            fontsize=28, fontweight="bold", color=C_BLUE_D)
    ax.text(0, -0.55, "当前值", ha="center", va="center", fontsize=10, color=C_GRAY)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-0.7, 1.3)
    ax.axis("off")
    ax.set_title("图22 仪表盘图", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "22_仪表盘图")


def chart_23():
    """23 柱形折线图（组合图）"""
    df = read_sheet(F2, "23 柱形折线图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    bars = ax.bar(x, df["销售量"], width=0.5, color=C_BLUE, edgecolor="white",
                  linewidth=1.5, zorder=3, label="销售量")
    for b, v in zip(bars, df["销售量"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 40, f"{v}",
                ha="center", fontsize=9, color=C_DARK)
    ax.set_ylabel("销售量", color=C_BLUE_D)
    # 折线（同比）
    ax2 = ax.twinx()
    ax2.plot(x, df["同比"], color=C_ORANGE, linewidth=2.5, marker="D",
             markersize=8, markeredgecolor="white", markeredgewidth=1.5,
             zorder=4, label="同比")
    for i, v in enumerate(df["同比"]):
        ax2.text(i, v + 0.02, f"{v*100:.1f}%", ha="center", fontsize=8, color=C_ORANGE_D)
    ax2.set_ylabel("同比", color=C_ORANGE_D)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_xticks(x)
    ax.set_xticklabels(df["年份"])
    style_ax(ax, "图23 柱形折线图 — 销售量与同比")
    ax2.spines["top"].set_visible(False)
    ax.set_ylim(0, df["销售量"].max() * 1.18)
    ax2.set_ylim(0, df["同比"].max() * 1.3)
    return save(fig, "23_柱形折线图")


def chart_24():
    """24 目标柱形图（实际 vs 目标）"""
    df = read_sheet(F2, "24 目标柱形图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    w = 0.35
    ax.bar(x - w/2, df["实际销量"], w, color=C_BLUE, label="实际销量",
           edgecolor="white", linewidth=1, zorder=3)
    ax.bar(x + w/2, df["目标销量"], w, color=C_GRAY, label="目标销量",
           edgecolor="white", linewidth=1, zorder=3)
    for i, (a, t) in enumerate(zip(df["实际销量"], df["目标销量"])):
        ax.text(i - w/2, a + 15, f"{a}", ha="center", fontsize=8, color=C_DARK)
        ax.text(i + w/2, t + 15, f"{t}", ha="center", fontsize=8, color=C_GRAY)
        # 达成率标注
        rate = a / t
        color = C_GREEN if rate >= 1 else C_RED
        ax.text(i, max(a, t) + 80, f"{rate*100:.0f}%", ha="center",
                fontsize=9, color=color, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(df["商品"])
    ax.legend(frameon=False)
    style_ax(ax, "图24 目标柱形图 — 实际 vs 目标销量")
    ax.set_ylim(0, max(df["实际销量"].max(), df["目标销量"].max()) * 1.2)
    return save(fig, "24_目标柱形图")


def chart_25():
    """25 子弹图"""
    df = read_sheet(F2, "25 子弹图", header_row=2)
    fig, ax = new_fig((8, 4.5))
    n = len(df)
    bar_h = 0.5
    for i, (_, row) in enumerate(df.iterrows()):
        y = n - i - 1
        # 背景范围条: 及格/良好/优秀
        ax.add_patch(Rectangle((0, y - bar_h/2), row["及格"], bar_h,
                                facecolor="#E8E8E8", edgecolor="none", zorder=1))
        ax.add_patch(Rectangle((row["及格"], y - bar_h/2), row["良好"], bar_h,
                                facecolor="#C8C8C8", edgecolor="none", zorder=1))
        ax.add_patch(Rectangle((row["及格"] + row["良好"], y - bar_h/2), row["优秀"], bar_h,
                                facecolor="#A8A8A8", edgecolor="none", zorder=1))
        # 实际值（深色细条）
        ax.add_patch(Rectangle((0, y - bar_h/4), row["实际"], bar_h/2,
                                facecolor=C_BLUE_D, edgecolor="none", zorder=3))
        # 目标线
        ax.plot([row["目标"], row["目标"]], [y - bar_h/2, y + bar_h/2],
                color=C_RED, linewidth=2.5, zorder=4)
        ax.text(row["实际"] + 20, y, f"实际:{row['实际']}", va="center", fontsize=8, color=C_BLUE_D)
        ax.text(row["目标"] + 20, y + bar_h/2 + 0.1, f"目标:{row['目标']}",
                va="center", fontsize=7, color=C_RED)
        ax.text(-30, y, row["商品"], ha="right", va="center", fontsize=10, color=C_DARK)
    ax.set_xlim(-40, df["实际"].max() + df["优秀"].max() + 150)
    ax.set_ylim(-0.5, n - 0.5)
    ax.set_yticks([])
    style_ax(ax, "图25 子弹图 — 实际/目标/绩效区间", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    # 图例
    handles = [mpatches.Patch(color=C_BLUE_D, label="实际值"),
               plt.Line2D([0], [0], color=C_RED, linewidth=2.5, label="目标值"),
               mpatches.Patch(color="#E8E8E8", label="及格区间"),
               mpatches.Patch(color="#C8C8C8", label="良好区间"),
               mpatches.Patch(color="#A8A8A8", label="优秀区间")]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8)
    return save(fig, "25_子弹图")


def chart_26():
    """26 柱形圆（柱形+圆形标注同比）"""
    df = read_sheet(F2, "26 柱形圆")
    fig, ax = new_fig((7.5, 4.5))
    bars = ax.bar(df["区域"], df["销量"], width=0.5, color=C_BLUE,
                  edgecolor="white", linewidth=1.5, zorder=3)
    for b, v, r in zip(bars, df["销量"], df["同比去年"]):
        ax.text(b.get_x() + b.get_width() / 2, v + 40, f"{v}",
                ha="center", fontsize=10, color=C_DARK, fontweight="bold")
        # 圆形同比标注
        circle = Circle((b.get_x() + b.get_width() / 2, v / 2), 0.15,
                        facecolor=C_ORANGE, edgecolor="white", linewidth=1.5, zorder=5)
        ax.add_patch(circle)
        ax.text(b.get_x() + b.get_width() / 2, v / 2, f"{r*100:.0f}%",
                ha="center", va="center", fontsize=8, color="white",
                fontweight="bold", zorder=6)
    style_ax(ax, "图26 柱形圆 — 区域销量与同比标注")
    ax.set_ylim(0, df["销量"].max() * 1.15)
    return save(fig, "26_柱形圆")


def chart_27():
    """27 簇状柱形折线图"""
    df = read_sheet(F2, "27 簇状柱形折线图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    w = 0.35
    ax.bar(x - w/2, df["2022销量"], w, color=C_BLUE, label="2022销量",
           edgecolor="white", linewidth=1, zorder=3)
    ax.bar(x + w/2, df["2021销量"], w, color=C_ORANGE, label="2021销量",
           edgecolor="white", linewidth=1, zorder=3)
    for i, (v22, v21) in enumerate(zip(df["2022销量"], df["2021销量"])):
        ax.text(i - w/2, v22 + 30, f"{v22}", ha="center", fontsize=8, color=C_DARK)
        ax.text(i + w/2, v21 + 30, f"{v21}", ha="center", fontsize=8, color=C_DARK)
    # 同比折线
    ax2 = ax.twinx()
    ax2.plot(x, df["同比去年"], color=C_RED, linewidth=2.5, marker="o",
             markersize=7, markeredgecolor="white", markeredgewidth=1.5,
             zorder=4, label="同比")
    for i, v in enumerate(df["同比去年"]):
        ax2.text(i, v + 0.015, f"{v*100:.0f}%", ha="center", fontsize=8, color=C_RED)
    ax2.set_ylabel("同比", color=C_RED)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_xticks(x)
    ax.set_xticklabels(df["区域"])
    ax.legend(loc="upper left", frameon=False)
    ax2.legend(loc="upper right", frameon=False)
    style_ax(ax, "图27 簇状柱形折线图 — 2022 vs 2021 + 同比")
    ax2.spines["top"].set_visible(False)
    ax.set_ylim(0, max(df["2022销量"].max(), df["2021销量"].max()) * 1.2)
    ax2.set_ylim(0, df["同比去年"].max() * 1.4)
    return save(fig, "27_簇状柱形折线图")


def chart_28():
    """28 复合柱形图（月度+季度叠加）"""
    df = read_sheet(F2, "28 复合柱形图")
    df = df.dropna(subset=["月份"])
    fig, ax = new_fig((8, 4.5))
    x = np.arange(len(df))
    # 季度柱（浅色背景）
    ax.bar(x, df["季度销量"], width=0.6, color="#D6E4F0", edgecolor="white",
           linewidth=1, zorder=2, label="季度销量")
    # 月度柱（深色前景）
    ax.bar(x, df["月度销量"], width=0.4, color=C_BLUE, edgecolor="white",
           linewidth=1.5, zorder=3, label="月度销量")
    for i, (m, q) in enumerate(zip(df["月度销量"], df["季度销量"])):
        ax.text(i, m + 40, f"{m}", ha="center", fontsize=8, color=C_DARK)
    ax.set_xticks(x)
    ax.set_xticklabels(df["月份"])
    ax.legend(frameon=False)
    style_ax(ax, "图28 复合柱形图 — 月度销量(深)叠加季度销量(浅)")
    ax.set_ylim(0, df["季度销量"].max() * 1.15)
    return save(fig, "28_复合柱形图")


def chart_29():
    """29 滑珠图（哑铃图）"""
    df = read_sheet(F2, "29 滑珠图")
    fig, ax = new_fig((7.5, 4.5))
    y = np.arange(len(df))
    for i, (_, row) in enumerate(df.iterrows()):
        # 连接线
        ax.plot([0, row["完成率"]], [i, i], color=C_GRAY, linewidth=2, zorder=2)
        # 起点圆（0%）
        ax.scatter(0, i, s=200, color=C_GRAY, edgecolor="white", linewidth=1.5, zorder=3)
        # 终点圆（完成率）
        ax.scatter(row["完成率"], i, s=250, color=C_BLUE, edgecolor="white", linewidth=1.5, zorder=4)
        ax.text(row["完成率"] + 0.02, i, f"{row['完成率']*100:.0f}%",
                va="center", fontsize=9, color=C_BLUE_D, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(df["区域"])
    ax.set_xlim(-0.05, 1.1)
    style_ax(ax, "图29 滑珠图 — 区域完成率", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    return save(fig, "29_滑珠图")


def chart_30():
    """30 对比滑珠图"""
    df = read_sheet(F2, "30 对比滑珠图", header_row=2)
    fig, ax = new_fig((7.5, 4.5))
    y = np.arange(len(df))
    for i, (_, row) in enumerate(df.iterrows()):
        v22 = row["2022完成率"]
        v21 = row["2021完成率"]
        # 连接线
        ax.plot([v21, v22], [i, i], color=C_GRAY, linewidth=2.5, zorder=2)
        # 2021圆
        ax.scatter(v21, i, s=200, color=C_ORANGE, edgecolor="white", linewidth=1.5, zorder=3)
        # 2022圆
        ax.scatter(v22, i, s=250, color=C_BLUE, edgecolor="white", linewidth=1.5, zorder=4)
        ax.text(v21 - 0.03, i, f"{v21*100:.0f}%", va="center", ha="right",
                fontsize=8, color=C_ORANGE_D)
        ax.text(v22 + 0.02, i, f"{v22*100:.0f}%", va="center", ha="left",
                fontsize=8, color=C_BLUE_D, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(df["区域"])
    ax.set_xlim(-0.05, 1.1)
    style_ax(ax, "图30 对比滑珠图 — 2022 vs 2021 完成率", grid=False)
    ax.grid(axis="x", linestyle="--", alpha=0.3, zorder=0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    # 图例
    handles = [plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=C_ORANGE,
                          markersize=10, label="2021完成率"),
               plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=C_BLUE,
                          markersize=10, label="2022完成率")]
    ax.legend(handles=handles, loc="lower right", frameon=False)
    return save(fig, "30_对比滑珠图")


def run():
    results = []
    for fn in [chart_21, chart_22, chart_23, chart_24, chart_25,
               chart_26, chart_27, chart_28, chart_29, chart_30]:
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