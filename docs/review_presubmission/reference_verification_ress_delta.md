# Reference verification — RESS delta (§8.5 hard-block, 2026-06-30)

> 补全 `submissions/RESS/references.bib`（57 条）相对两份既有验证的缺口。
> 方法：paper-search MCP `get_crossref_paper_by_doi`（DOI-first），逐条比对
> title / authors / venue / year 与 BibTeX。

## 覆盖来源

| 来源 | 条数 | 状态 |
|---|---|---|
| `reference_verification.md`（IST 轮，2026-06-17） | 37 | 既往 ✓ |
| `paper/lit_undermind_RESS_2026-06-29/verification.md`（10 条新 RESS 文献） | 10 | 既往 ✓（10/10 全真）|
| 本文件（IST 中间轮新增、晚于 2026-06-17 快照，前两份未覆盖） | 10 | 本次 ✓ |
| **合计** | **57** | **✗ = 0，门槛 PASS** |

## 本次核实的 10 条（全部 ✓，Crossref DOI 直查）

| key | DOI | Crossref 命中 title/authors/venue | 状态 |
|---|---|---|---|
| srinivasan2022prioritization | 10.1002/stvr.1807 | Metamorphic relation prioritization … / Srinivasan, Kanewala / STVR 32(3) 2022 | ✓（首查瞬时空，重试命中）|
| saha2019faultdetection | 10.1109/aitest.2019.00019 | Fault Detection Effectiveness … Supervised Classifiers / Saha, Kanewala / AITest 2019, p157-164 | ✓ |
| spieker2024trajectory | 10.1145/3679006.3685071 | Evaluating Human Trajectory Prediction with MT / Spieker, Belmecheri, Gotlieb, Lazaar / MET 2024, p34-40 | ✓ |
| spieker2025multimodal | 10.1016/j.infsof.2025.107890 | Metamorphic Testing of Multimodal Human Trajectory Prediction / Spieker et al. / IST 188:107890 (2025) | ✓ |
| kanewalaBieman2014slr | 10.1016/j.infsof.2014.05.006 | Testing scientific software: A SLR / Kanewala, Bieman / IST 56(10):1219-1232 | ✓ |
| yan2024elliptic | 10.1002/stvr.1912 | MT on Scientific Programs … Second-Order Elliptic DEs / Yan, Zhu / STVR 35(1) | ✓ |
| stevens2025mars | 10.1109/ICSE-NIER66352.2025.00012 | Model Assisted Refinement of MRs … / Stevens, Kjeer, Richard, Valeev, Cohen / ICSE-NIER 2025, p31-35 | ✓ |
| wang2022mridentification | 10.1145/3514105.3514109 | Dynamic Identification … Separation of Input/Output Pattern / Wang, Yang, Li, Liu, Yan, Fu / ICWCSN 2022, p16-24 | ✓ |
| fu2021burnup | 10.1109/IAECST54258.2021.9695750 | Identification Method … Burnup Calculation Program / Fu, Yang, Li, Wang / IAECST 2021, p811-818 | ✓ |
| li2022nuclearmr | 10.3389/fenrg.2022.788753 | Lightweight Verification … MR for Nuclear Power Software / Li, Yang, Yan, Liu, Liu, Sun / Front. Energy Res. 10 | ✓ |

## 页码复核 —— 已逐条比对，全部一致

- 5 篇会议论文 bib 页码与 Crossref 精确匹配：saha 157-164、spieker2024 34-40、stevens 31-35、wang 16-24、fu 811-818（全 ✓）。
- srinivasan(STVR e1807)、yan(STVR 35(1))、li(Front. Energy Res. 文章号 788753) 采用期刊文章号/卷期格式，Crossref 同样无传统页码，正确。
- **结论：10 条 title/authors/venue/year/pages 全部一致，无需改 bib。**

## △ 既有清理项（不影响真实性门槛）
- 既有清理项（不影响真实性门槛）：`kirsch2024naca` 空页字段；`lim2026/shikhman2026` 补 arXiv id；`zhao2026noether`→`li2026noether` 键名；`yang2021hydromt` number=9。
