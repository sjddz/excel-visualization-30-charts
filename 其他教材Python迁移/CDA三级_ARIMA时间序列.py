# -*- coding: utf-8 -*-
"""CDA 三级教材 · 4.1 时间序列预测（AR / MA / ARMA / ARIMA）

来源：CDA 三级教材配套 notebook「ARIMA.ipynb」
改写目标：教材在同一份 notebook 里连做四个模型，原稿存在两个问题：
         ① 依赖 `%matplotlib inline`、`get_ipython()` 等只能在 Jupyter 里跑的语法；
         ② ARMA 一节引用了未定义的变量 `param_seasonal`，直接运行会报错。
         本脚本改用 statsmodels 新版 `arima.model.ARIMA` 接口，并把四类模型的
         识别 → 定阶 → 建模拟合 → 残差检验 → 预测 全流程写清楚。

数据：ts_simu200.csv 是 200 期模拟序列，列名即"真实数据生成过程"，
      例如 AR1_a 由 AR(1) 生成、ARIMA_110 由 ARIMA(1,1,0) 生成，
      方便验证"模型识别得对不对"。

运行：python CDA三级_ARIMA时间序列.py
"""
import os
import sys
import warnings

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import itertools

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.graphics.gofplots import qqplot
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller

from common_data import load_csv, save, title

warnings.filterwarnings("ignore")
plt.rcParams["figure.figsize"] = (8, 4)

# ---------------------------------------------------------------- 1. 读数据
title("1. 读取模拟序列")
df = load_csv("ts_simu200.csv", index_col="t")
# 用真实日历日期做索引，画图 x 轴更直观（200 天）
df.index = pd.date_range(start="2017-01-01", periods=len(df), freq="D")
print(f"序列长度：{len(df)} 期，可用列：")
print(", ".join(df.columns))

# ---------------------------------------------------------------- 2. 自相关工具
title("2. 如何用 ACF / PACF 定阶（先记结论再看图）")
print("· AR(p)：ACF 拖尾（缓慢衰减），PACF 在 p 阶后截尾；")
print("· MA(q)：ACF 在 q 阶后截尾，PACF 拖尾；")
print("· ARMA(p,q)：ACF 与 PACF 都拖尾，需要靠 AIC/BIC 网格搜索定阶；")
print("· 非平稳序列：先差分（d 阶），再对差分后序列重复上面的判断。")

# ---------------------------------------------------------------- 3. AR(1)
title("3. AR(1) 模型：AR1_a")
dta = df["AR1_a"]
fig, ax = plt.subplots()
ax.plot(dta.index, dta.values, color="#4A90E2")
ax.set_title("AR(1) 序列：围绕均值上下波动，无明显趋势")
ax.set_ylabel("取值")
save(fig, "三级_AR1_序列图")

fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
plot_acf(dta, lags=20, ax=axes[0])
plot_pacf(dta, lags=20, ax=axes[1], method="ywm")
fig.suptitle("AR(1) 的 ACF（拖尾）与 PACF（1 阶截尾）")
save(fig, "三级_AR1_ACF_PACF")

ar1 = ARIMA(dta, order=(1, 0, 0)).fit()
print(f"AR(1) 拟合结果：AR 系数 = {ar1.params['ar.L1']:.3f}，AIC = {ar1.aic:.2f}")
print(f"（真实生成过程就是 AR(1)，系数接近理论值说明识别正确）")

# 残差检验：残差应接近白噪声
resid = ar1.resid
dw = sm.stats.durbin_watson(resid)
p_norm = stats.normaltest(resid).pvalue
print(f"\n残差检验：DW = {dw:.3f}（接近 2 表示无一阶自相关）")
print(f"          正态性检验 p = {p_norm:.3f}（>0.05 不能拒绝正态）")

fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
plot_acf(resid, lags=20, ax=axes[0])
plot_pacf(resid, lags=20, ax=axes[1], method="ywm")
qqplot(resid, line="45", ax=axes[2], fit=True)
axes[0].set_title("残差 ACF")
axes[1].set_title("残差 PACF")
axes[2].set_title("残差 Q-Q")
fig.tight_layout()
save(fig, "三级_AR1_残差检验")

fc = ar1.get_forecast(steps=5)
print("\n未来 5 期预测：")
print(fc.summary_frame()[["mean", "mean_ci_lower", "mean_ci_upper"]].round(2).to_string())

# ---------------------------------------------------------------- 4. MA(1)
title("4. MA(1) 模型：MA1_a")
dta = df["MA1_a"]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
plot_acf(dta, lags=20, ax=axes[0])
plot_pacf(dta, lags=20, ax=axes[1], method="ywm")
fig.suptitle("MA(1) 的 ACF（1 阶截尾）与 PACF（拖尾）")
save(fig, "三级_MA1_ACF_PACF")

ma1 = ARIMA(dta, order=(0, 0, 1)).fit()
print(f"MA(1) 拟合结果：MA 系数 = {ma1.params['ma.L1']:.3f}，AIC = {ma1.aic:.2f}")
print(f"残差 DW = {sm.stats.durbin_watson(ma1.resid):.3f}，"
      f"正态性 p = {stats.normaltest(ma1.resid).pvalue:.3f}")
print("\n未来 5 期预测：")
print(ma1.get_forecast(steps=5).summary_frame()[["mean"]].round(2).to_string())

# ---------------------------------------------------------------- 5. ARMA(1,1)
title("5. ARMA(1,1)：网格搜索定阶")
dta = df["ARMA_11_b"]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))
plot_acf(dta, lags=20, ax=axes[0])
plot_pacf(dta, lags=20, ax=axes[1], method="ywm")
fig.suptitle("ARMA 的 ACF / PACF 均拖尾，无法直接定阶")
save(fig, "三级_ARMA_ACF_PACF")

best_aic, best_order = np.inf, None
rows = []
for p, d, q in itertools.product(range(2), range(2), range(2)):
    if p == 0 and q == 0:
        continue
    try:
        m = ARIMA(dta, order=(p, d, q)).fit()
        rows.append({"p": p, "d": d, "q": q, "AIC": round(m.aic, 2)})
        if m.aic < best_aic:
            best_aic, best_order = m.aic, (p, d, q)
    except Exception:
        continue

print(pd.DataFrame(rows).sort_values("AIC").to_string(index=False))
print(f"\nAIC 最优阶数：ARIMA{best_order}，AIC = {best_aic:.2f}")

arma = ARIMA(dta, order=best_order).fit()
print(f"拟合参数：\n{arma.params.round(3).to_string()}")

# ---------------------------------------------------------------- 6. ARIMA(1,1,0)
title("6. 非平稳序列：ARIMA(1,1,0)")
dta = df["ARIMA_110"]

# 6.1 平稳性检验：p 值大 → 不能拒绝"有单位根"，说明不平稳
adf = adfuller(dta)
print(f"原序列 ADF 统计量 = {adf[0]:.3f}，p = {adf[1]:.4f}")
print("结论：p 值较大，序列非平稳，需要差分。" if adf[1] > 0.05 else "结论：序列平稳。")

fig, ax = plt.subplots()
ax.plot(dta.index, dta.values, color="#E74C3C")
ax.set_title("ARIMA(1,1,0) 序列：带明显趋势，均值和方差都不稳定")
save(fig, "三级_ARIMA_原序列")

# 6.2 一阶差分后再检验
diff1 = dta.diff().dropna()
adf_diff = adfuller(diff1)
print(f"\n一阶差分后 ADF 统计量 = {adf_diff[0]:.3f}，p = {adf_diff[1]:.4f}")
print("结论：差分后平稳，d = 1。" if adf_diff[1] < 0.05 else "结论：仍不平稳，可能需二阶差分。")

fig, ax = plt.subplots()
ax.plot(diff1.index, diff1.values, color="#2E5C8A")
ax.axhline(0, color="#4A4A4A", linestyle="--", linewidth=1)
ax.set_title("一阶差分后的序列：围绕 0 波动")
save(fig, "三级_ARIMA_一阶差分")

# 6.3 同样用网格搜索确认 p/q
best_aic, best_order = np.inf, None
for p, d, q in itertools.product(range(2), range(2), range(2)):
    try:
        m = ARIMA(dta, order=(p, d, q)).fit()
        if m.aic < best_aic:
            best_aic, best_order = m.aic, (p, d, q)
    except Exception:
        continue
print(f"\nAIC 最优阶数：ARIMA{best_order}，AIC = {best_aic:.2f}")

arima_model = ARIMA(dta, order=best_order).fit()
print(f"模型摘要：\n{arima_model.summary().tables[1]}")

# 6.4 预测并画出置信区间
fc = arima_model.get_forecast(steps=10)
frame = fc.summary_frame()
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(dta.index[-60:], dta.values[-60:], label="历史值", color="#4A90E2")
ax.plot(frame.index, frame["mean"], label="预测值", color="#E74C3C", marker="o", markersize=3)
ax.fill_between(frame.index, frame["mean_ci_lower"], frame["mean_ci_upper"],
                color="#E74C3C", alpha=0.15, label="95% 置信区间")
ax.set_title(f"ARIMA{best_order} 未来 10 期预测")
ax.legend()
save(fig, "三级_ARIMA_预测")

print("\n未来 10 期预测值：")
print(frame[["mean", "mean_ci_lower", "mean_ci_upper"]].round(2).to_string())

# ---------------------------------------------------------------- 7. 结论
title("7. 结论")
print("· AR/MA 用 ACF、PACF 的截尾/拖尾特征就能定阶；")
print("· ARMA 两者都拖尾，只能靠 AIC 网格搜索；")
print("· 带趋势的序列必须先做 ADF 检验 + 差分，否则模型会伪回归；")
print("· 残差应通过 DW（≈2）和正态性检验，否则模型还需要调整；")
print("· 输出图片见 images/ 目录。")
