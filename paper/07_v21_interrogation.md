# 方案 v2.1 拷问报告（deep-research 对抗性评审，第二轮）

> 日期：2026-06-04  
> 对象：`06_paper_plan_v2.md`（v2.1，NOETHER + 层次分类模型双理论基座版）  
> 方法：4 路并行检索（出版伦理 / 流体物理 / 中文文献规范 / Lie 对称在先性），逐项裁决。  
> 总裁决：**方案骨架成立，但有 1 个致命物理错误（Noether 叙事）、1 个物理无效 block 映射（时间反演）、2 篇 2026 年新竞品必须处理；其余风险均有可执行的化解路径。**

---

## 拷问一：Noether 定理叙事 —— 🚨 致命，已被物理学击穿，必须重写

**v2.1 原话**："守恒律 MR 可经 symmetry block 由 Noether 对应导出（Noether 定理：连续对称 ↔ 守恒律——与框架命名同源，叙事上极强）"。

**裁决：FALSE，会被任何流体力学背景的审稿人判定为"作者不懂物理"。**

- Noether 定理要求变分/Lagrangian 结构；粘性 N-S 方程**非变分**——这是 **Millikan (1929) 定理**，2024 年 JFM 论文仍在引用（"A canonical Hamiltonian formulation of the Navier-Stokes problem", JFM 984:A27）。
- **div u = 0 根本不是 Noether 守恒律**：它是不可压缩流的连续性方程/运动学约束，压力是强制该约束的 Lagrange 乘子——结构上与"对称导出守恒律"相反。理想流体变分形式中，particle-relabeling 对称经 Noether 给出的是 **Kelvin 环量定理/cross-helicity**，不是质量守恒（Cotter & Holm, arXiv:1808.05486；Webb, Rev. Mod. Plasma Phys. 2024）。
- **讽刺点必须正视**：框架名叫 NOETHER，但本域恰恰不能用 Noether 定理。若不改写，这是审稿人最容易抓的把柄。

**修正（代价为零，MR 一条不少）**：
1. 散度 MR 改述为"**不可压缩流的质量守恒/连续性约束**"，并引 Millikan 1929 说明**为何不走 Noether 路线**——化攻击点为专业性展示。
2. 对称 MR 改由 **N-S 方程的 Lie 点对称群**奠基（Bytev 1972; Lloyd 1981; Olver GTM 107; Frisch 1995 §2.2）——无需 Lagrangian，严格成立。
3. §2.3 理论回馈的双向设计**保留**，但表述改为："散度约束 MR 是否落在 symmetry block 经 Translate 的像内"——若不在（预期如此，因为它是约束而非对称像），即为 conservation/constraint 候选第九 block 的 empirical witness。**物理修正后，双向设计反而更可能落在'第九 block witness'一侧，理论回馈更实。**

## 拷问二：时间反演 block 映射 —— 🚨 物理无效，必须显式排除

**v2.1 原话**：自回归演化算子 → "Time-reversal / Qualitative-dynamics (T*, D*)"。

**裁决：粘性破坏时间反演对称**（耗散项在 t→−t, u→−u 下反号；arXiv 1801.00944、Gallavotti arXiv:1711.05684 整个文献方向的前提就是粘性 N-S 不可逆）。涡脱落 Re≈47–200 区间不可逆性显著（Stokes 极限可逆性与本域无关）。

**修正**：rollout 前缀一致/确定性 MR 挂 **qualitative-dynamics（演化半群性质）**，**显式声明排除 time-reversal MR 并给物理理由**——论文中这一排除本身就是 validity rubric 起作用的最佳示例（"MR 集是物理过滤的，不是对称性照单全收"）。

## 拷问三："经典 Lie 对称群早已给出这些变换" —— ⚠️ 审稿人数学上正确，立场必须重摆

**杀手级质疑**：镜像/平移/缩放/Re-St 全部可从 N-S 经典对称群（Bytev 1972; Lloyd 1981——无穷维群，含任意加速参考系）直接读出，"要框架何用？"

**裁决：数学上对，但可防御——前提是论文主动缴械再反击。**

- **不能声称**：发现这些变换；首创"对称用于求解器校验"（Galilean 不变性测试是 CFD 老传统，Athena code 文档级实践；Hiremath 三部曲——注意还有第三篇 arXiv:2206.05457 此前未掌握，必须补引）；首创"检查流体 ML 模型对称合规"（见拷问四）。
- **可守的阵地**（检索确认无在先工作）：
  1. **非对称 blocks 是经典 Lie 分析完全不覆盖的**：order（St 随 Re 单调）、limit（Re→Re_crit 起涡分岔）、method-comparison（跨实现）、qualitative-dynamics（尾迹拓扑/半群）——Lie 群不产这些，等变评估论文也不测这些。**这是对杀手质疑的核心反击：symmetry 只是 8 block 之一。**
  2. Translate 闭包（Thm 1）+ 多项式可判定（Thm 2）——Lie 文献只告诉你变换存在，不给封闭、可判定、带 verdict 语义的可执行 MR 目录。
  3. **BC 兼容子群选择**：圆柱几何+入流边界破坏了无穷维群的绝大部分，只剩镜像/时间平移/Re-St 缩放等有限子集可测——把"选 BC 兼容子群"写成框架的显式步骤（而非被审稿人指出的遗漏）。
- **写法**：设一段"the symmetry block is classically determined"，正面引 Lloyd/Bytev/Olver，声明 NOETHER 把经典群**作为 symmetry block 的输入消费**（上游代数 curation 正是经典知识的入口）——主动缴械，把战场移到非对称 blocks 与可执行性。

## 拷问四：2026 年两篇等变评估新竞品 —— ⚠️ 时间窗内出现，必引必区分

- **arXiv 2602.04695**（2026-02，投 JFM）"Turbulence teaches equivariance to neural networks"：**已经量化测量训练后流体模型的等变误差**并用作诊断——最危险的近邻。
- **arXiv 2605.18816**（2026-05）"Symmetry in the Wild: The Role of Equivariance in Neural Fluid Surrogates"：系统评估等变 vs 非等变流体代理。
- 另：Brandstetter ICML 2022（arXiv 2202.07643）的 Lie 点对称数据增广已为各 PDE 推导全套保解变换——本文"变换推导半边"与其重叠，必须引用并区分（增广 vs 测试）。

**区分话术**：它们是 **symmetry-only、metric 式评估**——无 MR 语义、无 oracle verdict、无阈值/失效定位、无非对称关系。本文是带 verdict 的完整测试框架且对称只占 1/8。**但发表竞速压力真实存在：等变评估社区正快速逼近"测试"语义，建议 2026 内完成投稿。**

## 拷问五：预印本理论基座 + 双投伦理 —— ✅ 合规可行，须按清单执行

- **政策**：Elsevier 允许引 arXiv（"citations should generally be peer-reviewed"——例外许可而非禁止）；COPE 切香肠红线 = 相同研究问题/重复结果/不披露。理论稿（TOSEM）与实例化+实证稿（IST）研究问题不同，合法。
- **执行清单**：① IST 稿必须 **self-contained**（8-block + CONSTRUCT-MP 要点在文内重述到可独立评审的程度，不能要求审稿人去读 arXiv）；② 双向 cover letter 披露另一投稿与重叠范围；③ 交叉引用；④ 结果章节零复用。
- **⚠ 与投稿包冲突的发现**：核查显示 **TOSEM 现行为单盲**（dl.acm.org/journal/tosem/author-guidelines；2025 新 EiC 编辑文未提双匿名），而 NOETHER 投稿包按双盲准备。两者必有一错——**请在 ScholarOne 提交页面亲自核实当前政策**；若确为单盲，IST 稿引用 arXiv 不构成任何去匿名问题，自引措辞约束也可放宽。

## 拷问六：中文理论基座（阳小华 2020） —— ✅ 可行，且有本组现成先例照搬

- 政策无禁令；惯例 = 引文给英译题名 + DOI（+"(in Chinese)"可选）。
- **关键发现：本组已两次用英文重述该模型**——Frontiers in Energy Research 2022（10.3389/fenrg.2022.788753，核电软件轻量验证）与 JKSU-CIS 2026 SimiMR（10.1007/s44443-026-00597-7，§2.1 用约 6 段英文+重绘图完整重述四层模型）。**照搬该模式**：正文英文重述 + 引阳 2020 为出处 + 共引两篇英文论文作为可达版本。
- **连带修正**：SimiMR（Zhao, **Li**, Luo, **Yang**, **Liu**, **Yan**, Yu）**是本组论文**——v2 拷问及 baseline 讨论中曾把它当外部竞品，所有文档中涉及 SimiMR 处须标注自引属性；baseline B2 用 MR-Scout/Kanewala（真外部）不受影响。

---

## 裁决汇总与安全表述对照

| # | 攻击面 | 裁决 | 动作 |
|---|---|---|---|
| 1 | Noether 导出散度 MR | 🚨 物理错误 | 改连续性约束叙事 + 引 Millikan 1929；理论回馈双向设计保留且更实 |
| 2 | time-reversal block | 🚨 本域无效 | 改挂 qualitative-dynamics；显式排除并作为 rubric 示例 |
| 3 | Lie 群经典在先 | ⚠ 须重摆立场 | 主动引 Bytev/Lloyd/Olver；阵地移至非对称 blocks + 闭包/可判定 + BC 子群选择 |
| 4 | 2026 等变评估竞品 | ⚠ 必引必区分 | 引 2602.04695/2605.18816/2202.07643；强调 MR-verdict 语义差；**年内投出** |
| 5 | 预印本基座/双投 | ✅ 合规 | self-contained + 双向披露 + 核实 TOSEM 盲审模式 |
| 6 | 中文理论基座 | ✅ 有先例 | 英文重述 + 共引 Frontiers'22 与 JKSU-CIS'26；SimiMR 改标自引 |

| 危险表述（删） | 安全表述（用） |
|---|---|
| "由 Noether 定理导出守恒 MR" | "div-free 是不可压缩流的连续性约束；N-S 无经典变分结构（Millikan 1929），故对称 MR 由方程的 Lie 点对称群奠基" |
| "时间反演 block 实例化 rollout MR" | "粘性显式破坏 T 对称，本域排除 time-reversal MR（rubric 过滤示例）；演化 MR 属半群性质" |
| "框架推导出镜像/缩放等变换" | "symmetry block 消费经典 N-S 对称群（Bytev; Lloyd; Olver）；框架贡献在 BC 兼容子群选择、非对称 blocks 与可执行 MR 目录" |
| "首次检验流体代理模型对称性" | "区别于 symmetry-only 等变误差度量（2602.04695 等），本文给出带阈值/verdict/失效定位的完整 MR 测试框架" |

## 主要来源

物理：Millikan 定理见 JFM 2024 (10.1017/jfm.2024.229 区段) 与 arXiv:2302.14716；relabeling→Kelvin：arXiv:1808.05486；T 对称破坏：arXiv:1801.00944, 1711.05684；Lie 群：Lloyd 1981 Acta Mechanica, Bytev 1972, Olver GTM 107, Oberlack MDPI Symmetry 2010；Buckingham-Pi=缩放群：Bluman & Kumei 1989 ch.1, Barenblatt 1996。  
竞品：arXiv 2602.04695; 2605.18816; 2202.07643; 2206.05457（Hiremath 第三篇）; AIES Pangu 动力学检验 (10.1175/AIES-D-23-0090.1)。  
伦理：Elsevier Publishing Ethics; COPE salami-slicing & concurrent-submission; TOSEM author guidelines (dl.acm.org)。  
中文引用先例：10.3389/fenrg.2022.788753; 10.1007/s44443-026-00597-7; IEEE Reference Guide。
