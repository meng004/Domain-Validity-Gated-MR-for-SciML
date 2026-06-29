# 52 · IST 桌拒诊断与下一步投稿评估

> 日期：2026-06-29
> 输入材料：
> - 投稿版 PDF：`dist/IST-submission-2026-06-27/main.pdf`（50 页）
> - IST 可审性判据社论：Staron et al., *How not to get your paper rejected — From the editors' notebook*, Information and Software Technology 197 (2026) 108197（4 页，DOI 10.1016/j.infsof.2026.108197）
> - 拒稿信：INFSOF-D-26-01271，EIC Miroslaw Staron 签发

---

## 0. 关键事实：这是 EIC 本人的桌拒，不是同行评审退稿

拒稿信中的 "Reviewer comments" 与正文 desk-reject 模板**一字不差**，且都指向 Staron 自己撰写的社论 `10.1016/j.infsof.2026.108197`。即：判定"不适合送审"的人，正是那套可审性判据的作者，用他自己发表的分类法在 suitability 扫描阶段否掉了本文。诊断必须严格对照该社论，而非猜测匿名审稿口味。

社论给出的 2025 桌拒分布：

| 类别 | 占比 |
|---|---|
| 低新颖（Low novelty） | 56.7% |
| 超范围（Out of scope） | 32.3% |
| 质量不足（Insufficient quality） | 7.7% |
| 不成熟（Premature work） | 3.3% |

三道闸门：**Scope**（是否面向软件工程师）、**Novelty & impact**（能否超出单一案例泛化）、**Research excellence**（含 "write in the style appropriate for the audience" / "treat reviewers as your friends"）。

**排除误区：不是格式问题。** 投稿包合规——结构化摘要五段（Context/Objective/Method/Results/Conclusion）齐全、Highlights 5 条、elsarticle、单盲保留作者、字数在 15k 内。问题全在实质/范围/成熟度/可读性。

---

## 1. 拒稿原因（按优先级）

### P1 — 超范围反射：读起来像"把别领域 ML 搬来做 V&V"，SE 贡献被物理术语淹没
对应 Out-of-scope（32.3%）+ Low-novelty 第一信号。

社论原话两处几乎为本文量身定做：
- 超范围："applications of software/IT in other fields … our journal focuses on **software engineers as its audience**"；
- 低新颖被 ML 类占据："apply machine learning, neural networks, or large language models **from other domains, without contributing to the development of the models themselves**"。

本文摘要/标题/引言第一屏给编辑的视觉是：MeshGraphNets、cylinder-flow、divergence、mirror-y symmetry、PINN、FNO、compressible airfoil、Reynolds–Strouhal、Noether。SE 真正贡献（"用数值可判定性给候选 MR 把关的 admissibility gate"）被埋在物理黑话下。社论核心闸门 "Is this a problem that concerns a software engineer?" 在一次略读里过不了——问题表述是 SciML/物理的，不是 SE 测试从业者一眼能认领的痛点。**第一杀手：编辑在 suitability 阶段把它归成了"计算物理/SciML 论文"。**

### P2 — 不成熟/经验不足：本质上一个 SUT、一个任务、全是自注故障
对应 Premature work + Insufficient quality。

社论 Premature 原话："test it against only a small number of existing approaches and **on only one or a few datasets** … Simply training a new model and evaluating it on one or two datasets will almost certainly be obsolete"；它想要 "broadly applicable methods, rigorously compared … assessed in real-world scenarios beyond standard benchmark datasets"。

本文恰是反面，且为作者反复自承：
- 主证据 = **一个**训练好的 MGN cylinder-flow checkpoint（S0）；K=6 roster 自己写明 "S0 reuses the pilot checkpoint, **rather than six independent SUTs**"——复现非独立样本；
- 第二任务 airfoil 代理**欠训练**（rollout L2 0.92），明说只用于 "typed gate discrimination, not model accuracy"；
- 故障**全是作者注入**的 seeded faults，检出 5/10，10/10 处精确二项 CI 宽到 [0.69,1.00]；
- 通篇 "bounded / pilot / underpowered / not a real-world defect-detection rate / future work"。

编辑读到的不是"严谨经验研究"，而是"一个模型、一两个数据集、无真实缺陷、无横向胜出对比"——正中 Premature。

### P3 — 新颖性难以提取、看着像增量
对应 Low novelty（56.7%，社论最大类）。

社论低新颖首句即 "the manuscript **does not clearly articulate the importance** of the research"，并点名 "tool/method 描述多于对 SE 的贡献" / "overly incremental / 很窄"。

本文单一方法思想——"把候选 MR 可采性 gate 在数值可判定性上（tolerance 压过算子误差地板）"——本身窄；论文又主动声明：以候选 MR 为输入、**不发明 MT、不声称优于基线、不是新的 MR 识别方法**，且 Related Work 承认 Duque-Torres / MetaTrimmer / relaxations 三线 "closest to this paper"。编辑易将 delta 读成"MR 适用性已有工作的窄域细化"。**为诚实做的全部 disclaim，在 suitability 阶段被读成"作者自己都说贡献有限"。**

### P4 — 可读性/受众：自造术语 + 重度对冲，一遍读不出贡献
对应 Research excellence 的 "write in the style appropriate for the audience" / "treat reviewers as your friends"。

MetaPattern、MR family、f_inv.eqv sans-serif 算子记号、out-of-relation-domain、validity-gated V&V asset construction……单摘要堆十几个新词，每个结论外包三层边界声明。EIC suitability 扫描无法快速判断"贡献是什么、为什么重要"。此条与 P1/P3 叠加放大：importance 讲不清，正是低新颖头号触发器。

### P5 — 自我框定抽掉了"如何推进领域"的肯定句
对应 Novelty & impact 闸门，几乎等于自认。

社论问 "How will this manuscript advance the field? 要么经验评估、要么有可信方式表明结果能 scale beyond the sample"。本文明确写结果**不能**外推出样本（"not population-wide / bounded / no general claim"）。在 suitability 关，相当于自交 impact 闸门钥匙——没有一句"本文把领域往前推了 X"能让编辑抓住。

### 拒稿机理一句话
合规没问题；它在 EIC 的 30 秒可审性扫描里同时撞上"超范围（看着是 SciML 物理）+ 不成熟（单 SUT、自注故障）+ importance 讲不清（自造术语 + 全程对冲）"。三者任一在他自己的分类法里都够桌拒，何况叠加。

---

## 2. 下一个最佳期刊

先排除：**STVR**（MT 天然归宿，但项目标准约束已禁用）；**TSE / TOSEM / EMSE**（要多个真实 SUT、真实缺陷、明确胜出对比，差距以"月"计，非 next-best）。剩两条策略路线，取舍取决于作者想保持哪种身份。

| 候选 | 路线 | 为什么合适 | 与现稿差距 | 工作量 |
|---|---|---|---|---|
| **Software Quality Journal**（Springer, Q2）**— 首选** | 留在 SE 测试 | 范围明确含 V&V/测试方法/质量保证；对"方法 + 有界案例研究"最宽容；新颖性/经验门槛低于 IST/JSS；Springer 非 Elsevier，无"姊妹刊已拒"包袱 | 主要是重定位 + 去术语 + 诚实处理单 SUT，基本不需新实验 | 低–中（数周写作） |
| **Journal of Systems and Software**（Elsevier, Q1）— 同档备选 | 留在 SE 测试 | 与 IST 同档，MT/测试方法文常登；想保 Q1 时选择 | 同上，外加很可能要 ≥1 个真正独立真实 SUT 或 1 个真实（非自注）缺陷挡 premature | 中–高 |
| **Reliability Engineering & System Safety**（Elsevier, Q1）/ **Journal of Computational Science**（Q2）— 换身份 | 重定位为"可信 SciML 代理验证" | MeshGraphNets/CFD/PINN 在此是**资产非负债**；契合"高可信计算/核行业"署名；无 SE 的 out-of-scope 反射 | 术语改向该受众，弱化 MT 黑话，强化 trustworthy surrogate validation | 中 |

### 推荐
**以 Software Quality Journal 为主投。** 理由：接受概率 ÷ 改写成本最高——现有证据流水线、claim ledger、真实运行扎实，硬伤是定位/可读性/成熟度，而 SQJ 恰是对"方法 + 有界 demonstration"最不挑、且不会因物理外壳反射判超范围的 SE 刊。

- 若更看重 Q1 且愿补一个独立真实 SUT → **JSS**。
- 若认同本质是 SciML-V&V（IST 反复判超范围其实在说这件事）→ **RESS**，天花板最高、与署名最契合的换道选择。

### 无论投哪家，三件必做（数据不是问题，定位才是）
1. **倒置叙事**：摘要/引言第一段先讲 SE 测试痛点（oracle-free 代理软件，MR 失败时分不清真缺陷/越域/数值噪声），物理放到方法层再展开。
2. **大幅去黑话**：砍掉 MetaPattern / MR-family / sans-serif 记号等自造体系，让贡献一遍读懂。
3. **改对冲的措辞而非内容**：把"我们什么都不声称"改成"我们在 X 范围内确立了 Y"——保留诚实边界，但要有一句肯定的 impact 句。

---

## 3. 后续动作（待用户拍板）
- 选定目标刊后，产出一版重定位方案：新摘要 + 引言开头 + 术语精简清单 + 针对该刊的逐项 gap 核对。
