# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-12 by claude-code (Phase 17 gate-closure session)

## 🔴 Blockers（阻塞项，必须先解决）
- [ ] 面板 v17 量分被 LLM 网关凭据阻塞：当前云执行环境未配置
  `OPENAI_API_KEY`/`OPENAI_BASE_URL`，`tools/run_academic_review_panel.py`
  fail-closed（`BLOCKED_NO_LLM_CREDENTIALS`）。Phase 17 修订（clarity 手术 +
  新颖性重定位 + PhysicsNeMo 规模化证据）已完成但未量分。需要在环境配置中
  恢复网关凭据后跑 v17。

## 🟡 In Progress（进行中）
- [ ] PhysicsNeMo MGN 规模化工作流（官方 128/15 架构、25 训练轨迹、40 测试
  轨迹）后台训练中 — `tools/run_physicsnemo_mgn_scaled_workflow.py`，产物落
  `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-vortex-shedding-scaled/`。
  完成后需：提交产物 + 启用 `/workspace/test_physicsnemo_scaled_workflow.py.staged`
  → `tests/`、新增 C30 claim-ledger 条目、把 §5.4 多架构段落和 5.1/5.2 表行
  从 smoke 升级为 scaled 数字、main.tex 同步、重编译。

## 🟢 Backlog（按优先级）
- [ ] P1: 真实回归缺陷目录（v16 三位评审仍点名"合成粗粒度"）。本会话调研：
  PhysicsNeMo 官方 git 历史中 MGN/datapipe 相关提交多为重构/依赖，干净的
  SUT 级 bug-fix 提取收益低。备选：v17 反馈若仍以此为主要扣分项，再投入
  GitHub issue 挖掘或 DeepMind meshgraphnets 历史。
- [ ] P2: Zenodo DOI（需要账户/token；稿件已加"acceptance 时归档 DOI"承诺，
  关切已部分回应）。

## ✅ Done（本会话 2026-06-12）
- [x] 环境恢复：CPU torch + nvidia-physicsnemo 2.1.1 + torch_geometric +
  torch_scatter + tfrecord + TeX Live；278 测试全绿
- [x] pytest 时间戳污染修复：D-score 再生器加 `--out`，测试写临时文件 —
  73025e9
- [x] Clarity 手术（manuscript.md）：删内部元信息块、摘要 Results 重构、
  4.1/4.5 正面改写、第 5 节三层重组、5.3 五个超长 bullet 压缩 ~35%、
  5.6.4-5.6.6 编号修复 — 9de2d9d
- [x] 新颖性重定位：2.7 first-end-to-end-pipeline 声明 + 2.4 最近先验能力
  对比表 + 多架构覆盖叙事 — 9de2d9d
- [x] LaTeX 同步移植 + 重编译（0 Overfull、无 undefined）；内部字数 buffer
  11000→11500（有据注释）— ac3c856
- [x] PhysicsNeMo 规模化工具 + 数据 staging（25+40 官方轨迹，~870MB，外部
  暂存）+ 共享 graph 原地改写 bug 修复（node-perm 假 0.148 → 精确 0.0）
- [x] 36 号→37 号执行记录：paper/37_phase17_gate_closure_execution.md
