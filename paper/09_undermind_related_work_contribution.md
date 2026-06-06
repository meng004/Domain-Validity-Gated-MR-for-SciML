# Undermind 调研后的 Related Work 与 Contribution 准备稿

> 日期：2026-06-05  
> 输入材料：`theory/undermind/undermind-sciml-metamorphic-testing-report.pdf`  
> 用途：为 `paper/manuscript.md` 的 Related Work、Introduction contribution 段和文献对比表做准备。  
> 状态：写作工作稿。文献题录、DOI 和最终引用格式仍需在正式投稿前逐条核验。

## 1. 调研结论先行

Undermind 报告给出的总体判断可以作为本文 related work 的骨架：

1. 直接贴近本文的工作很少。最接近的是面向物理场预测智能模型的流体代理模型蜕变测试工作，尤其是 Qi 等和 Yu 等关于物理场预测、流速场预测、Reynolds 数和 Strouhal 数关系的研究。
2. 其它文献不是直接竞争者，而是提供拼图块：科学软件蜕变测试、仿真模型验证、CPS 设计假设 MR、海洋模型 MR 自动发现、PINN/神经 PDE 的残差认证和不确定性量化、混合 ML-CFD 求解器中的残差阈值切换。
3. 目前尚未看到一个完整框架同时做到：从方程和物理约束识别多类可执行 MR；用物理变换生成 follow-up cases；统计 relation-level violation；并为每条 MR 显式记录适用边界、边界条件、离散格式和数值阈值。

这支持本文的安全定位：

> 本文不是提出更准的圆柱绕流预测模型，而是提出一套面向科学机器学习程序的、领域有效性约束下的蜕变关系识别与执行框架，用关系违反情况帮助判断被测程序在特定分布外变换下的可信边界。

## 2. Related Work 建议结构

### 2.1 Metamorphic Testing and the Oracle Problem

这一节只交代地基，不要写太长。

要点：

- 蜕变测试用多次执行之间应满足的关系缓解 test oracle problem。
- 科学计算、仿真模型和机器学习模型都常遇到精确 oracle 不可得的问题。
- 本文继承这个基本思想，但问题更窄：面向科学机器学习程序，尤其是 mesh-based cylinder-flow neural surrogates。

可写句：

> Metamorphic testing addresses the oracle problem by checking necessary relations among multiple executions rather than requiring an exact expected output for each test case. This idea is particularly relevant to scientific and simulation software, where a trusted output for every possible input may require expensive high-fidelity computation or may be unavailable.

需要引用：

- Segura et al., A Survey on Metamorphic Testing, TSE, 2016.
- Chen et al., Testing and validating machine learning classifiers by metamorphic testing, JSS, 2011.
- Kanewala and Chen, Metamorphic Testing: A Simple Yet Effective Approach for Testing Scientific Software, CiSE, 2019.
- Olsen and Raunak, Increasing Validity of Simulation Models Through Metamorphic Testing, IEEE Transactions on Reliability, 2019.

### 2.2 MR Identification for Scientific and Simulation Software

这一节回答：已有工作如何找 MR。

要点：

- 科学软件 MR 识别通常依赖领域知识、单调性、守恒性、近似不变性和仿真行为模式。
- 海洋模型、仿真模型和 CPS 的工作说明，MR 可以来自系统假设、物理模型或设计假设。
- 这些工作支撑“MR 识别需要领域知识”的说法，但没有解决 SciML 中的物理适用边界、数值容差和分布外 transformation 问题。

需要引用：

- Hiremath et al., Towards Automated Metamorphic Test Identification for Ocean System Models, MET, 2021.
- Mandrioli et al., Testing CPS with Design Assumptions-Based Metamorphic Relations and Genetic Programming, TSE, 2025.
- Lin et al., Exploratory Metamorphic Testing for Scientific Software, CiSE, 2018.
- Sun et al., Identifying metamorphic relations: A data mutation directed approach, Software: Practice and Experience, 2023.

可写句：

> Prior work has shown that MRs can be elicited from domain assumptions, simulation behavior, or design constraints. However, these approaches usually stop at identifying or generating candidate relations. They do not explicitly require each retained relation to carry a domain-of-validity record that states the governing assumptions, boundary-condition compatibility, discretization requirements, and numerical tolerance rationale.

### 2.3 Metamorphic Testing for Machine Learning and AI Systems

这一节不要泛泛综述全部 ML testing。只保留与本文相关的两点：

- ML 系统也有 oracle problem。
- 图像、分类器、自动驾驶等 MT 不能直接迁移到 SciML，因为 SciML 的 transformation 必须受方程和物理约束限制。

需要引用：

- Chen et al., JSS, 2011.
- DeepRoad 等 DNN/自动驾驶 MT 工作可作为“ML MT 已存在”的背景，但不要展开。
- LLM-assisted MR generation 只作为候选生成和整理工具，不作为 MR 有效性裁判。

安全写法：

> Although metamorphic testing has been applied to machine-learning systems, many transformations in conventional ML testing are defined over input semantics such as image appearance, classification labels, or data perturbations. In scientific machine learning, a transformation is only meaningful when the corresponding physical relation is valid under the governing equations, boundary conditions, numerical representation, and measurement tolerance.

### 2.4 Physics-Based MT for Scientific ML Surrogates

这是最关键的一节，要正面承认最近邻工作，不能弱化。

Undermind 报告认为最接近本文的是两篇：

- Qi et al., Research on Multi-scenario Collaborative Testing Methods for Intelligent Algorithms in Physical Field Prediction.
- Yu et al., Research on Mutation Testing Strategies for Intelligent Models Predicting Fluid Velocity Fields.

它们已经做了：

- 面向物理场或流速场预测智能模型；
- 用物理约束或经验规律构造 MR；
- 用 benchmark、extreme、perturbation、cross-domain 等场景测试模型；
- 使用 Reynolds 数、Strouhal 数等无量纲关系来判断物理一致性和外推能力。

本文必须承认：

> 物理约束驱动的 SciML 蜕变测试不是本文从零开创。

本文仍可主张的差异：

- 不只依赖 Re/St 这类少数无量纲全局关系，还把 MR 来源扩展到表示等变、几何对称、连续性约束、边界条件、数值稳定、时间一致性和跨实现一致性候选。
- 重点不是“多场景测试”，而是“候选 MR -> 领域有效性 rubric -> 可执行 MR card -> relation-level verdict -> violation statistics -> 可信边界解释”。
- 显式记录每条 MR 的适用条件，区分 MR 本身条件不满足、分布外 stress、数值容差问题和 SUT 真实失效。

可写句：

> The closest studies to ours are recent physics-based metamorphic testing approaches for physical-field or fluid-velocity prediction models. They demonstrate that dimensionless physical quantities such as Reynolds and Strouhal numbers can guide follow-up scenarios and assess physical consistency. Our work builds on this direction but shifts the emphasis from scenario-level physical consistency checks to a validity-gated MR workflow in which each retained relation is represented as an executable test asset with explicit preconditions, output mapping, tolerance rationale, exclusion rules, and relation-level verdicts.

### 2.5 SciML V&V, Residuals, UQ, and Failure Modes

这一节负责把本文和 SciML 可靠性文献接上。

要点：

- PINN、神经算子和 neural PDE surrogate 文献已经关注残差、不确定性、误差界、分布外泛化和 failure modes。
- Gopakumar 等的 calibrated physics-informed UQ 使用 PDE residual 作为 nonconformity score，并通过 conformal prediction 给出覆盖保证。
- 这些工作给本文的阈值解释和 violation 统计提供方法启发，但它们不是 MT：没有 source/follow-up transformation，也没有 MR card 或 relation-level verdict。

可写句：

> Residual-based UQ and certification methods provide important tools for calibrating physically meaningful thresholds. Yet their primary object is uncertainty or error certification, whereas our object is an executable relation: a source case, a physically constrained follow-up transformation, an output relation, and a verdict rule.

需要引用：

- Raissi et al., Physics-informed neural networks, JCP, 2019.
- Karniadakis et al., Physics-informed machine learning, Nature Reviews Physics, 2021.
- Li et al., Fourier Neural Operator for Parametric PDEs, ICLR, 2021.
- Gopakumar et al., Calibrated Physics-Informed Uncertainty Quantification, ICML/PMLR, 2025.
- PINN failure mode 文献，如 Krishnapriyan et al., NeurIPS, 2021.

### 2.6 Hybrid ML-Solver Trust Regions

这一节可短写，用来说明“可信边界”不是凭空来的。

Undermind 报告提到 XRePIT 和 DeepONet-FE coupling：

- 这些方法用残差或误差指标决定何时相信 ML、何时切回传统求解器。
- 它们体现了 operational trust region，但不是离线 MR 测试，也没有多关系 violation rate map。

可写句：

> Hybrid solver frameworks show that residual thresholds can be used operationally to decide when a learned component is trusted. Our work pursues a complementary offline testing direction: before deployment, physically derived transformations are used to estimate where relation violations occur and what boundary conditions or regimes are associated with them.

## 3. 三篇最近邻论文对比

### 3.1 推荐作为三篇最近邻

建议论文正文中重点对比三篇：

| 编号 | 论文 | 为什么选它 |
|---|---|---|
| P1 | Qi et al., Multi-scenario collaborative testing for intelligent algorithms in physical field prediction | 最直接：物理场预测 + 场景化 + 物理约束 MR |
| P2 | Yu et al., Mutation testing strategies for intelligent models predicting fluid velocity fields | 最直接：流速场预测 + Re/St + disturbance/cross-domain transformation |
| P3 | Gopakumar et al., Calibrated Physics-Informed Uncertainty Quantification | 最重要补充：PDE residual + violation/statistical calibration + SciML reliability |

Mandrioli et al. TSE 2025 应作为强方法论对照放在 related work 中，但不建议放进“三篇最近邻”主表。原因是它的 SE 方法质量高，但 SUT 是 CPS 控制，不是 SciML/PDE surrogate；它更适合支撑“设计假设可以转成 MR”和“domain assumption matters”。

### 3.2 对比表

| 维度 | P1 Qi et al. | P2 Yu et al. | P3 Gopakumar et al. | 本文 |
|---|---|---|---|---|
| 被测对象 | 物理场预测智能模型 | 流速场预测智能模型 | neural PDE surrogate | MeshGraphNets-family cylinder-flow surrogate |
| 主要目标 | 多场景协同测试 | 物理约束驱动的变异/蜕变测试 | 物理残差驱动 UQ | 领域有效性约束下的 MR 识别与执行 |
| 关系来源 | 多参数物理相关性、经验统计规律 | Reynolds 数守恒、Strouhal 数相关 | PDE residual | 方程、边界条件、几何/表示变换、连续性约束、无量纲关系、实现一致性候选 |
| transformation | benchmark、extreme、perturbation、cross-domain | disturbance、cross-domain | 非主要对象 | source/follow-up OOD transformations with MR cards |
| verdict | 物理一致性、外推能力评价 | Re/St 关系违反和物理一致性 | conformal coverage / residual nonconformity | relation-level pass/fail/skip/OOD verdict |
| domain validity | 场景层面隐含 | Re/St 适用范围隐含 | PDE 假设隐含 | 每条 MR 显式记录 preconditions、BC、离散算子、阈值来源、排除规则 |
| operating boundary | 多场景画像，未形成正式边界图 | 有外推评价，但边界映射不充分 | 预测集/覆盖保证，不是 MR 边界 | 计划用 violation statistics 描述 SUT 在特定 OOD transformation 下的适用边界 |
| 本文应承认 | 已经有 physics-based MT for fluid/field predictors | 已经有 Re/St-based MT for fluid velocity prediction | 已经有 residual-based calibrated reliability | 本文不声称首创物理约束测试，只主张系统化、可执行化和关系级判定 |

### 3.3 最近邻对比的英文段落草稿

> Recent work has started to connect metamorphic testing with learned physical-field predictors. Qi et al. propose a multi-scenario testing framework for intelligent physical-field prediction models, and Yu et al. construct metamorphic tests for fluid-velocity predictors using Reynolds-number conservation and Strouhal-number correlations. These studies are closest to ours because they use physical knowledge to define follow-up scenarios and assess extrapolation or physical consistency. Our work builds on this line but addresses a different methodological gap: how candidate relations are screened for domain validity, represented as executable MR assets, and reported as relation-level verdicts under explicitly stated boundary conditions, discretization assumptions, and tolerance rules.

> A complementary line of work studies reliability and uncertainty for neural PDE surrogates. For example, calibrated physics-informed UQ uses PDE residuals as nonconformity scores in a conformal prediction framework. Such methods are valuable for threshold calibration and residual-based reliability assessment, but they do not formulate validation as metamorphic testing: there is no source/follow-up transformation, no MR card, and no relation-level verdict. This distinction is central to our paper: residuals, conservation errors, and equivariance errors are not merely diagnostic metrics; when paired with physically valid transformations and explicit preconditions, they become executable oracle-free relations.

## 4. Contribution 建议写法

### 4.1 中文安全版

本文贡献建议写成四条：

1. **提出面向科学机器学习的 MR 领域有效性 rubric。** 该 rubric 用物理依据、边界条件兼容性、语义保持、可测量输出关系、阈值来源和失效可解释性筛选候选 MR，避免把“能变换输入”误当成“关系一定成立”。
2. **提出 NOETHER-informed、rubric-gated 的可执行 MR 工作流。** 该流程用 NOETHER 组织候选关系结构，但不把 NOETHER 当作物理有效性的证明；候选关系只有通过领域有效性检查后，才被转成 source case、follow-up case、metric、threshold 和 verdict。
3. **提出 relation-level verdict 和 violation statistics 记录方式。** 每条 MR 的执行结果不仅记录 pass/fail，还记录 skip、out-of-relation-domain、数值容差问题和可能的 SUT inconsistency，从而支持对分布外 transformation 下适用边界的解释。
4. **在三个 MeshGraphNets-family 圆柱绕流实现/配置上进行经验评估并沉淀可复现资产。** 该贡献必须等实验完成后再写成结果型贡献；当前只能写成 planned empirical evaluation。

### 4.2 英文投稿版

当前阶段建议在 introduction 中这样写：

> This paper makes four contributions. First, we propose a domain-validity rubric for screening candidate MRs in scientific machine learning. The rubric checks whether a relation has a clear physical basis, compatible boundary conditions, a semantics-preserving transformation, a measurable output relation, an interpretable tolerance, and a diagnosable failure mode. Second, we present a NOETHER-informed and rubric-gated workflow that organizes candidate relation structures and converts only retained relations into executable oracle-free MR assets. Third, we define relation-level verdicts and violation-statistics records for OOD transformations, distinguishing model inconsistency from out-of-relation-domain cases and numerical-tolerance effects. Fourth, we plan an empirical evaluation on three MeshGraphNets-family cylinder-flow implementations/configurations, with reproducible MR cards, transformation code, metrics, thresholds, and execution artifacts.

实验完成前，第四条要用 `plan` / `we evaluate in a planned study` 这类谨慎表达；正式投稿前改成结果型表达。

## 5. Claim Ledger

| Claim | 当前状态 | 证据来源 | 安全写法 |
|---|---|---|---|
| 直接相关文献很少 | qualified | Undermind report, free-tier search | "The report found only a small number of directly aligned studies; this should be verified by manual database search." |
| Qi/Yu 是最近邻 | qualified | Undermind report；Yu DOI 已可查；Qi 题录仍需核验 | "The closest identified studies are recent physics-based MT works for physical-field/fluid-velocity predictors." |
| 本文首次做 physics-based MT for fluid ML | blocked | Qi/Yu 已覆盖部分 | 不写首次；写本文提供更系统的 validity-gated executable workflow |
| 本文比 accuracy 更好 | blocked | 尚无实验证据，且问题维度不同 | "MR verdicts complement accuracy by checking relation preservation under transformations." |
| Gopakumar residual UQ 可直接当 MR | insufficient | 其目标是 UQ，不是 MT | "Residual-based UQ informs threshold calibration but does not itself provide source/follow-up MR tests." |
| MR violation 能划定 SUT 适用边界 | qualified until experiment | 需要 violation statistics 和采样协议 | "We use violation statistics to characterize the tested boundary under specified transformations." |
| LLM 可自动识别有效 MR | blocked | 规划已降级 | "LLMs can assist candidate generation and evidence organization; validity is decided by rules, execution, and review." |

## 6. Manuscript 修改建议

建议下一步改 `paper/manuscript.md` 时做四件事：

1. 在 `2.2 Metamorphic Testing and the Oracle Problem` 下先写 MT 基础，再接科学软件和仿真模型。
2. 新增 `2.3 Physics-Based Metamorphic Testing for Learned Scientific Simulators`，正面对比 Qi/Yu。
3. 新增 `2.4 Residual-Based Reliability and UQ for SciML`，把 Gopakumar、PINN/FNO 和 failure modes 放进去。
4. 把 contribution 改成 `domain-validity rubric`、`NOETHER-informed candidate organization`、`executable MR asset/verdict`、`three-MGN-family empirical evaluation` 四条，不再写“自动识别有效 MR”。

## 7. 待核验文献清单

正式进入 manuscript 前，应逐条核验：

- Qi et al., Research on Multi-scenario Collaborative Testing Methods for Intelligent Algorithms in Physical Field Prediction. Undermind 标为 2025 conference paper，但网页检索出现 2026 题录痕迹，需核验会议、页码和 DOI。
- Yu et al., Research on Mutation Testing Strategies for Intelligent Models Predicting Fluid Velocity Fields. Web 检索显示 IAECST 2025, pp. 178-182, DOI 10.1109/IAECST68792.2025.11415187。
- Gopakumar et al., Calibrated Physics-Informed Uncertainty Quantification. PMLR/ICML 2025, PMLR 267:20103-20141。
- Mandrioli et al., Testing CPS with Design Assumptions-Based Metamorphic Relations and Genetic Programming. TSE 2025, DOI 10.1109/TSE.2025.3563121 或相关 IEEE 终版信息需核验。
- Undermind 报告列出的 Pasupuleti 两篇认证类论文目标期刊质量和同行评审状态较弱，建议只作为边缘材料，不作为主对比论文。

