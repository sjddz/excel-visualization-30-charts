# CDA 一级教材《商业数据分析》· Python 迁移

把教材中用 **Excel / Power BI / MySQL** 完成的 7 个章节案例，用 Python
（pandas + matplotlib + statsmodels）重新实现，共 **61 张图表**。

## 一、章节覆盖

| 章节 | 脚本 | 图表数 | 教材原型 | Python 实现 |
|------|------|:------:|----------|-------------|
| 第 1 章 数据分析思维 | `第1章_数据分析思维.py` | 8 | Excel 柱/饼/散点；Power BI 关系模型与维度模型 | matplotlib 图表 + `merge` 多表连接 + 星型模型演示 |
| 第 2 章 数据分析方法 | `第2章_数据分析方法.py` | 9 | Excel 透视表做波士顿矩阵/RFM/同期群/漏斗/相关 | `groupby`+`qcut` 打分、`pivot_table`、`scatter`、`stats` |
| 第 3 章 商业数据分析框架 | `第3章_商业数据分析框架.py` | 11 | Excel 财务分析图表、热力图、排行图 | 堆叠柱、热力图、双向条形、帕累托 |
| 第 5 章 业务数据分析 | `第5章_业务数据分析.py` | 9 | Power BI 银行理财产品销售看板 + WPS 归因分析 | 多子图看板 + 贡献度归因 |
| 第 8 章 SQL 语言基础 | `第8章_SQL基础.py` | 7 | MySQL 语法（WHERE/GROUP BY/JOIN/子查询/UNION） | 逐条对照 pandas 写法并可视化结果 |
| 第 9 章 用户画像 | `第9章_用户画像.py` | 8 | SQL 打标签 + Power BI 画像看板 | pandas 计算 R/F/M、雷达图、交叉矩阵 |
| 第 10 章 效应分解 | `第10章_效应分解.py` | 9 | Excel 预测工作表 / 移动平均 | `seasonal_decompose` 乘法与加法模型 + 趋势外推 |
| **合计** | **7 个脚本** | **61** | | |

## 二、未纳入的章节及原因

| 章节 | 原因 |
|------|------|
| 第 4、6 章 | 教材配套资料包中未提供这两章的案例文件 |
| 第 7 章 指标体系构建 | 配套资料是《指标体系设计模板.xlsx》与课件，属于**制度设计**，没有可执行的分析逻辑 |
| 第 11 章 数据治理 | 配套资料为 GB/T 36073、GB/T 42129 等**标准 PDF** |
| 第 12 章 数据模型与数据建模 | 配套资料为数据中台**白皮书 PDF** |
| 第 13 章 指标体系管理 | 配套资料为**数据标准编制模板**与行业标准 PDF |

这些章节考的是规范与方法论，用 Python 复现代码并不能体现其内容，故只做说明、不硬凑图表。

## 三、运行

```bash
pip install -r ../requirements.txt

python 第1章_数据分析思维.py
python 第2章_数据分析方法.py
python 第3章_商业数据分析框架.py
python 第5章_业务数据分析.py
python 第8章_SQL基础.py
python 第9章_用户画像.py
python 第10章_效应分解.py

python make_summary.py        # 生成 CDA一级教材_汇总.html
```

- 图片输出到 `charts/`（文件名形如 `ch01_01_市场销售额对比.png`）
- 每个脚本都会先打印数据预览和每一步的中间结果，便于核对教材结论

## 四、数据

`data/` 目录按教材章节原样镜像，只保留**脚本实际读取**的文件：

```
data/
├── 第1章 数据分析思维/            sale.csv、关系模型 6 张表、维度模型 xlsx
├── 第2章 数据分析方法/            波士顿矩阵/RFM/同期群/漏斗/相关分析 参考表
├── 第3章 商业数据分析框架/        3 个案例的原始数据
├── 第5章 业务数据分析/            银行看板数据、归因分析数据
├── 第9章 用户标签体系与用户画像专题/  accounts/clients/disp/card/loans/district/trans
└── 第10章 使用效应分解方法做预报/   AirPassengers.csv、信用卡消费额
```

> 第 8 章直接复用第 1 章的银行关系模型数据，因此 `data/` 中没有单独的 8 章目录。

**关于 `trans.csv.gz`**：银行交易流水原始 CSV 约 57 MB，GitHub 不适合放这么大的文本，
因此压缩为 `.gz`（16 MB）。`common.py` 的 `read_csv()` 在原文件不存在时会自动回退读 `.gz`，
脚本无需改动。

数据版权归教材作者与出版社所有，仅用于课程学习。

## 五、几个关键迁移点

| 教材做法 | 迁移实现 | 代码位置 |
|----------|----------|----------|
| Power BI 关系模型：card→disp→clients→district 链式关联 | `pd.merge(..., how="left")` 逐层拼接 | 第1章 |
| 维度模型（事实表 + 维度表） | 事实表与维度表 join 后按维聚合 | 第1章 |
| Excel 波士顿矩阵（四象限散点） | `scatter` + `axhline/axvline` + 象限标注 | 第2章 |
| Excel RFM：按分位数打分再组合 | `pd.qcut(..., labels=[1,2,3])` + 字符串拼接 | 第2章 |
| Excel 同期群（透视表 + 留存率） | `pivot_table` + 按首单月份对齐 | 第2章 |
| Excel 漏斗图 | `barh` + 居中 + 逐层收窄 | 第2章 |
| SQL `WHERE / GROUP BY / HAVING` | 布尔索引 / `groupby().agg()` / `query()` | 第8章 |
| SQL `JOIN` / 子查询 / `UNION` | `merge` / `isin` / `concat` | 第8章 |
| SQL `DATEDIFF` + `CASE WHEN` 打标签 | `pd.Timedelta` / `np.where` / `pd.cut` | 第9章 |
| Excel 预测工作表（移动平均、季节分解） | `statsmodels.tsa.seasonal_decompose` | 第10章 |
