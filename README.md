# TSV-RLCK / TSV-RLCK（中英双语）

[English](#english) | [中文](#中文)

---

## English

Analytical TSV RLCK extraction toolkit for fast research iteration.

### Features

- Single-point TSV RLCK extraction
- TSV array extraction with coupling matrices
- Frequency sweep (`lin` / `log`) output
- Monte Carlo perturbation analysis with summary statistics
- Benchmark comparison report (absolute / relative error)
- SPICE subcircuit export (single operating point)
- Reproducible notebook demo

### Project Structure

- `src/tsv_rlck/` - core models, formulas, extractor, CLI, SPICE export
- `tests/` - unit tests
- `benchmarks/example_reference.json` - benchmark input/reference example
- `notebooks/tsv_iteration2_demo.ipynb` - iteration-2 demo notebook

### Requirements

- Python >= 3.10

### Install

```bash
cd "tsv_rlck"
python -m pip install -e .
```

### Quick Start

#### 1) Single-point extraction

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9
```

#### 2) Frequency sweep

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --sweep-start-hz 1e6 \
  --sweep-stop-hz 1e10 \
  --sweep-points 21 \
  --sweep-spacing log
```

#### 3) Monte Carlo

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --mc-samples 200 \
  --seed 42 \
  --sigma-diameter-um 0.1 \
  --sigma-oxide-thickness-nm 2.0 \
  --sigma-metal-resistivity-ohm-m 1e-10 \
  --sigma-substrate-resistivity-ohm-cm 0.2 \
  --sigma-temperature-c 2.0
```

#### 4) Benchmark report

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-file benchmarks/example_reference.json
```

#### 5) Export JSON/SPICE

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --json-out out.json \
  --spice-out out.sp
```

### Tests

```bash
python -m unittest discover -s tests -v
```

### Notes

- Current wideband behavior focuses on frequency-dependent `R`; `L/C` are currently treated as static per operating condition.
- SPICE export is currently single operating point.

---

## 中文

用于快速研究迭代的 TSV RLCK 解析提取工具。

### 功能

- 单工作点 TSV RLCK 提取
- TSV 阵列提取与耦合矩阵
- 频率扫描输出（`lin` / `log`）
- Monte Carlo 工艺/温度扰动分析与统计汇总
- 基准对比误差报告（绝对误差 / 相对误差）
- SPICE 子电路导出（单工作点）
- 可复现实验 Notebook 示例

### 项目结构

- `src/tsv_rlck/`：核心模型、公式、提取、CLI、SPICE 导出
- `tests/`：单元测试
- `benchmarks/example_reference.json`：基准输入与参考值示例
- `notebooks/tsv_iteration2_demo.ipynb`：第二轮迭代演示 Notebook

### 环境要求

- Python >= 3.10

### 安装

```bash
cd "tsv_rlck"
python -m pip install -e .
```

### 快速开始

#### 1）单点提取

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9
```

#### 2）频率扫描

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --sweep-start-hz 1e6 \
  --sweep-stop-hz 1e10 \
  --sweep-points 21 \
  --sweep-spacing log
```

#### 3）Monte Carlo

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --mc-samples 200 \
  --seed 42 \
  --sigma-diameter-um 0.1 \
  --sigma-oxide-thickness-nm 2.0 \
  --sigma-metal-resistivity-ohm-m 1e-10 \
  --sigma-substrate-resistivity-ohm-cm 0.2 \
  --sigma-temperature-c 2.0
```

#### 4）基准误差报告

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-file benchmarks/example_reference.json
```

#### 5）导出 JSON/SPICE

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --json-out out.json \
  --spice-out out.sp
```

### 测试

```bash
python -m unittest discover -s tests -v
```

### 说明

- 当前宽带行为优先覆盖 `R` 的频率依赖；`L/C` 暂按工作条件静态处理。
- SPICE 导出目前为单工作点模型。
