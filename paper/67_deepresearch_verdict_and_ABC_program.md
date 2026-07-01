# 67 · Deep-Research 学术水平裁定 + A+B+C 执行程序（用户拍板 2026-07-01）

> 日期：2026-07-01 · 触发：用户「使用 deep research 评估本文学术水平，基于现有证据（理论+实证），
> 努力提升（补实验/完善理论框架/提炼聚焦核心问题）可达上限，客观给天花板与最适合期刊」。
> 决策：用户选 **A+B+C 三杆全上，目标 TOSEM 稳投**。
> 方法：亲读 `submissions/RESS/main.tex` 全稿做 ground truth + 派代理用 paper-search（crossref ISSN/dblp/semantic）
> 独立核实 7 类 venue 近 2 年真实证据门槛。结论可回溯到手稿行号 + 真实检索到的论文。

---

## 一、当前档位（现稿原样）

**一句话：理论有硬核、诚信满格、但实证规模压在单 SUT 的"聚焦方法稿"。现稿原样归宿 = IST/STVR 档（中 Q1），达不到 TSE/TOSEM，够不着 CCF-A。**

| 维度 | 判定 | 证据（手稿行号）|
|---|---|---|
| 新颖性 | 真且 crisp | floor gate 对 Eniser/Duque-Torres 有明确 delta（L125）；niche 检索证实几乎无人占 |
| 理论深度 | 高于典型 SE 稿 | floor 闭式 + 0.5% 预测器 + a-priori bound + O(h) R²=0.9999 + 跨两拓扑稳定（L470）|
| 实证规模 | 弱（限高主因）| 主定量证据单 MGN checkpoint；K=6 的 S0 复用 pilot、同架构同数据集（L458）|
| 对比强度 | 自陈互补非超越 | complementarity not superiority（L155）；无击败 SOTA、无真实 bug |
| 故障证据 | 自造 gross corruption | 5/10「任何检测器都能抓」（L424）；无独立真实缺陷语料 |
| 诚信 | 满格（罕见优点）| claim ledger + typed verdict + 处处边界句 + 宽 CI 照实 |

## 二、venue 真实门槛对标（paper-search 独立检索）

| Venue | 证据门槛 | 本主题先例 | 对「单SUT+complementarity+seeded」现实档 |
|---|---|---|---|
| IST | 中 | 有（MT-Nod 2025 / credit-score 2025）| **可接收**（但已桌拒，须重框定）|
| STVR | 中 | 有（Traon&Xie 2024 / Kanewala 科学软件）| 可行（**非候选**，用户约束排除）|
| **TOSEM** | 高 | 多（CCML 2026 / MET-MAPF / MR-Scout，**均首创框架不靠击败 SOTA**）| 边缘偏弱 → **补强后最适合**|
| EMSE | 中–高 | 少 | 偏弱（样本/统计功效是硬点）|
| TSE | 高 | 多 | 偏弱（偏好真实 bug + 多系统）|
| RESS | 高（后果维度）| **0 篇 MT（已证实）**| 高风险 novel-to-venue |
| ICSE/FSE/ISSTA/ASE | 最高 | 多 | **结构性不匹配**（要真实系统真实 bug）|

**两个硬锚点**：① RESS 近年 0 篇 MT 先例（crossref ISSN 精确证实）；② 「MT of SciML surrogate（neural operator/MeshGraphNets）」几乎空白 niche，最近真实先例仅 Reichert 2024（HESS，水文科学刊，非 SE，多模型对比）。

## 三、三杆补强 ROI + 可达上限（核心分析）

**关键洞察：本文强弱高度不对称——理论强、实证弱。三杆 ROI 天差地别，且杆 A 有结构墙。**

- **杆 A｜补实验（贵、高风险、有结构墙）**：SciML surrogate 领域**无现成真实缺陷语料**（自建=Defects4J-for-SciML 社区资源级、多年，`paper/51`）。故**单靠补实验也到不了 CCF-A/TSE**（它们要的「真实 bug」本领域产不出）。上限≈把 IST 档做扎实、够 TOSEM 门槛一半。
- **杆 B｜完善理论（中成本、低风险、最高 ROI）⭐**：floor gate 现仅在结构网格 + 单 Delaunay 严格证明（general unstructured-mesh bound 明写 future work，L575）。补成一般非结构网格（或良定义网格类）soundness 定理 → floor gate 从「单网格好启发式」升为「可证明健全的可采性判据」。**这正是 TOSEM 收货币（framework+soundness），打在强项、不依赖真实缺陷语料、风险有界。单这一杆就能把天花板从 IST 抬到 TOSEM。**
- **杆 C｜聚焦核心（最便宜、感知增益大）⭐**：现稿是「gate+MR card+typed verdict+coverage」四件套，MR-card/typed-verdict 偏增量。提炼成单一贡献——**「数值可判定性作为 oracle-free 测试的可采性判据」，以 floor 理论为脊柱**——novelty 立刻 crisp，部分解决 IST 桌拒的「importance 不清」。

| 路径 | 成本/风险 | 可达上限 |
|---|---|---|
| 只表面重投（C 轻）| 低 | IST/STVR（中 Q1）|
| 补实验冲规模（A）| 4–6 月/HIGH | 封顶 TOSEM 门槛下沿，够不到 CCF-A |
| 理论+聚焦（B+C）⭐ | ~3–5 月/MED | **TOSEM（现实天花板）**|
| **三杆全上（A+B+C）** ← 用户选 | **6+ 月/MED-HIGH** | **TOSEM 稳投 + TSE 可冲一次**|

## 四、天花板与最适合期刊

- **理论上限**：TSE/TOSEM（CCF-A 期刊）。**ICSE/FSE/ISSTA 结构性够不着**（接收货币=真实系统找到确认 bug，本领域无真实缺陷语料，补实验翻不过这堵墙）。
- **现实可达天花板**：**TOSEM**（走 B+C，A 作 breadth 支撑）。
- **最适合 = TOSEM**（既是天花板又最适合，因其接收货币匹配本文**可补强的强项**、代偿本文**永远产不出的短板**）：① DNA 吻合（CCML/MET-MAPF/MR-Scout 均首创框架不靠击败 SOTA）；② 短板可代偿（单 SUT 窄证据面可被强理论新颖性补，TSE 要的真实 bug 不可代偿）；③ 强项被奖励（floor 理论在 IST 是加分、在 TOSEM 是收货币）。
- **Reviewer-2 最狠一条（=杆 B 存在理由）**：「floor gate 只在一张部署网格+一个 Delaunay 被证明，换任意非结构网格是否成立你自己写进 future work——那真正被证明的只是『这张网格上容差要大于地板』，凭什么算 TOSEM 级？」→ 补 general-mesh soundness 直接消掉，是天花板判断的枢轴。

---

## 五、决策：A+B+C 三杆全上 → TOSEM 稳投

用户拍板：**不走单杆，三杆全上，理论优先，做到 TOSEM 稳投（robust 而非边缘）**。「稳投」判据 = 杆 B 理论闭合 + 杆 A 多 SUT breadth + 诚信 ledger 干净，三者齐备方投。

### 执行程序（理论优先排序，带 gate；精修 `paper/66` 的实验-only 排序）

> 排序原则：杆 C 先行定靶（便宜）→ 杆 B 为枢轴主攻（决定 TOSEM 成败）→ 杆 A 并行作 breadth 与必要性演示。杆 B 不闭合不投稿。

- **Phase C｜聚焦重框定（1–2 周，先做，写作任务）**
  把 thesis 收敛到「numerical-decidability admissibility 判据」单一贡献；contributions 重排以 floor gate + 理论为脊柱，MR-card/typed-verdict 降为支撑机制。产出=新版 intro/contributions 骨架 + 弃增量卖点清单。**过 gate**：核心问题一句话可述、novelty delta 一句话锁定。

- **Phase B｜floor 理论一般化（枢轴，1.5–3 月，MED 风险）⭐**
  ① 形式化 admissibility 谓词 + 四条件 + soundness 命题；② 把 a-priori floor bound 从结构网格+单 Delaunay 推广到一般非结构网格类（或良定义子类）；③ 诚实刻画失效边界（何种网格/算子下不成立）。**过 gate**：存在可陈述条件下的 soundness 定理 + 证明或严格 a-priori bound，能消掉 Reviewer-2 枢轴反驳。**不闭合 → 触发降落评估（重框定 IST）。**

- **Phase A｜实验 breadth + 必要性演示（并行，1.5–2 月，部分从现有数据）**
  ① measured-advantage 证据表（从 committed C38/C42：MGN MR 抓 2/10 accuracy 漏、PointMLP 门控 0% vs 被拒模板 100% 误警）；② 独立多 SUT 证门控价值（0%-vs-100% FP）跨架构×跨物理域 ≥3–5 稳定（airfoil 训到位 + 补 2–3 域）；③ 可辩护真实故障基准（最稀缺，现降为 breadth 支撑非唯一命脉）；④ 全 baseline head-to-head。**过 gate**：门控价值在 ≥3 独立 SUT 方向一致。

- **Phase L｜诚信 ledger 升级（贯穿 A，硬 gate）**
  measured-advantage 新增 claim ID（C42 现禁 superiority，不得改写蒙混，prose≤ledger，§4/§6.4）；同步 guards + 两 validator rc=0。

- **Phase S｜TOSEM 投稿包（2–3 周）**
  soundness 定理为中心的框架化写作 + 必要性叙事（complementarity → "catch what others are structurally blind to"）+ 建 `venues/TOSEM.md`（acmart 双盲/CCF-A/CAS 1区）+ TSE 等价包（IEEEtran 单盲）备选冲一次。

**总工期** ~6+ 月，MED-HIGH；**枢轴风险=杆 B 理论能否一般化**（低于杆 A「measured-advantage 在真实语料存活」的核心不确定，因打在本文强项）。

### 边界铁律
- prose≤ledger：superiority/soundness 先落 claim/定理 + 证据，再写正文。
- 实事求是：杆 B 若某类网格证不出，如实刻画失效边界，不掩盖（§6.4）。
- 姊妹库只读；SE 化框定（oracle/MT/admissibility/故障归因语汇），弱化纯 CFD 物理叙事。
