# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-11 by claude-code (Phase 4/5 session)

## 🔴 Blockers（阻塞项，必须先解决）
- [ ] 平台期已确认（v4 7.34 / v5 7.80 / v6 7.49，accept 0.45–0.62 振荡），按 32 号计划 Phase 5 预设出口停止 prose-only 迭代，等用户战略拍板（见 Open Questions）
  - artifact: paper/34_phase5_v5_v6_panel_outcome.md（三轮对比 + 判读）

## 🟡 In Progress（进行中）
- [ ] v4/v5 收敛关切修复（status: 3/5 已关闭）
  - 已关闭：D-score 全 MR 类操作化（bbbf4f5）；operator-floor 9 分辨率 + slope CI、去防御化手术（2ab58d4）
  - 未关闭（结构性）：窄实证基座、新颖性定位；v6 新增"rubric 验证部分循环"（glm，可先写作承认）

## 🟢 Backlog（待启动，按优先级排序）
- [x] P0a: 增加同域第二 checkpoint family 的完整 primary workflow（S4/S5 wider/deeper MGN variants；artifact: `research_assets/runs/same-domain-variant-primary-workflow/same_domain_variant_primary_workflow_report.json`；注意：仍非 PhysicsNeMo/EchoWave 外部架构）
- [x] P0b: 增加真正不同的轻量 SUT/架构家族产物（PointMLP row-wise coordinate network on cylinder；artifact: `research_assets/runs/pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json`；注意：仍非 PhysicsNeMo/EchoWave 生产级外部实现）
- [ ] P0c: 生产级外部 SUT extension（Task 1 feasibility audit + Task 2 candidate ledgers + Task 2.5 PhysicsNeMo runtime staging 已完成但 blocked；artifacts: `feasibility_report.json`、per-object `candidate_ledger.json`、`physicsnemo_runtime_staging_report.json`；下一步需 staged official data/checkpoint/API/raw outputs/metric ledgers 后才能进入 Task 3-5 workflows）
- [ ] P1: 用真实回归/修复历史缺陷或更强对抗目录替换/补充合成种子缺陷（v4 关切"catalogue 合成且粗粒度"）
- [ ] P2: 投稿前把复现包归档到带 DOI 的永久存储（Zenodo），消除"仓库路径不持久"关切
- [ ] P2: 新颖性定位重写（novelty 6.4 是定位问题；32 号文档明确"加实验救不了，需用户拍板重定位"）

## 🔵 Open Questions（待用户拍板的开放问题）
- [ ] novelty/empirical 距 8.0 还差 1.4–1.6 分，触发 27 号文档 Path B（JSS）决策点的条件是"连续两轮平台期"——v4 相比 v3 总分 7.51→7.34 不升反降，是否继续 IST 强化循环，还是评估 Path B？
  - options: A 继续 IST（做 Backlog P0/P1 新证据后跑 v5）/ B 触发 Path B 评估（JSS）/ C 接受 major-revision 风险按 §11 流水线直接投 IST
  - claude-recommendation: A；v4 的四项关切有三项可用已规划资产关闭，且 scope_match_to_ist 8.8 是七维最高分，换刊损失最大单项优势

## ✅ Done（最近 7 天完成项）
- [x] 2026-06-12 P0c Task 2.5 PhysicsNeMo runtime staging：`nvidia-physicsnemo==2.1.1` 与 CPU torch/torchvision 可 import，MeshGraphNet/vortex datapipe/DoMINO datapipe import probe 通过；CUDA/GPU 与 official data/checkpoint/API/raw outputs/metric ledgers 仍 blocked — artifact `research_assets/runs/production-grade-sut-extension/physicsnemo_runtime_staging_report.json`
- [x] 2026-06-12 P0c Task 2 candidate ledgers：三项 PhysicsNeMo 生产级对象均完成 representation/symmetry/conservation-flux/boundary-contract/numerical-floor 候选关系分类与四条件 admissibility predicate；由于 Task 1 blocked，所有 workflow execution 仍禁止 — artifacts `research_assets/runs/production-grade-sut-extension/*/candidate_ledger.json`
- [x] 2026-06-12 P0c Task 1 feasibility audit：三项 PhysicsNeMo 生产级对象官方文档可达；已补足 CPU torch 依赖用于现有测试，但 PhysicsNeMo 仍不可 import，且未 staged official checkpoint/data/API，production workflow claims 仍 blocked — artifact `research_assets/runs/production-grade-sut-extension/feasibility_report.json`
- [x] 2026-06-12 PointMLP 非 MGN cylinder-flow primary workflow：9/9 node-perm pass、10/10 mirror OOD fail、9/9 conservation diagnostic pass、3/3 exact-sym fail、median rollout rel L2 0.0298 — artifact `research_assets/runs/pointmlp-cylinder-primary-workflow/`
- [x] 2026-06-12 同域 S4/S5 wider/deeper MeshGraphNet variant primary workflow：2/2 node-perm pass、60/60 mirror OOD fail、54/54 conservation diagnostic pass、6/6 exact-sym fail — artifact `research_assets/runs/same-domain-variant-primary-workflow/`
- [x] 2026-06-11 Phase 0–3：分支合并、专家/LLM/generic 基线、PINN K=6 roster、36 条统一缺陷目录 + 推断统计 — 9dddc97
- [x] 2026-06-11 Phase 4 清晰度手术：IST 字数 12,401→10,919（≤11,000 门槛）、Abstract/标题/负面句 P0 修复 — 5b17ac1（并行会话）
- [x] 2026-06-11 Phase 6 硬门槛测试 + LaTeX 冲突标记/重复 label 清理 — 5b17ac1（并行会话）
- [x] 2026-06-11 D-score 扩展到全部已执行 MR 类（C17，11 条目，1 条诚实标注不可操作化）；Overfull 0、undefined 0、209 测试全绿 — bbbf4f5
- [x] 2026-06-11 面板 v4 执行 + triage（结论：major_revision，需新证据） — paper/33_phase5_review_panel_triage.md
