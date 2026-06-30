# 56 · Phase 10.0 编辑可审性预检（投稿前评审）—— RESS

> 日期：2026-06-30 · 方法：§10.9 Council Mode，两个独立对抗性 RESS handling-editor persona（general-purpose 子代理）通读 `submissions/RESS/main.tex`，各自渲染 desk-reject 裁定，本文件为合成结论。
> 判据：`科研工作流指南.md` §Phase 10.0（四类桌拒 + 三道闸门 + 受众）；RESS scope 自述（`venues/RESS.md` §6.1）。

## 总裁定：**FAIL — 两个编辑独立均判 DESK-REJECT（针对 RESS）**

过关要求「A 四类 0 命中 / B 三闸门全是 / C 两项满足」——三项均不满足。

### A. 四类桌拒自查

| 类 | 裁定 | 依据（引稿件原文）|
|---|---|---|
| 超范围 | **命中（高危）** | 可靠性连接靠 scope 原文断言、未实例化。所有实验对象=cylinder/airfoil/Burgers/heat 纯 CFD/PDE surrogate，**无任何被嵌入的复杂工程系统在环**：无 PSA/fault tree/失效率/风险量化/system-level reliability 指标。abstract 承诺「an unnoticed fault propagates into whatever system consumes its output」在证据里从未兑现。智识归属 SE：自称 "software V&V / SciML V&V asset construction"，引 Duque-Torres/MetaTrimmer/Ralph Empirical Standards/Verdecchia（全 SE testing 谱系）。|
| 低新颖 | **未命中（楔子成立）** | operator-floor numerical-decidability gate「a test that to our knowledge is new for learned SciML surrogates evaluated OOD」；§2.2「The floor gate, not the recording discipline, is what is genuinely new here」逐一切割 Eniser/Duque-Torres/Lim2026/Kirsch。差异化站得住。**但 impact 落在 auditability 非 reliability**（§5「makes MR identification and execution more auditable」；conclusion「contribution is methodological」）。|
| 不成熟 | **命中（高危）** | 主定量证据=单 MGN 圆柱绕流 checkpoint（S0 复用 pilot，"K=6 roster as effective independent unit"）。四种宽度**全被作者本人边界句降级**：method-transfer「supporting breadth, not a cross-SUT or geometry-independent rate」；airfoil 用 rel L2 0.92 半废模型（"read for typed gate discrimination, not model accuracy"，近同义反复）；PINN/FNO「cross-family probe, not calibrated coverage」；外部 7 程序「read-only generalization check, not end-to-end, asserts no per-program reliability」。**过滤后无可靠性/覆盖/优越结论幸存。** |
| 质量不足 | **部分命中** | 过硬面：文献当前（Kirsch/Lim/Shikhman/Hillebrecht/Haugen）、统计审慎（Wilson/Wilcoxon/Cliff δ/bootstrap）、operator-floor 可复现（floor 预测差 0.5%、斜率 0.984 匹配 O(h)、R²=0.9999）、Zenodo+ledger 透明。薄面（作为可靠性证据）：**无任何基线被击败**（"complementarity ... not superiority"）、第二 SUT 半废、seeded mutants 自造且「gross corruptions that any divergence- or symmetry-sensitive detector would catch」5/10 平凡。|

### B. 三道闸门

| 闸门 | 答 | 回退 |
|---|---|---|
| Scope | **否** | Phase 0 |
| Novelty & impact | **否（impact 维度）** | Phase 1/3/4 |
| Research excellence | **勉强/否** | Phase 4（基线 + 第二 SUT 训练）|

### C. 表达与受众

| 项 | 裁定 | 依据 |
|---|---|---|
| 为该刊读者而写 | **否** | 摘要单块 ~250 词长跑句、无结构标签；术语面向 MT 小圈（domain-validity-gated/typed verdict/out-of-relation-domain/operator floor）；RESS 核心读者（PRA/系统安全）无 MT 背景，一次略读抓不到肯定结论。|
| 把审稿人当朋友 | **过度（病态对冲）** | 全文 9 张否定式边界表，几乎每个结果句跟 disclaimer（"suggestive rather than a validation"/"asserts no..."/"not licensed"/"bounded"）。持续 under-claim 到读者抓不住任何肯定结论。|

## 核心 convergent 诊断（两编辑独立一致）

**这是一篇 software-V&V / SE 方法论文，被重定位封面投 RESS，但正文没挣得这个 scope。** 同一稿在 IST/TSE 很可能 SEND——问题不在工作本身，而在「受众 × 主张」双错位：把一篇自陈「不主张任何可靠性率」的测试方法文，投到要可靠性/安全实证的 Q1 期刊。

诚信不是问题（恰相反，过硬到 under-claim）。死结是 scope + maturity 的**结构性**缺口，**框架/重写救不了**。

## 被埋没的真钩子（两编辑都点到）

署名含 CNNC High Trusted Computing 重点实验室 + 附录 C 的 OpenMC（蒙卡中子输运，核安全）。若以「核 surrogate 可靠性」立题、让 gate 的 typed verdict 去改变一个**可量化的可靠性/风险结论**（系统在环），scope 会硬得多——但这是**补证据（Phase 4 结构性工作）**，非改 intro。

## 退回判定（遵 Phase 10.0「任一不过留在对应 phase 修，不带病投稿」）

FAIL → 不得带病投 RESS。战略分叉（用户决策）：
1. 改投 SE 期刊（回 Phase 0）：编辑判 IST/TSE 更契合；但 IST 已桌拒此稿（含单 SUT/importance 同病），实际指向 TSE/TOSEM（门槛更高）。
2. 留 RESS，补结构性可靠性证据（回 Phase 4）：兑现 CNNC 核/OpenMC 系统在环案例 + 训好 airfoil + 打一个基线 + 为可靠性读者去对冲重写。补证据非粉饰，工作量大。
3. 其他（如先做可救的表达层再评估）。

---

## 复核：编辑裁定是否过严？—— 对照 RESS 真实发表谱（Crossref，issn 0951-8320）

> 用户要求先核实「RESS 真会桌拒这类稿」还是 persona 过严。方法：Crossref 按 RESS ISSN 过滤，查近 5 年实际发表论文的 profile。

**结论：persona 未过严——真实发表谱 *确认* desk-reject 风险，甚至更强。**

### 证据 1 · 蜕变测试在 RESS 近乎零先例
查 "metamorphic testing machine learning verification" + ISSN 过滤：**0 篇蜕变测试论文**。返回的全是「ML 做可靠性分析」（metamodel/reliability-based design/risk assessment）。本文核心方法（MT）不在 RESS 已发表词汇里。

### 证据 2 · RESS 的每一篇 ML-surrogate/CFD/软件-V&V 论文都桥接到一个**可靠性/风险/诊断量或决策**
- ML-surrogate 类：全部服务于失效概率/极限状态/RUL/退化/风险（"reliability-based metamodel"、"active learning surrogate for reliability analysis"、"mean time to failure prediction"、"seismic risk assessment using surrogate"）。
- PINN 类：全部产出可靠性/退化/RUL/诊断（"PINN-based reliability analysis"、"degradation modeling & RUL"、"resilience assessment"、"fault diagnosis"）。
- CFD 类：CFD 永远耦合到风险量化（"QRA through CFD for societal risk"、"CFD-informed fire-failure safety assessment"、"safety barrier performance by CFD for gas leakage"）——**无 CFD-surrogate-自身验证为目的**的论文。
- 软件/测试类：「software defect prediction」「coupled FMEA for HW-SW failure」「risk-informed verification prioritization」——均接到可靠性量/决策。
- physical-consistency NN：接到 fault diagnosis（"physical information consistency network for bearing fault diagnosis"）。

本文恰恰**显式拒绝**产出任何此类量（"asserts no per-program reliability"、"not a defect-detection rate"、"complementarity not superiority"）——落在 RESS 已发表分布之外。

### 证据 3 · 最近邻先例反而点明**制胜桥接**
RESS 确实发过安全关键软件测试方法：**"Exhaustive testing of safety-critical software for reactor protection system"（Lee et al., RESS 2020）**——核反应堆保护系统、系统在环、接到安全。这正是两 persona 指出的被埋没真钩子（CNNC 核背景 + OpenMC）。RESS 收这类稿的条件是：**绑定一个安全关键系统 + 可靠性/安全后果**，不是孤立验证 surrogate。

### 复核裁定
两 persona 的 DESK-REJECT **被真实发表谱坐实**，非过严。同时验证也**确证了制胜路径**：把 gate 的 typed verdict 接到一个可靠性/风险/安全量或决策（最自然=核安全关键 surrogate，系统在环）。这是 Phase 4 结构性补证据，框架救不了。→ 战略分叉中**选项①（留 RESS 补结构性可靠性证据，走核/OpenMC 桥接）有最强的发表谱支持**；选项②（改投 SE）是承认错配的退路。
