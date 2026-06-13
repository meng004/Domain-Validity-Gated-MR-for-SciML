# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-13 by claude-code (Phase 17/18 gate-closure session)

## 🎯 里程碑：Phase-5 四项门槛全部达标（v18，2026-06-12）

| 维度 | v16 | v17 | v18 | 门槛 | 状态 |
|---|---:|---:|---:|---:|:--:|
| overall | 7.31 | 7.66 | **7.83** | ≥7.8 | ✅ |
| accept | 0.572 | 0.666 | **0.686** | ≥0.65 | ✅ |
| clarity | 6.0 | 7.0 | **7.2** | ≥7.0 | ✅ |
| empirical | 7.2 | 7.6 | **8.0** | ≥8.0 | ✅ |
| novelty | 6.8 | 7.0 | 7.2 | — | — |

裁决 4×minor / 1×major(EIC)。平台期（v7–v16 卡在 ~7.3）已突破。
artifact: `research_assets/runs/academic-review-panel-v18/review_panel_report.json`

## 🟡 待用户拍板：是否投稿
v18 已达到自定义 Phase-5 出口门槛。建议路径：
- A（推荐）：按当前 v18 稿件走 §11 投稿流水线投 IST（accept≈0.69，预期 minor revision）
- B：再做一轮 v19 把 novelty(7.2)/EIC(major) 往上推后再投（边际收益递减）

## 🟢 Backlog（投稿前可选项）
- [ ] v18 残余共性意见（非门槛阻塞，可在 minor-revision 阶段回应）：
  单任务外部效度（5/5 仍提）、D-score 跨类未校准（3/5）、seeded-fault
  目录合成粗粒度（4/5）、glm 建议正文再压缩 30–40%
- [ ] P2: Zenodo DOI（稿件已承诺 acceptance 时归档）

## ✅ Done（本会话 2026-06-12/13）
- [x] 环境恢复 + 286 测试全绿；D-score 时间戳污染修复（73025e9）
- [x] Phase 17 clarity 手术 + 新颖性重定位（9de2d9d, ac3c856）
- [x] PhysicsNeMo smoke→scaled 官方架构工作流（25+40 官方轨迹，node-perm
  40/40 精确、mirror 40/40 OOD）+ C30 claim + 数据管道 bug 修复（8903e71）
- [x] v17 panel（7.66）+ triage（守恒 deferral 重构、跨家族整合、caveat
  去重）（bf8aca6, 9c047e6）
- [x] v18 panel：四项门槛全过（036ff5d）

## 📌 历史 provenance（守卫钉死，勿删）
- P0c Task 3 minimal Object-A smoke workflow 已完成（smoke 子集，已被 scaled
  工作流取代为主要证据，但 smoke 产物与 claim 仍保留）；full-scale Object-A
  与 Task 4-5 仍 blocked。
- P0c Task 2.8 complete DeepMind TFRecord staging 已记录。
