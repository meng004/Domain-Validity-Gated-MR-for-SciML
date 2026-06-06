# 插图规划 -- Rubric-Gated Oracle-Free Testing of Mesh-Based Neural Surrogates for Cylinder Flow

> 源文件: `paper/ist-submission/main.tex`  
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
- 拟生成: `fig_3_mr_hierarchy.{pdf,png}` + `src/fig_3_mr_hierarchy.mmd`。
- 生成建议: 建议生成，但正文是否放入取决于最终篇幅。

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
