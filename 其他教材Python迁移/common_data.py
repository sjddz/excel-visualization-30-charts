# -*- coding: utf-8 -*-
"""代表案例公共模块：数据加载、路径定位、中文字体、图片保存

路径全部相对本文件，clone 下来无需改代码即可运行。
大文件（data_clust / creditdata_small）以 .csv.gz 存放，pandas 会自动解压。
"""
import os
import sys

# Windows 控制台默认 GBK，遇到个别符号会直接抛 UnicodeEncodeError，这里降级为替换
try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("CASE_DATA_DIR", os.path.join(BASE_DIR, "data"))
IMG_DIR = os.environ.get("CASE_IMG_DIR", os.path.join(BASE_DIR, "images"))
os.makedirs(IMG_DIR, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 100
plt.rcParams["savefig.dpi"] = 120
plt.rcParams["savefig.bbox"] = "tight"


def _locate(name):
    """依次尝试原文件与 .gz 压缩版"""
    for cand in (name, name + ".gz"):
        path = os.path.join(DATA_DIR, cand)
        if os.path.exists(path):
            return path
    raise SystemExit(
        f"缺少数据文件：{name}\n"
        f"请确认 data/ 目录完整（见 data/README.md），"
        f"或用环境变量 CASE_DATA_DIR 指向数据目录。"
    )


def load_csv(name, **kw):
    return pd.read_csv(_locate(name), **kw)


def load_excel(name, **kw):
    return pd.read_excel(_locate(name), **kw)


def save(fig, name):
    """保存图片到 images/，返回路径"""
    path = os.path.join(IMG_DIR, f"{name}.png")
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    print(f"  图片已保存: {os.path.relpath(path, BASE_DIR)}")
    return path


def title(text):
    """统一的分节标题"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)
