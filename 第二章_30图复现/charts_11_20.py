# -*- coding: utf-8 -*-
"""图表 11-20：折线图 + 圆环图 + 水球图 + 玉玦图 + 跑道图 + 南丁格尔图"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle, FancyBboxPatch
import common as C
from common import (read_sheet, save, new_fig, style_ax,
                    C_BLUE, C_BLUE_D, C_ORANGE, C_ORANGE_D, C_GREEN, C_RED,
                    C_GRAY, C_DARK, F1, F2)


def chart_11():
    """11 平滑折线图"""
    df = read_sheet(F1, "11 平滑折线图")
    # 合并年份+月份为标签
    df["标签"] = df["年份"].astype(str) + "-" + df["月份"].astype(str)
    fig, ax = new_fig((9, 4.5))
    from scipy.interpolate import make_interp_spline
    x = np.arange(len(df))
    x_smooth = np.linspace(x.min(), x.max(), 200)
    spl = make_interp_spline(x, df["销量"], k=3)
    y_smooth = spl(x_smooth)
    ax.plot(x_smooth, y_smooth, color=C_BLUE, linewidth=2.5, zorder=3)
    ax.fill_between(x_smooth, y_smooth, alpha=0.15, color=C_BLUE, zorder=2)
    ax.scatter(x, df["销量"], color=C_BLUE_D, s=50, zorder=4, edgecolor="white", linewidth=1.5)
    for i, v in enumerate(df["销量"]):
        ax.text(i, v + 15, f"{v}", ha="center", fontsize=8, color=C_DARK)
    ax.set_xticks(x)
    ax.set_xticklabels(df["标签"], rotation=45, ha="right", fontsize=8)
    style_ax(ax, "图11 平滑折线图 — 月度销量趋势")
    ax.set_ylim(0, df["销量"].max() * 1.15)
    return save(fig, "11_平滑折线图")


def chart_12():
    """12 菱形走势图"""
    df = read_sheet(F1, "12 菱形走势图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    ax.plot(x, df["完成率"], color=C_BLUE, linewidth=2, zorder=2, alpha=0.5)
    ax.scatter(x, df["完成率"], marker="D", s=180, color=C_ORANGE,
               edgecolor=C_BLUE_D, linewidth=1.5, zorder=4)
    for i, v in enumerate(df["完成率"]):
        ax.text(i, v + 0.03, f"{v*100:.1f}%", ha="center", fontsize=9,
                color=C_DARK, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(df["月份"])
    style_ax(ax, "图12 菱形走势图 — 月度完成率")
    ax.set_ylim(0, df["完成率"].max() * 1.2)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    return save(fig, "12_菱形走势图")


def chart_13():
    """13 对比折线图"""
    df = read_sheet(F1, "13 对比折线图")
    fig, ax = new_fig((7.5, 4.5))
    x = np.arange(len(df))
    ax.plot(x, df["2021年"], color=C_BLUE, linewidth=2.5, marker="o",
            markersize=7, label="2021年", markeredgecolor="white",
            markeredgewidth=1.5, zorder=3)
    ax.plot(x, df["2022年"], color=C_ORANGE, linewidth=2.5, marker="s",
            markersize=7, label="2022年", markeredgecolor="white",
            markeredgewidth=1.5, zorder=3)
    ax.fill_between(x, df["2021年"], df["2022年"], alpha=0.12, color=C_GRAY, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(df["月份"])
    ax.legend(frameon=False)
    style_ax(ax, "图13 对比折线图 — 2021 vs 2022 月度销量")
    ax.set_ylim(0, max(df["2021年"].max(), df["2022年"].max()) * 1.15)
    return save(fig, "13_对比折线图")


def chart_14():
    """14 单值圆环图"""
    df = read_sheet(F1, "14 单值圆环图")
    rate = df["完成率"].iloc[0]
    fig, ax = new_fig((5, 5))
    ax.set_aspect("equal")
    # 背景环
    ax.add_patch(Wedge((0, 0), 1, 0, 360, width=0.25, facecolor="#E8E8E8"))
    # 完成环
    ax.add_patch(Wedge((0, 0), 1, 90, 90 - 360 * rate, width=0.25, facecolor=C_BLUE))
    ax.text(0, 0, f"{rate*100:.0f}%", ha="center", va="center",
            fontsize=32, fontweight="bold", color=C_BLUE_D)
    ax.text(0, -0.3, "完成率", ha="center", va="center", fontsize=12, color=C_GRAY)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图14 单值圆环图", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "14_单值圆环图")


def chart_15():
    """15 水球图"""
    df = read_sheet(F1, "15 水球图")
    rate = df["完成率"].iloc[0]
    fig, ax = new_fig((5, 5))
    ax.set_aspect("equal")
    # 外圆
    ax.add_patch(Circle((0, 0), 1, facecolor="#E8F4FD", edgecolor=C_BLUE, linewidth=2))
    # 水面（波浪效果）
    theta = np.linspace(0, 2 * np.pi, 200)
    water_level = -1 + 2 * rate  # 水面y坐标
    x_wave = np.linspace(-1, 1, 200)
    y_wave = water_level + 0.04 * np.sin(10 * x_wave * np.pi)
    # 裁剪到圆内
    mask = x_wave**2 + y_wave**2 <= 1
    ax.fill_between(x_wave, y_wave, -1, where=mask, color=C_BLUE, alpha=0.7, zorder=2)
    # 第二层波浪
    y_wave2 = water_level + 0.04 * np.sin(10 * x_wave * np.pi + np.pi) + 0.06
    mask2 = x_wave**2 + y_wave2**2 <= 1
    ax.fill_between(x_wave, y_wave2, -1, where=mask2, color=C_BLUE, alpha=0.4, zorder=1)
    ax.text(0, 0.15, f"{rate*100:.0f}%", ha="center", va="center",
            fontsize=30, fontweight="bold", color="white", zorder=5)
    ax.text(0, -0.15, "完成率", ha="center", va="center", fontsize=11, color="white", zorder=5)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图15 水球图", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "15_水球图")


def chart_16():
    """16 波浪水球图"""
    df = read_sheet(F2, "16 波浪水球图 ", header_row=2)
    rate = df["完成率"].iloc[0]
    fig, ax = new_fig((5, 5))
    ax.set_aspect("equal")
    ax.add_patch(Circle((0, 0), 1, facecolor="#E8F4FD", edgecolor=C_BLUE, linewidth=2))
    water_level = -1 + 2 * rate
    x_wave = np.linspace(-1.1, 1.1, 300)
    # 多层波浪
    for layer, (amp, phase, alpha) in enumerate([(0.05, 0, 0.7), (0.04, np.pi, 0.5), (0.03, np.pi/2, 0.3)]):
        y_wave = water_level + amp * np.sin(8 * x_wave * np.pi + phase) - layer * 0.05
        mask = x_wave**2 + np.maximum(y_wave, -1)**2 <= 1
        ax.fill_between(x_wave, y_wave, -1.1, where=mask, color=C_BLUE, alpha=alpha, zorder=2-layer)
    ax.text(0, 0.15, f"{rate*100:.0f}%", ha="center", va="center",
            fontsize=30, fontweight="bold", color="white", zorder=5)
    ax.text(0, -0.15, "完成率", ha="center", va="center", fontsize=11, color="white", zorder=5)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图16 波浪水球图", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "16_波浪水球图")


def chart_17():
    """17 玉玦图（同心圆环）"""
    df = read_sheet(F2, "17 玉玦图")
    fig, ax = new_fig((6, 5))
    ax.set_aspect("equal")
    n = len(df)
    colors = [plt.cm.viridis(i / n) for i in range(n)]
    for i, (_, row) in enumerate(df.iterrows()):
        r = n - i  # 外圈半径大
        # 背景环
        ax.add_patch(Wedge((0, 0), r, 0, 360, width=0.6, facecolor="#F0F0F0"))
        # 数据环（有缺口的玉玦）
        ratio = row["占比"]
        ax.add_patch(Wedge((0, 0), r, 90, 90 - 360 * ratio, width=0.6, facecolor=colors[i]))
        ax.text(r + 0.3, 0, f"{row['年龄']}: {ratio*100:.1f}%",
                ha="left", va="center", fontsize=9, color=C_DARK)
    ax.set_xlim(-n - 0.5, n + 3.5)
    ax.set_ylim(-n - 0.5, n + 0.5)
    ax.axis("off")
    ax.set_title("图17 玉玦图 — 年龄占比", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "17_玉玦图")


def chart_18():
    """18 跑道图"""
    df = read_sheet(F2, "18 跑道图")
    fig, ax = new_fig((7, 5))
    ax.set_aspect("equal")
    n = len(df)
    colors = [plt.cm.plasma(i / n) for i in range(n)]
    max_val = df["人数"].max()
    for i, (_, row) in enumerate(df.iterrows()):
        r = n - i
        # 背景跑道
        ax.add_patch(Wedge((0, 0), r, 0, 360, width=0.5, facecolor="#F0F0F0"))
        # 数据跑道
        ratio = row["人数"] / max_val
        ax.add_patch(Wedge((0, 0), r, 90, 90 - 360 * ratio, width=0.5, facecolor=colors[i]))
        ax.text(0, r, f"{row['部门'].strip()} {row['人数']}人",
                ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    ax.set_xlim(-n - 0.5, n + 0.5)
    ax.set_ylim(-n - 0.5, n + 0.5)
    ax.axis("off")
    ax.set_title("图18 跑道图 — 部门人数", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "18_跑道图")


def chart_19():
    """19 南丁格尔圆饼图（玫瑰图）"""
    df = read_sheet(F2, "19 南丁格尔圆饼图")
    fig, ax = new_fig((6, 6))
    ax.set_aspect("equal")
    n = len(df)
    colors = [plt.cm.Set2(i / n) for i in range(n)]
    max_ratio = df["人数占比"].max()
    for i, (_, row) in enumerate(df.iterrows()):
        r = row["人数占比"] / max_ratio
        theta1 = 90 - i * (360 / n)
        theta2 = theta1 - (360 / n)
        ax.add_patch(Wedge((0, 0), r, theta2, theta1, facecolor=colors[i],
                            edgecolor="white", linewidth=2))
        angle_mid = np.radians((theta1 + theta2) / 2)
        ax.text(r * 0.7 * np.cos(angle_mid), r * 0.7 * np.sin(angle_mid),
                f"{row['部门']}\n{row['人数占比']*100:.1f}%",
                ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图19 南丁格尔圆饼图 — 部门人数占比", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "19_南丁格尔圆饼图")


def chart_20():
    """20 南丁格尔圆环图"""
    df = read_sheet(F2, "20 南丁格尔圆环图")
    fig, ax = new_fig((6, 6))
    ax.set_aspect("equal")
    n = len(df)
    colors = [plt.cm.Set3(i / n) for i in range(n)]
    max_ratio = df["人数占比"].max()
    for i, (_, row) in enumerate(df.iterrows()):
        r = row["人数占比"] / max_ratio
        theta1 = 90 - i * (360 / n)
        theta2 = theta1 - (360 / n)
        ax.add_patch(Wedge((0, 0), r, theta2, theta1, width=0.4,
                            facecolor=colors[i], edgecolor="white", linewidth=2))
        angle_mid = np.radians((theta1 + theta2) / 2)
        ax.text(r * 0.8 * np.cos(angle_mid), r * 0.8 * np.sin(angle_mid),
                f"{row['年龄']}\n{row['人数占比']*100:.1f}%",
                ha="center", va="center", fontsize=8, color=C_DARK, fontweight="bold")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")
    ax.set_title("图20 南丁格尔圆环图 — 年龄人数占比", fontsize=13, fontweight="bold", color=C_DARK, pad=10)
    return save(fig, "20_南丁格尔圆环图")


def run():
    results = []
    for fn in [chart_11, chart_12, chart_13, chart_14, chart_15,
               chart_16, chart_17, chart_18, chart_19, chart_20]:
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