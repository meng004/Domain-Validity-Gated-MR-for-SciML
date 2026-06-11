# Phase 5 v5/v6 panel outcome and plateau determination

Date: 2026-06-11

Artifacts:
- v5: `research_assets/runs/academic-review-panel-v5/review_panel_report.json`
- v6: `research_assets/runs/academic-review-panel-v6/review_panel_report.json`

## Score trajectory（同一稿件家族，五厂商面板）

| 维度 | v4 (09:35) | v5 (D-score 全 MR 后) | v6 (去防御化 + floor CI 后) | 用户目标 |
|---|---:|---:|---:|---:|
| novelty | 6.4 | 7.0 | 6.6 | 8.0 |
| technical | 7.4 | 7.8 | 7.6 | 8.0 |
| empirical | 6.6 | 7.4 | 7.0 | 8.0 |
| clarity | 7.0 | 7.0 | 6.6 | 8.0 |
| related work | 8.0 | 8.4 | 8.0 | — |
| reproducibility | 7.6 | 8.4 | 8.2 | — |
| scope match | 8.4 | 8.6 | 8.4 | — |
| **overall** | 7.34 | **7.80** | 7.49 | ≥7.8 |
| **accept** | 0.452 | **0.616** | 0.546 | ≥0.65 |

## 判读

1. **v4→v5 的 +0.46 是真实改进**（D-score 扩展到全部 MR 类直接回应了 v4 的 5/5 收敛关切）。
2. **v5→v6 的 −0.31 发生在稿件只变好（去防御化、9 点 floor sweep + CI、字数再降）的情况下**，
   且 v6 的关切清单与 v5 基本同构。结论：±0.3 量级是面板采样噪声，不是稿件信号。
3. 三轮均值约 7.5、accept 均值约 0.54，与 31 号评估的 v1–v3 平台（7.51/0.54）一致。
   **平台期确认**，触发 32 号计划 Phase 5 的预设出口：停止 prose-only 迭代，交用户拍板。

## 剩余结构性关切（v5/v6 合并，按频次）

1. **窄实证基座**（10/10 人次）：单 MGN 家族 + 单数据集；K=6 是 seed/config 变体；PINN roster 被视为 minimal。
   唯一解：真正的第二独立 SUT 家族（Geo-FNO 等）或真实世界缺陷证据。
2. **新颖性增量**（7/10）：相对 Eniser/Duque-Torres/Reichert 被读作"重新包装"。
   解：定位重写（用户拍板），或用新实证把 admissibility predicate 的区分度做实。
3. **rubric 验证部分循环**（glm v6 新提出）：expert/LLM 基线用 rubric 本身度量 admissibility gap。
   可写作上承认 + 提出独立效标（如 catalogue 检出率作为外部效标）；彻底解需独立判据实验。
4. 防御文风（v6 kimi 仍提 clarity 5）：已做两轮删减（12,401→10,856 词），边际收益递减。

## 已在本轮关闭的关切

- D-score 仅单关系量化（v4 5/5）→ 全 MR 类逐关系操作化（C17），v5 empirical +0.8。
- operator-floor 4 点 R²=1.000 不可靠（v5 kimi）→ 9 分辨率、slope 0.984、95% CI [0.975, 0.992]（C12 扩展）。
- 路径堆砌/重复免责（v5 3/5）→ 删减手术（"not a" 41→31 / 35→29，路径 7→2 / 12→8）。

## 状态

Phase 5 gate（empirical ≥8.0 ∧ overall ≥7.8 ∧ accept ≥0.65 ∧ clarity ≥7.0）：v5 过 2/4，v6 过 0/4。
用户目标（novelty/clarity/empirical/technical 均 ≥8.0）：未达成；面板噪声 ±0.3 下，
即使 v5 最优轮也距 novelty/clarity 目标 ≥1.0 分。

**结论：稿件保持 major-revision / not-yet-submit 状态。纯写作迭代的天花板已到，
需要新证据（独立 SUT 家族 / 真实缺陷 / DOI 归档）或战略决策（Path B：JSS；或接受
major-revision 风险直接投 IST）。should not be repaired by prose alone；
the honest next step is new evidence is added before any v7 cycle.**
