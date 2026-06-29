# undermind 检索：offline oracle-free validation of physics-based ML surrogates（RESS 定位）

> 日期：2026-06-29 · 目的：解 `paper/54` DA-1（scope-by-convenience）+ 补 RESS 谱系定位
> 提示词与定调见 `paper/55`。报告在线版：app.undermind.ai/report/7a6654ea…（页 1）

## 文件
| 文件 | 说明 |
|---|---|
| `undermind_report.pdf` | 37 页报告（文字浅色，需 `pdftotext -layout` 提取）|
| `undermind_candidate_pool.bib` | 172 条候选池（hash 键 @misc，含 author/title/year/doi/abstract）|

## 报告中心发现（对本文极有利）
undermind 独立判定：现有文献已成熟覆盖**两簇**——
1. **神经 PDE/ODE 代理的 oracle-free 误差/残差认证**（多为 PINN）：Eiras ∂-CROWN、Hillebrecht & Unger、Mukherjee、Haugen 等 [1-13,16,21,22]；
2. **CFD 中 ML 代理的可信性/credibility 框架**：Kirsch et al. PCMM/NACA-0012 三部曲 [18,19,20]。

**但"恰恰缺少本文要做的中间件"**（报告原话）：
- "No explicit, modular catalogues of **admissibility properties as offline tests**";
- "No **typed admissibility gating or contract system**";
- "No **diagnostic attribution framework for failed property checks**" —— 并逐字列出本文的判决类目："**Surrogate defect vs out-of-domain input vs invalid property assumption vs numerical artefact vs inconclusive**";
- "Lack of **non-statistical false-alarm control** methods";
- "Sparse integration with **safety cases and reliability arguments**"。

→ **这是对本文新颖性/必要性（Phase 3）的独立外部印证**，几乎逐字吻合本文 RQ3 类型化判决；同时给出 DA-1 的解法：把本文的 property-based typed V&V 作为"被点名的开放缺口"接入认证线（技术骨架）+ Kirsch PCMM/credibility（assurance 框架）两簇对话。

## 定位用法（Related Work reliability 段，解 DA-1）
- **技术骨架对照**：Eiras/Hillebrecht-Unger/Mukherjee/Haugen 的 oracle-free 误差认证 = 本文"数值可判定性地板"所依赖/对话的近邻；本文不重做误差界，而是**在其上加"多属性 admissibility 门控 + 类型化归因"层**（报告明示这层"remains open territory"）。
- **assurance 对话锚**：Kirsch et al. PCMM/credibility 三部曲（NACA-0012，与本文 airfoil 任务同域）= 本文 V&V 产物可作为"validation artefacts"slot 进的 credibility 结构；本文补其所缺的 property-based typed 证据。
- **边界铁律（漂移检查 paper/53 §G）**：这些文献用于**定位对话与佐证缺口**，不据此新增 reliability 度量/泛化/UQ claim。

## 核实状态 —— 已核实（见 `verification.md`）
- **核心 10 篇全真，0 伪造**（含 Kirsch PCMM 三部曲、Hillebrecht-Unger、Eiras ∂-CROWN、Haugen、Mukherjee）。
- **缺口主张**：精确"(a)多属性事后测试 +(b)类型化门控 +(c)违例归因"三合一表述下**成立**；宽泛表述会 overclaim。
- **新硬约束**：Related Work 必须显式引用并**区分** Lim 2026（核工业 validation-gated，**最近邻竞争**，在线 vs 本文部署前）/ Shikhman 2026 / Daniels 2025 / Spotorno 2026 / Van Acker 2019（"domain-validity"命名祖先）。
- 元数据必改：Eiras→ICML 2024；Kirsch PCMM→2025。预印本仅作前沿点缀（§8.6）。
- 入选 bib 前按 §11.2.1 全引用审计；hash 键改可读 cite-key。
