# -*- coding: utf-8 -*-
"""生成CDA一级教材Python迁移汇总HTML页面"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *

charts_dir = OUT_DIR
chapters = {
    "第1章 数据分析思维": ["ch01_01_市场销售额对比", "ch01_02_市场利润率对比", "ch01_03_销售利润散点",
                      "ch01_04_信用卡类型分布", "ch01_05_发卡年度趋势", "ch01_06_贷款状态分布",
                      "ch01_07_客户性别分布", "ch01_08_维度模型_产品信息表"],
    "第2章 数据分析方法": ["ch02_01_波士顿矩阵", "ch02_02_RFM客户分群", "ch02_03_RFM散点",
                      "ch02_04_同期群留存", "ch02_05_漏斗图", "ch02_06_相关系数矩阵",
                      "ch02_07_相关散点回归", "ch02_08_忠诚度分群", "ch02_09_忠诚度分布"],
    "第3章 商业数据分析框架": ["ch03_01_省份销售趋势", "ch03_02_月度销售热力图", "ch03_03_省份销售排名",
                          "ch03_04_期间费用对比", "ch03_05_管理费用明细", "ch03_06_期间费用饼图",
                          "ch03_07_品类性别分析", "ch03_08_年龄分布", "ch03_09_支付方式",
                          "ch03_10_品类销量排名", "ch03_11_年龄品类热力图"],
    "第5章 业务数据分析": ["ch05_01_品类销售分布", "ch05_02_风险偏好分布", "ch05_03_年龄收入散点",
                      "ch05_04_购买目的", "ch05_05_性别品类交叉", "ch05_06_渠道申请量",
                      "ch05_07_日度趋势", "ch05_08_渠道占比", "ch05_09_累计申请量"],
    "第8章 SQL基础": ["ch08_01_过滤排序", "ch08_02_表达式新列", "ch08_03_列重编码",
                   "ch08_04_分组汇总", "ch08_05_横向连接", "ch08_06_子查询", "ch08_07_集合操作"],
    "第9章 用户画像": ["ch09_01_性别分布", "ch09_02_年龄分布", "ch09_03_卡类型年龄",
                   "ch09_04_交易频次", "ch09_05_年龄交易频次", "ch09_06_出入账比例",
                   "ch09_07_画像雷达图", "ch09_08_RFM矩阵"],
    "第10章 效应分解": ["ch10_01_原始序列", "ch10_02_对数序列", "ch10_03_乘法分解",
                     "ch10_04_加法分解", "ch10_05_季节因子", "ch10_06_趋势效应",
                     "ch10_07_残差分布", "ch10_08_预测", "ch10_09_信用卡消费分解"],
}

html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>CDA一级教材《商业数据分析》Python迁移 - 汇总</title>
<style>
body { font-family: 'Microsoft YaHei', sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
h1 { text-align: center; color: #2E5C8A; border-bottom: 3px solid #4A90E2; padding-bottom: 10px; }
h2 { color: #2E5C8A; border-left: 5px solid #F5A623; padding-left: 10px; margin-top: 30px; }
.chapter { background: white; border-radius: 8px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.chart { display: inline-block; margin: 10px; text-align: center; }
.chart img { max-width: 550px; border: 1px solid #ddd; border-radius: 4px; }
.chart .name { display: block; font-size: 13px; color: #666; margin-top: 5px; }
.summary { background: #4A90E2; color: white; padding: 15px; border-radius: 8px; text-align: center; font-size: 16px; }
</style>
</head>
<body>
<h1>CDA一级教材《商业数据分析》Python迁移</h1>
<div class="summary">共7个章节 · 61张图表 · 用Python复现PowerBI/Excel/SQL实现</div>
"""

total = 0
for ch_name, charts in chapters.items():
    html += f'<h2>{ch_name}（{len(charts)}张）</h2>\n<div class="chapter">\n'
    for c in charts:
        path = os.path.join(charts_dir, f"{c}.png")
        if os.path.exists(path):
            html += f'<div class="chart"><img src="charts/{c}.png"><span class="name">{c}</span></div>\n'
            total += 1
    html += "</div>\n"

html += f"\n<div class='summary'>总计 {total} 张图表</div>\n</body>\n</html>"

out_path = os.path.join(os.path.dirname(charts_dir), "CDA一级教材_汇总.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)
print(f"汇总页面已生成: {out_path}")
print(f"共 {total} 张图表")