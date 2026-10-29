# 数据说明

6 个代表案例所需的全部数据，均来自 CDA 二级 / 三级 / 金融数据分析三本教材的配套资料。

| 文件 | 大小 | 来源 | 字段说明 |
|------|------|------|----------|
| `LR_practice.xlsx` | 19 KB | CDA 二级 第8章 线性回归 | 76 条信用卡客户样本：avg_exp、Income、Age、edu_class 等 |
| `profile_bank.csv` | 2.4 MB | CDA 二级 第9章 k-means聚类 | 10 万客户 × 4 个渠道交易次数（TBM/ATM/POS/CSC） |
| `creditcard_exp.csv` | 7 KB | CDA 三级 2.1 | 100 条有因变量样本（avg_exp 月均支出） |
| `creditcard_exp_out_of_sample.csv` | 1.3 KB | CDA 三级 2.1 | 待打分的样本外客户 |
| `ts_simu200.csv` | 38 KB | CDA 三级 4.1 | 200 期模拟序列，列名即数据生成过程（AR1_a、MA1_a、ARIMA_110…） |
| `data_clust.csv.gz` | 3.2 MB | 金融 第3章 | 17 个客户属性字段；原始 9.7 MB，压缩存放 |
| `creditdata_small.csv.gz` | 4.1 MB | 金融 第5章 A卡 | 3 万条申请、120 个特征、TARGET 违约标识；原始 15.8 MB，压缩存放 |

## .gz 文件的读取

pandas 会根据扩展名自动解压，两种写法都行：

```python
pd.read_csv("data_clust.csv.gz")                          # 直接读
load_csv("data_clust.csv")                               # 走 common_data 的封装，自动找 .gz
```

`common_data.load_csv()` 的查找顺序是：先找同名 `.csv`，再找 `.csv.gz`，
所以本地如果放了未压缩的原文件，会优先用原文件。

## 换数据目录

```bash
# Windows
$env:CASE_DATA_DIR = "D:\我的数据"
# macOS / Linux
export CASE_DATA_DIR=/path/to/data
```

## 版权

数据来自教材配套资料，版权归各教材作者与出版社所有，仅用于课程学习与教学演示。
