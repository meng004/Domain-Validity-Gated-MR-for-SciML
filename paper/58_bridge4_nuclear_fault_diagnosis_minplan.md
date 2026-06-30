# 58 · 桥接(4) 强档最小可执行方案 —— 核 surrogate 故障诊断分诊（留 RESS 的高 ROI 路径）

> 日期：2026-06-30 · 依据 `paper/57` 多 LLM 面板（桥接(4)=High/High）+ 姊妹库实际资产勘察。
> 一句话定题：**把 validity gate 的 typed verdict 变成「ML 反应堆 surrogate 物理一致性违例的故障分诊」，对接核保护系统的误警率/漏检率（FAR/MDR），呼应 Lee et al. RESS 2020 系统在环先例。**
> 铁律：姊妹库 `../最小完备MR子集/` **只读**——可 import 其 scripts/、读其 committed data/，所有新写落本仓。

## 0. 为什么这条可行（已勘察的真实资产，非设想）

| 资产 | 位置（姊妹库，只读）| 桥接用途 |
|---|---|---|
| point-kinetics 求解器 + **PINN 代理** | `experiments/p5_pke/`、`runs/abd-witness-pke-pinn-*` | 反应堆瞬态的**学习型 surrogate**（无需重训）|
| PKE/HNN **mutant_catalog.csv** 带 `fault_class` | `runs/abd-witness-pke-pinn-fresh-runtime-*/mutant_catalog.csv` | **三分诊断 ground truth**：`physical_parameter_fault`(真异常 PK1_rho_sign) / `numerical_tolerance_fault`(数值伪影 PK2_beta_drop) / `equivalent_control`(无效) |
| OpenMC **C5G7 真实反应堆** + 5-MR kill matrix + scenario mutants | `scripts/exp/openmc_c5g7_killmatrix.py`、`runs/g2-openmc-c5g7-real*` | 第二核 SUT（临界 k-eff），守恒 MR=中子平衡 |
| 已导入的 OpenMC kill_matrix（只读副本）| 本仓 `research_assets/external/minimum-mr-subset-killmatrices/r1-openmc/` | 导入设施已存在 |
| 跨程序执行 runner | 本仓 `tools/run_cross_program_coverage.py` | 复用为分诊 runner |

**关键**：`fault_class` 标签已把「真物理故障 vs 数值容差故障 vs 无效」分好——这恰是本文 typed verdict（surrogate fault / numerical artifact / inadmissible）的**外部金标准**。本文现在只读引用它们并写「asserts no per-program reliability」；桥接=**新执行** gate+verdict 做分诊 + 算 FAR/MDR。

## 1. RESS 重定位（题/摘要/scope）

- 新题（示例）：*Validity-Gated Fault Diagnosis for Learned Reactor-Physics Surrogates: Separating Physical Anomalies from Numerical Artifacts for Protection-System False-Alarm Control*。
- 摘要首段直接出现 **fault detection and diagnostic triage** + **false-alarm / missed-detection rate** + **reactor protection**，不再只说 auditable verification assets。
- scope 对接句：核安全关键 surrogate 的自动故障检测与诊断（RESS 明列主题）+ 系统在环（RPS trip 决策）。

## 2. 实验设计（新执行，落本仓）

**SUT-A（主）**：point-kinetics PINN 反应堆瞬态 surrogate（只读 import 代理权重/数据）。RPS 相关决策 = 功率超安全限值触发 trip（用 `solve_pke` 的 power(t) 极值定义 trip 阈值）。

**SUT-B（佐证）**：OpenMC C5G7 临界 surrogate；守恒 MR=中子平衡(nu-fission/k vs absorption)。

**故障集（只读 import mutant_catalog，按 `fault_class` 分三类）**：
- 真物理异常（应触发 RPS / 真故障）：`physical_parameter_fault`（如 PK1_rho_sign 反应性符号、C5G7 截面扰动）。
- 数值伪影（**不应**触发 RPS=假警源）：`numerical_tolerance_fault`（如 PK2_beta_drop、stiff-ODE 步长失稳伪振荡、tally 方差）。
- 无效对照：`equivalent_control`（HN5_equiv，gate 应判 inadmissible/不告警）。

**分诊流程（本文已有 gate，新执行）**：对每个 mutant，跑 4 条件 admissibility gate + typed verdict →
输出 `{trip-fault / numerical-artifact / inadmissible}`，与 `fault_class` 金标准对照。

**核心可靠性量（新计算，= RESS 要的输出）**：
- **FAR（误警率）** = P(gate 判 trip-fault | 真类=numerical_tolerance_fault ∪ equivalent_control)。
- **MDR（漏检率）** = P(gate 漏判 | 真类=physical_parameter_fault)。
- 两者带 Wilson 95% CI；按 SUT 报。

**基线对照（坐实 gate 的价值）**：accuracy-only 监控器（rollout 误差阈值）vs validity-gated。
预期机制（待实测，不预设结果）：**numerical_tolerance_fault 会让 accuracy 监控器误触发 trip，而 gate 的 numerical-decidability 地板把它正确归为数值伪影 → FAR 下降**。这就是「validity gating *changes* a reliability outcome」的系统在环实证。

## 3. 哪些只读复用 / 哪些本仓新建

| 项 | 来源 | 工作量 |
|---|---|---|
| PKE PINN 代理 + 数据 + mutant 标签 | 姊妹库只读 import | 0（已存在）|
| OpenMC C5G7 kill matrix + scenario mutants | 姊妹库只读（部分已导入本仓）| 低（补导入 PROVENANCE）|
| admissibility gate + typed verdict 代码 | 本仓已有 | 0 |
| **分诊 runner**（gate→{trip/artifact/inadmissible} vs fault_class）| **本仓新建**（改 `run_cross_program_coverage.py`）| 中 |
| **FAR/MDR + RPS trip 决策层 + Wilson CI + 基线对照** | **本仓新建** | 中 |
| claim-ledger 新增 PC/C 条目（FAR/MDR 量、gate-value）| 本仓新建 | 低 |
| 正文重写为 fault-diagnosis 叙事、MT/LLM 下沉附录 | 本仓 | 中（prose）|

**净新增执行**：分诊 runner + FAR/MDR 计算 + 基线对照 + 正文重写。**无新的重型训练**（PKE PINN 已存在；OpenMC mutants 已存在，至多 CPU 重跑 draws，姊妹库有 `Dockerfile.openmc`）。

## 4. 验收 / 成功判据

- gate-as-triage 对 `fault_class` 金标准产出 confusion matrix（真物理 / 数值 / 无效 三类）。
- FAR、MDR 带 Wilson CI，按 SUT-A/B 报。
- **gate-value 实证**：validity-gated 的 FAR 显著低于 accuracy-only 基线（若成立=核心 RESS 卖点；若不成立=诚实报告，gate 在此无 FAR 优势，回退 SE）。
- 守边界：仍标注单/双核 SUT、mutant 自造、FAR/MDR 是受控注入下的量非现场缺陷率。

## 5. 工作量 + 风险 + 诚实边界

- **工作量：中（周级，非月级）**。重资产（代理、故障目录、导入设施、gate 代码）全部就绪；新建=分诊 runner + 指标 + 基线 + 重写。
- **风险 0（先验）**：mutant 数可能偏少（PK1/PK2/HN1-5…）→ FAR/MDR 统计功效不足。**第 0 步必做**：清点 PKE+C5G7 各 fault_class 的 mutant 计数；不足则用 OpenMC scenario-mutation catalog 扩样（只读已有更大目录）。
- **风险（结构）**：promote 只读资产为一等可靠性 claim，须真**新执行** gate+verdict+FAR/MDR（不是再读姊妹库 kill matrix），否则又落回「read-only, asserts no reliability」。
- **诚实边界**：这是受控故障注入下的 surrogate 诊断分诊 + FAR/MDR；不声称现场反应堆可靠性、不声称击败 PRA。但**有了一个真实可靠性量（FAR/MDR）+ 系统在环决策（RPS trip）+ gate 改变该量的对照**——这正是 RESS 谱要求、且现稿完全缺失的东西。

## 6. 结论

桥接(4)强档**可行且工作量中等**：核资产已就绪，新增=把本文 gate 在反应堆 surrogate 上**新执行为故障分诊** + 算 FAR/MDR + 基线对照 + 重写。这把现稿从「自陈不主张任何可靠性量的 SE 测试方法文」转成「核 surrogate 故障诊断 + 保护系统误警控制」——RESS scope 正中、有系统在环、有可靠性量。**若用户认可此工作量 → 留 RESS 走此路；若不愿做核执行实验 → 改投 SE(TSE/TOSEM)。**
