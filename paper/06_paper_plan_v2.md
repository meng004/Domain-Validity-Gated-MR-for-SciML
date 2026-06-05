# 论文加强版方案 v2.1（面向 IST）

> 日期：2026-06-04（v2.1：理论基座替换为本组自有理论）
> 依据：`05_ist_selling_point_interrogation.md` 拷问结论 + NOETHER 投稿包（TOSEM 在审）+ 实验对象可行性核实。
> **v2.1 核心变更**：MR 识别的两套理论不再借用外部文献（Zhou MRP / Lin 层次 MR），改为**本组自有理论**——
> ① 元模式理论 = **NOETHER**（Li, Yang, Liu, Yan, "NOETHER: A Constructive Framework for Metamorphic Pattern Discovery from Operator Algebras," arXiv:2605.17390，TOSEM 在审）；
> ② 层次分类拓扑结构理论 = **阳小华, 闫仕宇, 刘杰, 李萌. 科学计算程序蜕变关系层次分类模型. 计算机科学, 2020. DOI 10.11896/jsjkx.200200015**（PDF 已存 `theory/`）。
> 这一替换把本文从"借两套理论的应用研究"升格为"**自有研究纲领的第四域实例化 + 理论检验**"。

---

## 1. 一句话定位（v2.1）

**本文将 mesh-based 神经流体代理模型构造为 NOETHER-informed 的程序诱导算子代数 A_cyl，经 8-block 分解与 CONSTRUCT-MP 形成候选 MetaPattern 集，再由 validity rubric 与边界条件兼容性筛选保留关系，按层次分类拓扑组织为可执行 MR 树与失效定位协议，在三个 MeshGraphNets-family 实现/配置上进行 oracle-free 评估——同时探测 NOETHER 的 Hypothesis 1 在物理代理模型域的适用边界。**

相对 v1/v2 的提升：
- "MR 靠直觉/领域经验" → **候选生成有 NOETHER 的结构化约束**；但 cylinder-flow 上游算子枚举、block 分配、边界条件兼容性与阈值解释仍是需要 rubric 审核的 domain curation，不能把下游定理偷换成物理有效性证明。
- "理论是借的" → 两套理论均为本组自有，论文构成**研究纲领的连续性证据**（NOETHER 原文明言 "engineering payoff awaits empirical follow-up work"——本文就是那个 follow-up）。
- "单 case 应用" → 本文兼具**理论回馈**：连续性约束 MR 是否可落在 symmetry block 经 Translate 的像内，或构成 constraint 类候选第九 block 的 empirical witness——两个结果都直接回应 NOETHER 留下的 ninth-block 接口，同时避开"用 Noether 定理导出散度约束"的物理错误。

---

## 2. 方法论核心：两套自有理论驱动的结构化 MR 识别

### 2.1 理论一：NOETHER 元模式（候选关系的代数骨架）

**出处：** Li, Yang, Liu, Yan, arXiv:2605.17390（TOSEM 在审，2026-05-20 投稿）。
**结构：** 上游 = 8-block 分解（symmetry, order, self-adjoint, time-reversal, limit, qualitative-dynamics, method-comparison, relational equivalence），作为显式 empirical hypothesis；下游 = CONSTRUCT-MP 算法，Translate 算子下代数闭包（Thm 1）+ 有限生成集下多项式时间可判定（Thm 2）。已实例化三个域：Boltzmann 反应堆物理、等变 ML、关系查询优化器。

**本文用法：把圆柱绕流 GNN 代理构造为第四个域 A_cyl。** 枚举 A_cyl 的算子并做 8-block 分配：

| 圆柱绕流算子/不变量 | NOETHER block | 实例化 MR |
|---|---|---|
| 节点置换、face 重编码 | Symmetry（置换子群）/ Relational equivalence | 置换等变、face 顺序不变 |
| y 镜像、刚体平移 | Symmetry（群作用 G_geom） | 镜像等变、平移不变 |
| 几何/速度缩放、Re-St 相似 | Symmetry（缩放群 + 无量纲约束） | 尺度相似、Re-St 不变 |
| 速度微扰、网格连续性 | Limit（L*） | 扰动稳定、连续性 |
| 自回归演化算子（半群性质） | Qualitative-dynamics（D*）；**time-reversal 显式排除**（粘性破坏 T 对称，rubric 过滤示例） | rollout 前缀一致、确定性 |
| 跨实现对照（3 个 MGN 实现） | Method-comparison（E_cmp） | 跨实现一致 MR（直接支撑 3-SUT 设计） |
| **质量守恒（散度=连续性约束）** | **开放：是否落在 symmetry block 经 Translate 的像内，或候选第九 block（constraint 类）** | divergence 有界 MR |

最后一行是**本文对 NOETHER 的理论回馈点**（详见 §2.3）。注意：NOETHER 的等变 ML 域已处理 SO(3)×Sn 等变分类器，本文把它推进到**回归型、自回归、非结构网格**的物理代理模型——算子代数显著更丰富（时间演化半群 + 无量纲相似 + 守恒），不是同域复述。

### 2.2 理论二：蜕变关系层次分类模型（组织、定位与覆盖）

**出处：** 阳小华, 闫仕宇, 刘杰, 李萌. 科学计算程序蜕变关系层次分类模型. 计算机科学, 2020. DOI 10.11896/jsjkx.200200015（英文题录：YANG Xiao-hua et al., "Hierarchical Classification Model for Metamorphic Relations of Scientific Computing Programs"）。

**理论内容（已核实原文）：** 按科学计算程序研制过程"物理现象→物理建模→计算建模→程序编码"，将 MR 分为三层——**物理模型蜕变关系**（物理模型解析解内在的输入输出模式，如共轭/齐次等性质导出的 MR1/MR2）、**计算模型蜕变关系**（离散化数值方法性质，如多网格收敛阶 MR3/MR4）、**代码模型蜕变关系**（程序实现层）——并给出三层间的层次结构与发现方法应用前景。

**本文用法：** A_cyl 经 CONSTRUCT-MP 产出的 MR 按此三层模型挂载——对 GNN 代理模型，"计算模型"层自然对应**图表示/消息传递离散结构**：

```
物理模型 MR 层：守恒(divergence)、对称(镜像/平移)、Re-St 相似   ← N-S 方程性质
计算模型 MR 层：节点置换、face 顺序、网格加密收敛、扰动稳定     ← 图离散表示性质
代码模型 MR 层：确定性、rollout 前缀一致、跨实现一致(3 SUT)     ← 实现层性质
```

提供两项 NOETHER 单独不具备的能力：**失效定位**（某层 MR 违反可归因到对应研制阶段——物理学错了、离散表示错了、还是实现错了；这正是 RQ3"表示层 vs 物理层失效"的理论化）与**覆盖论证**（对三层各有 MR 覆盖，而非"列了几个 MR"）。两套理论各管一段：NOETHER 管"从哪来、推导是否封闭"，层次分类模型管"放在哪层、失效归因到哪个研制阶段"——互补关系在论文中明示。**理论增量点**：原文面向传统科学计算程序，本文把"计算建模"层重新诠释为神经网络的图表示/归纳偏置层，是该模型向 ML 代理模型的首次延拓。

### 2.3 理论回馈：连续性约束 MR 对 Hypothesis 1 的域外检验

⚠ **物理表述已按 07 拷问修正**：div u = 0 是不可压缩流的**质量守恒/连续性约束**（压力为其 Lagrange 乘子），**不是** Noether 守恒律——粘性 N-S 无经典变分结构（Millikan 1929 定理），Noether 定理不适用；理想流体中 relabeling 对称经 Noether 给出的是 Kelvin 环量定理而非质量守恒。论文必须以此为由**显式说明不走 Noether 路线**（化攻击点为专业性），对称 MR 改由 **N-S 方程的 Lie 点对称群**（Bytev 1972; Lloyd 1981; Olver）奠基。

修正后的双向检验依然成立且更实：

- **若** divergence 约束 MR 可表述为 symmetry block 不变量经 Translate 的像，扩大 Thm 1 已验证范围；
- **若不可**（预期如此——它是约束而非对称像；Translate 的单 block、一阶 π-模板表达力不足），则得到 **constraint 类候选第九 block** 的干净 empirical witness。

**无论哪个结果都是贡献**——且物理修正后更可能落在"第九 block witness"一侧，理论回馈更实。同时显式排除 time-reversal MR（粘性不可逆，Re≈47–200 涡脱落区间显著）——这一排除本身是 validity rubric 起作用的最佳论文内示例。

### 2.4 结构化识别流程（方法主线）

```
A_cyl 算子枚举（物理/数值/表示先验）
  → 8-block 分配                       [NOETHER 上游；不可分配算子=理论信号]
  → CONSTRUCT-MP 推导 MetaPattern 集   [机械、可证明：Thm 1/Thm 2]
  → 层次分类拓扑挂载                    [jsjkx 理论：组织+失效定位+覆盖]
  → validity rubric 判物理有效性        [v1 头号卖点保留]
  → 实例化为 case/runner/parser/metric/threshold/assertion
```

---

## 3. 近 5 年 3 篇最接近论文的横向对比与本文立场

（P1/P2/P3 维持 v2 选择，"本文"列按 v2.1 更新）

| 维度 | P1 Hiremath'21（海洋模型） | P2 Reichert HESS'24（水文 ML） | P3 MR-Scout TOSEM'24 | **本文** |
|---|---|---|---|---|
| 被测对象 | 传统有限差分代码 | 集总 ML 水文模型 | 通用 OSS 程序 | **mesh-based GNN 流体代理 ×3 实现** |
| MR 来源 | 物理对称（限仿射搜索） | 定性专家期待 | 既有测试挖掘 | **算子代数 8-block + CONSTRUCT-MP 机械推导** |
| 推导性质 | 黑盒搜索，无封闭性保证 | 人工假设 | 自动但依赖现成测试 | **可证明封闭（Thm 1）、多项式可判定（Thm 2）** |
| 关系类型 | 仿射变换 | 定性单调 | 句法/代码层 | **守恒+相似+对称+演化+方法对照，定量** |
| 失效定位 | 无 | 无 | 无 | **层次分类拓扑向上归因** |
| 理论回馈 | 无 | 无 | 无 | **Hypothesis 1 域外检验（ninth-block witness）** |

**一句话立场：** P1 有物理但无可执行 verdict 资产，P2 有 ML 对象但 MR 多为定性假设，P3 结构化但产不出物理语义；本文以 NOETHER-informed 算子代数提供候选关系组织方式，以 validity rubric 决定物理有效性，以层次分类拓扑提供失效定位协议，并把对象收窄到 MeshGraphNets-family cylinder-flow 代理模型的可复现实证——这一"候选生成 + 有效性筛选 + 可执行证据"结构是本文可守的 IST 立场。

> 自引注意：IST 官方为 single anonymized review，作者身份对审稿人可见；引用 NOETHER 可用 arXiv:2605.17390，但正文仍建议第三人称表述（"the NOETHER framework [X]"），避免把贡献写成内部项目汇报。若未来转投双匿名渠道，再按匿名规则重写。

---

## 4. 实验设计（≥3 SUT / ≥3 baseline / ≥1000 LOC，维持 v2 并小幅升级）

### 4.1 三个被测系统（已核实）

| SUT | 仓库 | 框架 | 数据/checkpoint | 角色 |
|---|---|---|---|---|
| SUT-1 echowve MGN | github.com/echowve/meshGraphNets_pytorch | PyTorch+PyG | cylinder_flow，自训 | 主案例 |
| SUT-2 NVIDIA PhysicsNeMo MGN | github.com/NVIDIA/physicsnemo（vortex_shedding_mgn） | PyTorch | 含 NGC 预训练 checkpoint | 跨实现 + method-comparison block 实例化 |
| SUT-3 DeepMind MGN（TF1） | github.com/google-deepmind/deepmind-research/meshgraphnets | TF1 | cylinder_flow + airfoil | 跨框架 + 跨几何外部效度 |

v2.1 新增联动：三 SUT 不只是外部效度样本，**它们本身实例化 method-comparison block 的跨实现 MR**——实验设计与理论框架自洽。

### 4.2 三类 baseline

1. **B1 人工经验 MR**（复现 P2 式专家路线）；
2. **B2 通用自动 MR 识别**（MR-Scout / Kanewala 分类器；预期对物理语义 MR 产出为零，阴性结果即证据）；
3. **B3 LLM 生成 MR**（GPT-4 提示生成——v2.1 升级：NOETHER S3 已有 set_L_llm.py + prompt_log 可直接复用协议，且 arXiv 2503.22141 提供其 correctness 缺陷的文献预期）；
4. **B4 纯精度评估**（rollout 误差；展示"低误差但违反物理 MR"反例）。

评估配 mutation/seeded-fault（可复用 NOETHER S3 的 DeepCrime pilot 协议）与违反率统计检验。

### 4.3 代码规模（≥1000 LOC）

| 模块 | 预估 LOC | 说明 |
|---|---|---|
| A_cyl 算子代数定义 + 8-block 分配 | ~150 | 算子枚举、block 分配表、不可分配算子记录 |
| CONSTRUCT-MP 适配层 | ~150 | 复用 NOETHER S1 参考实现，适配 mesh 输入 |
| MR 实例化（6 类变换+输出关系） | ~350 | 置换/镜像/平移/尺度/Re-St/守恒 |
| 层次拓扑 + 失效定位引擎 | ~180 | MR 树、向上归因、覆盖统计 |
| runner/parser/metric/threshold | ~250 | 统一指标、阈值分层、verdict |
| 故障注入 + 统计检验 | ~150 | mutation 算子、显著性检验 |
| 三 SUT 适配器 | ~200 | PyG/NVIDIA/TF1 |
| **合计** | **~1430** | 含与 NOETHER mr_interface/model_interface 约定对接 |

---

## 5. 升级后的贡献（v2.1，按 IST 稳健表述重排）

- **C1 Validity rubric（头号贡献）**：提出物理 MR 有效性的可操作判定准则，将物理依据、语义保持、可度量性、阈值可解释性与失效可归因性连接起来，避免把"可执行变换"误当作"有效 MR"。
- **C2 NOETHER-informed executable MR framework**：把 NOETHER 算子代数框架条件性实例化到 mesh-based 神经物理代理模型，通过 8-block 分配 + CONSTRUCT-MP 组织候选 MetaPattern，再经 rubric 筛选后将 SciML 诊断量提升为带阈值/verdict 的 oracle-free 蜕变断言。
- **C3 层次分类拓扑的失效定位协议**：把 jsjkx 层次分类拓扑理论与 NOETHER-informed 产出对接，形成 MR 树、向上归因规则与覆盖论证；是否能形成 validated localization model 取决于 seeded-fault layer evidence。
- **C4 三实现/配置四 baseline 实证与复现资产**：在三个 MeshGraphNets-family 实现/配置上评估框架，包含人工 MR、generic scope-contrast MR baseline、LLM 生成 MR、纯精度评估四类 baseline，配故障注入、统计检验和 ~1430 LOC MetBench 复现包。

---

## 6. 必引与相关工作分层

- **理论基座（自引，第三人称）**：NOETHER arXiv:2605.17390；阳小华等, 科学计算程序蜕变关系层次分类模型, 计算机科学 2020, 10.11896/jsjkx.200200015。注意：两文作者高度重叠（阳小华/刘杰/李萌均在 NOETHER 作者列），自引措辞务必第三人称。
- **横向对比**：Hiremath'21（arXiv 2103.09782）、Reichert HESS'24、MR-Scout TOSEM'24。
- **相关工作（v2 的理论基座降级至此）**：Zhou et al. TSE'20（MRP——NOETHER 原文已论证差异，照搬其论证）、Segura et al. TSE'18（MROP）、Lin/Niu SE4Science'18 + CiSE'20（层次 MR——须与 jsjkx 理论明确区分，说明后者的拓扑结构增量）。
- **框架来源**：CheckList ACL'20、DeepTest ICSE'18、Xie et al.。
- **缺口背书 + 反 LLM**：TOSEM 2025 综述（10.1145/3708521）、arXiv 2503.22141。

---

## 7. 待确认决策点（v2.1）

1. ~~jsjkx.200200015 题录~~ ✅ 已解决：PDF 已入 `theory/`，§2.2 已按原文三层模型重写（卷期页码请按 CNKI 终版再核一次）。
2. **第三个 SUT**：维持 DeepMind TF1（外部效度最强但环境老旧，cylinder_flow 在新栈有已知 issue #321）还是改用 PhysicsNeMo 第二几何配置？建议优先前者。
3. **投稿通道**：IST MT 专刊已关闭（Submission Deadline: 2025-04-13），当前按 IST 常规 research paper 通道准备；专刊只作为社区适配和相关工作证据。
4. **与 NOETHER 的发表时序**：本文若先于 NOETHER 录用，引用只能挂 arXiv——可接受；但若 NOETHER 被要求拆分/大改 8-block 表述，本文 §2.1 须同步，建议两稿变更联动管理（CHANGELOG 互链）。

---

## 8. 风险与边界（v2.1 新增项）

- **理论依赖风险**：本文方法有效性部分依赖 NOETHER 的 Hypothesis 1 在 A_cyl 上成立；若多数算子不可分配，需如 NOETHER §2557 行指引如实报告为 block 扩展候选——这本身是合法结果，但会削弱"机械推导"叙事，写作时以 §2.3 的双向设计兜底。
- **v2.2 立场降级**：NOETHER 只能作为 candidate-generation / organization framework；物理有效性由 rubric、BC compatibility、离散算子和阈值证据决定。三 SUT 只能支持 MeshGraphNets-family cylinder-flow 范围内的 cross-implementation stress test，不能写成 neural fluid surrogates 的广义外部效度。
- **自引集中风险**：两套理论均自引，审稿人可能质疑独立性。对策：横向对比三篇外部论文 + B2/B3 外部 baseline + 开放复现包，证据链不依赖自家声明。
- 其余（环境老旧、阈值解释、OOD 归因）同 v2。

## 9. 来源

- NOETHER：arXiv https://arxiv.org/abs/2605.17390 ；Zenodo 10.5281/zenodo.20250634（投稿包内核实）
- 层次分类模型：阳小华等, 计算机科学 2020, https://doi.org/10.11896/jsjkx.200200015（PDF：`theory/阳小华 et al. - 2020 - 科学计算程序蜕变关系层次分类模型.pdf`）
- P1：https://arxiv.org/abs/2103.09782 ；P2：https://hess.copernicus.org/articles/28/2505/2024/ ；P3：https://dl.acm.org/doi/10.1145/3656340
- TOSEM'25 综述：https://dl.acm.org/doi/10.1145/3708521 ；ChatGPT-MR：https://arxiv.org/abs/2503.22141
- SUT：https://github.com/echowve/meshGraphNets_pytorch ；https://github.com/NVIDIA/physicsnemo/tree/main/examples/cfd/vortex_shedding_mgn ；https://github.com/google-deepmind/deepmind-research/tree/master/meshgraphnets
