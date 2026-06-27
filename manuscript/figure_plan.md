# 插图规划 -- Rubric-Gated Oracle-Free Testing of Mesh-Based Neural Surrogates for Cylinder Flow

> 源文件: `submissions/IST/main.tex`  
> 评估日期: 2026-06-05  
> 目标期刊: Information and Software Technology  
> 使用技能: `paper-figure-planner` + `ppw:visualization`  
> 总判断: 应该用图，但要少而准。当前稿最需要方法图和证据链图；结果图必须等待真实实验数据。

## 一、现有插图盘点

| 编号 | 当前位置 | 类型 | 工具 | 评估 |
|---|---|---|---|---|
| 无 | 全文 | 无 | 无 | 当前 LaTeX 稿没有 `figure` / `includegraphics`。 |

当前已有三张表：

| 表 | 内容 | 是否替代图 |
|---|---|---|
| Table 1 | domain-validity rubric | 不替代方法流程图。表给判据，图给流程。 |
| Table 2 | initial MR card skeletons | 不替代 MR asset 数据流图。表给例子，图给执行关系。 |
| Table 3 | RQ/evidence map | 部分替代实验设计图。若篇幅紧，可不再画实验设计图。 |

## 二、建议插图清单

### Fig 1 -- Validity-gated MR testing workflow

- 位置: §3.1 Method Overview 第一段后。
- 类型: 流程图 -> Mermaid。
- 必要性: 高 -- 这是整篇方法论文的入口图。没有这张图，读者需要从多段文字中拼出“候选生成、rubric 筛选、MR card、执行、verdict”的关系。
- 内容要点: candidate relation sources -> NOETHER-informed organization -> domain-validity rubric -> MR card -> executable asset -> relation-level verdict -> evidence ledger。
- 数据来源: 无需实验数据。
- caption 草稿: `Figure 1. Validity-gated workflow for converting physically motivated candidate relations into executable oracle-free MR assets and relation-level verdicts.`
- 拟生成: `fig_1_validity_gated_workflow.{pdf,png}` + `src/fig_1_validity_gated_workflow.mmd`。
- 生成建议: 现在即可生成，因为它是概念/方法图，不依赖结果数据。

### Fig 2 -- Executable MR asset and verdict data flow

- 位置: §3.3 MR card and executable asset format 后。
- 类型: 数据流 / 架构图 -> Mermaid。
- 必要性: 高 -- 这是 contribution C2/C3 的核心。它能说明 MR 不是一句物理直觉，而是由 source case、follow-up transformation、SUT runs、metric、tolerance、exclusion rule 和 verdict ledger 组成的可审计资产。
- 内容要点: MR card fields; source case; follow-up transform; SUT execution; output mapping; metric; tolerance; exclusion rule; verdict classes; artifacts。
- 数据来源: 无需实验数据。
- caption 草稿: `Figure 2. Executable MR asset structure and verdict data flow. Each retained relation becomes an auditable asset with transformation, metric, tolerance, exclusion, and artifact records.`
- 拟生成: `fig_2_mr_asset_dataflow.{pdf,png}` + `src/fig_2_mr_asset_dataflow.mmd`。
- 生成建议: 现在即可生成。

### Fig 3 -- MR hierarchy and interpretation protocol

- 位置: §3.5 Hierarchical interpretation protocol 后。
- 类型: 层次树 / 分类图 -> Mermaid。
- 必要性: 中到高 -- 如果论文要强调“failure interpretation / localization protocol”，这张图应该保留；如果篇幅压力大，可以并入 Fig 2 或留到 appendix。
- 内容要点: representation/preprocessing MRs; physical-model MRs; temporal/rollout MRs; method-comparison MRs; implementation/runtime MRs; possible interpretation; evidence caution。
- 数据来源: 无需实验数据。
- caption 草稿: `Figure 3. Hierarchical interpretation protocol for grouping MR violations by representation, physical-model, temporal, cross-SUT, and implementation layers.`
- 状态: 已弃用 -- 此 MR-hierarchy 图未纳入终稿；正文 Figure 3 改用 2D 判定图 `fig_3_verdict_2d.{pdf,png}`。源文件 `fig_3_mr_hierarchy.{pdf,png,mmd}` 已于 2026-06-17 删除。

### Fig 4 -- Experiment design and evidence gates

- 位置: §4 Empirical Design 开头或 §4.4 RQ-to-evidence map 前。
- 类型: 实验设计图 / swimlane -> Mermaid。
- 必要性: 中 -- Table 3 已经承担了 RQ、参数、baseline、artifact 映射。若评审容易误解“结果尚未完成”，这张图可帮助强调 evidence gate；否则可砍掉。
- 内容要点: three SUTs; four comparator families; MR execution; statistics; blocked result claims; reproducibility package。
- 数据来源: 无需实验数据。
- caption 草稿: `Figure 4. Empirical design and evidence gates for the three-SUT evaluation. Result claims remain blocked until MR cards, logs, verdict ledgers, and statistical artifacts exist.`
- 拟生成: `fig_4_experiment_design_gates.{pdf,png}` + `src/fig_4_experiment_design_gates.mmd`。
- 生成建议: 可选。若正文已经有 Table 3，可暂不生成。

### Fig 5 -- Verdict distribution by SUT and MR class

- 位置: Results，第一张结果图。
- 类型: 堆叠横向条形图 -> seaborn / matplotlib。
- 必要性: 高，但必须等待真实数据。
- 内容要点: 每个 SUT 或每类 MR 的 verdict 构成：pass, fail, skip, out-of-relation-domain, numerical-tolerance issue, inconclusive。
- 数据来源: `verdict_ledger.csv`，最低字段：`sut_id`, `mr_id`, `mr_class`, `verdict`, `case_id`。
- visualization recommendation:
  - 推荐方案: 堆叠横向条形图。
  - 核心理由: verdict 是分类结果，且类别名较长；横向堆叠能直接展示每个 SUT/MR class 的通过、失败、跳过和 out-of-domain 构成。
  - 坐标轴: X 轴为 case count 或 proportion；Y 轴为 SUT 或 MR class。
  - 尺度处理: 若不同 MR class 样本数差异大，优先用 proportion，并在条形末端标注总样本数。
  - 统计要素: 若有 bootstrap 区间，可在补充图中给比例置信区间；主图不强行加误差线。
  - 配色与样式: 使用灰阶兼容色板；fail/out-of-domain 用可区分深浅，不使用红绿二元对立。
- caption 草稿: `Figure 5. Relation-level verdict distribution across SUTs and MR classes.`
- 拟生成: `fig_5_verdict_distribution.{pdf,png}` + `src/fig_5_verdict_distribution.py`。
- 生成建议: 等真实 `verdict_ledger.csv` 出来后生成。现在不能画占位数据。

### Fig 6 -- Rollout accuracy versus MR violation evidence

- 位置: Results 或 Discussion 中“complementarity with rollout accuracy”段落后。
- 类型: 散点图 / 二维象限图 -> seaborn / matplotlib。
- 必要性: 高 -- 这是回答“MR 与 accuracy-only 是否互补”的关键图。
- 内容要点: 每个点代表一个 SUT-MR-class-bin 或 case group；X 轴 rollout error；Y 轴 MR violation rate 或 violation magnitude；用颜色区分 SUT，用形状区分 MR class。
- 数据来源: `accuracy_mr_joined.csv`，最低字段：`sut_id`, `mr_class`, `group_id`, `rollout_error`, `violation_rate` 或 `violation_magnitude`, `n_cases`。
- visualization recommendation:
  - 推荐方案: 散点图，配参考线或象限分区。
  - 核心理由: 论文需要展示 accuracy-only 与 relation-level evidence 是否回答不同问题；二维散点能显示“低 rollout error 但高 MR violation”等互补案例。
  - 坐标轴: X 轴为 rollout error；Y 轴为 MR violation rate 或 standardized violation magnitude。
  - 尺度处理: 若 violation magnitude 跨数量级，用 log scale；若用 violation rate，保留 0--1 比例尺。
  - 统计要素: 点大小可表示 `n_cases`；若有重复运行，可添加置信椭圆或分面图，不宜过度装饰。
  - 配色与样式: SUT 用颜色，MR class 用 marker；保证黑白打印时 marker 仍可区分。
- caption 草稿: `Figure 6. Complementarity between rollout accuracy and relation-level MR violation evidence.`
- 拟生成: `fig_6_accuracy_vs_mr_violation.{pdf,png}` + `src/fig_6_accuracy_vs_mr_violation.py`。
- 生成建议: 等真实 join 表出来后生成。

### Fig 7 -- Violation-rate heatmap over MR class and SUT

- 位置: Results 中 verdict 图之后。
- 类型: 热力图 -> seaborn / matplotlib。
- 必要性: 中到高 -- 如果 MR class x SUT 的二维结构明显，这张图很有价值；否则用表即可。
- 内容要点: 行为 MR class，列为 SUT 或 transformation bin，颜色为 violation rate / fail proportion。
- 数据来源: `mr_violation_summary.csv`，最低字段：`sut_id`, `mr_class`, `violation_rate`, `n_cases`, `ci_low`, `ci_high` 可选。
- visualization recommendation:
  - 推荐方案: 热力图。
  - 核心理由: 研究问题含多个 SUT 和多个 MR class；热力图能让读者一眼看到 violation 集中在哪些 SUT-MR 组合。
  - 坐标轴: X 轴为 SUT 或 transformation bin；Y 轴为 MR class；颜色为 violation rate。
  - 尺度处理: 统一 0--1 色标，避免每个子图单独归一化造成误读。
  - 统计要素: 单元格标注 `rate` 和 `n`；样本数太小的单元格用 hatch 或浅灰标记为 low evidence。
  - 配色与样式: 使用单调灰阶/蓝灰色板，避免彩虹色。
- caption 草稿: `Figure 7. MR violation-rate heatmap across SUTs and MR classes.`
- 拟生成: `fig_7_violation_heatmap.{pdf,png}` + `src/fig_7_violation_heatmap.py`。
- 生成建议: 等真实 summary 表出来后生成。

### Fig 8 -- OOD transformation boundary curve

- 位置: Results 或 Discussion 中“boundary characterization”段落后。
- 类型: 带置信区间折线图 -> seaborn / matplotlib。
- 必要性: 高，前提是实验确实有 transformation magnitude / OOD distance 维度。
- 内容要点: X 轴为 transformation magnitude、Reynolds shift、OOD bin 或 perturbation level；Y 轴为 violation rate / violation magnitude；线条按 SUT 或 MR class 分组。
- 数据来源: `ood_boundary_curve.csv`，最低字段：`sut_id`, `mr_class`, `transform_name`, `ood_level`, `violation_rate`, `ci_low`, `ci_high`, `n_cases`。
- visualization recommendation:
  - 推荐方案: 带置信区域的折线图。
  - 核心理由: 论文希望回答“这个 SUT 在 OOD transformation 下不可靠”和“适用边界在哪里”；折线加置信区间最直接表达边界变化。
  - 坐标轴: X 轴为 OOD transformation 强度或 bin；Y 轴为 violation rate 或 violation magnitude。
  - 尺度处理: 若不同 MR class 的数值范围差异大，使用分面网格，不建议双 Y 轴。
  - 统计要素: 必须给置信区间或 bootstrap band；样本数不足的 bin 应标注或剔除。
  - 配色与样式: 每个 SUT 一种线型或 marker，颜色只作辅助。
- caption 草稿: `Figure 8. Boundary characterization under increasing OOD transformation strength.`
- 拟生成: `fig_8_ood_boundary_curve.{pdf,png}` + `src/fig_8_ood_boundary_curve.py`。
- 生成建议: 等真实 OOD 分层数据出来后生成。

### Fig 9 -- Seeded-fault detection by MR layer

- 位置: Results 中 seeded faults/mutations 小节。
- 类型: 分组横向条形图或检测矩阵热力图 -> seaborn / matplotlib。
- 必要性: 中 -- 只有做了 seeded faults/mutations 才需要。否则不要放。
- 内容要点: MR layer 对 seeded fault class 的 detection count/rate；展示 localization utility。
- 数据来源: `seeded_fault_detection.csv`，最低字段：`fault_id`, `fault_layer`, `sut_id`, `mr_id`, `mr_layer`, `detected`, `topk_match` 可选。
- visualization recommendation:
  - 推荐方案: 检测矩阵热力图。
  - 核心理由: fault layer 和 MR layer 都是分类维度；矩阵比柱状图更能展示“哪类 MR 检出哪类 fault”。
  - 坐标轴: X 轴为 fault layer；Y 轴为 MR layer；颜色为 detection rate。
  - 尺度处理: 统一 0--1 色标；低样本单元格单独标注。
  - 统计要素: 有重复 mutant 时可报告置信区间；否则只报告 count/rate，不做显著性装饰。
  - 配色与样式: 使用单调色板，单元格内写 `rate (n)`。
- caption 草稿: `Figure 9. Seeded-fault detection matrix by fault layer and MR layer.`
- 拟生成: `fig_9_seeded_fault_detection_matrix.{pdf,png}` + `src/fig_9_seeded_fault_detection_matrix.py`。
- 生成建议: 只有 seeded-fault 实验真实存在时生成。

## 三、合理性评估

- 建议正文首轮采用 3 张方法图：Fig 1、Fig 2、Fig 3。
- Fig 4 可选；如果 Table 3 已足够清楚，建议先不放 Fig 4。
- 结果完成后优先生成 3 张数据图：Fig 5、Fig 6、Fig 8。
- Fig 7 取决于二维矩阵是否有清晰结构；Fig 9 取决于 seeded-fault 实验是否真实完成。
- 不建议画 cylinder-flow 场景的装饰性流场图，除非它来自真实 SUT/数据并服务于 MR transformation 示例。
- 不建议在结果未完成前生成任何数据图占位图。

推荐最终正文图数：

| 阶段 | 图数 | 建议 |
|---|---:|---|
| 当前方法稿 | 3 | Fig 1--3 |
| 实验完成后 | 6--7 | Fig 1--3 + Fig 5 + Fig 6 + Fig 8 + 可选 Fig 7/9 |
| 篇幅压缩版 | 4--5 | Fig 1 + Fig 2 + Fig 5 + Fig 6 + Fig 8 |

## 四、图表代码生成路线

按 `paper-figure-planner` 的规则，本文件是阶段一评估产物。下一步需要作者确认图单后再生成代码和图片。

确认后可生成：

| 图 | 源码类型 | 可否现在生成 |
|---|---|---|
| Fig 1 | Mermaid `.mmd` | 可以 |
| Fig 2 | Mermaid `.mmd` | 可以 |
| Fig 3 | Mermaid `.mmd` | 可以 |
| Fig 4 | Mermaid `.mmd` | 可选 |
| Fig 5 | Python `.py` | 等 `verdict_ledger.csv` |
| Fig 6 | Python `.py` | 等 `accuracy_mr_joined.csv` |
| Fig 7 | Python `.py` | 等 `mr_violation_summary.csv` |
| Fig 8 | Python `.py` | 等 `ood_boundary_curve.csv` |
| Fig 9 | Python `.py` | 等 `seeded_fault_detection.csv` |

数据图代码应只读取真实 CSV/JSON，不生成 synthetic demo data。若需要先搭脚本骨架，脚本也应在缺少输入文件时退出并提示所需字段，而不是画假图。

---

# 追加评估 — 2026-06-21 IST 投稿前 float 必要性/数量复核

> 此节为终稿(4 图 + 6 表已落定)的事后评估,与上方 2026-06-05 生成规划区分。仅评估,不改正文。

## 终稿 float 盘点(4 图 + 6 表 = 10 float)

| float | 评估 | 理由 |
|---|---|---|
| fig_1 validity-gated workflow | **保留(高)** | 方法中心图,candidate→gate→admit/reject/defer→card/runner/ledger 全链 |
| fig_2 mr_asset_dataflow | **建议砍/并入 fig_1(低)** | 内容近线性,与 fig_1 尾段 + tab:rubric(card 字段)重叠 |
| fig_3 verdict_2d | **保留(高)** | 两轴 typed verdict 核心新意,图让 relation×domain 一眼可见 |
| fig_4 operator_floor_loglog | **保留(高)** | O(h) 斜率标定关键定量结果 |
| tab:rq-contribution-evidence | **建议砍/并(中)** | 与 tab:rqmap 同为 RQ×N 表,前段连遇两张;独有列 Primary section 可下放正文 |
| tab:closest-prior-positioning | **保留(高)** | closest-prior 能力矩阵,正面回应"incremental" |
| tab:rubric | **保留(高)** | 准入门+card 字段+verdict 语义方法主表 |
| tab:rqmap | **保留(高)** | 评估设计×RQ,列更密,信息独有 |
| tab:mr-card-verdict | **保留(高)** | MR-card→verdict 结果主表 |
| tab:claim-evidence(附录) | **保留(高)** | claim→artifact 可审计映射,复现核心 |

## 三问结论

1. **篇幅**:IST-counted 12676 / 15000,**合规**,余量 ~2300。float 不是篇幅瓶颈。
2. **必要/合适**:8 个 float 个体充分必要;**2 个偏弱**——fig_2(与 fig_1/tab:rubric 重叠)、tab:rq-contribution-evidence(与 tab:rqmap 重复 RQ 索引)。
3. **数量**:10 float 对 ~12.7k 词方法论文**偏多**(常见 4–8);且 float 密度正是 EIC 多轮"dense/overextended"的来源之一。

---

# 追加评估 — 2026-06-26 IST 同步稿 float 必要性与 caption 精简

> 源文件: `manuscript/main.tex`  
> 当前状态: 3 图 + 5 表/长表 = 8 floats。  
> 本轮处理: 保留全部 floats；仅压缩图题和表题，删去 caption 中可由正文承担的解释性句子。

## 当前 float 必要性

| float | 保留判断 | 理由 |
|---|---|---|
| `fig:workflow` | **保留(高)** | 方法入口图，概括 candidate relation → admissibility gate → MR asset/evidence ledger 的主流程。 |
| `fig:verdict-2d` | **保留(高)** | RQ3 的核心判别空间；用图比文字更快说明 relation violation 与 domain violation 的二维解释。 |
| `fig:operator-floor` | **保留(高)** | P1 divergence floor 的关键定量证据；删图会削弱 numerical decidability 的可审查性。 |
| `tab:closest-prior-positioning` | **保留(高)** | 回答 closest-prior/incrementality；表格比段落更适合多工作多能力对照。 |
| `tab:rubric` | **保留(高)** | 方法主表，集中给出 admissibility gate、MR-card fields、verdict semantics。 |
| `tab:rqmap` | **保留(高)** | 评估设计索引，避免 reviewer 将 primary/supporting/secondary/stress evidence 混读。 |
| `tab:mr-card-verdict` | **保留(高)** | 结果主表，连接 MR card、rubric decision、runtime verdict 和解释边界。 |
| `tab:claim-evidence` | **保留(高)** | 附录证据索引，支撑 claim-to-artifact traceability。 |

## caption 精简结果

| float | 新 caption |
|---|---|
| `tab:closest-prior-positioning` | Closest-prior capability matrix. |
| `fig:workflow` | Validity-gated V\&V workflow. |
| `tab:rubric` | Admissibility gate and verdict semantics. |
| `fig:verdict-2d` | Two-dimensional relation and domain verdict space. |
| `tab:rqmap` | Evaluation design. |
| `tab:mr-card-verdict` | MR-card verdict map. |
| `fig:operator-floor` | P1 divergence operator-floor calibration. |
| `tab:claim-evidence` | Claim-to-evidence map. |

## 总判断

当前 8 个 floats 对 IST regular 方法论文是可接受的上限内配置。三张图分别服务于方法流程、判别语义和数值证据；五张表分别服务于相关工作定位、方法定义、实验设计、结果映射和证据追踪。不存在明显装饰性图片；也不存在可无损删除的表格。若后续还需进一步压缩，优先压缩正文解释和长表单元格，而不是删除这些 floats。

## 最高 ROI 删减(可选,直击 EIC reason-b)

- **砍 fig_2** → 并入 fig_1 尾段;省 200 词,4→3 图。需删 `\ref{fig:asset-flow}`(1 处)。
- **砍 tab:rq-contribution-evidence** → Primary-section 指向下放正文,RQ×evidence 交 tab:rqmap;省 200–400 词,消前段两张相似 RQ 表。需删 `\ref{tab:rq-contribution-evidence}`(2 处:L110、L118)。
- 净:10→8 float,省 ~400–600 词,main 密度下降。均需重建 + 复测(test_phase6 查 \ref、test_phase4 字数)。

> 决策权在作者。采纳则我执行删减 + 清引用 + 重建 + 全测试;否则保持现状(亦合规)。

---

# 追加评估 — 2026-06-24 必要性 / 位置 / 内容三问复核

> 源文件已迁至 `manuscript/main.tex`(repo 已拆分,旧 `submissions/IST/` 名废弃)。
> 字数:IST-counted 13020 / 15000,headroom ≈ 1980;每浮动体 200 词。本节仅评估,不改正文/图。

## 三问逐图结论(4 图 + 6 表)

| 图 | 1 必要性 | 2 位置 | 3 内容 |
|---|---|---|---|
| Fig 1 workflow | 高 — 方法中心图 | 合适(紧跟 L239 首引,Method 开篇) | 准确,与 §3.5 判决四类一致 |
| Fig 2 asset dataflow | 中(四图最弱,与 Fig 1 尾段 + tab:rubric 概念重叠) | 合适(紧跟 L293) | 准确 |
| Fig 3 verdict 2D | 高 — RQ3 核心,概念+真实 pilot 双用 | 合适(紧跟 L307) | 基本准确;**1 处需澄清(见下)** |
| Fig 4 operator-floor | 高 — 支撑唯一 load-bearing 新点 | 合适(紧跟 L457) | **⚠ 数字与正文不符,需重生成(见下)** |

## ⚠ 必须修(stage-2,待用户确认)— Fig 4 数据源错位

- fig_4 及其源 `src/fig_4_operator_floor_loglog.py` 读取
  `research_assets/runs/operator-floor-sweep/operator_floor_report.json`
  —— **仅 4 分辨率**(h0,h0/2,h0/4,h0/8),fit_all slope = **0.988**,interior 0.994。
- 正文 L457 与 claim-evidence 表 L603 引的是 **9 分辨率**、slope **0.984**(interior 0.989)、95% CI [0.975,0.992]。
  该数据在 `operator-floor-sweep-extended/operator_floor_extended_report.json`(9 levels,fit_all 0.9837≈0.984,interior 0.9893≈0.989)。
- 另 `operator-floor-sweep-mesh2`(8 levels,非结构 Delaunay,slope 0.983)= 正文第二拓扑。
- **后果**:审稿人比对图"slope=0.988 / 4 点"与正文"nine resolutions … 0.984"会发现矛盾。违 §3/§6 数字溯源。
- **修复**:fig_4 数据源改为 extended(9 点,slope 0.984),可选叠加 mesh2 Delaunay 点;并修脚本写死的旧输出路径 `submissions/IST/figures/` → `manuscript/figures/`。

## 建议修(措辞)— Fig 3 caption

- 横轴单一共享对数刻度,却混入不同 MR 族(V/tol 与 V/floor);正文 L309 明确这些 per-relation 值"不能跨族平均或排序"。图易被读成正文否认的跨族标定。
- 建议 caption 补一句:横轴为 per-relation 示意放置,非跨族标定刻度。**仅改 caption,不动数据**。
- 数字核对:图中 mirror-y `V/floor 3.96`、对称网格 `relL2 1.10` 与正文 L430/L436 逐字一致。✓

## 数量与重复

- 4 图配比合理(2 流程/数据流 + 1 概念 + 1 数据),无冗图;**不建议新增图**(headroom 紧)。
- 唯一可选新增(低优先,需先腾词):MR 族 × 故障类 检测命中小矩阵,让"按族定位"覆盖几何一眼可见(数据已在 §4.1/§4.9 + claim-evidence 表)。
- 省词杠杆同 2026-06-21 结论:Fig 2、tab:rq-contribution-evidence 为最弱两项,如需压词优先处理。

## 待办优先级

1. **(必须,待确认)** Fig 4 改用 9 分辨率 extended 报告重生成 + 修脚本路径。
2. **(建议)** Fig 3 caption 加 per-relation 示意说明。
3. **(可选)** 压词时砍/并 Fig 2。

---

# 追加评估 — 2026-06-27 第 5 章阅读节奏复核

> 用户问题:第 5 章大段文字表达缺乏多样性,是否可增加图片或表格。

## 判断

- 不建议新增概念图:第 5 章已有 `tab:mr-card-verdict` 和 `fig:operator-floor`,再加概念图会与结果映射/证据边界重复。
- 不建议新增数据图:可视化真实 verdict distribution 或 seeded-fault matrix 需要整理 ledger 为图表输入,且会增加一个 200-word float 成本;当前最直接的问题是读者在进入长段结果前缺少扫读入口。
- 建议新增一个短表:在 `Primary cylinder-flow evidence` 开头加入 `tab:primary-result-summary`,把六个长段结果压成“check / observed result / interpretation / boundary”四列。该表不引入新证据,只重排已报告结果,主要功能是降低阅读疲劳和防止过度解读。

## 已执行

- 新增 `Primary result summary.` 表。
- 同步更新正文后需重新编译、同步投稿包并复查 IST 字数和 LaTeX 日志。

---

# 追加评估 — 2026-06-27 第 5 章全局图表规划

> 用户问题:5.6、5.7 仍有大段文字疲劳感,需从全局视角规划插图和表格提升可读性。  
> 当前状态:正文已计数约 13.3k / 15k;第 5 章已有 `tab:mr-card-verdict`、`tab:primary-result-summary`、`fig:operator-floor`。新增图表必须有明确分工,不能只是把同一信息重排。

## 一、全局诊断

| 位置 | 当前承载方式 | 阅读问题 | 建议动作 |
|---|---|---|---|
| §5.1 Evidence overview | 长表 `tab:mr-card-verdict` | 承担全章索引,功能明确 | 保留,不再加同类总表 |
| §5.2 Primary cylinder-flow evidence | 已新增 `tab:primary-result-summary` + 六个短主题段 | 已有扫读入口 | 保留;不再加图 |
| §5.3 Same-task replication | 两段文字,数字密集但短 | 可读性尚可 | 暂不加图表 |
| §5.4 Second-task gate discrimination | 一个长段同时讲 airfoil、四类 verdict、边界 | 可读性中等偏弱 | 可选新增小表,但优先级低于 §5.6/§5.7 |
| §5.5 Operator-floor resolution sweep | 数据图 + 解释段 | 图文搭配合理 | 保留 |
| §5.6 Coverage implication | 多个证据层混在连续段落:K=6 复现、severity sweep、60-entry catalogue、adversarial、cross-SUT、cross-program | 最疲劳;核心“coverage geometry”不够一眼可见 | **优先新增 1 张检测矩阵图或 1 张矩阵表** |
| §5.7 Interpretation and boundaries | 反驳、边界、实践含义连续展开 | 读者需要自己整理“能 claim 什么/不能 claim 什么/何时使用” | **新增 1 张 claim-boundary / use-condition 表**,并压缩原文 |

## 二、推荐新增/替换清单

### Table R1 -- Coverage-geometry matrix

- 位置:§5.6 第一段后,在 `Aggregate reading and Phase-3 unified catalogue` 之前。
- 类型:结果矩阵表;若后续整理出 CSV,可升级为热力图。
- 必要性:高 -- §5.6 的主张是“admitted MR set 决定可见/不可见 fault directions”,这是二维结构,表/矩阵比长段更适合。
- 内容要点:
  - 行: detector or MR family (`node permutation`, `continuity/conservation`, `mirror-y`, `full admitted suite`)。
  - 列: fault/evidence group (`boundary/scale`, `physical-channel/adjacency`, `output scaling`, `partial v_y zeroing`, `adversarial`, `airfoil mirror removed`, `cross-program`)。
  - 单元格: detected / blind / excluded / supporting breadth,并在可用处给 count 或 rate,如 `5/10 union`, `0/6`, `6/6`, `240/240 node permutation` 等。
- 数据来源:正文 §5.6 已报告数值 + `claim-ledger.yml` / seeded-fault ledgers;若实施为图,必须先整理为 `seeded_fault_detection_summary.csv`,不得手填假数据。
- caption 草稿:`Coverage-geometry matrix for the admitted MR set. Cells distinguish detected, blind, excluded, and scope-breadth evidence, showing that coverage follows the invariants measured by admitted relations.`
- 拟生成/实现:
  - 快速实施:LaTeX `table` / `tabularx`,不新增图文件。
  - 数据图实施: `fig_5_coverage_geometry_matrix.{pdf,png}` + `src/fig_5_coverage_geometry_matrix.py`。
- 预计正文改动:新增表后,压缩 §5.6 的 `Aggregate reading` 和 `Cross-SUT coverage` 两段各 2--3 句,让表承担枚举细节。

### Table R2 -- Interpretation and claim-boundary guide

- 位置:§5.7 开头,第一段后;或替换 `Boundary of claims` 与 `Implications for SciML testing` 两个加粗段的部分内容。
- 类型:解释边界表。
- 必要性:高 -- §5.7 不是数据结果,而是“如何读这些结果”。表格能防止读者在长段中丢失 permitted claim 与 blocked claim。
- 内容要点:
  - 行: `value beyond accuracy`, `predicate not post-hoc`, `deferred conservation`, `overclaim blocked`, `when to use`, `cost profile`。
  - 列: `reader concern`, `evidence response`, `licensed claim`, `not licensed`。
- 数据来源:正文 §5.7 现有文字和 Table~\ref{tab:claim-evidence};不新增实验证据。
- caption 草稿:`Interpretation and claim-boundary guide. The table separates what the evidence licenses from claims that remain outside the study scope.`
- 拟实现:`tab:interpretation-boundary-guide`。
- 预计正文改动:新增表后,把 §5.7 中 `Boundary of claims`、`Implications`、`When to use` 三段各压缩为 1--2 句,避免“表 + 原文重复”。

### Table R3 -- Cross-task gate discrimination summary (optional)

- 位置:§5.4 第二句后。
- 类型:小型对比表。
- 必要性:中 -- §5.4 单段较长,但不像 §5.6 那样结构复杂;若还要进一步改善,这张表能让 cylinder vs airfoil 的 verdict type difference 更直观。
- 内容要点:
  - 行:`node permutation`, `incompressible continuity`, `compressible mass conservation`, `mirror-y`。
  - 列:`cylinder-flow gate`, `airfoil gate`, `reason for difference`, `claim boundary`。
- 数据来源:正文 §5.4 与 `tab:mr-card-verdict`。
- caption 草稿:`Cross-task gate discrimination between incompressible cylinder flow and compressible airfoil flow.`
- 拟实现:`tab:cross-task-gate-summary`。
- 取舍建议:仅当实施 R1/R2 后仍觉得 §5.4 疲劳时再加;否则先不加,避免第 5 章表格过密。

## 三、是否新增图片

| 候选图 | 结论 | 原因 |
|---|---|---|
| Verdict distribution stacked bar | 暂不推荐 | `tab:mr-card-verdict` 已给 verdict map;若无整理好的 per-case ledger 图会增加数据处理风险 |
| Coverage geometry heatmap | 推荐为 R1 的二阶段版本 | 这是唯一真正能呈现表没有展示的二维结构的图;但必须从真实 summary CSV 生成 |
| Claim-boundary concept diagram | 不推荐 | §5.7 更像解释/范围界定,表格比概念图更精确 |
| Cross-task Sankey/flow | 不推荐 | 信息量不足,容易装饰化 |

## 四、优先级与实施策略

1. **优先实施 R1 + R2**:一个 coverage 矩阵 + 一个 claim-boundary 表,直接针对 §5.6/§5.7 的疲劳点。
2. **控制净增量**:新增两个表会按 IST 规则增加约 400 counted words;当前 headroom 约 1689,形式上安全,但应同步压缩 §5.6/§5.7 原文约 250--400 words,让可读性提升而非简单增厚。
3. **不建议一次性加 R1/R2/R3 三张表**:第 5 章会从“文字疲劳”变成“表格疲劳”。R3 作为备选。
4. **若作者偏好图片**:把 R1 做成 heatmap,不要另加 R1 表;R2 仍用表。
5. **实施后验证**:重编译两遍,检查 `Overfull \hbox`、undefined refs、IST wordcount、PDF/hash/zip 同步。

## 五、建议的最终第 5 章 float 布局

| 位置 | float | 功能 |
|---|---|---|
| §5.1 | `tab:mr-card-verdict` | 全章 verdict map |
| §5.2 | `tab:primary-result-summary` | 主案例扫读入口 |
| §5.5 | `fig:operator-floor` | 数值可判定性定量证据 |
| §5.6 | `tab:coverage-geometry-matrix` 或 `fig:coverage-geometry-matrix` | coverage/blind-spot 二维结构 |
| §5.7 | `tab:interpretation-boundary-guide` | allowed vs blocked claims / use conditions |

推荐最终增量:新增 2 个浮动体,同时删减相应段落细节;不新增概念图。

## 六、执行记录

- 已实施 R1:`tab:coverage-geometry` 加入 §5.6,用 detector / relation family 行组织 visible directions、blind/excluded directions、scope and boundary。
- 已压缩 §5.6:原先的 aggregate reading、Phase-3 catalogue、adversarial mutants、cross-SUT/cross-program 长段压缩为三个解释段,避免和矩阵重复。
- 已实施 R2:`tab:interpretation-boundary` 加入 §5.7,按 reader concern、evidence response、licensed claim、not licensed 四列组织解释边界。
- 已压缩 §5.7:保留关键 misreading、claim boundary、implications、cost profile,删去与表格重复的长解释。
- 未实施 R3:§5.4 暂不新增 cross-task gate summary,避免第 5 章表格过密。
