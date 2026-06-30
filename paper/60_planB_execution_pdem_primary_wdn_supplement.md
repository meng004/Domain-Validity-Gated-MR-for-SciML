# 60 · 方案 B 执行方案 —— PINN-PDEM 主 + Fink WDN 漏损 GNN 补

> 日期：2026-06-30 · 用户拍板：方案 B；主=PINN-PDEM 失效概率；补=Fink 组开源 WDN 漏损 GNN；本机已有数据。
> 依据 `paper/59` 评估 + 本机资产勘察 + Fink 项目定位。

## 本机资产勘察结论（实事求是）

| 需求 | 本机状态 |
|---|---|
| PINN 训练/MR 工具链（PDEM 主线）| **✓ 已有**：本仓 `tools/train_pinn_diffusion2d.py`、`train_pinn_burgers2d.py`、`run_pinn_k6_roster.py`、`run_pinn_diffusion_mr_extension.py`、`run_seeded_fault_detection_pinn.py` + 姊妹库 PKE PINN(`p10_pinn_hnn`)。PDEM 数据由求解 GDEE **生成**，非下载。|
| WDN / L-Town / BattLeDIM / EPANET 数据 | **✗ 未找到**（搜遍 ~/Codes、OneDrive、Downloads、Documents、Desktop、中文关键词均空）。|

→ "本机已有数据"对 **PDEM 主线成立**（PINN 设施在，数据可生成）；对 **WDN 补充不成立**（需 Fink 开源基准，待用户指明本地路径或授权获取）。

## 主线：PINN-PDEM 失效概率（RESS 锚问题 = Das2023 ress.2023.109849 等簇）

**问题**：用 PINN 解广义密度演化方程(GDEE) `∂p/∂t + ẋ(Θ,t)·∂p/∂x = 0`（Li & Chen 概率密度演化法），得状态量 PDF → 由超越极限状态算失效概率 P_f。
**标准基准（本地生成，无需外部数据）**：典型随机激励下的非线性 SDOF 振子（如 Duffing / Bouc-Wen），是 PDEM 文献的 canonical demo；Θ=随机参数，物理解析可得参照 PDF。
**MR 适用性理论嫁接（本文核心，原样迁移）**：
- **守恒 MR（概率守恒 ∫p dx = 1）**——本文守恒 MR 族最干净的可采实例；admissibility 的 numerical-decidability 地板从「离散散度地板」变为「**求积分地板**」：∫p 的数值求积误差须低于守恒容差，gate 才 admit。
- **正性/单调 MR**：p ≥ 0；初值/边界条件 MR。
**typed verdict + 可靠性量**：判一个概率守恒/正性违例是 **(a) 真模型故障**（PINN 的 PDF 不可信 → P_f 不可信）/ **(b) 数值伪影**（配点/求积地板）/ **(c) inadmissible**。**可靠性量 = 失效概率 P_f 的可信度**：gate 价值 = 在 P_f 上标注「此估计是否经物理一致性可判定」。
**故障注入**：复用本仓 `run_seeded_fault_detection_pinn.py` 框架，注入 (i) 物理参数错误(真故障，应使 P_f 偏) vs (ii) 数值容差故障(配点不足/求积粗，伪 P_f 偏)，看 gate 能否分诊 → FAR/MDR on P_f-trust 决策。
**基线对照**：accuracy-only(PDE 残差阈值) vs validity-gated。预期机制(待实测)：求积地板上的伪守恒违例会让残差监控误报 P_f 不可信，gate 正确归数值伪影 → 降 FAR。

## 补充：Fink WDN 漏损 GNN（RESS = Zhang & Fink ress.2025.111494）

**实验对象**：EPFL-IMOS AIGNN（arXiv 2408.02797）+ **L-Town/BattLeDIM** 基准（782 节点/905 管，EPANET 合成，漏损检测事实标准）。代码组织 github.com/EPFL-IMOS/。
**嫁接点**：管网**节点质量守恒**(Σ流入=Σ流出) = 本文守恒 MR；GNN 代理预测压力/流量。
**可靠性量**：漏损检测/定位（RESS scope 明列 fault detection & diagnosis）。
**gate 价值**：判节点守恒违例是**真漏损**(物理故障) vs 传感器噪声/数值伪影 → 降漏损检测**误警率 FAR**（管网运维核心痛点：误报漏损=误派工）。
**数据状态（已解决 2026-06-30，用户授权获取）**：Fink 团队 AIGNN **专属码未公开**（EPFL-IMOS 组织/作者账号/搜索均无）→ 用开放栈、引 Fink 作对话锚。已 clone 到 `~/Codes/wdn-external/`（peer 外部只读，不入本仓 git）：
- `BattLeDIM/`（KIOS 官方，72M）：`Dataset Generator/L-TOWN_v2_Real.inp` + `_Model.inp`（L-Town EPANET 网络）、`Scoring Algorithm/competition_leakages`（**漏损金标准 = FAR/MDR ground truth**）。
- `physics_informed_gnns_for_wds/`（AAAI 官方码，inaamashraf，45M）：完整 WDN-GNN（`models/`、`train_test.py`、`dataset_generator.py`）+ **`trained_models/l_town` 预训练模型（免重训，直接推理）** + `networks/l_town`；物理信息 GNN=尊重质量守恒，**本文守恒 MR 正好审计其输出**；支持 hanoi/fossolo/pescara/l_town/zhijiang。
- 锚 RESS：引 Zhang & Fink (ress.2025.111494) 作 WDN-漏损可靠性对话锚；实验用开放 PI-GNN-WDS + L-Town（合法、可复现）。

## 整体结构（最终论文）

- 主 RESS-fit 案例：PINN-PDEM 概率守恒 → P_f 可信度（失效概率，RESS 原生量）。
- 补充：WDN 节点守恒 → 漏损 FAR（fault diagnosis，RESS 原生量）。
- supporting breadth（已有，证明方法不依赖单一 SUT）：现有 CFD(MGN cylinder/airfoil) + PINN(Burgers/heat) + FNO + 姊妹库跨程序——降级为附录广度，不主张可靠性率。
- 统一贡献叙事：**MR 适用性(admissibility)理论 + numerical-decidability 地板 + typed verdict**，把物理一致性违例归因为「可靠性量不可信的真故障 / 数值伪影 / 不可采」，作用在 RESS 原生可靠性量(P_f / 漏损)上。

## 待澄清（启动前唯一 blocker）

WDN 补充的 L-Town 数据：**(A)** 本机某路径已有（请指明）；**(B)** 授权我从开放基准(battledim/EPFL-IMOS)获取；**(C)** 暂只做 PDEM 主线、WDN 后补。
PDEM 主线**无 blocker**，可即启（第 0 步：选定 SDOF 基准 + 跑通本仓 PINN 解 GDEE 的最小原型）。
