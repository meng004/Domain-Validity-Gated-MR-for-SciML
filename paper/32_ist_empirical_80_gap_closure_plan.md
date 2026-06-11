# 32 — IST 实证 80 分达标方案（基于 T2 资产复用 + trusting-curie 分支合并）

Date: 2026-06-11
Inputs: `origin/claude/trusting-curie-i2VHM`（48 commits，含 P1+P2 全部产物与 31 号就绪评估）、
meng004/Minimum-MR-SubSet（下称 T2）资产审计、27 号成熟度评估 v2。

---

## 0. 目标定义

"实证 80 分" 操作化为五厂商评审面板（`tools/run_academic_review_panel.py`，v3 基线见
`paper/31_ist_submission_readiness_assessment.md`）的：

| 指标 | v3 现状 | 目标 |
|---|---|---|
| Empirical rigor | 7.2 | **≥ 8.0** |
| Overall（七维均值） | 7.51 | ≥ 7.8 |
| Accept probability | 0.54 | ≥ 0.65 |
| Clarity | 6.2 | ≥ 7.0 |

声明：面板是自动化三角测量工具，不是真实 IST 编辑决策的预测器；80 分是内部质量门槛，
不构成录用承诺。

---

## 1. T2（Minimum-MR-SubSet）实证复用审计

### 1.1 已复用（main 分支，已入稿）

| T2 资产 | 本文用途 | 证据 |
|---|---|---|
| 只读 MGN trainer + DeepMind cylinder-flow 数据集 | E1 K=6 checkpoint roster 训练 | C11，`multicheckpoint/` |
| 原始训练 checkpoint | 三个 within-SUT pilot 的 SUT | C1–C10 |
| 10-mutant witness taxonomy | 种子故障目录（numpy/torch 重实现） | C10、C13 |

### 1.2 已复用（trusting-curie 分支，未合并）

| 资产/方法 | 分支产物 | 关闭的审稿关切 |
|---|---|---|
| T2 多厂商 rater-panel 方法学（rater alignment / Fleiss-κ 协议） | P2-2 LLM-MR 基线：8 候选、predicate 全收、6/8 与论文 MR 重叠、3 厂商互斥 rater（κ=0.077, PRA=0.79） | 基线 blocked（部分） |
| —— | C3 generic-MR 基线：13 模板 → predicate 仅收 3，全部与论文 MR 重合；按四条件给出拒绝分解 | 基线 blocked（部分） |
| T2 PINN witness 思路（T2 经 submodule 反向消费本仓库） | P2-1 跨家族 PINN×2（Burgers2D 9/12 mutants admitted；Diffusion2D 10/12），checkpoint+manifest 已提交 | 单架构家族（2 个有界点） |
| —— | P2-3 对抗突变（R3 盲区=子空间）、D-score（0.00 对称 / 0.51 真实）、effect_size_tests.py、IST 合规修复（Abstract 301 词、声明节齐全） | 对抗目录 / 域违反轴定性 / 合规 |

### 1.3 可复用但尚未开发

| T2 资产 | 复用方式 | 节省 |
|---|---|---|
| PINN 12-mutant catalogue ×2（burgers2d / diffusion2d witness runs 的 `mutant_catalog.csv` + kill matrix） | 移植入本仓库 runner，统一故障目录至 ≥34 | A3 从 3–5 天 → 1–2 天 |
| `data/raw/_mr_corpus` S1–S13（已发表专家 MR，含作者本人 2017–2021 核工程 MT 论文 + Zhao2026） | 专家 MR 基线的引出协议与对照语料 | 专家基线协议设计从零 → 半天 |
| `annotator_rubric_v1` + 9 厂商 rater 校准数据 | 专家基线的标注与 κ 计算协议 | 直接套用 |
| p10_pinn_hnn / p7_burgers PUT adapter | 第三 PDE 问题候选（HNN，stretch） | 可选 |
| p1–p8 经典数值 PUT、OpenMC/pincell、DNN/csmith/SQL witnesses | **不复用**——非学习型 surrogate，超出本文 SciML 主张范围 | — |

### 1.4 复用的诚实性边界（必须写进 Data Availability）

- 两文主张不相交：T2 主张最小完备 MR 子集理论（NP-hard/ILP/退化定理，目标 TSE）；
  本文主张可采性门控工作流（目标 IST）。共享的是 SUT/trainer/突变分类法等**基础设施**，
  不共享任何作为贡献呈现的**结果**。
- T2 未发表，引用方式为 repository citation（Zenodo DOI 或 GitHub commit），并在
  Data Availability 中披露 artifact 谱系，防 salami-slicing 质疑。
- T2 维持只读约束（27 号文档既有约束沿用）。

---

## 2. 五阶段方案

### Phase 0 — 合并 trusting-curie 分支 + 合规收尾（0.5–1 天，前置门槛）

merge `origin/claude/trusting-curie-i2VHM` → main；跑全部测试（分支自带 ~10 个新测试文件）；
重建 PDF；补 Funding 声明（分支唯一缺项）；按 venues/IST.md 复跑合规脚本。

**理由**：48 个 commit 的 P1+P2 产物（两个跨家族 PINN、LLM/generic 基线、对抗突变、D-score、
合规修复）目前对 main 不可见。不合并，后续一切工作都在重复造轮子。这是零新实验成本拿回
约 1.5–2 周已完成工作的动作，ROI 无穷大。

### Phase 1 — 专家 MR 基线（人在环，3–5 天人时；**立即启动，与后续并行**）

- 设计：N≥2 名真实人类专家（作者本人为已发表 MT-for-scientific-software 专家 + 1 名
  CFD/SciML 背景同事），在**不接触 rubric**的条件下，按固定 brief（SUT 描述 + I/O 契约 +
  2 小时预算）独立提出候选 MR。
- 评分：rubric 四条件筛选 → retain/downgrade/reject 分布、与论文 MR 重叠、rubric 增量
  （validity 条件精确化、tolerance 溯源）；标注协议与 κ 计算复用 T2 `annotator_rubric_v1`。
- 产出：PC3 的专家比较器从 blocked → observed；RQ4 四比较器全部落地
  （rollout ✅ / LLM ✅ / generic ✅ / expert ✅）。

**理由**：这是面板 5/5 一致的最高关切，31 号评估明确"cannot be fabricated"——它是
唯一必须人类输入的项，也是 accept probability 的主天花板。人的招募延迟主导工期，
故必须第一个启动。实事求是约束下唯一合法做法就是真实专家。

### Phase 2 — 第二架构家族规模化：PINN K=6 roster（约 1 周，纯计算）

- 复用 `tools/train_pinn_burgers2d.py` / `train_pinn_diffusion2d.py`：3 seeds × 2 PDEs
  = 6 个 PINN checkpoint（小网络，单机可训）。
- 对每个 checkpoint 跑全部适用 MR runner + 移植的 12-mutant PINN 目录（§1.3），
  完全复制 E1 的 manifest/bootstrap-CI 模式。
- 产出：跨家族证据从"2 个有界点"升级为**带 95% CI 的家族级 rate**；外部效度叙述变为
  "2 个架构家族 × 3 个 PDE 问题"。
- Stretch（不设门槛）：Geo-FNO on cylinder——仅当 Phase 1 等待人时有富余再做；
  规则网格插值的合法性问题使其风险高，不纳入达标路径。

**理由**：面板 4/5 关切"narrow scope"，且 31 号评估明确指出面板"discounts 2 bounded
points"，需要的是 rate 不是 point。E1 的全部工程模式（orchestrator、manifest、CI）
直接套用，边际成本只剩训练计算；这是分数弹性最大的实验项。

### Phase 3 — 统一故障目录 + 推断统计升级（3–4 天）

- 合并故障目录：10 MGN mutants + P2-3 对抗突变 + 12×2 PINN mutants ≥ 34，跨两个家族。
- 把 §5.6 by-class localization 形式化为按故障类的 precision/recall + Wilson CI；
  连续量比较补 Wilcoxon + Cliff's δ（`tools/effect_size_tests.py` 已在分支）；
  引用 Empirical Standards for SE Research。

**理由**：同时关闭 27 号评估的 A3（目录小、非对抗）与 A4（无显著性检验/效应量）两项，
且素材几乎全部现成，是单位时间分数增量第二高的项。precision/recall 形式化把
"suggestive localization"升级为可检验断言，直接抬 empirical rigor。

### Phase 4 — 仅删不增的清晰度手术（2–3 天）

- 目标 −15% 正文：claim-to-evidence 大表移附录；每小节重复的 scope disclaimer 收敛为
  一处 canonical "Still blocked"；§5.3/§5.6 复述数字去重。
- 硬约束：分支上约 25 个 test-guarded marker 字符串必须在 main.tex 与 manuscript.md
  同步保留（31 号评估已标记此风险）；改后全量跑测试。
- 同步项：Abstract 去经验数字复核（IST.md §2 禁数字）、Highlights ≤85 字符复核。

**理由**：clarity 6.2 是七维最低分且随每次加内容继续下跌（6.6→6.2）；面板 4/5 关切
"overlong/hedged/ledger-heavy"。这是唯一**不加任何实验**就能涨分的维度，并且若不做，
Phase 1–3 的新增内容会把 clarity 进一步压低、对冲掉实证涨分——所以它是实证分的保护性
配套，不是可选美化。

### Phase 5 — 重跑面板 + §11 提交前流水线（2 天）

- 重跑五厂商面板 v4：门槛 = empirical ≥8.0 ∧ overall ≥7.8 ∧ accept ≥0.65 ∧ clarity ≥7.0。
- 未达标 → 按 v4 收敛关切做一轮定向修复后 v5；连续两轮平台期则触发 27 号文档 Path B
  （JSS）决策点，交用户拍板。
- 达标 → 走 CLAUDE.md §11 五步流水线（bib 审计、proofread、humanizer、构建验证）。

**理由**：用同一把尺子验收，避免自由心证；预设平台期出口防止无限强化循环。

---

## 3. 分数论证（为什么这套组合能过 8.0）

v3 的 empirical rigor 7.2 被三件事压住（31 号评估 §4）：专家基线缺失（5/5）、单家族
（4/5）、小样本统计（1/5，但被 DevilsAdvocate 反复点名）。本方案 Phase 1/2/3 一一对应：

| 压分项 | 关闭动作 | 预期面板反应 |
|---|---|---|
| expert-MR blocked（5/5） | Phase 1 真实双专家基线 | RQ4 比较器闭环，"blocked"措辞从正文消失 |
| 单家族 2 点（4/5） | Phase 2 PINN K=6 rate | 外部效度叙述质变：family×PDE 矩阵 + CI |
| 统计薄弱（1/5） | Phase 3 P/R + Wilcoxon + δ | 与 IST 2023–2025 常模对齐（27 号 §scorecard） |
| clarity 下行风险 | Phase 4 删减手术 | 防止新增内容对冲实证涨分 |

v1→v3 的教训是"加有界子结果不动总分"（每项 +0.2 被 clarity −0.4 对冲）。本方案与之的
本质区别：Phase 1/2 不是"再加一个有界点"，而是把面板点名的**两个结构性缺口**（比较器
闭环、家族级 rate）补成结构完整，同时 Phase 4 主动管理对冲项。这是平台期诊断本身给出的
处方（31 号 §5 gap-closure list 的 A+B+C 三类全覆盖，C 类中可行的那一项），而非我的发明。

预算外风险：novelty 6.6 是定位问题，加实验救不了；若 v4 面板显示 novelty 成为新的
binding constraint，处置是重定位写作（用户拍板），不在本方案射程内。

---

## 4. 工期与关键路径

```
Day 0      Phase 0 合并+合规          ──┐
Day 0      Phase 1 专家招募启动（人时）  │ 并行
Day 1-7    Phase 2 PINN roster（计算）  │
Day 7-10   Phase 3 目录+统计           ──┘（依赖 Phase 2 产物）
Day 10-13  Phase 4 清晰度手术（依赖 1-3 内容定稿）
Day 13-15  Phase 5 面板 v4 + §11 流水线
```

关键路径 = Phase 1 的专家可用性（人因），不是计算。日历工期 **≈ 3 周**（对照 27 号
Path A 原估 4–6 周；压缩来源 = trusting-curie 已完成项 + T2 目录/协议复用）。

## 5. 明确不做

- 不复用 T2 的 p1–p8 经典数值 PUT 结果（非 SciML surrogate，主张范围外）。
- 不把 T2 的 kill matrix 数字直接当本文证据（必须在本文 rubric/verdict 体系内重跑重评）。
- 不做 cross-architecture-family **generalization** 声明（K=6+6 仍是两个家族的有界证据）。
- 不在达标路径上押注 FNO（仅 stretch）。
- STVR 不考虑（用户既有约束）。
