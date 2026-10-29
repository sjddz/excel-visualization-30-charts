# 数据说明

本目录按《CDA 一级认证教材：商业数据分析》的章节结构镜像存放，
只保留**章节脚本实际读取**的数据文件（课件、PDF、`.pbix` 等非数据文件未纳入）。

```
data/
├── 第1章 数据分析思维/
│   ├── sale.csv
│   ├── 关系模型演示-不建议用poweBI操作关系型数据模型/   accounts/clients/disp/card/loans/district/order/trans
│   └── 维度模型演示/商场销售数据表.xlsx
├── 第2章 数据分析方法/1、分析的基础范式/data-有答案/
│   ├── 1-1波士顿矩阵-参考.xlsx
│   ├── 1-2RFM模型-参考.xlsx
│   ├── 1-3用户忠诚度模型-参考.xlsx
│   ├── 1-4同期群分析-参考.xlsx
│   ├── 2-1漏斗图-参考.xlsx
│   └── 3-1相关分析-参考.xlsx
├── 第3章 商业数据分析框架/
│   ├── 案例1：收入趋势分析/案例1：收入趋势分析原始数据.xlsx
│   ├── 案例2：财务费用分析/案例2：财务费用分析-原始数据.xlsx
│   └── 案例3：电商平台的精准营销/案例3：电商平台的精准营销-原始数据.xlsx
├── 第5章 业务数据分析/
│   ├── 第5章  PowerBI业务看板案例-银行案例/银行案例数据 - 学员用.xlsx
│   └── 第5章 WPS归因分析案例-银行案例/归因分析数据.xlsx
├── 第9章 用户标签体系与用户画像专题/data/    accounts/clients/disp/card/loans/district/order/trans
└── 第10章 使用效应分解方法做预报/
    ├── AirPassengers.csv
    └── 信用卡消费额_去除节日.xlsx
```

## 两个要点

**1. 第 8 章没有单独数据目录**
`第8章_SQL基础.py` 演示的是 SQL 语法与 pandas 的对照，
用的就是第 1 章那套银行关系模型数据（`data/第1章 数据分析思维/关系模型演示-.../`）。

**2. 交易流水用 .gz 压缩**
`trans.csv` 原始文件约 57 MB，两张副本会让仓库膨胀到 130 MB。
压缩后各约 16 MB。`common.py` 的 `read_csv()` 会先找 `trans.csv`，
找不到时自动读取 `trans.csv.gz`，脚本代码完全不用改：

```python
def resolve(path):
    if os.path.exists(path):        return path
    if os.path.exists(path + ".gz"): return path + ".gz"
    raise FileNotFoundError(...)
```

## 换数据目录

```bash
# Windows
$env:CDA_DATA_ROOT = "D:\教材\CDA一级数据"
# macOS / Linux
export CDA_DATA_ROOT=/path/to/cda_data
```

## 版权

数据来自 CDA 认证教材配套资料，版权归教材编写方所有，仅用于课程学习。
如教材方要求，可整体删除本目录，脚本会提示缺少哪个文件。
