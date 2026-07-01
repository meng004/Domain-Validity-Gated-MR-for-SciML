# 66 · Path A 执行程序：纵向冲顶 TOSEM/TSE（用户拍板 2026-06-30）

> 日期：2026-06-30 · 决策：用户在 `paper/65` 三选一中选 **A = 纵向冲顶 SE 天花板 → TOSEM（首选）/ TSE（等价）**。
> 前置证据：`paper/62/63/64`（四刊评估、实验难度、首方法接收 playbook）+ `paper/65`（天花板决策）。
> 本文档：把 A 落成带 gate 的执行程序，并**用现有资产底数重新校准风险**（关键：风险显著低于 `paper/63` 的先验估计）。

---

## 一、资产底数实检（2026-06-30）—— 重估 path A 风险

`paper/63/64` 把 path A 的**核心下行风险**定为「门控可能在真实代理上**测不出**显著优势
（measured harm/fix 跑不出来）」。**实检现有提交数据，这个信号已经存在**，核心风险被大幅前置退掉：

### 现有 measured-advantage 证据（committed，非新跑）

| 证据 | 来源 run / claim | 数值 |
|---|---|---|
| **MGN 上 MR 对 accuracy 近似严格占优** | `detection-vs-accuracy` / **C38**（10 故障）| MR 抓到 **2/10** 是 accuracy 漏的；accuracy 抓到 **0/10** 是 MR 漏的 |
| **PointMLP 上 MR-only 盲区 + 门控误警修复** | `pointmlp-three-arm-complementarity` / **C42/C43**（20 故障，4 预声明类）| gated-MR **13/20** vs accuracy **6/20**；**9 个 MR-only** 故障 accuracy 结构盲；**门控价值=采信检测器 0% 基线误警，6 个被拒模板 100% 误警** |
| 自然 baseline 已全建 | `generic-mr-baseline` / `expert-mr-baseline` / `llm-mr-baseline` / `rollout-accuracy-baseline` | generic/expert 均 `novel_retained=[]`（门控外无新采信不变量），LLM 对照已评分 |
| 统一故障目录 + 统计 | `phase3-unified-fault-catalog`（**60 条 / 1032 trials**）| MGN 10 executed mutants + 2 adversarial + PINN/FNO 各 24 闭式探针 |
| 跨架构 / 跨程序广度 | `cross-architecture-duality` / `cross-program-coverage` / `multicheckpoint` S0–S5 | 已有 |

**结论**：「门控 0% 误警 vs 被拒模板 100% 误警」+「9 个 accuracy 盲的 MR-only 故障」**就是**
paper/64 §四要的 measured harm + measured fix，**已经在数据里**。path A 不是「赌能不能测出优势」，
而是「把已存在的优势信号做到**可辩护 + 可泛化 + ledger 合法授权**」。**这比 `paper/63` 的
『4–6 月 HIGH、可能跑不出』风险画像好一档。**

### 但现有信号有三个封顶，构成真正的 path-A 工作（非修辞）

1. **ledger 封顶（诚信硬 gate）**：C42 现 `wording_forbidden` 明禁 superiority；「complementarity
   NOT superiority」是既定边界。要把上述信号升为 TOSEM 头条必要性结果，**必须新增 claim ID +
   配套证据 + 过 validator/guards**，不能改写 C42 措辞蒙混（违反本仓「prose ≤ ledger」不变量、§4/§6.4）。
2. **故障基准封顶（最稀缺，`paper/63` 阶段2）**：现有故障多为自造 mutant，「9 个 MR-only」易被审
   稿人斥「gross corruption，任何检测器都能抓 / 自造有利」。须建**有物理依据、经独立校验**的真实
   SciML-surrogate 故障分类，让占优信号在其上幸存。
3. **多被测封顶**：「0% vs 100% 误警」目前主要在**单 PointMLP** + MGN 两点。TOSEM 要 ≥3–5 独立
   训练、跨架构×跨物理域，须证门控价值**跨 SUT 稳定**（airfoil 训到位 + 补 2–3 独立物理域真实代理）。

---

## 二、执行程序（de-risk 优先排序，带 gate）

> 原则：最贵最不确定的先证；每个 Phase 有明确「过 / 不过」判据；不过则触发 `paper/65` 的优雅降落（IST 重框定 / ICST）。

### Phase 0 — 优势信号盘点与可辩护性预检（1–2 周，最先，几乎全读现有数据）
- 把 C38 + C42/C43 + 统一目录的 measured-advantage 信号系统汇总成一张「gate-value 证据表」。
- **诚实预判**：现有「9 MR-only / 0%-vs-100% FP」有多少依赖自造故障？逐条标注「若换真实故障基准是否可能存活」。
- **过 gate 判据**：存在 ≥1 条 measured-advantage 信号，其成立**不本质依赖**故障的自造平凡性 → 继续 Phase 1；否则回 `paper/65` 降落评估。

### Phase 1 — 可辩护真实故障基准（`paper/63` 阶段2，最稀缺，1–1.5 月，HIGH）
- 弃/降权自造平凡 mutant；建有物理/离散化依据、经独立校验的真实 SciML-surrogate 故障分类（含采样框架 + 外部效度论证）。
- 复用资产：`phase3-unified-fault-catalog`（60 条框架）+ 姊妹库 mutant_catalog（fault_class 三分）作**起点**，但须补真实性论证。
- **过 gate 判据**：故障基准能经受「非自造、非平凡、有代表性」审稿三问 → 继续。

### Phase 2 — 多被测真实代理（`paper/63` 阶段1，1–2 月 GPU，中）
- airfoil 训到位（现 rel L2 0.92 半废）+ 补 2–3 独立物理域真实代理，凑跨架构×跨物理域 ≥3–5。
- **过 gate 判据**：门控价值（误警修复 + MR-only 盲区）在 ≥3 独立 SUT 上**方向一致** → 继续。

### Phase 3 — 全 baseline head-to-head + measured harm/fix 定稿（3–4 周，中）
- 自然 baseline 全跑（generic-MR / accuracy-residual / UQ-conformal / Kanewala 式），量化各自结构盲区。
- 主结果：**「不做 admissibility 门控时标准做法在真实代理上产生 X% 误警/误归因；门控修掉」**，带 Wilson CI。
- **过 gate 判据**：measured advantage 在真实基准 + 多 SUT 上统计站得住 → 继续；**跑不出显著优势 → 降落**（`paper/65` 尾注，诚实下行）。

### Phase 4 — 诚信 ledger 升级（贯穿 Phase 1–3，硬 gate）
- 为 measured-advantage 新增 claim ID（如 `C-nec-1 门控误警修复率` / `C-nec-2 MR-only 盲区`），
  `wording_allowed` 精确到证据边界；C42「complementarity」保留为历史/更窄陈述，**不删不改写蒙混**。
- 同步 guards（`tests/test_*`）+ 两 validator rc=0。**过 gate 判据**：新 claim 全部 licensed by 真实运行，prose ≤ ledger。

### Phase 5 — TOSEM 框架化 + 投稿包（3–4 周，中）
- soundness 形式化（admissibility 定义 + 四条件 + gate soundness 论证；「容差须压过算子误差地板」形式化）→ TOSEM 偏爱形状。
- 必要性叙事重写（`paper/64` §五：complementarity → "catch what others are structurally blind to"）。
- 建 `venues/TOSEM.md`（acmart 双盲、CCF-A、CAS 1区）；TSE 等价包（IEEEtran 单盲，零双盲化成本）作备选。
- **无 deadline**：TOSEM/TSE 滚动投；R&R 多轮吸收残余风险（`paper/65` 决策核心理由）。

**总工期**：约 4–6 月（与 `paper/63` 同量级），但**风险重心已从「优势能否测出」前移到「优势能否在真实基准 + 多 SUT 上存活」**——后者可控性更高。

---

## 三、边界铁律（承接本仓不变量）

- **prose ≤ ledger**：任何 superiority/necessity 头条**先落 claim + 真实运行 + guard**，再写正文。C42 禁 superiority 的现状**不得**靠改写绕过（§4/§6.4）。
- **实事求是**：measured advantage 若在真实基准上消失，**如实降落**，不 disguise（`paper/65` 尾注、§6.4）。
- **姊妹库只读**：`../最小完备MR子集/` 只读，可 import/read，写只落本仓。
- **SE 化框定**：标题/摘要/引言用 oracle / MT / admissibility / 故障归因语汇，弱化 CFD 物理叙事（IST 桌拒同一坑，`paper/64` §三）。

---

## 四、立即下一步（Phase 0 第 0 动作）

盘点并汇总现有 measured-advantage 证据成「gate-value 证据表」+ 逐条标注对自造故障的依赖度——
**几乎全读现有 committed 数据，CPU、无凭据、无新训练**，是最便宜的 de-risk 起点。待用户认可即可启动 Phase 0。
