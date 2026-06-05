# 本文立场拷问报告（deep-research 第三轮）

> 日期：2026-06-04
> 对象：`paper/06_paper_plan_v2.md`、`paper/04_ist_outline_evidence_map.md`、`paper/manuscript.md`
> 方法：deep-research review mode + academic-paper-reviewer devil's advocate + research-evidence-gate。外部证据优先使用 IST 官方指南、ScienceDirect 专刊页、arXiv/PMLR/期刊原文、NVIDIA/DeepMind 一手页面。
> 总裁决：**IST regular track 的大方向仍然合理，但当前主立场必须再降一档。最安全的论文不是 "NOETHER 证明/机械推导了物理 MR"，而是 "rubric-gated, NOETHER-informed, executable oracle-free testing framework for mesh-based neural surrogates"。**

---

## 0. 一句话审判

当前 v2.1 最危险的不是期刊选择，而是**立场主语过强**：

> 过强立场：本文以 NOETHER 算子代数机械推导出 mesh-based GNN 圆柱绕流的 MR，并通过三 SUT 证明其有效。

这句话会同时被四类审稿人攻击：软件测试审稿人会问证据链是否可复现；流体审稿人会问边界条件与离散算子是否支持这些关系；ML 审稿人会说等变性/对称性评估已有大量近作；方法论审稿人会质疑三 SUT 是否真有外部效度。

安全立场应改成：

> 安全立场：本文提出一套 validity-rubric-first 的物理 MR 筛选与执行框架，用 NOETHER 作为候选关系组织与生成的指导结构，并把保留下来的关系转化为可复现的 oracle-free MR assets；经验部分只在三个 MeshGraphNets-family 实现/配置内评估，不外推到所有 neural fluid surrogates。

---

## 1. 拷问 A：IST fit 成立，但必须写成 SE/V&V 论文

IST 官方 scope 明确要求论文对 software engineering 或 software development practice 有清晰贡献，覆盖 software testing、verification & validation、empirical studies；research paper 上限 15,000 words，必须有 Context / Objectives / Methods / Results / Conclusion 五段结构化摘要。IST MT 专刊已经关闭，deadline 为 2025-04-13，但专刊页面列出的 2025-2026 MT 文章说明 IST 社区确实接收 MT 方向。

裁决：**IST 目标成立，但引言第一屏必须是 testing/V&V problem，不是 CFD/SciML problem。**

安全动作：

- Abstract 的 Objective 句写 "operationalize physically valid MRs as executable oracle-free tests"，不要写 "improve fluid surrogate modeling"。
- Contribution C4 必须落到 testing evidence：MR execution, seeded faults/mutations, baseline protocol, reproducibility assets。
- Results 未生成前，不能写任何 "effective", "outperforms", "detects more", "generalizes"。

---

## 2. 拷问 B：NOETHER 依赖是最大叙事杠杆，也是最大软肋

NOETHER arXiv 摘要本身承认：下游从 operator algebra 到 MetaPattern set 是 mechanical and provable，但**上游 algebra curation 是 empirical hypothesis with explicit scope precondition**。这对本文非常关键：`A_cyl` 的算子枚举、边界条件兼容子群、离散 divergence、Re-St 相似、cross-SUT comparability，全部属于上游 curation。

裁决：**不能把 "NOETHER 下游性质" 偷渡成 "本文所有物理 MR 都机械可证"。**

安全表述：

| 危险写法 | 安全写法 |
|---|---|
| "mechanically and provably derives cylinder-flow MRs" | "uses NOETHER to organize and generate candidate relation structures; each retained MR is then screened by a domain-validity rubric" |
| "NOETHER proves physical validity" | "NOETHER supplies a candidate-generation grammar; physical validity is established by boundary-condition and measurement checks" |
| "Hypothesis 1 is validated" | "the cylinder-flow case probes the scope of Hypothesis 1; results may support, qualify, or expose a constraint-block extension" |

写作动作：C2 的标题可保留 "NOETHER-guided"，但摘要、引言和贡献列表中应避免 "proved derivation" 这种强词。建议统一为 **NOETHER-informed candidate generation + rubric-gated operationalization**。

---

## 3. 拷问 C：已有工作已经占掉"物理 MR 测 ML 模型"大半地盘

Reichert et al. (HESS 2024) 已经把 metamorphic testing 用在 machine-learning hydrologic models，并强调普通 calibration/validation 之外还要检验 modified inputs 下的预期响应。Brandstetter et al. (ICML 2022) 已经基于 PDE 的 Lie point symmetries 推导数据变换以增强 neural PDE solvers。2026 年两篇 neural fluid surrogate/equivariance 预印本进一步逼近本文：一篇直接研究 Navier-Stokes 学习映射的 coordinate-frame generalization/equivariance error，另一篇系统评估 neural CFD surrogates 中等变架构何时有益、何时有害。

裁决：**不能宣称"首次把物理关系用于 neural surrogate 测试"或"首次测试流体代理模型对称性"。**

可守阵地只剩这些：

1. **MR validity rubric**：区分 physically valid / executable but invalid / OOD brittle relation。
2. **oracle-free verdict assets**：不是只报告 equivariance error 或物理诊断量，而是形成 source/follow-up transform、metric、threshold、assertion、verdict、artifact trail。
3. **非对称关系覆盖**：order、limit、qualitative dynamics、method comparison、constraint-style relations，而不是只做 symmetry/equivariance。
4. **failure localization**：如果有 seeded fault ground truth，能从 MR tree 指向 representation / physics / temporal / adapter layer。

写作动作：Related Work 必须正面承认 "symmetry and physical diagnostics are not new"；本文的新意只能放在 "validity-gated testing workflow + executable evidence package"。

---

## 4. 拷问 D：三 SUT 不是广义外部效度，只是同族实现压力测试

PhysicsNeMo 文档明确其 vortex shedding MGN 是 DeepMind vortex shedding example 的 PyTorch re-implementation，并依赖 DeepMind dataset；MeshGraphNets 官方页面列出 CylinderFlow 是同一个 COMSOL ground-truth simulator、1885 average nodes、600 timesteps 的 benchmark。也就是说，SUT-1/SUT-2/SUT-3 很可能共享数据谱系、任务谱系和 MGN 架构谱系。

裁决：**"three SUT empirical evaluation" 可以保留；"generalizes across neural fluid surrogates" 不成立。**

更尖锐的问题：cross-SUT agreement 只有在以下条件同时满足时才是 MR：

- same physical case or explicitly transformed equivalent case;
- comparable nondimensional variables and units;
- comparable mesh fields and output channels;
- comparable rollout horizon and boundary conditions;
- threshold accounts for training/checkpoint differences.

否则，cross-SUT agreement 只能是 **cross-implementation triangulation / consistency analysis**，不能叫 metamorphic relation。

安全动作：

- C4 改写为 "three MeshGraphNets-family implementations/configurations"。
- Threats to Validity 明说 external validity 仍局限在 cylinder-flow/MGN family。
- `method-comparison block` 的 MR status 设为 conditional：comparability protocol 通过后才升为 retained MR。

---

## 5. 拷问 E：物理 MR 仍有 5 个容易翻车的边界条件

1. **Mirror-y equivariance**：只在几何、入流、上下边界、node type 和输出向量变换都对称时成立。若 cylinder 位置、domain 裁剪、边界标签或数据增强策略破坏镜像，MR 必须降级。
2. **Rigid translation**：若只平移坐标而不平移 cylinder/domain/BC，物理语义不保持；若整体平移但边界坐标编码进入模型，测试到的是表示偏置而非纯物理关系。
3. **Re-St similarity**：不是任意 scaling 都有效。需要 nondimensionalization、Reynolds regime、Strouhal extraction window、vortex-shedding stationarity、训练分布覆盖共同成立。否则它是 OOD robustness test，不是 physics-preserving MR。
4. **Divergence boundedness**：是连续性/质量约束，不是 Noether law；且需要定义离散 divergence operator、mesh area/volume weights、边界节点处理、COMSOL/数据噪声阈值。
5. **Rollout prefix consistency**：主要是 determinism/semigroup sanity gate，不应包装成物理 MR 的核心发现。

裁决：**MR cards 必须先于 Results 写完；没有 MR card 的关系不能进入贡献表。**

每张 MR card 至少包含：

- physical basis;
- transformation preconditions;
- BC compatibility;
- output mapping;
- metric;
- threshold derivation;
- expected fault classes;
- exclusion/OOD rule;
- source/follow-up artifact schema.

---

## 6. 拷问 F：baseline 设计可能被判不公平

MR-Scout 一类方法从 existing test cases / OSS 项目中合成 MRs；SimiMR/语义相似类方法更偏程序文本/静态语义；LLM baseline 的风险是 prompt variability 和 correctness hallucination。若把这些方法直接丢到数值流体代理模型上，然后说 "它们找不到物理 MR"，审稿人可能判为 strawman baseline。

裁决：**B2/B3 可以保留，但不能用来证明外部方法"弱"；只能证明 domain-validity rubric 的必要性。**

安全动作：

- B2 改名为 "generic MR-generation scope contrast"，目标是展示其适用边界，而非直接性能击败。
- B3 LLM baseline 必须保留 prompt logs、model/version、temperature、candidate list、rubric decision，不得只报告 cherry-picked examples。
- Baseline comparison 指标应分成两类：candidate validity rate 与 executable fault-detection evidence。前者可以先做，后者必须等 MR assets 和 fault set 完成。

---

## 7. 拷问 G：C3 失效定位现在还是 taxonomy，未必是 localization

当前 C3 写法有风险：把 MR tree 映射到层次分类模型，并不自动等于 failure localization。真正的 localization 至少需要：

- seeded fault / mutant 的 ground-truth layer；
- 预注册的 MR-to-layer inference rule；
- 多 MR 冲突时的 tie-breaking rule；
- top-1/top-k 或 layer-level agreement metric；
- blind 或至少 fixed-before-run 的评估流程。

裁决：**C3 在实验前只能称为 localization protocol，不能称为 validated localization model。**

安全动作：在 manuscript 中把 C3 写成 "a hierarchical localization protocol and claim ledger"，Results 出来前不写 "localizes failures"。

---

## 8. Claim ledger：本文立场必须这样过闸

| Claim | 当前风险 | Evidence-gate 状态 | 安全写法 |
|---|---|---|---|
| IST 是首选期刊 | 已有官方 scope 与 MT 专刊证据 | supported | "IST regular research paper track is the primary target" |
| 本文解决 oracle problem | 容易过宽 | qualified | "addresses per-sample oracle absence through MR-based relational checks" |
| NOETHER 机械推导圆柱绕流 MR | 上游 curation 未证 | insufficient | "NOETHER-informed candidate generation, rubric-gated retention" |
| 首次测试 neural fluid surrogate 的对称性 | 被 2026 等变评估和 LPSDA 击穿 | blocked | "differs from symmetry-only evaluation by producing executable MR verdict assets" |
| 三 SUT 证明泛化 | 同族实现/同数据谱系 | blocked | "three MeshGraphNets-family implementations/configurations" |
| cross-SUT agreement 是 MR | comparability 未建立 | insufficient | "conditional method-comparison MR after comparability protocol passes" |
| C3 已能失效定位 | 无 seeded fault evidence | insufficient | "predeclared hierarchical localization protocol" |
| B2/B3 baseline 弱于本文 | 无公平协议/结果 | blocked | "baselines test scope contrast and validity-screening need" |
| divergence MR 是物理守恒测试 | 需离散算子和阈值 | qualified | "continuity-constraint check with explicit discrete-divergence operator and threshold" |
| Re-St MR 有效 | OOD 与 regime 风险 | insufficient | "candidate similarity MR, retained only under nondimensional and regime-compatibility checks" |

---

## 9. 立即修改建议（写作前 P0）

1. 把所有高层定位从 **NOETHER-guided** 进一步降级为 **NOETHER-informed + rubric-gated**，特别是 abstract Objective/Method 和 Introduction 末尾贡献段。
2. 在 `04_ist_outline_evidence_map.md` 的 Claim Ledger 增加 "blocked: first neural-fluid-symmetry-test claim, broad generalization, baseline superiority, validated localization"。
3. 在实验设计中把 "three SUT" 改成 "three MeshGraphNets-family implementations/configurations"，并把 external validity 风险前置。
4. 给 `method-comparison block` 增加 comparability protocol；协议未通过前，不叫 MR。
5. 在 MR card 模板里加入 BC compatibility、OOD rule、discrete operator、threshold provenance 四列。
6. B2 改成 scope contrast baseline；B3 增加 fixed prompt/model/version/prompt-log 约束。
7. C3 在 Results 前只写 protocol，不写 demonstrated localization。

---

## 10. 本轮主要来源

- IST Guide for Authors: https://www.sciencedirect.com/journal/information-and-software-technology/publish/guide-for-authors
- IST MT special issue: https://www.sciencedirect.com/special-issue/104J787KPKV
- Reichert et al. 2024, HESS: https://hess.copernicus.org/articles/28/2505/2024/hess-28-2505-2024.html
- NOETHER arXiv:2605.17390: https://arxiv.org/abs/2605.17390
- Brandstetter et al. 2022, ICML/PMLR LPSDA: https://proceedings.mlr.press/v162/brandstetter22a.html
- McConkey et al. 2026, arXiv:2602.04695: https://arxiv.org/abs/2602.04695
- Rygiel et al. 2026, arXiv:2605.18816 metadata: https://research.utwente.nl/en/publications/symmetry-in-the-wild-the-role-of-equivariance-in-neural-fluid-sur/
- NVIDIA PhysicsNeMo vortex shedding MGN: https://docs.nvidia.com/physicsnemo/latest/physicsnemo/examples/cfd/vortex_shedding_mgn/README.html
- MeshGraphNets project page: https://sites.google.com/view/meshgraphnets/home
- JFM 2024 Navier-Stokes Hamiltonian formulation / Millikan boundary: https://www.cambridge.org/core/product/identifier/S0022112024002295/type/journal_article
- Time irreversibility in turbulence / viscous term: https://arxiv.org/abs/1801.00944
- MR-Scout project: https://mr-scout.github.io/
