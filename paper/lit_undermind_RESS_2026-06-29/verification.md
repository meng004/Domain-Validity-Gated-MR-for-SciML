# undermind 报告核实（paper-search MCP，2026-06-29）

> 核实对象：`undermind_report.pdf` 依赖的核心论文真实性 + 中心"缺口未占"主张。
> 方法：paper-search MCP（Crossref DOI 直查 / arXiv / Semantic / OpenAlex）。实事求是，查不到即标 ✗/△。

## 1. 核心论文真实性 —— 10/10 全真，0 伪造

| 论文 | DOI/ID | 状态 | 载体 | 元数据修正 |
|---|---|---|---|---|
| Kirsch, Fathi, Rider — SciML-Adapted PCMM to DNN Surrogate (Aerodynamic Coeff.) | 10.1115/1.4071802 | ✓ | **ASME J. Verification, Validation & UQ 10(4):041001** | bib year=2026 → **实为 2025** |
| Kirsch, Rider, Fathi — Wholistic Credibility Assessment … Aerodynamics | 10.1115/vvuq2025-152225 | ✓ | ASME 2025 VVUQ Symposium | 官方拼写 "Wholistic" |
| Kirsch, Rider, Fathi — HOLISTIC Credibility Assessment … | 10.2172/3028632 | ✓ | DOE/OSTI 技术报告 | **与上条近重复，二选一** |
| Kirsch, Rider, Fathi — Credibility Assessment … NACA 0012 | 10.1115/vvuq2024-132964 | ✓ | ASME 2024 VVUQ Symposium | 三部曲最早一篇 |
| Hillebrecht & Unger — Rigorous a Posteriori Error Bounds, PDE-PINNs | 10.1109/TNNLS.2023.3335837 | ✓ | IEEE TNNLS 36(1):1583-1593 | 含 NSE 算例 |
| Hillebrecht & Unger — Certified ML: a posteriori for PINNs | 10.1109/IJCNN55064.2022.9892569 | ✓ | IJCNN 2022 | "certified ML"语汇起点 |
| Hillebrecht & Unger — Prediction error cert. … Stokes | arXiv 2508.07994 | ✓ | 预印本(2025) | semigroup；绕柱 Stokes |
| Mukherjee et al. — Rigorous Error Certification for Neural PDE Solvers | arXiv 2603.19165 | ✓ | 预印本(2026-03) | 极新、未评审 |
| Eiras et al. — Efficient Error Certification for PINNs (∂-CROWN) | arXiv 2305.10157 | ✓ | **ICML 2024 (PMLR 235:12318-12347)** | bib "Unknown Journal/2023" → **改 ICML 2024** |
| Haugen, Stepanenko, Hansen — Trustworthy AI in numerics | arXiv 2509.26122 | ✓ | 预印本(2025) | 覆盖 neural operator |

## 2. 中心"缺口未占"主张 —— 精确表述下成立，宽泛表述下 overclaim

反向搜证（172 池里抽 6 条最贴近"diagnosis/gating/validity/admissibility"的）：

| 邻接条目 | 真做了什么 | 占缺口? |
|---|---|---|
| Shikhman 2026 — Diagnosing Failure Modes of Neural Operators | 750 模型分布漂移鲁棒性基准 | 否（鲁棒性退化分级，非物理违例类型化归因）|
| **Lim, Lee, Bang 2026 — Validation-Gated Multi-Agent … Thermal-Hydraulic Surrogates** | validation-gated 多智能体在线治理（Monitor/Diagnosis/Safety-Auditor）| 否（**runtime monitoring**，本文明确排除）**但术语高度重叠（核工业+门控+诊断），必须显式划界** |
| Daniels et al. 2025 — Uncertainty-Aware Diagnostics for PIML | PILE/GP 做模型选择 | 否（纯 UQ，本文排除）|
| Spotorno et al. 2026 — Physical Fidelity → Fault Diagnosis (IEEE Access) | PINN 残差+EVT+Siamese 轴承故障诊断 | 否（PHM 下游诊断）但 RESS 血脉强，可引邻接 |
| **Van Acker et al. 2019 — Validity Frames** | 形式化捕获模型 range-of-validity 用于复用 | 否（设计期复用）**但"domain-validity gating"命名直系祖先，最佳血脉引用** |
| McGreivy & Hakim 2023 — Invariant preservation via error correction | 更新步按构造守恒 | 否（设计期 by-construction）|

**判定**：无任何一条同时满足本文三合一 ——(a) 物理一致性关系作独立**多属性**事后测试套件 + (b) 类型化（regime/precondition）**admissibility 门控** + (c) 违例向 真实模型故障 / 无效属性·测试 / 数值伪影 的**归因**。各家只命中一片。**缺口在精确三合一表述下成立。**

**→ 新硬约束（写稿铁律）**：
1. 缺口主张**必须收紧到 (a)+(b)+(c) 三合一**精确表述，不得写成"几乎无人做诊断/门控"。
2. Related Work **必须显式引用并区分** Lim 2026 / Shikhman 2026 / Daniels 2025 / Spotorno 2026 / Van Acker 2019，否则 RESS 审稿人有据可驳。
3. **Lim 2026 是最近邻竞争**（核工业 validation-gated diagnosis）——必须正面区分：本文是**部署前 oracle-free 属性测试**，Lim 是**在线多智能体治理**。

## 3. 最值得 cite 的 8 条（用途）
1. Kirsch et al. 2025 JVVUQ (10.1115/1.4071802) — credibility 框架锚 + 本文 V&V 证据的 SciML-PCMM 宿主（三部曲优先引此期刊版）。
2. Van Acker et al. 2019 Validity Frames (10.23919/SpringSim.2019.8732858) — "domain-validity gating"命名/方法学先驱。
3. Haugen et al. 2025 (2509.26122) — oracle-free 后验验证（trustworthy AI in numerics），覆盖 neural operator。
4. Eiras et al. 2024 ICML (2305.10157, ∂-CROWN) — 形式化最坏情况残差认证 cluster 代表。
5. Hillebrecht & Unger 2023 TNNLS (10.1109/TNNLS.2023.3335837) — 残差→解误差分解砖块（NSE 算例）。
6. Lim et al. 2026 (Validation-Gated Multi-Agent) — assurance/门控 + **对照**（在线 vs 部署前），核工业对口。
7. Shikhman 2026 (Diagnosing Failure Modes) — "诊断"缺口最近邻，显式划界。
8. Mukherjee et al. 2026 (2603.19165) — 残差→解空间泛化界前沿（标注预印本）。
> 备选：BEACONS（by-construction 形式验证对照）、Spotorno 2026 IEEE Access（PHM 邻接）。

## 4. 警示
- **无 ✗**；核心 10 条全真可定位。
- **元数据必改**：Eiras → ICML 2024（非 Unknown Journal/2023）；Kirsch PCMM → 2025（非 2026）。
- **近重复二选一**：Kirsch Wholistic 会议 (vvuq2025-152225) vs HOLISTIC OSTI 报告 (2172/3028632)。
- **预印本仅作前沿点缀（§8.6）**：Haugen/Mukherjee/Hillebrecht-Stokes/Huseynov；承重引用落已评审来源（Kirsch 期刊 / TNNLS / ICML / IEEE Access）。
