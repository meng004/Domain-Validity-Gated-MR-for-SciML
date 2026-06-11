# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-11 by claude-code (Phase 4/5 session)

## 🔴 Blockers（阻塞项，必须先解决）
- [ ] 重跑五厂商评审面板 v5（owner: user → claude）
  - context: Phase 5 验收门槛（empirical ≥8.0 ∧ overall ≥7.8 ∧ accept ≥0.65 ∧ clarity ≥7.0；用户追加目标 novelty/clarity/empirical/technical 均 ≥8.0）。本地环境缺少 `OPENAI_API_KEY`/`OPENAI_BASE_URL` 网关凭据，`tools/run_academic_review_panel.py` fail-closed。今日 09:35 UTC 的 v4 在另一环境跑通过，说明凭据存在于该环境。
  - next-action: 用户在本地 export 凭据，或在有凭据的环境执行 `python3 tools/run_academic_review_panel.py`
  - artifact: v4 结果 `research_assets/runs/academic-review-panel-phase5-baseurl-v1/review_panel_report.json`（empirical 6.6 / novelty 6.4 / technical 7.4 / clarity 7.0 / accept 0.452，major_revision）

## 🟡 In Progress（进行中）
- [ ] 把 v4 四项收敛关切修完后验收（status: 1/4 已关闭）
  - 已关闭：D-score 仅 mirror-y 量化（5/5 关切）→ 全 MR 类逐关系操作化，commit bbbf4f5
  - next-action: 见 Backlog 三项（均需新证据或用户拍板，纯改文字救不了，详见 paper/33_phase5_review_panel_triage.md）

## 🟢 Backlog（待启动，按优先级排序）
- [ ] P0: 增加一个真正不同的 SUT/架构家族产物（v4 5/5 关切"单家族单数据集"；候选：Geo-FNO on cylinder，27/32 号文档标记为 stretch、风险高）
- [ ] P1: 用真实回归/修复历史缺陷或更强对抗目录替换/补充合成种子缺陷（v4 关切"catalogue 合成且粗粒度"）
- [ ] P2: 投稿前把复现包归档到带 DOI 的永久存储（Zenodo），消除"仓库路径不持久"关切
- [ ] P2: 新颖性定位重写（novelty 6.4 是定位问题；32 号文档明确"加实验救不了，需用户拍板重定位"）

## 🔵 Open Questions（待用户拍板的开放问题）
- [ ] novelty/empirical 距 8.0 还差 1.4–1.6 分，触发 27 号文档 Path B（JSS）决策点的条件是"连续两轮平台期"——v4 相比 v3 总分 7.51→7.34 不升反降，是否继续 IST 强化循环，还是评估 Path B？
  - options: A 继续 IST（做 Backlog P0/P1 新证据后跑 v5）/ B 触发 Path B 评估（JSS）/ C 接受 major-revision 风险按 §11 流水线直接投 IST
  - claude-recommendation: A；v4 的四项关切有三项可用已规划资产关闭，且 scope_match_to_ist 8.8 是七维最高分，换刊损失最大单项优势

## ✅ Done（最近 7 天完成项）
- [x] 2026-06-11 Phase 0–3：分支合并、专家/LLM/generic 基线、PINN K=6 roster、36 条统一缺陷目录 + 推断统计 — 9dddc97
- [x] 2026-06-11 Phase 4 清晰度手术：IST 字数 12,401→10,919（≤11,000 门槛）、Abstract/标题/负面句 P0 修复 — 5b17ac1（并行会话）
- [x] 2026-06-11 Phase 6 硬门槛测试 + LaTeX 冲突标记/重复 label 清理 — 5b17ac1（并行会话）
- [x] 2026-06-11 D-score 扩展到全部已执行 MR 类（C17，11 条目，1 条诚实标注不可操作化）；Overfull 0、undefined 0、209 测试全绿 — bbbf4f5
- [x] 2026-06-11 面板 v4 执行 + triage（结论：major_revision，需新证据） — paper/33_phase5_review_panel_triage.md
