# -*- coding: utf-8 -*-
"""CDA一级教材Python迁移 - 公共工具模块"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"

# 路径全部相对脚本所在目录，换机器无需改代码
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 教材数据目录：默认 ./data，可用环境变量 CDA_DATA_ROOT 覆盖
BASE = os.environ.get("CDA_DATA_ROOT", os.path.join(BASE_DIR, "data"))

# 图表输出目录：默认 ./charts
OUT_DIR = os.environ.get("CDA_OUT_DIR", os.path.join(BASE_DIR, "charts"))
os.makedirs(OUT_DIR, exist_ok=True)

C_BLUE = "#4A90E2"
C_BLUE_D = "#2E5C8A"
C_ORANGE = "#F5A623"
C_ORANGE_D = "#D48806"
C_GREEN = "#7ED321"
C_RED = "#E74C3C"
C_GRAY = "#9B9B9B"
C_DARK = "#4A4A4A"
PALETTE = [C_BLUE, C_ORANGE, C_GREEN, C_RED, "#9B59B6", "#3498DB", "#E67E22", "#1ABC9C"]


def ch(n):
    return os.path.join(BASE, n)


def save(fig, name):
    path = os.path.join(OUT_DIR, f"{name}.png")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def style_ax(ax, title=None, grid=True):
    if title:
        ax.set_title(title, fontsize=13, fontweight="bold", color=C_DARK, pad=12)
    if grid:
        ax.grid(axis="y", linestyle="--", alpha=0.3, zorder=0)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(C_GRAY)
    ax.spines["bottom"].set_color(C_GRAY)
    ax.tick_params(colors=C_DARK)


def new_fig(figsize=(7, 4.5)):
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor("white")
    return fig, ax


def clean_money(s):
    """清洗带$和逗号的金额"""
    if pd.isna(s) or s == "":
        return np.nan
    if isinstance(s, (int, float)):
        return float(s)
    return float(str(s).replace("$", "").replace(",", "").strip())

def resolve(path):
    """数据文件定位：原文件不存在时自动回退到 .gz 压缩版"""
    if os.path.exists(path):
        return path
    if os.path.exists(path + ".gz"):
        return path + ".gz"
    raise FileNotFoundError(
        f"缺少数据文件：{path}\n"
        f"请确认 data/ 目录完整（见 data/README.md），"
        f"或用环境变量 CDA_DATA_ROOT 指向教材数据目录。"
    )


def read_csv(path, **kw):
    """自动尝试utf-8/gbk编码读取CSV；大文件可用 .csv.gz 存放"""
    path = resolve(path)
    for enc in ["utf-8", "gbk", "gb18030", "latin1"]:
        try:
            return pd.read_csv(path, encoding=enc, **kw)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path, **kw)