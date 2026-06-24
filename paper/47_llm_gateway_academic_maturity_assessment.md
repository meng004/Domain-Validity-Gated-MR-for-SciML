# 47 — LLM 网关多 Reviewer 学术成熟度评估

> 日期：2026-06-18  
> 评估对象：`submissions/IST/main.tex`  
> 目标期刊：Elsevier *Information and Software Technology*（IST）regular research paper  
> 方法：deep-research 式期刊匹配与证据审计 + academic-pipeline Stage 2.5/3 入口 + 通过 `.env` 中 OpenAI-compatible 网关运行五模型 reviewer panel。

## 执行结论

这篇稿件 **具备 IST 投稿竞争力，但还不能稳妥判断为 minor revision 成熟度**。最符合证据的判断是：

- **投稿成熟度：78/100。**
- **学术水平：IST regular paper 竞争性稿件；从选题、格式、复现性看，明显高于 desk-reject 风险线。**
- **最可能的一审结果：major revision 是众数结果，不是 reject。**
- **多模型 reviewer panel 对“正常修改周期后被 IST 接收”的平均概率估计：0.62，范围 0.40--0.85。**
- **主要风险：中心命题 “validity--coverage duality” 可能被审稿人认为拔高过度，甚至接近 tautology；除非全文持续把它表述为有边界的经验性原则，而不是普适理论。**

这不是对 IST 实际接收结果的预测承诺，而是基于当前稿件、IST 官方作者指南、evidence package、claim ledger、回归测试和 2026-06-18 多模型 reviewer 运行结果得到的投稿前成熟度评估。

## 证据基础

### IST 官方要求核对

来源：ScienceDirect 官方 *Information and Software Technology* Guide for Authors，访问日期 2026-06-18。

- IST 范围覆盖 software engineering methods、software testing、V&V，以及 empirical software engineering studies。
- Research paper 字数上限为 15,000。IST 计数包括 references 和 appendices，且每个 figure/table 按 200 words 计入。
- Structured abstract 为强制要求，五个标题为 Context、Objectives、Methods、Results、Conclusion。
- 投稿需提供 editable source files；LaTeX 可接受。
- Research data 需要 deposit/link；若不能共享，需要 data availability statement 说明。
- Software 和 datasets 在适用时应作为研究对象引用。
- 如使用 generative AI 辅助写作，需声明。

本地核对结果：

- `tools/ist_wordcount.py`：**12,470 IST-counted words**，距离 15,000 上限仍有 **2,530 words** 余量。
- `tests/test_p0_submission_readiness.py` + `tests/test_stage2p5_submission_readiness.py`：**17/17 passed**。
- `submissions/IST/main.tex` 包含 structured abstract headings、3 个 figures、8 个 tables、CRediT、competing-interest、generative-AI 和 data-availability sections。
- 既有投稿审计 `paper/43_journal_submission_audit.md` 显示 compile/audit clean，无投稿阻塞项。

### 证据完整性核对

主要本地证据来源：

- `research_assets/experiments/evidence-package.md`
- `research_assets/experiments/claim-ledger.yml`
- `submissions/IST/main.tex`
- `research_assets/runs/academic-review-panel-20260618-codex/review_panel_report.json`

evidence package 和 claim ledger 支撑了稿件当前的谨慎表述：多项 claim 被明确标记为 observed、qualified、secondary 或 blocked。证据充分支持的内容包括 domain-validity rubric、MR-card execution path、bounded cylinder-flow results、FNO/PINN transfer evidence、PhysicsNeMo smoke-scale execution、seeded-fault stress tests、baseline scope contrasts，以及 artifact-backed claim boundaries。ledger **不支持** broad reliability claim、baseline superiority、real-world defect-rate claim 或 geometry-independent pass/fail rate。

## 多 Reviewer LLM Panel

运行命令：

`rtk zsh -lc 'set -a; source .env; set +a; .venv/bin/python tools/run_academic_review_panel.py --outdir research_assets/runs/academic-review-panel-20260618-codex'`

Reviewer panel：

| 角色 | 模型 | Verdict | 接收概率估计 |
|---|---:|---|---:|
| EIC | gpt-5.5 | major_revision | 0.55 |
| MethodologyRigor | glm-5.1 | major_revision | 0.75 |
| DomainExpert | deepseek-v4-flash | major_revision | 0.40 |
| Perspective | qwen3-max | minor_revision | 0.85 |
| DevilsAdvocate | kimi-k2.6 | minor_revision | 0.55 |

聚合结果：

| 维度 | 平均分 / 10 | 解释 |
|---|---:|---|
| novelty_contribution | 7.2 | 达到可发表线，但 novelty 依赖“组合 + operationalization”的表述方式 |
| technical_soundness | 7.4 | 整体可靠，但 duality claim 存在表述风险 |
| empirical_rigor | 7.2 | 证据纪律较强，但外推范围有限 |
| related_work | 7.8 | 与接近 MT/SciML prior 的定位较充分 |
| clarity | 6.4 | 最弱项；密度和防御性边界表述影响可读性 |
| reproducibility | 8.2 | 明显强项 |
| scope_match_to_ist | 8.6 | 与 IST 范围高度匹配 |
| **overall** | **7.54** | IST-competitive，但 revision-likely |

Verdict distribution：**3 个 major revision，2 个 minor revision**。因此 panel majority verdict 为 **major revision**。

## 学术水平评估

### 有证据支撑的优势

1. **期刊匹配度强。** 论文是 software V&V / metamorphic testing 方法论文，目标是 SciML surrogate 的 oracle-free testing，符合 IST 对 software testing、V&V 和 empirical software engineering 的范围要求。

2. **核心方法具备可发表性。** Domain-validity rubric、measurement-floor admissibility gate、MR-card executable asset format 和 typed verdict design 都回应了一个真实问题：SciML 中的候选 MR 不能自动等同于有效测试。

3. **复现性明显高于一般投稿基线。** claim ledger、evidence package、committed artifacts、regression tests 和 explicit blocked-claim boundaries 是实质性优势。

4. **证据边界非常诚实。** 稿件反复避免过度声称：没有 broad reliability claim，没有 baseline-superiority claim，没有 real-world defect-rate claim，也没有无条件 geometry-independent rate。

5. **贡献有合理 novelty 路径。** 最强表述应是“validity-gated SciML metamorphic testing 的 end-to-end operationalization”，而不是声称发明了 metamorphic testing、constraints、relaxations 或 bug-vs-inapplicability separation。

### 有证据支撑的弱点

1. **Clarity 是主要短板。** 新 panel 的最低维度是 clarity，只有 6.4/10。多个 reviewer 独立指出稿件密度高、术语重、防御性边界说明频繁。这不是单纯文字润色问题，因为 IST 读者是 broad software engineering audience，而不只是 SciML/V&V 小圈子。

2. **“validity--coverage duality” 是最大论证风险。** 多个 reviewer 独立认为它可能接近 tautology 或被拔高过度。当前证据支持的是一个 scoped empirical principle，不支持 broad theorem。稿件已经写出 refutation conditions，这有帮助，但中心命题的 rhetorical weight 仍然偏重。

3. **实证广度在 artifact discipline 上很强，但 inferential force 仍有限。** evidence package 支撑了很多 bounded executions，但主线仍是一类主要 CFD family 加 secondary transfer/stress-test evidence。作者实现的 10-mutant catalogue 适合作为 stress-test evidence，不应被读成 real-world defect-rate evidence。

4. **Domain-violation scores 尚未跨 MR classes 校准。** ledger 与 reviewers 都指出，这限制了 two-dimensional verdict 在不同 MR 类型之间的可比性。

5. **Baseline comparisons 是 scope contrasts，不是 competitive evaluation。** 只要诚实表述，这是可以接受的；但 reviewer 仍可能要求与 accuracy/UQ/residual monitors 或其他 MR-generation methods 做更强对照。

## 量化成熟度 Rubric

| 类别 | 分数 / 100 | 证据 |
|---|---:|---|
| IST formal compliance | 92 | word count 12,470；structured abstract；声明齐备；17 tests passed |
| Journal scope fit | 86 | IST 官方范围 + panel scope_match 8.6/10 |
| Novelty/contribution | 72 | panel novelty mean 7.2/10；closest-prior positioning 合理但仍有风险 |
| Technical soundness | 74 | panel technical mean 7.4/10；operator-floor gate 强，但 duality framing 有风险 |
| Empirical rigor | 72 | panel rigor mean 7.2/10；evidence-gated 但 bounded |
| Related work | 78 | panel related-work mean 7.8/10；closest prior 覆盖较充分 |
| Reproducibility | 82 | panel reproducibility mean 8.2/10；claim/evidence artifacts 强 |
| Clarity/accessibility | 64 | panel clarity mean 6.4/10 |
| Claim discipline | 84 | claim ledger fail-closed，稿件 caveats 较强 |
| **Overall maturity** | **78** | 综合 venue compliance、reviewer panel 与 evidence integrity |

## 投稿建议

**如果作者能接受 likely major-revision pathway，可以投稿。** 当前稿件在格式和基本期刊匹配上并不脆弱。真正的投稿风险是 scientific/editorial 层面的：reviewer 是否认可 validity-gated operationalization 已经足够构成贡献，以及是否认为 duality claim 是 insight 而不是 rhetoric。

建议投稿前做五项轻量但高收益修改：

1. 降低 “validity--coverage duality” 的修辞负载。把它表述为由 admissibility gate 生成的 scoped, falsifiable observation，而不是 universal law。
2. 增加一个“reviewer 应该带走什么”的压缩段落或一页式总览，用 IST 读者容易接受的语言讲清 contribution、evidence 和 claim boundary。
3. 把部分防御性边界说明压缩到一个 claim-boundary paragraph/table，减少它们对主论证节奏的打断。
4. 更醒目地说明 mutant catalogue 的限制：它是 stress-test evidence，不是 real-world defect-rate evidence。
5. Cover letter 保持事实性，但略微软化 “first end-to-end” 的语气，除非每个 closest-prior distinction 都能立即锚定到证据。

## 底线判断

这篇稿件 **学术上扎实，实践上已经达到可投稿状态**，但诚实的结果预期应是 **major revision**，不是顺滑接收。最强资产是 journal fit、operational method novelty、reproducibility 和 evidence discipline；最弱资产是 readability、empirical breadth，以及中心 duality claim 的修辞脆弱性。

