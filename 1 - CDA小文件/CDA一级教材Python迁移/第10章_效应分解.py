# -*- coding: utf-8 -*-
"""
第10章 使用效应分解方法做预报
- AirPassengers时间序列效应分解（趋势+季节+循环+不规则）
- 乘法模型 vs 加法模型
- 信用卡消费额时间序列
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import pandas as pd
import numpy as np

print("=" * 60)
print("第10章 使用效应分解方法做预报")
print("=" * 60)

# ============================================================
# 一、AirPassengers 经典时间序列效应分解
# ============================================================
print("\n--- 10.1 AirPassengers效应分解 ---")
f = ch("第10章 使用效应分解方法做预报/AirPassengers.csv")
air = read_csv(f)
air["DATE"] = pd.to_datetime(air["DATE"])
air = air.sort_values("DATE").reset_index(drop=True)
print(f"数据: {air.shape}, 时间范围: {air['DATE'].min()} ~ {air['DATE'].max()}")
print(air.head())

# 原始序列图
fig, ax = new_fig((10, 4.5))
ax.plot(air["DATE"], air["AIR"], color=C_BLUE, linewidth=2, zorder=3)
ax.set_xlabel("日期")
ax.set_ylabel("旅客数（千人）")
style_ax(ax, "AirPassengers原始时间序列")
save(fig, "ch10_01_原始序列")

# 对数序列（稳定化）
fig, ax = new_fig((10, 4.5))
ax.plot(air["DATE"], air["ln_AIR"], color=C_ORANGE, linewidth=2, zorder=3)
ax.set_xlabel("日期")
ax.set_ylabel("ln(旅客数)")
style_ax(ax, "对数变换后的时间序列")
save(fig, "ch10_02_对数序列")

# 使用statsmodels进行效应分解
from statsmodels.tsa.seasonal import seasonal_decompose

ts = pd.Series(air["AIR"].values, index=air["DATE"])

# 乘法模型分解
result_mul = seasonal_decompose(ts, model="multiplicative", period=12)
# 加法模型分解
result_add = seasonal_decompose(ts, model="additive", period=12)

# 乘法模型四要素图
fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
fig.patch.set_facecolor("white")
components = [
    (result_mul.observed, "原始序列 (Observed)", C_BLUE),
    (result_mul.trend, "趋势效应 (Trend)", C_ORANGE),
    (result_mul.seasonal, "季节效应 (Seasonal)", C_GREEN),
    (result_mul.resid, "不规则效应 (Residual)", C_RED),
]
for i, (comp, label, color) in enumerate(components):
    axes[i].plot(comp, color=color, linewidth=1.5)
    axes[i].set_ylabel(label, fontsize=10)
    axes[i].grid(axis="y", linestyle="--", alpha=0.3)
    for s in ["top", "right"]:
        axes[i].spines[s].set_visible(False)
fig.suptitle("AirPassengers 乘法模型效应分解", fontsize=14, fontweight="bold", y=0.98)
save(fig, "ch10_03_乘法分解")

# 加法模型四要素图
fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
fig.patch.set_facecolor("white")
components = [
    (result_add.observed, "原始序列 (Observed)", C_BLUE),
    (result_add.trend, "趋势效应 (Trend)", C_ORANGE),
    (result_add.seasonal, "季节效应 (Seasonal)", C_GREEN),
    (result_add.resid, "不规则效应 (Residual)", C_RED),
]
for i, (comp, label, color) in enumerate(components):
    axes[i].plot(comp, color=color, linewidth=1.5)
    axes[i].set_ylabel(label, fontsize=10)
    axes[i].grid(axis="y", linestyle="--", alpha=0.3)
    for s in ["top", "right"]:
        axes[i].spines[s].set_visible(False)
fig.suptitle("AirPassengers 加法模型效应分解", fontsize=14, fontweight="bold", y=0.98)
save(fig, "ch10_04_加法分解")

# 季节效应柱形图
fig, ax = new_fig((8, 5))
seasonal = result_mul.seasonal[:12]
months = [f"{m}月" for m in range(1, 13)]
ax.bar(months, seasonal.values, color=PALETTE[:12], zorder=3)
ax.axhline(1, color=C_GRAY, linestyle="--", alpha=0.5)
ax.set_ylabel("季节因子")
ax.set_xticklabels(months, rotation=45)
style_ax(ax, "乘法模型季节效应因子（月度）")
save(fig, "ch10_05_季节因子")

# 趋势效应图
fig, ax = new_fig((10, 4.5))
ax.plot(result_mul.trend, color=C_ORANGE, linewidth=2.5, label="趋势效应", zorder=3)
ax.plot(ts, color=C_BLUE, linewidth=1, alpha=0.4, label="原始序列", zorder=2)
ax.set_xlabel("日期")
ax.set_ylabel("旅客数")
ax.legend()
style_ax(ax, "趋势效应 vs 原始序列")
save(fig, "ch10_06_趋势效应")

# 不规则效应分布
fig, ax = new_fig((8, 4.5))
resid = result_mul.resid.dropna()
ax.hist(resid, bins=30, color=C_RED, alpha=0.6, edgecolor="white", zorder=3)
ax.axvline(resid.mean(), color=C_BLUE, linestyle="--", linewidth=2, label=f"均值={resid.mean():.4f}")
ax.set_xlabel("不规则效应")
ax.set_ylabel("频次")
ax.legend()
style_ax(ax, "不规则效应（残差）分布")
save(fig, "ch10_07_残差分布")

# ============================================================
# 二、简单预测：趋势外推 + 季节因子
# ============================================================
print("\n--- 10.2 趋势外推预测 ---")
# 用线性回归拟合趋势
from numpy.polynomial import polynomial as P
trend_valid = result_mul.trend.dropna()
x_num = np.arange(len(trend_valid))
coeffs = np.polyfit(x_num, trend_valid.values, 2)

# 预测未来12个月
future_x = np.arange(len(trend_valid), len(trend_valid) + 12)
future_trend = np.polyval(coeffs, future_x)
future_dates = pd.date_range(trend_valid.index[-1] + pd.Timedelta(days=30), periods=12, freq="MS")
future_seasonal = seasonal.values
future_pred = future_trend * future_seasonal

fig, ax = new_fig((12, 5))
ax.plot(ts, color=C_BLUE, linewidth=2, label="历史数据", zorder=3)
ax.plot(future_dates, future_pred, color=C_RED, linewidth=2, linestyle="--", label="预测", zorder=4)
ax.axvline(trend_valid.index[-1], color=C_GRAY, linestyle=":", alpha=0.5)
ax.set_xlabel("日期")
ax.set_ylabel("旅客数（千人）")
ax.legend()
style_ax(ax, "AirPassengers未来12个月预测（趋势外推×季节因子）")
save(fig, "ch10_08_预测")

# ============================================================
# 三、信用卡消费额时间序列（如果有数据）
# ============================================================
print("\n--- 10.3 信用卡消费额时间序列 ---")
f2 = ch("第10章 使用效应分解方法做预报/信用卡消费额_去除节日.xlsx")
try:
    card_xls = pd.ExcelFile(f2)
    print(f"工作表: {card_xls.sheet_names}")
    for sn in card_xls.sheet_names:
        sdf = card_xls.parse(sn, nrows=3)
        print(f"  [{sn}] cols={list(sdf.columns)}")
    # 找到有日期和金额的表
    for sn in card_xls.sheet_names:
        sdf = card_xls.parse(sn)
        date_cols = [c for c in sdf.columns if any(k in str(c) for k in ["日期", "时间", "date", "月"])]
        amt_cols = [c for c in sdf.columns if any(k in str(c) for k in ["金额", "消费", "额", "amount"])]
        if date_cols and amt_cols:
            print(f"  使用表[{sn}]: date={date_cols[0]}, amount={amt_cols[0]}")
            sdf[date_cols[0]] = pd.to_datetime(sdf[date_cols[0]], errors="coerce")
            sdf = sdf.dropna(subset=[date_cols[0]]).sort_values(date_cols[0])
            ts2 = pd.Series(sdf[amt_cols[0]].values, index=sdf[date_cols[0]])
            if len(ts2) >= 24:
                result2 = seasonal_decompose(ts2, model="multiplicative", period=12, extrapolate_trend="freq")
                fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True)
                fig.patch.set_facecolor("white")
                for i, (comp, label, color) in enumerate([
                    (result2.observed, "原始序列", C_BLUE),
                    (result2.trend, "趋势效应", C_ORANGE),
                    (result2.seasonal, "季节效应", C_GREEN),
                    (result2.resid, "不规则效应", C_RED),
                ]):
                    axes[i].plot(comp, color=color, linewidth=1.5)
                    axes[i].set_ylabel(label, fontsize=10)
                    axes[i].grid(axis="y", linestyle="--", alpha=0.3)
                    for s in ["top", "right"]:
                        axes[i].spines[s].set_visible(False)
                fig.suptitle("信用卡消费额效应分解", fontsize=14, fontweight="bold", y=0.98)
                save(fig, "ch10_09_信用卡消费分解")
            break
except Exception as e:
    print(f"信用卡消费额处理跳过: {e}")

print("\n第10章完成！生成图表: ch10_01 ~ ch10_09")