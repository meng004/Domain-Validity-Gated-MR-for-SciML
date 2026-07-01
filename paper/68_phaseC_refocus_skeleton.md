# 68 · Phase C 交付物：重框定骨架（TOSEM 稳投）

> 日期：2026-07-01 · 决策链：`paper/65`（天花板=TOSEM）→ `paper/67`（deep-research 裁定 + A+B+C 理论优先）→ 本文（Phase C）。
> 目标：thesis 收敛到「数值可判定性可采性判据」单一贡献，脊柱 = floor gate + soundness 定理，其余降为支撑。
> 定位：**这是框架，不是终稿**。定理本体由 **Phase B** 填（下方 `[Phase B]` 占位）；正文改写由 **Phase S** 执行。
> 过 gate 判据（`paper/67` §五）：核心问题一句话可述 ✓、novelty delta 一句话锁定 ✓（见 §0）。
> 现稿行号引用基于 `submissions/RESS/main.tex`（2026-07-01 读）。

---

## §0 两句锁定（gate 判据）

**核心问题（importance，一句话）**
> 蜕变测试给 ML 代理一个 oracle-free 的通过/失败信号，但**没有任何判据判定一条蜕变关系对某个代理是否是"健全"的测试**——因此一次失败的检查无法被信任为代理故障，而非不适用关系或测量伪影。

**Novelty delta（一句话，锁死）**
> 我们把蜕变关系的可采性系于**数值可判定性**：判决容差必须**可证地压过**测量算子固有的离散化误差地板——这条健全性前置条件是 Eniser relaxations（容差挂 oracle）、Duque-Torres/MetaTrimmer（适用性过滤）、CCML（MR 规范语言）都不要求的，且我们**为一类刻画明确的离散化证明它成立**。

## §1 新标题候选（弃 workflow/attribution 味，取 criterion/soundness 味）

1. **"Numerical Decidability as a Soundness Criterion for Metamorphic Testing of Machine-Learning Surrogates"**（推荐，最直给）
2. "When Is a Metamorphic Test Sound? Operator-Floor Admissibility for Oracle-Free Verification of Learned Surrogates"
3. "Sound Metamorphic Testing of Scientific ML Surrogates via Operator-Floor Admissibility"

现标题 "Domain-Validity-Gated Verification … Auditable Fault Attribution"（L37）= 工作流+归因味，降感知新颖性，弃。
**待用户拍板：标题选哪个。**

## §2 新 thesis（理论前置，替换 L86 现 thesis）

- 现（L86）："admissibility gating *changes* V&V outcomes rather than merely annotating them."（工作流味）
- 新：**数值可判定性是 oracle-free 蜕变测试的一条*健全*可采性判据**——它是由离散化在任何故障/SUT 之前就固定的前置条件，可证地把"可信的关系违例判决"与"测量伪影"分开；缺了它，离散化代理上的蜕变判决**不健全**。

## §3 新贡献结构（单脊柱 + 支撑机制 + 演示）

| # | 角色 | 内容 | 相对现稿 |
|---|---|---|---|
| **C1** | **唯一头条（脊柱）** | 数值可判定性可采性判据 + **operator-floor soundness 定理**：MR 是可采测试当且仅当判决容差可证压过测量算子固有误差地板。(i) 形式化判据；(ii) 为一类刻画明确的网格/算子证明 a-priori floor bound `[Phase B]`；(iii) 诚实刻画失效边界 | 现"Measurement-floor admissibility"(L92)从**四贡献之一**升为**唯一头条**，且补一般化定理 |
| **C2** | 支撑机制（判据的实现）| 判据落成可审计可执行资产：MR card + runner + claim ledger，每个可采性决策独立可查 | 现贡献2"validity-gated V&V asset construction"(L94)从**并列**降为**"判据如何被执行/审计"** |
| **C3** | 支撑机制（判据的输出）| 两轴 typed verdict（relation-violation × domain-violation）是判据授权的解释层 | 现贡献3"typed verdicts"(L96)从**并列**降为**"判据输出什么"** |
| **C4** | 演示 + 必要性 | 跨 MGN/PointMLP/PhysicsNeMo/airfoil/PINN/FNO：判据按物理/离散化**不同地**采信/拒绝/延迟；**measured necessity**=门控移除 100% 误警检测器、surface 精度监控结构盲的故障 | 现贡献4"bounded empirical utility"(L98)从**"utility 记账"**重framed 为**必要性演示**（catch-what-others-miss）|

## §4 弃增量卖点清单（不再作头条）

- ✂ "Validity-gated V&V asset construction" 作**并列贡献** → 降 C2 机制。
- ✂ "Typed relation-level verdicts" 作**并列贡献** → 降 C3 输出层。
- ✂ 标题/摘要的 "workflow" / "auditable fault attribution" 主框 → 换 "criterion / soundness"。
- ✂ "四件套 workflow"叙事 → 换"我们识别并证明一条健全性判据，并将其操作化"。
- ✂ §2.4 reliability/assurance 桥接段（L159-166，为 RESS 写）→ 缩为纯 related-work 定位（目标已改 TOSEM 非 RESS，不需可靠性 scope 挣扎）。**待用户拍板：缩短 vs 整段删。**
- ✂ coverage/duality 讨论线 → 保留但明确次要（现状已次要，维持）。
- **保留不动**：诚信机制（ledger/边界句/宽 CI）——TOSEM 加分，不碰。

## §5 摘要骨架（TOSEM 式，非 IST 结构化五段）

- **S1 问题**：MT 给 ML 代理 oracle-free 判决，但无判据判定关系是否*健全*测试 → 失败检查不可信。
- **S2 缺口**：既有容差/过滤/规范语言都不要求判决容差压过测量算子数值地板。
- **S3 贡献**：我们把可采性系于数值可判定性，**为一类离散化证明 operator-floor bound**，并操作化为可审计资产 + typed verdict。
- **S4 证据**：跨 MGN/PointMLP/airfoil/PINN/FNO 判据按物理改变判决；measured necessity（移除 100% 误警检测器、surface 精度盲故障）。
- **S5 边界**：有界多被测演示，非一般可靠性或缺陷率主张。

## §6 章节重排图（关键结构动作）

| 节 | 现状 | 重排后 |
|---|---|---|
| §1 Intro | 4 贡献并列、workflow 味 | 领起 soundness 缺口（importance）→ 锁 novelty delta → 新 thesis → C1-C4（C1 独大）|
| §2 Related | §2.4 为 RESS 挣 reliability scope | wedge 重锚在 soundness/decidability delta；§2.4 缩短去可靠性挣扎 |
| §3 Method | 领起 overview/candidate sources（L171/185）| **领起判据 + soundness 定理**（Phase B），再讲 card/verdict 作"实现判据" |
| §4 设计 | RQ 围绕 workflow | RQ 围绕判据：RQ1 floor bound 是否成立/可预测；RQ2 判据是否按物理改判；RQ3 必要性/measured-advantage；RQ4 breadth |
| §5 结果 | operator-floor 埋 §5.6(L467)；measured-advantage 埋附录(C38/C42) | **operator-floor 定理验证 + measured necessity 提到最前**；其余作 breadth |
| §Threats/Future | "general unstructured mesh" 列 future work(L575) | Phase B 闭合它 → 从 future 移入 C1 贡献 |

## §7 一句话总结 + 对 Phase B 的靶子锁定

**骨架**：从"一个四件套可审计工作流"改成"**一条可证健全的测试可采性判据 + 它的实现与演示**"——脊柱是 floor 理论，其余都挂在它下面。

**锁定 Phase B 唯一枢轴**：**C1(ii) 的 operator-floor bound 一般化**（结构网格 + 单 Delaunay → 一类刻画明确的非结构网格 soundness 定理）。这个定理成/不成，直接决定这篇是 TOSEM 稿还是回落 IST 稿（`paper/67` Reviewer-2 枢轴反驳）。

## §8 待用户拍板项（Phase C 收尾前）

1. 标题三选一（§1）。
2. §2.4 可靠性段：缩短保留一句桥 vs 整段删（§4）。
3. 确认贡献重排 C1 独大、C2/C3 降支撑（§3）无异议后，进 Phase B 理论一般化技术路线。
