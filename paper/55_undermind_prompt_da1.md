# 55 · undermind.AI 检索提示词 —— 解除 DA-1（scope-by-convenience）

> 日期：2026-06-29 · 目标：为 RESS 重定位补足"可靠性工程对话"文献，使正文真正进入 RESS 血脉，而非封面重定位。
> 用法：复制下方整段贴入 undermind.AI（它按对"研究主题描述"的深层相关度排序，喜欢一段精确的研究问题陈述 + 相关性判据 + 排除项，而非关键词堆）。
> 已知 3 条 RESS 必补在 `paper/references_seed.md`；本检索是为找到**更广的可靠性对话**（assurance / OOD-trustworthy / surrogate V&V），把 Related Work 锚牢。

---

## 提示词（英文，直接粘贴）

I am writing a verification-and-validation method paper for the reliability engineering community and need to anchor it in the right literature. I am looking for research on the **verification, validation, and reliability assessment of machine-learning surrogate models** — data-driven models that replace expensive physical simulators or numerical solvers — when they are deployed as components of **complex, safety- or reliability-critical engineering systems**, with a specific focus on how to **trust such surrogates out-of-distribution**, where no exact ground-truth oracle is available.

The precise methodological problem I care about: when a learned surrogate is checked against a physically derived consistency property (a conservation law, a symmetry, a scaling relation, or a continuity condition) and that check fails, how does one **soundly decide whether the failure indicates a genuine model fault, an inapplicable or invalid test, or a numerical/discretization artifact** — that is, **fault attribution and false-alarm control in oracle-free verification of ML surrogates**.

A paper is **highly relevant** if it addresses one or more of:
- Reliability assessment, safety assurance, or assurance cases for machine-learning and surrogate/data-driven models in safety-critical domains (nuclear instrumentation and control, aerospace, structural, fluid/thermal, prognostics and health management, autonomous systems).
- Out-of-distribution detection, robustness, or validation of learned models **tied to trustworthiness, fault detection, or diagnosis** (not pure accuracy benchmarking).
- Property-based, physics-consistency, conservation/symmetry, or metamorphic checking of scientific/engineering ML models used **as a verification or validation technique**.
- Distinguishing model faults from invalid test conditions or numerical error in computational/ML model validation; **false-alarm control and trust calibration** in model validation.
- V&V methodology for surrogate, reduced-order, or physics-informed ML models in **engineering reliability and risk analysis**.

**Emphasis:** I especially want work from the **reliability engineering and system safety** community (Reliability Engineering & System Safety, IEEE Transactions on Reliability, prognostics and health management, risk/safety venues) and from the **ML-safety / assurance-case** literature, in addition to scientific-software V&V.

**Exclude or down-weight:** papers purely about improving surrogate accuracy or proposing new ML architectures with no validation/verification/trust/reliability angle; pure software-engineering metamorphic-testing papers with no scientific-ML or reliability connection (I already have full coverage of that strand).

**Time emphasis:** prioritize 2019–2026, but include foundational works on ML/model V&V in reliability engineering.

---

## undermind 澄清提问的定调答复（2026-06-29，已回）

undermind 回了两问，定调如下（忠于 RQ3 + 证据边界，防 UQ/runtime 漂移）：
- **Q1 pre-deployment vs runtime** → 以 **pre-deployment/离线 V&V 方法学**为中心（验证技术跑在代理模型上，非 runtime monitor）；runtime/OOD-monitoring 仅作邻接背景、低权重。**不声称/不评估 runtime。**
- **Q2 false-alarm 目标** → 主 **A（诊断性归因**：模型误差 / 无效属性·测试 / 数值伪影，= 本文类型化判决）；**B**（UQ/信任校准）作对照互补、非核心（判据是数值可判定性非统计置信）；**C**（assurance-case）作向上接入的定位锚、放几篇。
- **净权重**：A > C > B；下调纯 UQ-置信法、纯 runtime monitor。
- **交集定位**：scientific-model discrepancy attribution × surrogate validation（非 UQ-for-reliability、非 runtime monitoring）。

undermind 第二轮两问（已回）：
- **Q3 surrogate 类别** → **C（A 为主对象）**：A=科学计算替代（MeshGraphNets/PINN/FNO，我的真实 SUT，保持主）；**有意纳入 B**（PHM/SHM/核电 I&C/autonomous）**仅限"把学习型组件当 reliability-critical 并讨论验证/信任"的工作**（= 缺锚的可靠性对话）。别塌纯 A，也别塌纯 B（B 用于定位，非声称在那些域评估过）。
- **Q4 一致性属性** → **C**：解析关系(A)与可判定约束(B)都作实例出现；重心**不是属性类型**，而是**违例后的可采性门控 + 类型化归因/误报控制**（= RQ3 贡献）。偏向属性无关方法学，非 property-enforcing 架构。
- **互锁**：Q2=A、Q4=C 共同把重心钉在归因/误报控制；Q3 让 A 锚真实对象、B 补 RESS 血脉。

## 检索回来后怎么用（Phase 2→3 闭环）
1. 命中条目按 §8.3 用 paper-search MCP 核实真实性（有 DOI 直查 Crossref）。
2. 选 3–6 条进 `references.bib`，连同 `references_seed.md` 已记的 3 条 RESS 必补，跑 §11.2.1 全引用审计。
3. 在 Related Work 新增一段「Reliability and assurance of learned surrogates」，把贡献接进该对话——这一段 + 去黑话(§I) + 广度前置(§H) 共同解除 `paper/54` DA-1。
4. 严守边界（漂移检查 G）：补的文献用于**定位对话**，不得据此新增 reliability/泛化 claim。
