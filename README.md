# TSV-RLCK

[English](#english) | [中文](#中文)

---

## English

Analytical TSV RLCK extraction toolkit for fast research iteration.

### Features

- Single-point TSV RLCK extraction
- TSV array extraction with coupling matrices and topology presets (`grid` / `gsg` / `diff_pair`)
- Frequency sweep (`lin` / `log`) output with `model_level` (`simple` / `advanced`)
- Monte Carlo perturbation analysis with summary statistics
- Benchmark comparison report (single-case and batch)
- S-parameter (`.s2p`) export for two-port frequency-domain analysis, with topology metadata
- SPICE subcircuit export (single operating point)
- Reproducible notebook demo

### Project Structure

- `src/tsv_rlck/` - core models, formulas, extractor, CLI, SPICE export
- `tests/` - unit tests
- `benchmarks/example_reference.json` - benchmark input/reference example
- `benchmarks/batch_reference.json` - batch benchmark cases example
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

#### 4) Benchmark report (single-case)

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-file benchmarks/example_reference.json
```

#### 5) Benchmark batch report

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-batch-file benchmarks/batch_reference.json \
  --benchmark-report-out benchmark_report.json
```

#### 6) S-parameter export (`.s2p`)

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --model-level advanced \
  --sweep-start-hz 1e6 \
  --sweep-stop-hz 1e10 \
  --sweep-points 21 \
  --sweep-spacing log \
  --sparams-out out.s2p \
  --z0 50
```

#### 7) Export JSON/SPICE

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --json-out out.json \
  --spice-out out.sp
```

#### 8) Array topology preset example

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --rows 1 \
  --cols 3 \
  --topology gsg \
  --json-out array_gsg.json
```


```bash
python -m unittest discover -s tests -v
```

### Notes

- In `simple` mode, wideband behavior mainly captures frequency-dependent `R`; `L/C/G` are approximately static.
- In `advanced` mode, `L/C/G` use lightweight frequency-dependent approximations.
- SPICE export is currently single operating point.

---

## 中文

用于快速研究迭代的 TSV RLCK 解析提取工具。

### 功能

- 单工作点 TSV RLCK 提取
- TSV 阵列提取与耦合矩阵，支持拓扑预设（`grid` / `gsg` / `diff_pair`）
- 频率扫描输出（`lin` / `log`），支持 `model_level`（`simple` / `advanced`）
- Monte Carlo 工艺/温度扰动分析与统计汇总
- 基准对比误差报告（单case与批量case）
- S参数（`.s2p`）导出，用于频域对比，并包含拓扑元数据
- SPICE 子电路导出（单工作点）
- 可复现实验 Notebook 示例

### 项目结构

- `src/tsv_rlck/`：核心模型、公式、提取、CLI、SPICE 导出
- `tests/`：单元测试
- `benchmarks/example_reference.json`：基准输入与参考值示例
- `benchmarks/batch_reference.json`：批量基准案例示例
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

#### 4）基准误差报告（单case）

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-file benchmarks/example_reference.json
```

#### 5）批量基准误差报告

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --benchmark-batch-file benchmarks/batch_reference.json \
  --benchmark-report-out benchmark_report.json
```

#### 6）S 参数导出（`.s2p`）

```bash
python -m tsv_rlck \
  --diameter-um 10 \
  --height-um 60 \
  --oxide-thickness-nm 200 \
  --frequency-hz 1e9 \
  --model-level advanced \
  --sweep-start-hz 1e6 \
  --sweep-stop-hz 1e10 \
  --sweep-points 21 \
  --sweep-spacing log \
  --sparams-out out.s2p \
  --z0 50
```

#### 7）导出 JSON/SPICE

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

- `simple` 模式下，宽带行为优先覆盖 `R` 的频率依赖；`L/C/G` 近似静态。
- `advanced` 模式下，`L/C/G` 提供随频率变化的近似模型。
- SPICE 导出目前为单工作点模型。
