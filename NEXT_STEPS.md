# NEXT_STEPS - MR识别/圆柱绕流 (JSS regular paper 稳定接收主线)

> Last updated: 2026-07-03 by Codex · 当前主投已由用户改定为 **Journal of Systems and Software (JSS), regular paper**。`paper/75` 和 `paper/76` 已将 TOSEM 从当前主投降为 aspirational ceiling；`paper/77` 是 JSS 稳定接收执行计划，`paper/79` 是 Phase 8 pipeline/reviewer/humanizer 复核记录。

## 🟢 2026-07-03 用户改定：主投 JSS，按 JSS regular paper 修
- **当前唯一执行目标**：JSS regular paper；目标是提高到 JSS 可审、证据边界清楚、Major Revision-or-better 现实概率的状态。不得把“稳定接收”伪装成保证录用。
- **核心证据记录**：`paper/75_deep_research_rq_venue_recommendation.md`（deep-research RQ 与 venue 推荐，经 reviewer 校准）和 `paper/76_academic_reviewer_venue_recalibration.md`（academic-reviewer panel）均指向 JSS 为当前 operational target。
- **执行计划**：`paper/77_jss_stable_acceptance_execution_plan.md`。所有 phase 采用 Loop 工程：前置条件 → 核心步骤 → 结束条件 → 评审验收 → 主题漂移检查。
- **JSS 官方契约（2026-07-03 核验）**：JSS scope 覆盖 software engineering、V&V/testing、AI in SE、SE for AI systems；要求 claims 有 evidence，可为 empirical studies、simulation、formal proofs 或 other validation；single-anonymized；abstract ≤250 words；keywords 1–7；highlights 必交，3–5 条且每条 ≤85 characters；LaTeX editable source 可用；full-length paper 建议少于 36 pages single-column 或 18 pages double-column，超出时需解释长度合理性。
- **当前最高优先级**：Phase B/C。Phase A 已把 JSS 页数规则纳入项目护栏；Phase B 已将 JSS 投稿包详细附录迁出为 supplementary material，当前 `submissions/JSS/main.pdf` 是 45 pages single-column，仍超过 JSS 推荐长度；不得把它标记为 final-upload-ready，除非进一步压缩或编辑认可 cover letter 中的长度说明。
- **主题漂移禁区**：不得恢复 TOSEM 稳投主线；不得回到 IST 二投；不得转 RESS；不得写成 general SciML reliability、baseline superiority、arbitrary-mesh guarantee 或 real-world defect-rate 论文。

---

## 当前执行状态：Phase 0-8 已完成，Phase A-E 已执行
- **Phase 6 结果**：完成结构压缩和 evidence-role 重排；cylinder-flow 为 primary evidence，airfoil/PINN/FNO 为 supporting falsification checks，LLM/generic/sibling evidence 为 secondary scope contrasts，seeded faults 为 detector blind-spot stress tests。Phase 5 因此从“基本合格”补足为合格。
- **Phase 7 结果**：已创建并编译 `submissions/JSS/` 投稿包；JSS metadata、PDF、highlights、cover letter、declarations、README 均已生成。
- **Phase 8 结果**：`paper/79_phase8_jss_pipeline_reviewer_humanizer_report.md` 记录 integrity/reviewer/humanizer 复核。后续 Phase A 重新研读官网后修正了长度契约：当前 package 编译和 claim-faithfulness 通过，但页数是 P0 长度风险。
- **Phase B 当前结果**：JSS package 详细 claim-to-evidence、cross-program、secondary-baseline、cross-family appendices 已迁入 `submissions/JSS/supplementary/evidence_appendices.tex`；主稿从 49 页降为 45 页单栏，并在 `cover_letter.md` 中加入事实性长度说明。该结果满足 fallback 条件“压缩并说明”，但未达到 preferred 条件“少于 36 pages single-column”。
- **Phase C 当前结果**：`tab:effective-n` 已改为 independent evidence-unit 表，显式列出 SUT/task、MR/operator、independence source、evidence role、allowed/forbidden inference；未把 supporting evidence 伪装成 population-level representativeness。
- **Phase D 当前结果**：JSS data/software availability 已指向 Zenodo DOI `10.5281/zenodo.20702952`、GitHub 源仓库、`research_assets/runs/` 证据、Minimum-MR-SubSet commit 和 fail-closed credential 边界；新增 `submissions/JSS/open_science_checklist.md`，明确未获得 JSS Open Science Board validation/badge。
- **Phase E 当前结果**：完整 JSS 编译链 `pdflatex/bibtex/pdflatex/pdflatex` 通过；最终 `submissions/JSS/main.pdf` 为 45 pages、480870 bytes；JSS log scan 无 undefined refs/citations、LaTeX error、Missing character、Overfull、rerun marker；全量测试 `447 passed, 334 subtests passed`；证据门禁通过；legacy density diagnostic 为 14702/15000。
- **最近验证记录**：全量测试 `445 passed, 328 subtests passed`；证据门禁通过；JSS package LaTeX final log 无未定义引用/引用、LaTeX error、Missing character、Overfull、rerun marker；JSS abstract 209 words；highlights 5 条且最长 70 characters；legacy density diagnostic 14668。
- **不得伪装的结论**：这不是录用保证。残余风险包括 bounded external validity、JSS 审稿人可能要求更多 independent SUT evidence、当前 45 页单栏超过 JSS 推荐长度，以及尚未获得 JSS Open Science validation/badge。

## 活跃 fail-closed 守卫：生产 SUT 不得过度声称
- P0c Task 3 minimal Object-A smoke workflow 已完成，但只是 smoke/scaled 子集证据；Task 4-5 仍 blocked。
- P0c Task 2.8 complete DeepMind TFRecord staging 已记录；这只是官方数据 staging，不是 full-scale production MR workflow。
- Do not claim full-scale PhysicsNeMo/AeroGraphNet/DoMINO primary workflow results.

## 归档历史：不得作为当前执行路线
- 2026-07-02 以前的 TOSEM/IST/RESS 决策已被 2026-07-03 JSS 决策覆盖。
- 旧路线完整快照已存入 `paper/78_superseded_next_steps_history_20260703.md`，仅供追溯，不得恢复为主线。
- 详细历史材料仍保留在 `paper/52`-`paper/76`、投稿包目录和 git 历史中；本 live 文件不再重复旧计划，避免主题漂移。
