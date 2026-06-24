# 49 — 重构后 deep-research + academic-pipeline 学术成熟度评估

> 日期：2026-06-18  
> 评估对象：`submissions/IST/main.tex`  
> 目标期刊：Elsevier *Information and Software Technology*（IST）regular research paper  
> 方法：deep-research 证据审计 + academic-pipeline Stage 2.5/3 思路 + 外部 OpenAI-compatible LLM 网关五模型 reviewer panel。  
> 输出语言：中文。  

## 0. 诚实边界

本报告是投稿前内部评估，不是 IST 官方评审结果，也不是实际接收概率承诺。外部 LLM panel 为 temperature=0 的单轮自动 reviewer simulation；它可用于暴露风险和量化成熟度，但不能替代人类同行评审。Elsevier 的作者指南还特别说明，期刊审稿人/编辑当前不能在 peer review 和 manuscript evaluation 过程中使用 ChatGPT 等生成式 AI 工具；本报告属于作者侧投稿准备评估，不属于期刊审稿流程。

证据来源包括：

- IST 官方 Guide for Authors：`https://www.sciencedirect.com/journal/information-and-software-technology/publish/guide-for-authors`
- 当前稿件：`submissions/IST/main.tex`
- 当前 panel 原始报告：`research_assets/runs/academic-review-panel-20260618-postrestructure/review_panel_report.json`
- 本地测试与编译输出：`pytest`、`pdflatex+bibtex`、`tools/ist_wordcount.py`
- 既有 deep-research 文献审计：`paper/41_deep_research_academic_pipeline_review.md`
- 既有成熟度评估基线：`paper/47_llm_gateway_academic_maturity_assessment.md`

## 1. 执行结论

**当前稿件已经达到 IST regular paper 的投稿成熟度，最准确的状态判断是：minor-revision-ready，但仍有明确 major-revision 风险。**

量化判断：

| 项目 | 结论 | 证据 |
|---|---:|---|
| 投稿成熟度 | **82/100** | 当前 panel overall 7.83/10；形式检查通过；词数 11,868/15,000；5/5 reviewer 成功 |
| 最可能一审走向 | **Minor revision / Major revision 边界，当前多数为 minor** | 当前 panel：3 minor revision，2 major revision |
| 平均接受概率估计 | **0.686** | `review_panel_report.json` 中 `accept_probability_mean=0.686` |
| 接受概率范围 | **0.45--0.85** | EIC/DA 较保守，Methodology/Perspective 较乐观 |
| IST fit | **强** | panel `scope_match_to_ist=9.0/10`；IST 官方范围包括 software testing、V&V、empirical software engineering |
| 主要短板 | **novelty sharpness、稿件密度、证据外推、D-axis calibration、作者 mutant catalogue** | 五 reviewer 的 concern 汇总 |

与重构前报告相比，当前最重要的变化是：panel 多数 verdict 从 earlier major-revision boundary 转为 **minor_revision majority**，clarity 从此前较弱档明显上升到 **7.4/10**。但这不是“稳接收”信号，因为 EIC 和 Devil's Advocate 仍给出 major_revision。

## 2. 对照 IST 官方要求

IST 官方 Guide for Authors 给出的关键要求和范围如下：

| IST 要求 | 官方依据 | 当前稿件证据 | 判断 |
|---|---|---|---|
| 必须有清晰 software engineering component | IST aims and scope 明确要求投稿应有 software engineering component，并覆盖 software testing 与 verification & validation | 论文主题是 SciML surrogate 的 oracle-free metamorphic testing 与 V&V asset construction | 通过 |
| Research paper 上限 15,000 words | IST Article types: regular research paper max 15,000；references/appendices 计入；figures/tables 各按 200 words | `tools/ist_wordcount.py`: 11,868 counted words, headroom 3,132 | 通过 |
| Structured abstract 必须包括 Context, Objective(s), Method(s), Results, Conclusion | IST Guide: papers without structured abstract will not be handled | `main.tex` lines 42--57 包含 Context/Objectives/Method/Results/Conclusion | 通过 |
| 需声明 generative AI use | Elsevier Guide 要求作者声明 AI 工具使用并承担责任 | `main.tex` 有 `Declaration of generative AI and AI-assisted technologies...` | 通过 |
| 需 data availability | IST Guide 要求 submission 时说明 data availability；研究数据需 deposit/link 或说明不能共享 | `main.tex` 有 `Data availability`，含 Zenodo DOI 与 artifact path | 基本通过，建议提交前确认 DOI 可访问 |
| 可提交 LaTeX editable sources | Guide 要求 editable source files，LaTeX 可接受 | `elsarticle` source + 编译成功 | 通过 |

客观本地验证：

- `rtk .venv/bin/python tools/ist_wordcount.py`  
  结果：`IST-counted total: 11868 ... cap=15000 ... headroom=3132`
- `rtk .venv/bin/python -m pytest tests/test_p0_submission_readiness.py tests/test_stage2p5_submission_readiness.py`  
  结果：`17 passed`
- `pdflatex + bibtex + pdflatex + pdflatex`  
  结果：成功生成 `main.pdf`，44 页；仅有 underfull 警告和 3 条 BibTeX empty-pages warning。

## 3. 外部 LLM Gateway Reviewer Panel

运行命令：

```bash
rtk zsh -lc 'set -a; source .env; set +a; .venv/bin/python tools/run_academic_review_panel.py --outdir research_assets/runs/academic-review-panel-20260618-postrestructure'
```

运行状态：

- reviewer 成功数：5/5
- 网关：OpenAI-compatible gateway
- 模型：`gpt-5.5`、`glm-5.1`、`deepseek-v4-flash`、`qwen3-max`、`kimi-k2.6`
- 每个 reviewer 单轮、temperature=0、JSON-only
- 原始结果保存：`research_assets/runs/academic-review-panel-20260618-postrestructure/review_panel_report.json`

### 3.1 Panel 汇总

| 维度 | 均分 /10 | 解读 |
|---|---:|---|
| novelty_contribution | 7.0 | 达到可发表线，但不是突破式 novelty；更像强 operationalization |
| technical_soundness | 7.6 | 方法整体可靠，operator-floor gate 与 typed verdict 较强 |
| empirical_rigor | 7.8 | 证据纪律好，统计与边界说明较扎实 |
| related_work | 7.6 | 主要 prior 已覆盖，但仍需 sharper differentiation |
| clarity | 7.4 | 重构后明显改善，但 EIC 仍认为稿件 crowded |
| reproducibility | 8.4 | 最强维度之一，claim ledger / MR cards / artifacts 得分高 |
| scope_match_to_ist | 9.0 | 与 IST software V&V 范围高度匹配 |
| **overall** | **7.83** | IST-competitive，revision-likely |

Verdict distribution：

| Verdict | 数量 | Reviewer |
|---|---:|---|
| minor_revision | 3 | MethodologyRigor, DomainExpert, Perspective |
| major_revision | 2 | EIC, DevilsAdvocate |
| accept | 0 | 无 |
| reject | 0 | 无 |

当前多数 verdict 为 **minor_revision**。但由于 EIC 和 Devil's Advocate 均为 major_revision，实际投稿预期仍应按 **minor/major boundary** 管理。

### 3.2 Reviewer 分歧

| Reviewer | Model | Verdict | Accept probability | 关键证据 |
|---|---|---|---:|---|
| EIC | gpt-5.5 | major_revision | 0.68 | fit 强、artifact 强；但认为稿件 crowded，贡献是 known ideas 的 careful integration |
| MethodologyRigor | glm-5.1 | minor_revision | 0.85 | empirical rigor 9/10；但要求压缩术语密度、说明 D-axis 未跨 MR 校准 |
| DomainExpert | deepseek-v4-flash | minor_revision | 0.60 | operator-floor 和 admissibility 强；但 empirical breadth 与 coverage implication 较弱 |
| Perspective | qwen3-max | minor_revision | 0.85 | 软件工程相关性强；但 generalizability、coverage implication、operator-floor generality 有边界 |
| DevilsAdvocate | kimi-k2.6 | major_revision | 0.45 | novelty 仅 5/10、technical 6/10；认为 MR cards/gating 有 repackaging 风险 |

最可信的风险信号不是均分，而是分歧结构：方法论 reviewer 与 perspective reviewer 已认为 minor，但 EIC 仍担心主线拥挤、贡献 sharpness 不足；Devil's Advocate 仍认为 novelty 有 incremental/repackaging 风险。

## 4. Deep-Research 文献与学术水平判断

既有 deep-research 审计 `paper/41_deep_research_academic_pipeline_review.md` 已验证三类 closest prior：

| Prior | 证据状态 | 对当前论文的意义 |
|---|---|---|
| Reichert et al. 2024 HESS | DOI 与记录已确认 | 物理/水文 ML 模型上的 MR 使用，构成 SciML-MT 最近邻之一 |
| Eniser et al. 2022 ISSTA | DOI 与记录已确认 | relaxed MR / tolerance lineage，当前论文需说明 operator-floor gate 的差异 |
| Duque-Torres et al. 2023 SANER | DOI 与记录已确认 | bug-vs-inapplicability separation lineage，当前 typed verdict 需清晰定位 |

deep-research 结论仍成立：当前论文的 novelty 不是“发明 MT”，也不是“发明 SciML consistency checks”，而是：

1. 将 physics-derived MR 从 candidate 转成 **auditable/executable/interpretable V&V asset**；
2. 用 measurement operator 的 intrinsic numerical floor 作为 admissibility gate；
3. 用 typed verdict 将 SUT inconsistency、relation invalidity、OOD application、numerical deferral 分开；
4. 用 claim ledger 和 artifacts 建立可审计证据链。

这属于 IST 可接受的 **configurational / operational novelty**，不是算法突破。学术水平达到 regular paper 的竞争线，但 novelty sharpness 仍是 reviewer 可能卡住的地方。

## 5. 有证据支撑的优势

### 5.1 期刊匹配度强

证据：

- IST 官方 scope 明确包含 software testing 与 verification & validation。
- 当前 panel `scope_match_to_ist=9.0/10`。
- 稿件 RQ0 明确围绕 oracle-free V&V assets，而不是 CFD 模型性能。

判断：这是当前最稳的投稿理由。论文现在已经更像 IST software V&V paper，而不是 SciML/CFD application paper。

### 5.2 复现性和证据纪律强

证据：

- 当前 panel `reproducibility=8.4/10`。
- `main.tex` 有 `Data availability`、AI declaration、CRediT、conflict statement。
- 本地 `pytest` 17/17 passed；LaTeX 完整编译成功。
- Reviewer strengths 多次提到 claim ledger、MR cards、deterministic runtime traces、artifact-to-claim mapping。

判断：这是显著高于普通投稿的强项，建议在 cover letter 中作为投稿亮点，但不要声称“fully reproducible for all external systems”，因为 Threats 已承认旧 runtime / checkpoint barriers。

### 5.3 重构后 clarity 已改善

证据：

- 当前 panel clarity = 7.4/10。
- 旧报告 `paper/47...` 中 clarity 只有 6.4/10。
- 当前结构已改为 Introduction / Related Work / Method / Experimental Design / Results Analysis and Discussion / Threats / Future Work / Conclusion。

判断：重构有效；但 EIC 仍把 crowded manuscript 列为 concern，因此不能把 clarity 视为完全解决。

## 6. 有证据支撑的弱点

### 6.1 Novelty 仍可能被读成 incremental packaging

证据：

- 当前 panel novelty mean = 7.0/10，是最低之一。
- Devil's Advocate novelty = 5/10，认为 validity gating 和 MR cards 有 repackaging existing relaxations / inapplicability reasoning 的风险。
- EIC concern：contribution 是 known MT、constraint、tolerance ideas 的 careful integration，而非 sharply isolated new technique。

判断：投稿前不宜使用过强的 “first” 或 “new theory” 语言。最安全表述是：first evidence-backed operationalization / auditable asset workflow for this SciML-MT setting。

### 6.2 Empirical scope 仍有限

证据：

- DomainExpert concern：primarily one mesh-based surrogate family。
- DevilsAdvocate concern：one dominant architecture-family/dataset with shallow, explicitly disclaimed extensions。
- 稿件自身 Threats to Validity 已承认 broader neural operators、mesh simulators、production CFD solvers、datasets、geometries、training regimes remain outside evidence。

判断：当前证据足以支持 bounded empirical utility，不足以支持 broad generalization 或 real-world reliability。

### 6.3 Coverage implication 仍是风险点，但已降级到可控

证据：

- 当前 panel concerns 中仍出现 “coverage implication weakly supported / qualitative / bounded to injected faults”。
- 当前稿件已将 coverage 写为 `Coverage implication`，且 Table I 中列为 `Impl.` 而非 RQ。
- 旧报告 `paper/47...` 明确指出 validity--coverage duality 是最大风险；当前重构已删除该中心化表述。

判断：风险已经从“可能被认为中心命题过度拔高”降为“bounded implication 是否足够有用”。这是实质进步。

### 6.4 D-axis 未跨 MR classes 校准

证据：

- MethodologyRigor concern：domain-violation axis D is operationalized per-relation and not calibrated across MR classes。
- Perspective concern：verdict interpretation relies on per-relation metrics not cross-calibrated。
- Future Work 已将 calibration/generalization 作为后续工作。

判断：这是一个真实方法学限制。当前可接受的处理方式是继续明确 “per-relation, not cross-relation calibrated”；若再改稿，最好给出 future calibration protocol 的更具体步骤。

### 6.5 Seeded-fault catalogue 不能承担 real-world defect-rate claim

证据：

- MethodologyRigor concern：author-implemented gross corruptions。
- DomainExpert concern：10 mutants, one SUT family。
- DevilsAdvocate concern：small 10 author mutants, confirms expected structural insensitivities。
- 稿件 Threats 已写明 seeded-fault catalogue 不估计 real-world defect prevalence/effectiveness。

判断：当前表述方向正确。若后续还要加强，可在 Results 的 first mention 再加一句：catalogue is a stress test of interpretation, not a defect-rate benchmark。

## 7. 投稿成熟度 Rubric

| 类别 | 分数 /100 | 证据 |
|---|---:|---|
| IST formal compliance | 94 | 词数 11,868/15,000；structured abstract；声明齐备；编译成功；17 tests passed |
| Journal scope fit | 90 | IST official scope + panel scope_match 9.0/10 |
| Novelty/contribution | 72 | panel novelty 7.0/10；DA novelty 5/10 拉低，说明 novelty sharpness 仍需管理 |
| Technical soundness | 76 | panel technical 7.6/10；operator-floor/admissibility 强，但 D-axis/generalization 有边界 |
| Empirical rigor | 78 | panel rigor 7.8/10；证据纪律强，但外推边界窄 |
| Related work | 76 | panel related_work 7.6/10；closest prior 已处理，但仍可强化 coverage / physical-consistency cluster |
| Clarity/accessibility | 74 | panel clarity 7.4/10；较旧评估改善，但 EIC 仍担心 crowded |
| Reproducibility | 84 | panel reproducibility 8.4/10；artifacts/ledger 强 |
| Claim discipline | 86 | RQ5 降级；coverage 降级；Threats/Future Work 明确边界 |
| **Overall maturity** | **82** | 综合 formal compliance、panel、deep-research、local verification |

## 8. Editorial Decision Simulation

**模拟 EIC decision：Minor Revision leaning Major Revision for some reviewers.**

理由：

1. 无 desk-reject 型形式问题：IST scope、结构化摘要、字数、声明、数据可用性、LaTeX 均满足要求。
2. 无 reviewer panel reject：5 个 reviewer 中 0 reject，0 accept，3 minor，2 major。
3. 仍有 major revision 风险：EIC 和 Devil's Advocate 均要求 major_revision，且 concerns 是高层次问题，不是纯语言问题。
4. 当前稿件的学术贡献成立，但贡献性质是 operationalization / evidence-backed workflow，而不是新算法或普适理论。

因此，最诚实的投稿预期是：**可以投；如果遇到保守 reviewer，会 major revision；如果 reviewer 接受 bounded operational contribution，则 minor revision。**

## 9. 建议的投稿前最低修正

这些不是阻塞项，但能降低 major-revision 概率：

1. **再压缩 EIC concern 中的 crowded feeling。** 优先压缩 Results 中 secondary/external-scope material 的叙述密度，而不是再加新实验。
2. **进一步 sharpen novelty statement。** 明确说 novelty 是 measurement-floor admissibility + typed executable MR assets + evidence ledger 的组合式工程贡献。
3. **在 Related Work 中加强 coverage / MR fault-detection effectiveness cluster。** 既有 deep-research 曾指出 Kanewala coverage cluster 是 coverage implication 的相关邻域。
4. **给 D-axis calibration 一个具体 future protocol。** 即便不做实验，也可以说明未来如何校准 cross-MR domain distance。
5. **在 cover letter 中避免夸大。** 不写 “general SciML reliability” 或 “universal validity-coverage law”；写 “bounded, auditable V&V workflow for SciML surrogate testing”。

## 10. 底线判断

这篇论文目前 **学术水平达到 IST regular paper 可投稿线以上**。它最强的地方是：选题匹配 IST、方法边界清楚、证据链可审计、复现性强、重构后研究问题和章节结构已经统一。它最弱的地方是：贡献 novelty 不是爆发式而是 operational/configurational，empirical generalization 有边界，D-axis 仍未跨 MR 校准，fault catalogue 不能承载真实缺陷率结论。

结论必须实事求是地写成：

> 当前稿件已经具备投稿成熟度；最可能获得 revision 而非 reject；多数自动 reviewer 认为 minor revision，但 EIC/Devil's Advocate 风险仍指向 major revision。建议按 minor-revision-ready 稿件提交，同时在 cover letter 和正文中继续降低泛化与 coverage 相关修辞。

