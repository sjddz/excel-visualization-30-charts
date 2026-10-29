# -*- coding: utf-8 -*-
"""通用工具模块：字体设置、配色、数据读取、保存"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, Wedge, Circle, Rectangle, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# 中文字体
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"

# 路径全部相对脚本所在目录，换机器无需改代码
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据目录：默认 ./data，可用环境变量 EXCEL_VIZ_DATA 覆盖
DATA_DIR = os.environ.get("EXCEL_VIZ_DATA", os.path.join(BASE_DIR, "data"))

# 输出目录：默认 ./charts
OUT_DIR = os.environ.get("EXCEL_VIZ_OUT", os.path.join(BASE_DIR, "charts"))
os.makedirs(OUT_DIR, exist_ok=True)

# 教材配套 Excel（已随仓库放在 data/ 下）
F1 = os.path.join(DATA_DIR, "第二章 图表(前15).xlsx")
F2 = os.path.join(DATA_DIR, "第二章 图表(后15).xlsx")


def _require(path):
    """数据缺失时给出可操作的提示，而不是直接抛 FileNotFoundError"""
    if not os.path.exists(path):
        raise SystemExit(
            f"找不到数据文件：{path}\n"
            f"请确认 data/ 目录完整（见 data/README.md），"
            f"或用环境变量 EXCEL_VIZ_DATA 指向数据所在目录。"
        )
    return path


def read_sheet(file_path, sheet_name, header_row=1, usecols=None):
    """读取Excel工作表，跳过空列"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
    # 将空字符串视为nan
    df = df.replace("", pd.NA)
    # 删除全空列和以Unnamed开头的空列
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.astype(str).str.startswith("Unnamed")]
    # 删除全空行
    df = df.dropna(axis=0, how="all")
    return df


def save(fig, name):
    """保存图表"""
    path = os.path.join(OUT_DIR, f"{name}.png")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


# 配色方案（参考原书商务蓝橙色调）
C_BLUE = "#4A90E2"
C_BLUE_D = "#2E5C8A"
C_ORANGE = "#F5A623"
C_ORANGE_D = "#D48806"
C_GREEN = "#7ED321"
C_RED = "#E74C3C"
C_GRAY = "#9B9B9B"
C_DARK = "#4A4A4A"

# 渐变色列表
GRADIENT_BLUE = ["#1A5490", "#2E78B8", "#4A90E2", "#7FB3E8", "#B0D4F0"]
GRADIENT_ORANGE = ["#D48806", "#F5A623", "#F8B947", "#FAC870", "#FCD9A3"]


def gradient_bar(ax, x, y, width=0.6, colors=None, base_color=C_BLUE):
    """绘制渐变柱形"""
    if colors is None:
        n = len(y)
        colors = [plt.cm.get_cmap("Blues")(0.4 + 0.5 * i / max(n - 1, 1)) for i in range(n)]
    bars = ax.bar(x, y, width=width, color=colors, edgecolor="white", linewidth=1.2, zorder=3)
    return bars


def style_ax(ax, title=None, grid=True):
    """统一美化坐标轴"""
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color=C_DARK, pad=12)
    if grid:
        ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)
    ax.tick_params(colors=C_DARK)


def new_fig(figsize=(7, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    return fig, ax