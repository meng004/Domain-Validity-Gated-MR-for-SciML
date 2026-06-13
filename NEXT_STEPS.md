# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-13 by claude-code (Phase 17/18 gate-closure session)

## 🎯 里程碑：Phase-5 四项门槛全部达标（v18，2026-06-12）

| 维度 | v16 | v17 | v18 | v19(B轮,已回退) | 门槛 | 状态 |
|---|---:|---:|---:|---:|---:|:--:|
| overall | 7.31 | 7.66 | **7.83** | 7.54 | ≥7.8 | ✅(v18) |
| accept | 0.572 | 0.666 | **0.686** | 0.548 | ≥0.65 | ✅(v18) |
| clarity | 6.0 | 7.0 | **7.2** | 6.4 | ≥7.0 | ✅(v18) |
| empirical | 7.2 | 7.6 | **8.0** | 7.2 | ≥8.0 | ✅(v18) |
| novelty | 6.8 | 7.0 | 7.2 | 7.4 | — | — |

裁决 v18: 4×minor/1×major。**B 轮（v19，commit 486fa1b）尝试用 novelty 重定位
再加码，结果四项门槛全回退、裁决翻成多数 major**：novelty +0.2（噪声内），
但加长的"类别区分"论证段拉低 clarity（EIC/kimi 给 5），且把理论 distinction
拉满反招"floor 实为经验估计"的反击。已 revert 到 v18 达标 prose（commit
9446634），保留 v19 报告为证据。
**结论坐实：prose-only 加码已到天花板（32/34 号文档预判），门槛是被
PhysicsNeMo 规模化实证 + v17 clarity 工作清掉的，不是 prose 挤出来的。**

## 🟡 待用户拍板：是否投稿
当前 HEAD 稿件 = v18 达标版（overall 7.83、四项全过、accept≈0.69）。建议：
- A（推荐）：按当前稿件走投稿流水线投 IST，预期 minor revision
- B 已验证为负收益，不再重试 prose 加码

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
