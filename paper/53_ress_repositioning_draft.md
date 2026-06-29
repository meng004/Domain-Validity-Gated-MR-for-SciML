# 53 · RESS 导向改稿方案（重定位草案）

> 日期：2026-06-29
> 依据：`venues/RESS.md`（官方 16 页 Guide 坐实版）+ `paper/52`（IST 桌拒诊断）+ `科研工作流指南.md` Phase 10.0
> 核心动作：把叙事从「为 SciML 做 SE 蜕变测试」**重定位**为「为复杂系统中的学习型代理做可审计的故障归因验证」，
> 对接 RESS scope 的「reliability of complex systems / software reliability / automatic fault detection and diagnosis」。
> **铁律**：只改定位与措辞，不新增任何结果；严守原稿证据边界（不声称可靠性度量、不声称真实缺陷检出率）。

---

## A. 标题（reliability 引导，2 选 1）

1. **Domain-Validity-Gated Verification of Machine-Learning Surrogates: Auditable Fault Attribution for Out-of-Distribution Use**
2. **Trustworthy Fault Attribution for Learned Surrogates: A Domain-Validity-Gated, Oracle-Free Verification Method**

> 取舍：方案 1 把「verification + fault attribution + OOD」三词全摆到标题，最贴 RESS 检索；
> 「metamorphic testing」从标题撤下（RESS 读者不熟该术语），降为正文机制词并首次出现给释义。

---

## B. 非结构化摘要（RESS 风格，≤ 200 词，单段，无结构化标签，无内部引用）

Machine-learning surrogates are increasingly deployed as components of complex
engineering systems, where they must be trusted on operating points far from
their training distribution. Unlike the high-fidelity models they replace, such
surrogates have no cheap exact oracle, so a failed check cannot easily be
attributed to a genuine surrogate fault rather than an inapplicable test or a
numerical artifact, a recurring obstacle for verification, fault detection, and
diagnosis. We present a domain-validity-gated method that turns physically
derived consistency relations into auditable, executable verification assets and
decides, before any fault is reported, whether a relation is admissible for a
given surrogate: its preconditions must hold, its measuring operator must be
numerically decidable so that the tolerance dominates the operator's intrinsic
error floor, and its verdict is typed to separate a true surrogate inconsistency
from out-of-domain application and numerical limits. A claim ledger binds
every reported result to a recorded artifact. On a mesh-based computational-
fluid-dynamics surrogate, with supporting cross-architecture and cross-equation
studies, the gate removes detectors that would false-alarm on a correct
surrogate, rejects physically inapplicable relations, and bounds where the
admitted checks can and cannot surface seeded faults. The outcome is a more
auditable, false-alarm-controlled basis for attributing surrogate faults.

> 边界自检（已应用 G-2 红线）：末句用「basis for **attributing surrogate faults**」（= RQ3 typed verdict），
> 不用 "diagnosing/localizing"（避开未验证的 localization claim）；摘要中段 "fault detection, and diagnosis"
> 仅作动机语境，合规。未出现 superiority / reliability rate / real-world detection / trustworthy。

---

## C. 引言开头（前两段重写 + 贡献段，reliability 引导）

**1. Introduction**

**[第 1 段 · 把问题立成可靠性问题]**
Machine-learning (ML) surrogates are increasingly used as components of complex
technological systems: trained on simulator or sensor data, they replace
expensive physical or numerical models inside design, monitoring, and decision
pipelines. Once embedded, such a surrogate must be trusted on operating points
far from its training distribution, where its errors are least understood and
where an unnoticed fault propagates into whatever system consumes its output.
Unlike the high-fidelity model it replaces, a learned surrogate has no cheap
exact oracle: for most inputs there is no reference answer to check against, so
held-out accuracy alone cannot tell an engineer whether the surrogate has
violated a property that the underlying physics requires.

**[第 2 段 · 把 oracle-free 检查与"误归因"风险讲清，引出 admissibility 才是真问题]**
A practical response is to check *relations* that any correct surrogate must
satisfy under controlled transformations (conservation, symmetry, scaling,
continuity) instead of checking each output against a known value. These
physically derived checks give an oracle-free way to probe a surrogate and, when
one fails, a candidate signal for fault detection and diagnosis. But a physical
relation is not automatically a sound test of the software: a symmetry may
depend on geometry and boundary labels, a conservation law on a discrete
operator with its own error floor, and a transformed case may leave the
relation's domain of validity before it reveals any genuine fault. Treating every
failed check as a surrogate fault therefore risks false alarms and
misattribution: blaming the model when the test, not the model, was at fault.
The problem this paper addresses is how to decide, *before* a fault is reported,
whether a physically derived relation is an admissible, numerically decidable
check for a given surrogate, so that its verdict can be trusted to separate a
true surrogate inconsistency from an inapplicable relation or a numerical
artifact.

**[第 3 段 · 贡献 + scope 对接 + 案例，末句锁边界]**
This paper contributes a domain-validity-gated verification method: (i) an
admissibility gate that retains a candidate relation only when its preconditions
hold and its tolerance dominates the measuring operator's intrinsic error floor;
(ii) a structured, executable "MR-card" asset that records the transformation,
mapping, metric, tolerance, exclusions, and verdict for each retained relation;
and (iii) a typed verdict scheme that separates surrogate inconsistency from
out-of-domain application and numerical limits, with a claim ledger binding every
result to a recorded artifact. We instantiate and evaluate the method on a
mesh-based computational-fluid-dynamics surrogate (a MeshGraphNets cylinder-flow
model), with supporting studies across a second flow task, two further
architectures, and two partial-differential-equation families. The method is a
verification and fault-attribution technique with a discernible relationship to
the reliability of complex systems that embed learned surrogates; it complements,
and does not replace, accuracy, uncertainty, or trust-region diagnostics, and it
makes no claim of general surrogate reliability or real-world defect rates.

> 末句刻意复用 RESS scope 原句「discernible relationship to … reliability of complex systems」，
> 把 scope 闸门答在明面上，同时一句话锁住原稿全部边界。

---

## D. Phase 10.0 编辑桌拒预检（代入 RESS）

**A. 桌拒四类自查**
- [x] **超范围** —— 由 IST 的头号杀手**反转为 RESS 的资产**。CFD/MeshGraphNets/故障诊断内容正落在 RESS scope（reliability of complex systems / software reliability / automatic fault detection and diagnosis）。**通过。**
- [△] **低新颖** —— importance 现已一句话讲清（trusted-OOD 代理的可审计、控误报故障归因）。残留：gate 思想本身窄 → 用"单一清晰思想"正面包装，别再淹没在术语里。
- [△] **不成熟** —— RESS 明列「industrial case studies」为合法体裁，比 IST 宽容；但仍须把 **cross-architecture / cross-equation 广度前置**为"方法可迁移"的证据，单 SUT 诚实标注但不作为全部。**最弱项，须靠叙事重排缓解。**
- [x] **质量不足** —— 真实运行 + claim ledger + Wilson/Wilcoxon 统计 + 学术写作达标。**通过。**

**B. 三道编辑闸门**
- [x] **Scope 闸门** → 通过（reliability of complex systems + fault diagnosis）。
- [△] **Novelty & impact 闸门** → "如何推进领域"= 让学习型代理的故障归因可审计、控误报；"scale 出样本"须倚重 cross-arch/cross-equation 广度 + 方法 SUT-agnostic。前置广度即可过。
- [x] **Research excellence 闸门** → 方法论扎实；数据/基线为当前 SOTA（DeepMind MeshGraphNets、NVIDIA PhysicsNeMo），最新。通过。

**C. 表达与受众**
- [△] **为 RESS 读者写** → 主改写任务：删/译 SE 专属黑话（MetaPattern、MR-family、f_inv.eqv sans-serif 记号），reliability 读者不识；首次出现的「metamorphic relation」给释义。
- [△] **把审稿人当朋友** → 把"什么都不声称"的全程对冲，改为"在 X 范围内确立 Y"的诚实肯定句。

**结论**：scope 闸门已稳过（IST 的死因在此反转）；残留全是**叙事/可读性 + 把广度前置**，无需新实验。

---

## E. 摘要/引言之外的下游改动清单（同一版改稿一并做）

1. **去黑话**：全文删/译 MetaPattern、MR-family、sans-serif 算子记号；保留机制但首现给释义。
2. **前置广度**：把 cross-architecture（PointMLP、PhysicsNeMo）+ cross-equation（PINN/FNO over Burgers/heat）从 Appendix/支撑级**提到结果主线靠前**，作为"方法不依赖单一 SUT"的证据。
3. **贡献节**重写为 reliability/verification 语汇；新增一段显式 scope 对接。
4. **Related Work** 补 1–2 条 RESS 谱系引用（safety-critical/复杂系统中 ML 的 V&V 与可信性），把对话对象从纯 MT 圈扩到可靠性圈。
5. **合规**（按 `venues/RESS.md`）：摘要 ≤200 词（本草案已达标）；单一通讯作者；GenAI 声明节标题固定为
   `Declaration of generative AI and AI-assisted technologies in the manuscript preparation process`（references 前）；
   Data statement（Option C）；Funding 声明；参考文献 elsarticle-num。
6. **跑** `python venues/templates/RESS/precheck_RESS.py <tex> highlights.txt` 全过。

---

## F. Highlights（RESS：3–5 条 × ≤85 字符，可直接套）
- Validity gate decides when a physics check can soundly fault a learned surrogate
- Tolerance must dominate the measuring operator's numerical floor to admit a check
- Typed verdicts separate surrogate faults from out-of-domain and numerical limits
- A claim ledger binds every reported verdict to a recorded artifact
- Case study bounds where admitted checks can and cannot surface seeded faults

---

## G. 主题漂移检查（对照 RQ0–RQ4 + 证据边界）

> 真源：`manuscript/manuscript.md` L43–55（RQ0–RQ4）；`README.md` L54–77（Evidence boundary）。
> 边界明确 **not claimed**：cross-SUT/geometry-independent rates、general/real-world fault-detection rates、
> **validated localization**、runtime、**reliability**、model accuracy。

**结论：实质无漂移，但有 3 处措辞越界风险，必须在重定位中夹死。**

RQ → 重定位元素 → 判定：

| 锚点 | 重定位如何对应 | 判定 |
|---|---|---|
| RQ0 候选 MR 域有效性筛选 + 转可执行 oracle-free 资产 | 摘要/引言主线、贡献 (i)(ii) | ✅ 一致 |
| RQ1 validity rubric 区分有效/无效/越域 | 摘要「whether a relation is admissible…preconditions…numerically decidable」| ✅ 一致 |
| RQ2 MR card / 可执行资产 | 贡献 (ii) + claim ledger | ✅ 一致 |
| RQ3 typed verdict（fault/OOD/numerical/inconclusive）| 「typed to separate true surrogate inconsistency from out-of-domain and numerical limits」| ✅ 一致 |
| RQ4 案例证据 vs rollout/LLM 基线，scoped 非 cross-SUT 率 | 「On a mesh-based CFD surrogate, with **supporting** cross-arch/cross-eq studies…bounds where…can and cannot surface seeded faults」| ✅ 一致（"supporting"+"bounds"保住边界）|

**3 处越界风险（重定位引入的新词，必须收敛）：**

1. **「Trustworthy」/「trusted」** —— README not-claimed 含 **reliability**。
   - 红线：标题取**方案 1（Auditable…）勿取方案 2（Trustworthy…）**；「trusted on OOD」只可作**动机背景**，绝不可写成"方法交付了 trust/reliability"。
2. **「diagnosis / diagnosing」** —— README not-claimed 含 **validated localization**；本文 localization 仅「first suggestive test」。
   - 红线：把交付能力词统一为 **fault attribution / typed verdict**（= RQ3）；「diagnosis」只可出现在**动机句**，不可作为已交付能力。摘要末句 "basis for diagnosing" → 建议改 "basis for **attributing faults in**"。
3. **广度前置（H 节）可能把 supporting 证据升格为 primary 泛化claim** —— 违反 "within one SUT / not cross-SUT rates"。
   - 红线：H 节只提升**可见度**，每处保留「**supporting breadth, bounded, NOT a cross-SUT generalization rate**」标签；K=6 roster 仍标"复现非独立样本"。

> 一句话：重定位是**受众/语汇**变更，RQ、claim、证据边界三者一字未动；唯一要守的是别让 reliability 域的词（trust/diagnosis/泛化）反向污染成超出 ledger 的claim。

---

## H. 交付件 1 · 广度前置重排方案（夹带 G 节红线）

**问题**：cross-architecture / cross-equation 证据现散在 §5.3（same-task replication）、§5.4（airfoil）、Appendix C（PINN/FNO），
读者在主线读不到"方法不依赖单一 SUT"，正中"不成熟/单 SUT"桌拒风险。

**动作**：在主结果 §5.2（primary cylinder-flow）**之后立刻**新增一小节
`5.3 Method transfer across architectures and equations`，用**一张表**收拢全部广度证据，再把原 §5.3/§5.4/Appendix C 降为该表的展开细节。

新表（每行已是 ledger 内既有运行，不新增结果）：

| Setting | 架构/方程变化 | 同一 admissibility predicate 的判定 | 边界标签 |
|---|---|---|---|
| MGN S4/S5 variants | 同任务、更宽/更深 | node-perm pass；mirror-y OOD fail；conservation diag pass；exact-sym fail | supporting；同架构族，非 cross-SUT 率 |
| PointMLP | 不同架构类（无 message passing）| 同上типed 判定复现 | supporting；不同非-MGN SUT，非率 |
| PhysicsNeMo MGN | 生产框架实现 | node-perm pass；mirror-y OOD fail | 生产框架 smoke，非率 |
| PINN / FNO | 跨方程（Burgers/heat）| relation-appropriate typed verdicts | breadth probe，非 calibrated coverage |

**前置后必须保留的红线句**（防 G-3 漂移）：
> "These settings show the **same predicate produces typed decisions** across architectures and
> equations on **bounded** subjects; they are supporting breadth, **not a cross-SUT or
> geometry-independent pass/fail rate**. The primary quantitative evidence remains within one
> MeshGraphNets checkpoint (§5.2)."

**效果**：把"广度"摆到编辑略读看得到的位置（缓解不成熟桌拒），同时一句话锁死不越界成泛化 claim。

---

## I. 交付件 2 · SE 黑话去/译清单（面向 RESS 可靠性读者）

策略：**保留**核心技术词但首现给释义；**替换/删**只有 SE/NOETHER 圈认得的自造记号。

| 现稿术语 | 处置 | RESS 读者友好渲染 |
|---|---|---|
| MetaPattern（Layer 1）/ MR family（Layer 2）| **删层级体系** | 直接说"relation families (symmetry, conservation, …)"，不引 Layer 1/2 抽象 |
| `f_inv.eqv` `f_conv.lim` 等 sans-serif 算子记号 + a–j 字母 | **删记号** | 用英文名直呼："the symmetry-equivariance family"、"the convergence-order family" |
| MetaPattern/MR 的 Noether 对应 | **降为一句脚注或删** | RESS 读者无需算子代数；保留会触发"超范围/晦涩" |
| metamorphic relation (MR) / metamorphic testing | **保留 + 首现释义** | "metamorphic relations (properties that must hold between related runs, used as oracle-free checks)" |
| out-of-relation-domain（verdict）| 保留但**首现释义** | "out-of-relation-domain (the transformed case left the relation's validity domain)" |
| admissibility gate / admissible MR | 保留（核心贡献词）| 已在引言释义，OK |
| domain-validity-gated / validity-gated V&V asset construction | **简化** | "domain-validity-gated verification"（去掉 "asset construction" 行话）|
| SUT (system under test) | 保留 | 可靠性圈通用，OK |
| SciML surrogate | **首现展开** | "machine-learning surrogate (a learned model that replaces a simulator)" |
| rollout error / held-out trajectories | **首现释义** | "rollout error (multi-step prediction error on held-out test trajectories)" |
| OOD | **首现展开** | "out-of-distribution (OOD)" |
| typed verdicts | 保留 | 已释义，OK |
| MR-card | 保留 + 释义 | "MR card (a structured, executable record of one admitted relation)" |
| MetaTrimmer / constraint-architecture pattern | **降为 Related Work 一句** | 不进方法叙事主线 |

**红线（同 G-2）**：去黑话时把交付能力词收敛到 **fault attribution / typed verdict**，
凡 "diagnosis/localization/diagnose" 仅留在动机句。

**执行顺序**：先 H（重排，结构定稿）→ 再 I（去黑话，逐节扫）→ 跑 `precheck_RESS.py` + humanizer 扫描。
