# 候选期刊适配分析（v2，deep-research 复核更新版）

> 目标：科研工作流 Phase 0 期刊定位。  
> 初版：2026-06-02；本版复核更新：2026-06-04（5 路并行检索 + 关键声明对抗性核验，7/7 关键声明 VERIFIED）。  
> 数据基准：JCR 2024（2025-06 发布，JCR 2025 预计 2026-06 下旬发布、尚未出）；中科院分区 2025 年 3 月升级版（经 letpub/iikx 双镜像交叉，未直接登录 fenqubiao.com）。  
> 筛选权重（用户确认）：scope 契合度 + 影响因子/分区 + 录用难度/周期 + OA/费用。

## 0. 与初版结论的关键差异

初版（2026-06-02）推荐 **STVR 为首选**。本次复核发现两点实质性新证据，导致排序调整：

1. **STVR 计量指标显著弱于预期**：JCR 2024 IF 仅 1.2（2023 年 1.9 → 下滑 ~36%），JCR **Q4**，中科院 2025 版**大类 4 区**非 Top。若分区/影响因子在考核中有权重，STVR 不宜作首选。
2. **MT/MR 识别社区的主阵地证据更新**：IST 已发布 **Metamorphic Testing 专刊**（客座编辑 Huai Liu、Aldeida Aleti、Aitor Arrieta——均为 MT 核心学者；截稿 2025-04-13，当前已关闭），且 2026 年仍有多篇 MT 文章 in press；TOSEM 近两年密集发表 MR 识别方向论文（MR-Scout 2024、MR Generation Roadmap 2025、MT for Deep Code Models SLR 2025），且 2025 版中科院分区升为 **1 区 Top**、ACM 自 2026-01-01 全面 OA（ACM Open 成员机构免 APC）。

**更新后结论：首选 IST，冲高 TOSEM，稳妥备选 JSS，保底 STVR。ASE Journal 与 SQJ 降级排除。**

## 1. 投稿定位（不变）

本研究定位为**软件测试 / V&V 论文**：oracle problem 下面向科学 ML 代理模型（以 MeshGraphNets 圆柱绕流为核心场景）的物理约束 MR 识别与工程化框架。v2.1 贡献顺序为：C1 物理 MR validity rubric；C2 NOETHER-guided executable oracle-free MR framework；C3 hierarchical failure localization；C4 三 SUT 经验评估与 MetBench 可复现资产。不是 CFD 论文，也不是 AI 模型论文。

## 2. 核心数据对比

| 期刊 | IF (JCR 2024) | JCR 分区 | 中科院 2025 版 | 周期（官方/社区） | 录用难度 | OA/费用 |
|---|---|---|---|---|---|---|
| **IST** (Elsevier) | 4.3 | Q1 (SE 21/129) | 大类 2 区 | 首决 7 天（含 desk）；投稿→录用 ~217 天 | 中等（社区"较易"） | Hybrid；订阅路线免费；APC $3,890 |
| **TOSEM** (ACM) | 6.2 | Q1 (SE 9/128) | **1 区 Top**（2025 升级） | 常规 >12 周；Fast-impact track 首审 ≤90 天 | 高 | **2026 起全 OA**；ACM Open 机构免 APC，否则 2026 补贴价 $250–1,000 |
| **JSS** (Elsevier) | 4.1 | Q1 (SE 23/129) | 大类 2 区 | desk 6 天；评审后决定 89 天；投稿→录用 ~256 天 | 官方接收率 ~20% | Hybrid；订阅免费；APC $3,670 |
| **STVR** (Wiley) | **1.2**（下滑） | **Q4** | **大类 4 区** | 社区 >12 周；年发文量小（2024 约 46 篇） | 低（社区"容易"） | Hybrid；订阅免费；APC 未核实 |
| TSE (IEEE) | 5.6 | Q1 | 1 区 Top | 社区 ~6–12 月，偏慢 | 很高 | Hybrid；订阅免费；APC $2,800 |
| EMSE (Springer) | 3.6 | Q1 | 大类 2 区 | 首轮 ~12 周 | 高 | Hybrid；APC $3,390 |
| ASE J (Springer) | 3.1 | Q2–Q3 | **4 区（自 2 区/小类 1 区大幅降级）** | 首决中位 16 天；社区 ~3 月 | 中 | Hybrid；APC $3,390 |
| SQJ (Springer) | 2.3 | Q2 | 4 区（自 3 区降） | 首决中位 12 天 | 低 | Hybrid；APC $3,390 |

## 3. 推荐排序与理由

### 第一推荐：Information and Software Technology (IST)

**综合最优：四项权重全部达标。**

- **Scope 契合**：官方 scope 明列 "Software testing and verification & validation" 与 "Empirical studies"；且已发布 **MT 专刊**（编辑含 Huai Liu、Aleti、Arrieta，截稿已过），证明编辑团队对 MT/MR 识别有直接兴趣与审稿能力。近年已发 MT-Nod（ADS 蜕变测试）、MT 国际象棋引擎复制研究、DL 系统覆盖测试等。
- **分区**：Q1 / 中科院 2 区，比 STVR 高两档。
- **难度/周期**：投稿→录用约 7 个月，desk 决定 7 天；社区评价"较易"，是 Q1/2 区刊中相对友好的。
- **费用**：订阅路线免费。
- **风险**：IST 偏好实证证据与实践改进叙事；单一 MeshGraphNets case 需强化为"多 MR × 多 fault type × 多 metric"的实证矩阵。系统综述类强势期刊，方法论文需 validation 扎实。
- **投稿策略**：以"physically grounded MR identification framework + 可复现实证评估"为主线，走 IST 常规 research paper 通道；MT 专刊只作为社区适配和相关工作证据。补 2–3 个 competing baselines（人工 MR、通用 MR 推荐方法、纯精度评估）。

### 第二推荐（冲高）：ACM TOSEM

**MR 识别方向当前最高水位的期刊阵地。**

- **Scope/社区契合**：2024–2025 连续发表 MR-Scout（从既有测试用例自动合成 MR）、"Metamorphic Relation Generation: State of the Art and Research Directions"（MR 生成路线图）、MT for Deep Code Models SLR——本文的"物理语义 MR 识别"正好回应该路线图指出的领域语义 MR 缺口，引用对话关系天然成立。
- **分区**：2025 版升为中科院 **1 区 Top**，IF 6.2，CCF-A。
- **周期**：Fast-impact track 首审 ≤90 天（官方承诺）。
- **费用**：ACM 2026-01-01 起全面 OA；ACM Open 成员机构（2,600+ 所）免 APC，非成员 2026 补贴价低至 $250。
- **风险**：录用门槛最高；单一 SUT 的 case study 大概率不够，需要方法框架的可迁移性论证（至少在第二个 mesh-based simulator 或注入故障矩阵上验证）+ 强 related work 对话。新任 EiC Abhik Roychoudhury（2025 起）。
- **投稿策略**：仅当实验扩展到 fault injection + 多模型/多场景、且 MR taxonomy 有形式化表述时再投；否则先投 IST。

### 第三推荐（稳妥同级备选）：Journal of Systems and Software (JSS)

- **契合**：scope 明列 V&V/testing 与 AI applied in SE；**JSS Open Science Board** 对 MetBench 可复现资产是直接加分项；近年发 MT（GUI 鉴权漏洞、LLM 代码生成对称 MR）与 ML 测试实证。
- **分区**：Q1 / 中科院 2 区，与 IST 同档。
- **难度/周期**：官方接收率 ~20%，投稿→录用 ~8.5 月，略慢于 IST。
- **与 IST 取舍**：JSS 要求贡献对 SE 共同体更广的影响面；IST 有 MT 专刊证据、周期略快，故 IST 在前。若被 IST 拒，JSS 是最自然的平移目标（注意 cover letter 重写为"方法+开放科学资产"叙事）。

### 第四推荐（保底）：STVR

- **契合**：依然是主题契合度最高的刊——2023–2026 持续发表 MT/MR 论文，且 2025 年刚发"Metamorphic Testing on Scientific Programs for Solving Second-Order Elliptic Differential Equations"（Yan & Zhu, STVR 35:e1912），与本文"科学程序 MT"叙事几乎同频；MRGS-ART、MR 预测（code representation learning）等也在其中。
- **硬伤**：IF 1.2 / JCR Q4 / 中科院 4 区且持续下滑；年发文量小、相当比例为 ICST 特刊扩展。
- **定位**：若 IST/JSS 均不顺利、或考核不计分区而只求进入 MT 核心社区对话，STVR 录用确定性最高、审稿人最懂行。

## 4. 降级与排除

- **ASE Journal**：2025 版中科院分区从"大类 2 区/小类 1 区"**断崖式降至 4 区**（已双镜像核实）；2023–2026 未检索到任何 MT 论文。两项均不利，移出候选。若日后做成全自动 MR 识别工具链可重评。
- **SQJ**：降至 4 区；虽有 MT 论文（neuron coverage MT 2025、MR composition 成本效益 2026），但与 STVR 同档分区下，STVR 社区契合更高。仅作最终保底。
- **TSE**：1 区 Top、有 GenMorph（GP 自动生成 MR, 2024）直接先例，但社区周期 6–12 月+、门槛与 TOSEM 相当而 OA 政策不如 TOSEM（2026 起）优惠。若冲顶级，TOSEM 优先于 TSE。
- **EMSE**：2 区 Q1 但要求强实证框架；本文以方法框架为主线，框架不改不投。
- 领域刊（J. Computational Science、CPC、EAAI）：维持初版判断，不投——贡献在软件测试而非计算方法。

## 5. 对论文写法的要求（按 IST 首选更新）

主线不变：oracle problem → MT 关系式 oracle → 物理语义 MR 识别缺口 → 框架 → 圆柱绕流 case study → failure signatures。新增三点：

1. **实证矩阵**：MR 类型 × fault/mutation 类型 × metric × 判定结果，作为 IST 偏好的 empirical validation 核心证据。
2. **Baselines**：人工经验 MR、至少一种自动 MR 推荐/生成方法（可引 MR-Scout / GenMorph / MR generation roadmap 作对话对象）、纯精度评估。
3. **开放资产**：MetBench case JSON、runner/parser、复现实验包公开（GitHub + Zenodo DOI）——对 IST/JSS 均加分。

## 6. 已知不确定性

- 中科院分区数据来自 letpub/iikx 镜像（官方 fenqubiao.com 需机构登录），两镜像一致；投稿前建议用机构账号最终确认。
- JCR 2025（2025 年度 IF）预计 2026 年 6 月下旬发布，发布后应复查 STVR 是否继续下滑、IST/JSS 是否稳定。
- IST MT 专刊已核实为关闭征稿，Submission Deadline: 2025-04-13；投稿前只需复查是否有新的续办专刊。
- STVR 的 APC 具体金额未核实（Wiley 价目表无法访问）；官方接收率/审稿周期 Wiley 未公开，相关数字均为社区数据。

## 7. 主要来源

- IST scope/专刊/指标：https://www.sciencedirect.com/journal/information-and-software-technology ；MT 专刊 https://www.sciencedirect.com/special-issue/104J787KPKV ；https://www.iikx.com/sci/technology/13193.html
- TOSEM：MR-Scout https://dl.acm.org/doi/10.1145/3656340 ；MR Generation Roadmap https://dl.acm.org/doi/10.1145/3708521 ；分区 https://www.iikx.com/sci/technology/9706.html ；ACM OA https://www.acm.org/articles/bulletins/2026/january/acm-open-access ；IF https://www.acm.org/media-center/2025/july/impact-factors-2025
- JSS：https://www.sciencedirect.com/journal/journal-of-systems-and-software ；https://www.letpub.com.cn/index.php?journalid=5213&page=journalapp&view=detail ；https://wos-journal.info/journalid/15378
- STVR：https://wos-journal.info/journalid/20039 ；https://www.iikx.com/sci/technology/17110.html ；科学程序 MT 论文 https://onlinelibrary.wiley.com/doi/10.1002/stvr.1912
- TSE：https://www.iikx.com/sci/technology/13054.html ；GenMorph https://ieeexplore.ieee.org/document/10542726/
- ASE J 降级：https://www.iikx.com/sci/technology/10664.html ；SQJ：https://link.springer.com/journal/11219 ；EMSE：https://www.iikx.com/sci/technology/12120.html
- JCR 时间线：https://clarivate.com/news/clarivate-unveils-the-2025-journal-citation-reports/
