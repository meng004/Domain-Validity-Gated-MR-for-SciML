# Domain-Validity-Gated-MR-for-SciML





现有工作有物理约束、有场景测试、有残差/UQ、有 MT 基础，但缺少一套面向 SciML 的“领域有效性优先”的 MR 识别与执行流程：每条 MR 都要说明它从哪里来、在什么物理和数值条件下成立、如何生成 follow-up case、如何设阈值、如何给 relation-level verdict，以及 violation 如何解释为 SUT 的适用边界。



换句话说，缺口不是“有没有 MR”，而是：

- MR 的**有效性边界**没有被系统记录；
- MR 从候选到可执行测试的**流程**不够结构化；
- violation 结果常被当成指标，没有变成**关系级判定证据**；
- accuracy、residual、UQ、equivariance error 和 MR 之间的关系没有被清楚区分；
- LLM/自动方法最多能生成候选，不能替代领域有效性判断，这一点值得明确。

**值不值得填**
值得，但条件很明确。

值得填的理由：

1. **软件测试问题真实存在。** SciML 的逐点 oracle 昂贵或不可得，MT 是合理工具。
2. **现有最近邻还没吃掉核心贡献。** Yu/Qi 更像物理场景测试和物理一致性评价；本文可以主打 MR card、rubric、verdict、证据链。
3. **IST/JSS/STVR 会关心这个问题。** 只要写成 V&V 方法论文，而不是 CFD 精度论文，期刊适配是合理的。
4. **即使实验不惊艳，也能成立。** 只要能说明 MR 如何界定 OOD transformation 下的适用边界，贡献不完全依赖“检出 accuracy 检不出的缺陷”。

不值得填的情况：

- 如果最后只是列几个物理 MR，没有 rubric、MR card、执行证据；
- 如果只报告 violation rate，但不能解释 violation 是 MR 条件不满足、数值容差、OOD stress，还是 SUT 问题；
- 如果三 SUT 只是跑 accuracy，没有 relation-level verdict；
- 如果 Qi/Yu 经过全文核验后已经包含“每条关系的适用边界 + violation-rate operating map + executable MR schema”，那本文新意会被压缩。

**我的建议**
继续做。这个缺口**够真、够窄、够可守**。但题目和贡献要降级为：

> A domain-validity-aware workflow for identifying and executing metamorphic relations in SciML OOD validation.

不要写成：

> A new metamorphic testing method that outperforms accuracy-based validation.

下一步最关键不是继续扩文献，而是做三件硬事：

1. 写 5-8 张高质量 MR card。
2. 给每张 MR 写清楚适用条件、排除条件、阈值来源。
3. 做一个小规模实验，证明 relation-level verdict 能给出 accuracy 之外的边界解释。

最近邻参考：Yu 等流速场 MR 工作已很接近；Gopakumar 等提供 residual/UQ 侧的对照；Mandrioli 等说明“设计假设转 MR”在高水平 SE 期刊中是可接受问题设置。
来源：[Yu 2025 题录](https://eurekamag.com/research/105/650/105650686.php)、[Gopakumar ICML/PMLR 2025](https://proceedings.mlr.press/v267/gopakumar25a.html)、[![img](https://arxiv.org/favicon.ico)Mandrioli arXiv/TSE](https://arxiv.org/abs/2412.03330)。



**总定位**
方法章的核心对象不是模型精度，而是：

> 一个 MR 候选从“看起来有物理道理”，到“可执行、可判定、可解释”的全过程。

所以 Method 需要围绕四件事组织：

1. 研究对象：三个 MeshGraphNets-family cylinder-flow SUT。
2. 干预方法：NOETHER-informed candidate generation + domain-validity rubric。
3. 对照方法：专家 MR、通用 MR 生成、LLM 候选、accuracy-only。
4. 功效判断：MR 是否有效、可执行、能检出/解释问题、能界定 OOD 适用边界。

**建议方法章结构**
可以这样写：

1. **Study Design**
   说明这是一个 empirical software engineering / V&V study。
   单元包括：MR candidate、retained MR、source case、follow-up case、SUT execution、seeded fault、transformation family。
2. **Subject Systems**
   三个 SUT 只写成同族实现/配置压力测试，不写泛化到所有 neural fluid surrogate。
   每个 SUT 记录：commit、checkpoint、dataset、输入输出字段、rollout horizon、mesh format、随机种子、运行环境。
3. **MR Identification Workflow**
   步骤：
   - 从方程、物理约束、边界条件、图表示、实现假设提取候选；
   - 用 NOETHER 组织候选结构；
   - 用 rubric 筛；
   - 形成 MR card；
   - 转成 executable test。
4. **Domain-Validity Rubric**
   每条 MR 至少判六项：
   - physical basis；
   - transformation preconditions；
   - boundary-condition compatibility；
   - output mapping；
   - metric and tolerance；
   - exclusion / OOD rule。
5. **Baselines**
   baseline 不能写成“我要打败它们”，要写成“不同证据来源的对照”。

| Baseline                 | 用途             | 避免的坑                               |
| ------------------------ | ---------------- | -------------------------------------- |
| Expert MR                | 人工领域知识对照 | 不把专家 MR 当金标准                   |
| Generic MR generation    | 范围对照         | 不说它弱，只说它不专为 SciML 设计      |
| LLM candidate generation | 候选质量对照     | LLM 只生成候选，不裁决有效性           |
| Accuracy-only            | 传统评价对照     | 不说 MR 更好，只说回答不同问题         |
| Residual/UQ metrics      | SciML 可靠性对照 | 它们是诊断量，不是 source/follow-up MR |

1. **Efficacy Parameters**
   这里建议明确分主指标和辅指标。

主指标：

| 指标                      | 含义                                   | 建议报告                      |
| ------------------------- | -------------------------------------- | ----------------------------- |
| Candidate retention rate  | 候选 MR 中有多少通过 rubric            | 比例 + 被拒原因分类           |
| Executable MR rate        | 通过 rubric 后有多少能实际运行         | 比例 + blocker                |
| MR violation rate         | OOD transformation 下关系违反比例      | Wilson CI 或 bootstrap CI     |
| Fault detection rate      | seeded fault / mutant 被 MR 检出的比例 | 按 MR 类别和 fault layer 报告 |
| Boundary characterization | 哪些 transformation region 违反率升高  | 分桶图、热力图、阈值区间      |

辅指标：

- MR construction cost：人工时间、LLM 候选数、筛选时间；
- inter-rater agreement：rubric 人工判断一致性，建议 Cohen’s kappa 或 Krippendorff’s alpha；
- flakiness rate：同一 MR 重复运行 verdict 是否稳定；
- localization agreement：MR tree 推断层级是否命中 seeded fault layer；
- complementarity with accuracy：accuracy 正常但 MR violation 高、或 accuracy 异常但 MR 正常的案例数。

1. **Statistical Plan**
   不要过度复杂，但要有预设。

建议：

- violation rate 用置信区间，不只报均值；
- MR 与 baseline 比较用 paired design；
- 分类比例比较可用 McNemar / Fisher exact；
- 连续误差或 violation magnitude 用 paired bootstrap；
- 多 MR、多 SUT、多 transformation 时做 Holm-Bonferroni 或 FDR；
- 小样本时不强调显著性，强调 effect size 和置信区间。

1. **Ethical and Integrity Considerations**
   伦理判断不是医学伦理，而是研究诚信和 AI 使用边界。

必须写：

- 不涉及人类受试者、隐私数据或敏感个人信息；
- SUT、dataset、checkpoint、脚本和运行日志尽量可复现；
- LLM 只用于候选生成和材料整理，不作为 MR 有效性裁判；
- 不把未验证候选写成有效 MR；
- 不把 OOD violation 直接等同于程序错误；
- 失败实验、skip、blocked case 都保留在 ledger；
- 若使用第三方代码和模型，遵守 license。

**DA 拷问**
最容易被审稿人打的点：

1. baseline 不公平：通用 MR 工具不适合 SciML，你却拿它当靶子。
   解决：称为 scope contrast，不称为击败对象。
2. 功效指标太像 accuracy。
   解决：把 primary outcome 放在 relation-level verdict、violation rate、domain boundary，而不是 rollout error。
3. MR validity 太主观。
   解决：rubric 双人评审，一致性统计，冲突裁决规则。
4. violation 解释过度。
   解决：verdict 分类加入 out-of-relation-domain、numerical tolerance issue、SUT inconsistency、inconclusive。
5. 伦理声明太空。
   解决：写研究诚信、AI 使用边界、artifact reproducibility，而不是泛泛说“无伦理风险”。

一句话：方法章要像一个**审计协议**，不是像一个算法说明。它要让审稿人相信：你不只是提出 MR，而是在控制 MR 的来源、适用边界、判定证据和失败解释。

