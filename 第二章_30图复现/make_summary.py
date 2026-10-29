# -*- coding: utf-8 -*-
"""生成30个图表的汇总HTML展示页面 + 6x5总览大图"""
import os
import glob
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.image import imread

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHARTS_DIR = os.environ.get("EXCEL_VIZ_OUT", os.path.join(BASE_DIR, "charts"))
OUT_DIR = BASE_DIR

# 按编号排序的图表文件
files = sorted(glob.glob(os.path.join(CHARTS_DIR, "*.png")))
# 提取标题（去掉编号和扩展名）
titles = []
for f in files:
    name = os.path.splitext(os.path.basename(f))[0]
    # 去掉 "01_" 前缀
    if len(name) > 3 and name[2] == "_":
        title = name[3:]
    else:
        title = name
    titles.append(title)

# ===== 1. 生成 6x5 总览大图 =====
fig, axes = plt.subplots(6, 5, figsize=(22, 26))
fig.patch.set_facecolor("white")
fig.suptitle("《Excel数据可视化 — 从图表到数据大屏》第二章  30个可视化图表 Python 复现",
             fontsize=20, fontweight="bold", y=0.995, color="#2C3E50")

for idx, (f, title) in enumerate(zip(files, titles)):
    r, c = divmod(idx, 5)
    ax = axes[r][c]
    img = imread(f)
    ax.imshow(img)
    ax.set_title(f"图{idx+1:02d}  {title}", fontsize=11, fontweight="bold",
                 color="#2C3E50", pad=6)
    ax.axis("off")

plt.tight_layout(rect=[0, 0, 1, 0.98])
overview_path = os.path.join(OUT_DIR, "第二章_30图复现_总览.png")
fig.savefig(overview_path, dpi=80, facecolor="white", bbox_inches="tight")
plt.close(fig)
print(f"总览大图已生成: {overview_path}")

# ===== 2. 生成 HTML 汇总页面 =====
html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>第二章 30个可视化图表 Python 复现</title>
<style>
  body { font-family: "Microsoft YaHei", sans-serif; margin: 0; padding: 20px;
         background: #f5f5f5; color: #333; }
  h1 { text-align: center; color: #2C3E50; border-bottom: 3px solid #4A90E2;
       padding-bottom: 15px; }
  .info { text-align: center; color: #666; margin-bottom: 25px; font-size: 14px; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 1400px; margin: 0 auto; }
  .card { background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          overflow: hidden; transition: transform 0.2s; }
  .card:hover { transform: translateY(-5px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
  .card img { width: 100%; display: block; }
  .card .label { padding: 10px 15px; font-size: 13px; font-weight: bold; color: #2C3E50;
                 border-top: 1px solid #eee; }
  .card .label .num { color: #4A90E2; }
</style>
</head>
<body>
<h1>《Excel数据可视化 — 从图表到数据大屏》第二章<br>30个可视化图表 Python 复现</h1>
<div class="info">数据来源：第二章 图表(前15).xlsx + 第二章 图表(后15).xlsx ｜ 绘图库：matplotlib + numpy + scipy ｜ 共 30 张图表</div>
<div class="grid">
"""
for idx, (f, title) in enumerate(zip(files, titles), 1):
    rel = os.path.relpath(f, OUT_DIR).replace("\\", "/")
    html += f'  <div class="card"><img src="{rel}" alt="{title}"><div class="label"><span class="num">图{idx:02d}</span> {title}</div></div>\n'

html += """</div>
</body>
</html>
"""
html_path = os.path.join(OUT_DIR, "第二章_30图复现_汇总.html")
with open(html_path, "w", encoding="utf-8") as fp:
    fp.write(html)
print(f"HTML汇总页面已生成: {html_path}")
print(f"\n共生成 {len(files)} 张图表")