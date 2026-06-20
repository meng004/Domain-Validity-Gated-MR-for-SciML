# 51 — 2026-06-20 deep-research + academic-pipeline 投稿成熟度复核

> 评估对象：`paper/ist-submission/main.tex`  
> 目标期刊：Elsevier *Information and Software Technology* (IST) regular research paper  
> 方法：deep-research 证据审计 + academic-pipeline Stage 2.5/3 入口 + academic-paper-reviewer 多 reviewer rubric。  
> 重要边界：用户已明确批准将完整稿件发送到 `.env` 配置的第三方 LLM 网关。2026-06-20 `opus47` panel 中 5/5 reviewer 均真实运行成功；原始结果保存在 `research_assets/runs/academic-review-panel-2026-06-20-opus47/review_panel_report.json`。  

## 1. 执行结论

当前稿件的投稿成熟度为 **83/100**，属于 **IST regular paper 可投稿区间**，但不是“稳妥接收”状态。最诚实的一审预期是：

- **最可能编辑结论**：minor revision 多数，但应按 major revision 风险准备。
- **desk reject 风险**：低到中低，主要因为 scope fit、structured abstract、声明、字数和软件 V&V 取向都基本满足 IST。
- **major revision 风险**：仍然存在，主要来自 novelty sharpness、实证外推边界、coverage implication、D-axis 跨 MR 校准，以及稿件密度。
- **当前最强资产**：可复现性、claim ledger、MR cards、artifact-to-claim traceability、fail-closed evidence discipline。
- **当前最弱资产**：贡献是否被 EIC 读成“known MT / tolerance / inapplicability ideas 的 careful integration”，而不是足够 sharp 的 IST contribution。

这是一篇 **学术上扎实、形式上可投、审稿中大概率需要认真修改** 的稿件。若作者接受 major-revision pathway，现在可以进入投稿准备；若目标是提高首轮 minor revision 概率，应先完成第 7 节的 P1 修改。

## 2. 对照 IST 作者指南

2026-06-20 重新核对 ScienceDirect 官方 IST Guide for Authors：

官方来源：<https://www.sciencedirect.com/journal/information-and-software-technology/publish/guide-for-authors>

| IST 要求 | 当前稿件状态 | 判断 |
|---|---|---|
| 主题需有 clear software engineering component，范围包括 software testing 与 verification & validation | 稿件聚焦 SciML surrogate 的 oracle-free metamorphic testing 与 V&V asset construction | 通过 |
| Regular research paper 上限 15,000 words，references / appendices 计入，figures/tables 各按 200 words | `tools/ist_wordcount.py`: **12,109** counted words；headroom **2,891** | 通过 |
| Structured abstract 必须包含 Context, Objectives, Methods, Results, Conclusion | `main.tex` abstract 已包含五个 structured headings | 通过 |
| 需 editable source files；LaTeX 可接受 | `paper/ist-submission/main.tex` + `elsarticle` template | 通过 |
| 需声明 generative AI use | `main.tex` line 546 有相关 section | 通过 |
| 需 data availability / repository link 或不能共享说明 | `main.tex` line 552 有 Data availability | 基本通过；提交前再确认 DOI/链接可访问 |
| 需 CRediT / competing interest 等声明 | `main.tex` lines 540、543 有 CRediT 和 competing interest | 通过 |

本地硬检查：

```text
IST-counted total: 12109 (body=8155 bib=1554 figs=4 tabs=8 floats=2400)
cap=15000; headroom=2891

pytest tests/test_p0_submission_readiness.py tests/test_stage2p5_submission_readiness.py
17 passed
```

## 3. LLM Gateway Reviewer Panel 状态

用户指定模型：

| Reviewer role | Requested model | 2026-06-20 状态 |
|---|---|---|
| EIC | `gpt-5.5` | 成功 |
| MethodologyRigor | `claude-opus-4-7` | 成功 |
| DomainExpert | `glm-5.2` | 成功 |
| Perspective | `deepseek-v4-pro` | 成功 |
| DevilsAdvocate | `qwen3-max` | 成功 |

我已将 `tools/run_academic_review_panel.py` 的默认 panel 更新为上述模型映射，并真实运行：

```bash
rtk zsh -lc 'set -a; source .env; set +a; .venv/bin/python tools/run_academic_review_panel.py --outdir research_assets/runs/academic-review-panel-2026-06-20-opus47'
```

用户批准后已通过外部权限运行。原始结果保存在：

`research_assets/runs/academic-review-panel-2026-06-20-opus47/review_panel_report.json`

### 3.1 Panel 聚合

| 指标 | 结果 |
|---|---:|
| reviewer 成功数 | 5/5 |
| overall dimension mean | **7.86/10** |
| accept probability mean | **0.702** |
| accept probability range | **0.58--0.75** |
| verdict distribution | **2 major_revision / 3 minor_revision** |
| panel majority verdict | **minor_revision** |

Per-dimension mean：

| 维度 | 均分 /10 | 解读 |
|---|---:|---|
| novelty_contribution | 7.20 | 可发表，但贡献仍可能被读成 incremental integration |
| technical_soundness | 8.00 | 方法总体扎实，operator-floor 与 typed verdict 支撑强 |
| empirical_rigor | 7.80 | 证据纪律强，但范围仍 bounded |
| related_work | 7.60 | closest-prior positioning 较充分，但仍可 sharpen |
| clarity | 7.60 | 已达可审稿水平，但 EIC 仍认为 dense / overloaded |
| reproducibility | 7.80 | 强项，但 non-redistributable checkpoints 限制 full replication |
| scope_match_to_ist | 9.00 | 与 IST software V&V / testing remit 高度匹配 |

### 3.2 Reviewer 分歧

| Reviewer | Model | Verdict | Accept probability | 关键 concern |
|---|---|---:|---:|---|
| EIC | `gpt-5.5` | major_revision | 0.58 | contribution 有价值但相对 MT constraints / relaxations / scientific-software MR work 偏 incremental；稿件 evidence tiers 与 claims 过载 |
| MethodologyRigor | `claude-opus-4-7` | minor_revision | 0.75 | 数值 admissibility gate 目前只在特定 mesh/operator setting 校准；实验单元非独立；absolute conservation 仍 deferred |
| DomainExpert | `glm-5.2` | minor_revision | 0.68 | admissibility predicate 需更形式化；D-axis 未跨 MR 校准；seeded-fault catalogue 小；稿件 boundary statements 可合并 |
| Perspective | `deepseek-v4-pro` | minor_revision | 0.75 | jargon/dense prose 影响 broad IST audience；coverage/fault-detection implication 易被过读；production-scale surrogate 尚未评估 |
| DevilsAdvocate | `qwen3-max` | major_revision | 0.75 | generalizability 仍可能过强；MR-card 缺少 formal specification/tooling evidence；fault-detection claims 易被过读 |

该 panel 与 2026-06-18 panel 的方向一致但略更乐观：平均分仍为 **7.86/10**，接收概率均值升至 **0.702**，多数 verdict 为 **minor_revision**。不过 EIC 与 Devil's Advocate 仍为 major_revision，风险集中在 novelty、scope、主线压缩、formalization/tooling evidence 和外推纪律。

## 4. Deep-Research 证据审计

`research_assets/experiments/evidence-package.md` 与 `claim-ledger.yml` 显示，当前稿件的证据体系总体是 fail-closed 的：

- 支持：domain-validity rubric、operator-floor admissibility、MR-card executable assets、typed verdict、artifact-backed claim ledger。
- 支持但需限定：K=6 MGN roster、same-domain variants、PointMLP cylinder workflow、FNO/PINN supporting evidence、minimum-MR-subset rerun。
- 不支持：broad SciML reliability、baseline superiority、real-world fault-detection rate、geometry-independent pass/fail rate、absolute mass conservation。

这对投稿是明显优势。IST 审稿人通常会奖励 reproducibility 和 empirical honesty，但不会因此自动放过 novelty 与 scope 问题。换句话说：**证据纪律已经强，贡献叙事仍要更锋利。**

## 5. 量化成熟度考核

| 维度 | 分数 /100 | 依据 |
|---|---:|---|
| IST formal compliance | 93 | 字数 12,109/15,000；structured abstract；声明齐备；17/17 tests passed |
| Journal scope fit | 88 | IST software testing / V&V scope 强匹配；既有 panel scope_match 9.0/10 |
| Novelty and contribution | 72 | operational novelty 成立，但 DA/EIC 风险集中在 incremental packaging |
| Technical soundness | 78 | operator-floor gate、typed verdict、MR cards 成熟；D-axis calibration 仍有限 |
| Empirical rigor | 78 | 证据边界诚实，K=6/多 workflow 有支撑；外推仍 bounded |
| Related work positioning | 76 | closest prior 已覆盖，但需要进一步压缩并 sharpen gap |
| Clarity and accessibility | 74 | 重构后比旧稿强；但 IST broad SE reader 仍可能觉得密度高 |
| Reproducibility | 87 | claim ledger、evidence package、tests、artifacts 是核心强项 |
| Claim discipline | 88 | blocked/qualified/observed 边界清楚；不支持项列得充分 |
| Reviewer risk control | 78 | 2026-06-20 `opus47` panel 5/5 成功；均分 7.86/10；3 minor vs 2 major，但 EIC+DA major_revision 不能忽略 |
| **Overall maturity** | **83** | 可投，但不是 acceptance-ready |

## 6. 模拟 Editorial Decision

**Decision: Minor Revision majority，保守按 Major Revision 风险准备。**

理由：

1. 形式与 scope 已经过线，desk-reject 风险不高。
2. 2026-06-20 `opus47` reviewer panel 出现 3 minor_revision / 2 major_revision，多数为 minor_revision；但 EIC 和 Devil's Advocate 都给 major_revision，应保守按 major-revision 风险准备。
3. 当前没有 fatal methodology flaw；问题主要是贡献清晰度、scope framing、外推纪律和读者负担，属于可修复问题。
4. 若不先压缩主线，EIC 可能认为稿件“证据很多，但 contribution not sharply isolated”。

## 7. 提高接收率的优先路线

### P1 — 投稿前必须处理

1. **把 contribution 从“完整系统”压成一句 sharp claim。**  
   建议主线：validity-gated transformation from physics-derived candidate MRs to auditable executable V&V assets for SciML surrogates。避免把 novelty 写成“发明 MT / 发明 relaxation / 发明 bug-vs-inapplicability”。

2. **降低 coverage implication 的承重。**  
   Coverage 继续作为 admitted MR set 的 bounded implication，不要作为独立强贡献或 general fault-detection claim。

3. **把 D-axis limitation 写得更主动。**  
   明说 D is relation-indexed and not cross-MR calibrated；给出 future calibration protocol 的 2-3 个具体步骤。

4. **压缩 secondary evidence，突出 primary evidence path。**  
   IST EIC 需要先看清 RQ0 -> gate -> MR cards -> typed verdict -> bounded results。FNO/PINN/PointMLP/Minimum-MR-SubSet 等证据要服务主线，不能淹没主线。

5. **提交前确认 data availability 链接。**  
   IST 要求 deposit/link 或说明不能共享；如果 Zenodo DOI 尚未最终公开，应在 manuscript 和 submission system 中保持一致。

### P2 — 强烈建议

1. Cover letter 中强调 software V&V contribution，而不是 CFD / SciML model performance。
2. Highlights 避免过度 claim；突出 validity gate、operator-floor、MR cards、claim ledger。
3. Related Work 末尾增加一段 compact closest-prior distinction，直接回应 Reichert / Eniser / Duque-Torres / MR specification tooling。
4. Results 第一段加一张“what evidence supports which claim”的 reader map，降低稿件密度造成的认知成本。

## 8. 后续可选动作

本轮 `opus47` panel 已 5/5 完成。后续若要进一步提高可信度，建议做两类真实补充而不是继续堆单轮 reviewer：一是只针对 EIC/DA 的 major concerns 做定向修订后 re-review；二是把 MR-card formal specification / tooling evidence 补成一页式 artifact-facing appendix 或 README。
