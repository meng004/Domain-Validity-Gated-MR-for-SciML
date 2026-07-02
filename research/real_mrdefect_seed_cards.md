# Real-MRDefect-10 · 种子缺陷卡 + SMS-vs-MS 判别力设计

> 2026-07-01 · 结构化数据集：`data/realdefects/seed_cards.json`（唯一真相源，validator 守）
> 校验/功效工具：`code/realdefects/{schema,validator,power}.py`；测试：`code/tests/realdefects/`
> 状态（2026-07-01 更新）：**1 verified**（xarray #7766：受影响版 2023.4.0 隔离 venv 复现 + 当前 2024.11.0 活体确认已修）+ **4 reproducible**（numpy #30349 / scipy #21876 / pandas #59350 / networkx #8093，当前版本本地复现）+ **4 candidate**（CLOSED，需旧版本，issue 经 `gh` 核实）。脚本 `code/realdefects/repro/`。
> ⚠️ 与已拍板论文的被测对象（SciML 代理）不同源，见执行日志 §0.4，不入正文。

## 1. 种子卡汇总（9 张，跨 6 库 8 个 MR family，DL/tensor 占比 0）

| ID | 库 | issue | MR family | issue 状态（gh 核实）|
|---|---|---|---|---|
| RMD-NUMPY-0001 | numpy | [#20305](https://github.com/numpy/numpy/issues/20305) | dtype / 数值等价（einsum float16 全零）| CLOSED COMPLETED 2021-11-12 |
| RMD-NUMPY-0002 | numpy | [#30349](https://github.com/numpy/numpy/issues/30349) | 优化等价（optimize flag 不变性）| OPEN · ✅reproducible(numpy 2.5.0) |
| RMD-SCIPY-0001 | scipy | [#21876](https://github.com/scipy/scipy/issues/21876) | mode 一致性/广播不变（valid/full 保 B、same 塌 1）| OPEN · ✅reproducible(scipy 1.18.0) |
| RMD-SCIPY-0002 | scipy | [#15927](https://github.com/scipy/scipy/issues/15927) | 方法等价（convolve fft vs direct）| CLOSED COMPLETED 2022-04-26 |
| RMD-PANDAS-0001 | pandas | [#59350](https://github.com/pandas-dev/pandas/issues/59350) | 行序不变（groupby+resample）| OPEN · ✅reproducible(pandas 2.2.3) |
| RMD-PANDAS-0002 | pandas | [#33732](https://github.com/pandas-dev/pandas/issues/33732) | transform 行对齐不变 | CLOSED COMPLETED 2020-04-24 |
| RMD-SKLEARN-0001 | scikit-learn | [#15438](https://github.com/scikit-learn/scikit-learn/issues/15438) | 稀疏-稠密等价（Ridge sample_weight）| CLOSED COMPLETED 2022-03-22 |
| RMD-NETWORKX-0001 | networkx | [#8093](https://github.com/networkx/networkx/issues/8093) | 图重标号：copy-flag 不变（node-merge）| CLOSED 2026-06-29 · ✅reproducible(nx 3.4.2) |
| RMD-XARRAY-0001 | xarray | [#7766](https://github.com/pydata/xarray/issues/7766) | 坐标/标签对应（coordinate-alignment）| CLOSED 2023-04-20 · ✅✅verified(2023.4.0→2024.11.0) |

MR family 覆盖：数值等价、dtype、优化/编译-JIT 等价、跨方法/方法等价、行序/置换不变、transform 对齐、稀疏-稠密等价、图重标号、坐标对齐。**缺**：图像变换不变性（OpenCV，DL/tensor reserve，暂未挖，保占比 0）。

## 2. SMS-vs-MS 判别力设计

### 2.1 定义（试点内锁定）

- **MS（传统变异分数）**：MR 测试套件杀死**合成语法 mutant**（AST 级算子/常量变异）的比例。
- **SMS（语义变异分数）**：MR 测试套件检出**真实语义缺陷**（上表 Real-MRDefect 卡）的比例。
- **判别力问题**：给若干强弱不同的 MR 测试套件，SMS 的**套件质量排序**是否比 MS 更接近「真实 MR-defect 检出能力」的排序？

### 2.2 suite-level 观测指标（可判定）

对每张缺陷卡的目标库，构造 K 个强弱不同的 MR 测试套件（如：仅测排序好的输入 vs 也测置换输入；仅测 dense vs 也测 sparse）：

1. **真实检出向量** `d_s`：套件 s 检出了哪些 Real-MRDefect 卡（金标准）。
2. **SMS(s)** = |检出真实缺陷| / |卡总数|。
3. **MS(s)** = 合成语法 mutant 杀伤率。
4. **判别力对比**：`corr(rank(SMS), rank(真实检出))` vs `corr(rank(MS), rank(真实检出))`；SMS 更高 → 支持假设。
5. **误导诊断**：找 MS 高但真实检出低的套件（语法 mutant 噪声高分）——这是 MS 被「等价/trivial mutant」误导的直接证据。

### 2.3 每假设绑定具体缺陷（不空谈）

| 假设 | 绑定缺陷/family | SMS 为何更判别 | MS 为何盲 |
|---|---|---|---|
| H-dtype | RMD-NUMPY-0001 | dtype-不变性 MR 直接抓 float16 全零 | 语法 mutant 不建模 dtype 累加缓冲回归；不测 float16 的套件仍高 MS |
| H-opt | RMD-NUMPY-0002 | optimize on/off 差分 MR 抓路径分歧 | mutant 在单一路径内，无法表达跨配置等价 |
| H-mode | RMD-SCIPY-0001 | 跨 mode 广播不变 MR（valid/full/same 保 batch 维）| mutant 不建模「batch 维跨 mode 保持」；单 mode 测试 MS 虚高 |
| H-method | RMD-SCIPY-0002 | fft-vs-direct 方法等价 MR | mutant 不建模数值路径分歧；单路径测试 MS 虚高 |
| H-perm | RMD-PANDAS-0001/0002 | 行置换/对齐不变 MR | mutant 不建模 index-ordering 耦合；测预排序帧的套件 MS 虚高 |
| H-sparse | RMD-SKLEARN-0001 | 稀疏-稠密等价 MR | mutant 不建模表示特定 sample_weight 路径 |
| H-relabel | RMD-NETWORKX-0001 | 重标号 copy-flag 不变 MR（node-merge 下 copy=True/False 须一致）| mutant 不建模「copy 标志不改语义」 |
| H-align | RMD-XARRAY-0001 | 标签对应 MR | mutant 不建模「标签须匹配 bin」 |

### 2.4 功效 / go-no-go（`code/realdefects/power.py`，诚实）

统计设计 = 对**判别缺陷**（SMS-偏好 vs MS-偏好，恰一方成立）做 McNemar 精确符号检验（单侧 α=0.05）。

- 用当前 9 张种子、假设全部 discordant 且 p_favor=0.9（乐观上界）：**精确符号检验功效 ≈ 0.77 < 0.80**，`decision = design-calibration-only`，`confirmatory = False`。
- 达 80% 功效需 ~8 张 discordant 缺陷（离散性使 n=8 优于 n=9）。
- discordant 比例 Wilson 95% CI（9/9）= [0.70, 1.00]。
- **结论（不可放松）**：Real-MRDefect-10 种子**只能**用于 go/no-go 判定与实验设计校准，**不能**作为「SMS 优于 MS」的最终统计结论。要 confirmatory 需扩到数十张、且真正复现（reproducible/verified）而非 candidate。

### 2.6 最小 SMS-vs-MS 判别力 PoC（存在性证明，n=1，非统计）

工具 `code/realdefects/sms_vs_ms_poc.py`（`test_sms_vs_ms_poc.py` 守，7 测试）。**锚定** reproducible 缺陷 RMD-PANDAS-0001（#59350，index-order 不变性违例）；用忠实重建该错位行为的参照 reducer 使 mutation 分析可行（真实缺陷 + 参照 SUT 方法，cf. Just et al. FSE 2014）。

**SUT**：对 (idx, bucket, value) 记录按 bucket 求和。`correct()` 严格按 bucket 分组（index-order 无关）；`reference()` 复现 #59350——值按行索引序取、标签按 bucket 序放，故乱序索引下**错位**（permute）各 bucket 和但**保总和**。

**两个 MR 套件 + 10 个合成语法 mutant** 实测（数字由 harness 跑出，非硬编码）：

| 套件 | MS（mutant 杀伤率）| 检出真实缺陷？|
|---|---|---|
| 守恒 MR（Σ输出=Σ输入）| **0.90**（杀 9/10，仅漏等价 mutant `abs`）| **否**（错位保总和，盲）|
| index-order 不变性 MR | **0.20**（只杀 2 个 order-dependent mutant）| **是** |

**结论**：MS 排序把守恒套件排在**上**，真实缺陷却**只**被低-MS 的 index-order 套件检出——**MS 排序与真实缺陷检出相矛盾**。这**存在性地**说明 SMS（真实缺陷检出）与 MS 判别 MR-套件质量的方式不同；**但 n=1，非统计证明**「SMS 优于 MS」。诚实要点：等价 mutant（`abs`）两套件皆不杀，正是 MS 虚高的经典来源之一。

### 2.7 从 candidate 到 reproducible/verified 的进度与下一步

- **✅ 已完成（2026-07-01）**：
  - **4 reproducible**：numpy #30349 / scipy #21876 / pandas #59350 / networkx #8093 在当前版本本地复现（脚本 `code/realdefects/repro/*.py`，`test_repro_open_defects.py` 守）。
  - **1 verified**：xarray #7766 走通全链——受影响版 2023.4.0（隔离 venv numpy1.26.4/pandas2.1.4）复现「标签错乱」（four=506 应 1、nine=1 应 506）+ 当前 2024.11.0 活体确认已修（0 mismatch，`verify_registry` + `test_verified_defects` 守）。
  - **两次实测自我更正**（诚实性）：scipy #21876 不是跨方法等价而是跨 mode 广播不变；networkx #8093 不是双射同构（干净双射无 bug）而是 node-merge 下 copy-flag 不一致。
- **下一步**：
  1. 6 张 candidate（含 4 张 CLOSED）：pin 受影响旧版本（`pip install <lib>==<affected>` 于隔离 venv）写复现脚本 → reproducible。
  2. CLOSED 卡在修复版验证关系恢复 + 补 fixed 版本/commit → **verified**。
  3. 构造 K 个强弱 MR 套件 + 合成 mutant 集，实测 SMS/MS 排序相关性（真正回答核心问题）。

## 3. 与已拍板计划的关系（实事求是）

- 本语料是**通用科学库函数级**缺陷，与现稿 SciML-代理被测对象不同（执行日志 §0.4 分叉）。
- 对已拍板 `paper/66` Phase 2「用真实、可辩护缺陷替换自造平凡 mutant」是**直接有效的可行性证据**：证明真实 MR-可检缺陷可低成本、可追溯地采集。
- 是否把 SMS-vs-MS 提升为论文主线 / 与 A+B+C 融合 = **头号 open question，待用户拍板**。
