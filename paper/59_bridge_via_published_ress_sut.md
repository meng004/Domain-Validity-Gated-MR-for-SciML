# 59 · 桥接方案 B —— 嫁接到 RESS 已发表论文的待测程序 + 可靠性量

> 日期：2026-06-30 · 问题：能否借一篇 RESS 已发表论文的 SUT + 它已被 RESS 接受的可靠性量，把本文的 MT 方法 + MR 适用性(admissibility)理论嫁接上去？
> 答案：**可以，且可能是最干净的桥接——scope 契合 by-construction。** 但成立须同时满足三条，且"用其原程序"通常要降级为"复现其可靠性问题(标准方法+开放基准)"。

## 成立的三个必要条件（本文方法的硬约束）

1. SUT 是**学习型 surrogate**（ML 代理 simulator/solver）——否则本文方法无对象。
2. 该 SUT 物理**容纳本文已有 MR 族**（守恒/对称/标度/连续/单调）作 admissible 检查——否则 MR 适用性理论无处落。
3. 有一个**可靠性量**(失效概率/故障定位/k-eff)，且 gate 能**改变/守护**它——否则不进 RESS 谱。
+ 工程前提：**可复现**（原论文开源，或标准方法+开放基准可重建）。

## 候选 RESS 目标（按嫁接契合度排序，均真实 RESS 论文）

### ★★★ 最优：PINN-PDEM 可靠性（概率守恒 MR → 失效概率）
RESS 已发表簇：Das & Tesfamariam 2023 (10.1016/j.ress.2023.109849, PINN-PDEM 随机动力系统可靠性, 53 引)、Guo/Zhang/Dong/Frangopol 2024 (10.1016/j.ress.2024.110234, probability-informed NN 点演化 KDE 时变可靠性)、Hao/Yan/Chen/Yuen 2026 (10.1016/j.ress.2026.112216, 多物理 PINN 解降维 PDEE)、Tang 2024 (10.1016/j.ress.2024.110762)。
- **MR 契合 = 极佳**：这些用 PINN 解广义密度演化方程(GDEE)得 PDF→失效概率。PDF **必须满足概率守恒 ∫p dx=1**——正是本文**守恒 MR 族**；还须非负(单调/正性)、满足初边值。
- **可靠性量 = 失效概率**（RESS 最经典量）。gate 价值：判一个概率守恒违例是**真模型故障**(失效概率不可信)还是**数值伪影**(配点/积分地板)——本文 typed verdict + operator-floor 直接适用。
- **MR 适用性理论桥接点**：本文的 numerical-decidability 地板(容差须压过测量算子固有误差)在此变成「概率守恒的**积分求积地板**何时低于容差」——**理论原样迁移，算子实例从离散散度换成求积分**。这正是"MR 适用性理论桥接"，忠实非牵强。
- **可复现 = 高**：PDEM(Li & Chen)是教科书方法，基准是标准随机振子(SDOF/MDOF)，**不需原作者代码**即可重建 PINN-PDEM。

### ★★ 次优：WDN 漏损 GNN（节点质量守恒 MR → 漏损故障定位）
RESS：Zhang & Fink 2026 (10.1016/j.ress.2025.111494, Algorithm-informed GNN 漏损检测与定位)。
- **MR 契合 = 好**：管网水力遵守**节点质量守恒(进=出)** = 本文守恒 MR。GNN 代理预测压力/流量；漏损=待定位故障。
- **可靠性量 = 漏损检测/定位**（RESS scope 明列 fault detection and diagnosis）。gate 价值：区分真漏损(物理故障) vs 传感器/数值伪影→降误警(FAR)。
- **可复现 = 高**：WDN 有开放标准基准(L-Town/BattLeDIM/LeakDB/EPANET 网络)，Fink 组常开源。

### ✗ 不契合：surrogate-assisted 结构可靠性（Kriging/active-learning）
如 AMFGP(10.1016/j.ress.2024.110020) 等大量。代理的是**抽象极限状态函数 g(x)**，其上**无守恒/对称/连续物理 MR**——本文 MR 族无处落。**不选。**

### ★ 备选：PINN 管道/结构失效概率（力学 PDE）
Taraghi 2026 (10.1016/j.ress.2026.112592)、Jiang 2026 (10.1016/j.ress.2026.113004 PINN+GBT 地震管道失效概率)。力学 PDE 有平衡/守恒结构(中等 MR)，失效概率输出；可复现中等。

## 方案 B vs 方案 A（核 PKE/OpenMC, paper/58）

| 维度 | B：嫁接 RESS 已发表 SUT | A：姊妹库核 PKE/OpenMC |
|---|---|---|
| RESS scope 契合 | **更强**（引 RESS 论文作锚问题，直接进其对话）| 强（核安全，但靠姊妹库借用）|
| 新增 ML 工作 | **更多**（须重建/训 PINN-PDEM 或 WDN-GNN，标准小模型）| 更少（PKE PINN 已只读存在）|
| 可复现/可信 | 高（标准方法+开放基准）| 中（受姊妹库只读约束，须本仓首次执行）|
| 可靠性量 | 失效概率 / 漏损定位（RESS 原生）| FAR/MDR（须自定义）|
| MR 适用性理论展示 | **极干净**（概率守恒 ∫p=1 + 求积地板）| 干净（三分诊断金标准已有）|
| 定位风险 | 低（题中题、有锚）| 中（核 framing 仍需说服非核审稿人）|

**互补而非互斥**：最强组合 = **B 作主 RESS-fit 案例**（PINN-PDEM 概率守恒→失效概率，或 WDN-GNN）+ **A/现有 CFD/PINN/FNO 作 supporting breadth**（方法跨架构/跨方程不依赖单一 SUT）。

## 结论与建议

**可行，且方案 B 的 scope 契合优于方案 A。** 最优单一目标 = **PINN-PDEM 可靠性**：概率守恒是本文守恒 MR 最严格、最干净的可采实例（∫p=1 精确，operator-floor 自然变成求积地板），失效概率是 RESS 最经典量，且**可不依赖原作者代码、用标准 PDEM 基准复现**。本文贡献由此变成「为 RESS 已确立的可靠性代理流程加上 validity-gated 故障归因——判一个物理一致性违例是失效概率不可信的真故障还是数值伪影」。

代价相对 A：多一次标准小模型训练。收益：scope 契合 by-construction、可复现性强、MR 适用性理论展示最干净。

**待用户定夺**：B(PINN-PDEM 失效概率，推荐) / B(WDN-GNN 漏损) / A(核 PKE/OpenMC) / A+B 组合(B 主 + 现有资产作 breadth)。
