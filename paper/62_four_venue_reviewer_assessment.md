# 62 · 四刊（IST/TSE/TOSEM/RESS）评审人客观评估

> 日期：2026-06-30 · 评审对象：`submissions/RESS/main.tex` 现稿。
> 方法：以四刊近 2 年(2024–2026)发表谱（Crossref 按 ISSN）提炼收稿方向+平均水平，再判本文研究问题/贡献/实验论证能否达各刊**中等被接收**水平。

## 各刊近 2 年发表谱（实检）

### IST (0950-5849) —— MT 的天然主场，但要"清楚是软件"
近 2 年 MT 论文密集，且**有 MT 专刊**(108094)：MT of ML 信用评分、MT-Boost、chess engine MT 复制研究、多模态轨迹预测 MT、GPT 生成 MR 的自动驾驶混合 MT、推荐系统 MT、电子表格错误检测 MT、CPMT(MR+用例排序)、MT4Image、DL 覆盖测试。**平均水平**：扎实经验型 SE，多为**单一应用域**(信用/棋/推荐/图像/表格) + 真实评估 + 通常有 baseline/有效性结果；novelty 中等。Q1 但四刊中最易进。**关键**：被收的都**无歧义是"软件"**(信用软件/棋引擎/推荐系统/图像应用)。

### TSE (0098-5589) —— MT of ML 在场，但评估门槛高
MORTAR(LLM 对话多轮 MT)、图像描述 MT、AIM(蜕变安全测试输入最小化)、CPS 设计假设 MR+遗传编程、DNN 复合 MR 有效性实证、神经 oracle 评估。**平均水平**：高——多被测对象、**击败 SOTA baseline**、统计显著、常配工具+发现真实 bug。

### TOSEM (1049-331X) —— MT 方法学在场，门槛同 TSE
深度代码模型 MT 的 SLR(45 篇)、机器翻译 Word-closure MT(F1 +29.9% 胜 SOTA)、DRL surrogate 测试(多 50% failures)、DLLens(LLM 差分测试，找到 71 真 bug)、**CCML(通用 MR 描述语言+工具)**、DL 边界测试、MAPF MT(10 MR)、DRLMutation(107 算子)。**平均水平**：高——强工具/基准、多被测、胜 baseline、真实 bug/可复现基准。

### RESS (0951-8320) —— 见 paper/56/57/59
每篇 ML-surrogate/CFD/PINN/软件-V&V 论文都桥接到**可靠性/风险/诊断量**；蜕变测试近 0 先例。

## 本文逐刊判定（现稿）

| 刊 | scope 契合 | 证据门槛 | 本文判定 |
|---|---|---|---|
| **IST** | MT 在 scope，但**CFD/MGN/PINN 物理重框定读成"非 SE"**(=实际桌拒主因) + importance 不清 | 中等经验型 + 通常有 baseline | **低于中等**(已被 EIC 桌拒)；差距主要在 framing+证据，**可恢复性最高** |
| **TSE** | MT of ML **在 scope**(图像描述/翻译/自动驾驶均收) | **高**：多被测+胜 SOTA+真 bug | **低于中等**：单 SUT、无 baseline 被击败、自降级证据；novelty 真但评估不够 |
| **TOSEM** | MT 方法学**在 scope**(CCML 等) | **高**：工具+多被测+真实影响 | **低于中等**：同 TSE，方法贡献真但评估薄 |
| **RESS** | **超 scope**(无可靠性量) | 须可靠性量 | **低于中等/桌拒**：scope+可靠性量双缺 |

## 三维客观评估（跨刊）

**研究问题**：定义清晰可证伪。对 IST/TSE/TOSEM **在域**(蜕变测试是 SE 核心)；对 RESS 超域。IST 的麻烦是**物理框定让 SE 编辑读成非软件**。

**学术贡献**：numerical-decidability admissibility 闸门是**真新**，且处 MT 活跃子领域(Duque-Torres MetaTrimmer / Eniser relaxations / Sun CCML 同空间)——对 SE 三刊是**接近中等的可引贡献**。短板：MR-card/typed verdict 偏增量。

**实验论证（决定性短板，对所有刊）**：
- 单个 MGN checkpoint 主证据；
- **无 baseline 被击败**(自陈 complementarity not superiority)——而 TSE/TOSEM 近 2 年 MT 论文**几乎都击败 SOTA/找到真 bug**；
- seeded faults 自造且"任何检测器都能抓"5/10；第二任务 airfoil 半废(rel L2 0.92)；
- 四种宽度全被边界句自降级。
- **诚信/统计/可复现超中等**(Wilson CI、operator-floor R²=0.9999)，但这救不了证据规模。

## 净结论

**现稿在四刊均达不到中等被接收水平。** 但**性质不同**：
- 对 **IST/TSE/TOSEM**：**在 scope**(蜕变测试是 SE 核心)，卡在**评估规模**——单 SUT、无 baseline 击败、自降级。novelty(decidability 闸门)够格，evidence 不够。
- 对 **RESS**：卡在**scope+缺可靠性量**(结构性，非评估规模)。

**可恢复性排序（达中等的工作量，由易到难）**：
1. **IST**：SE 化重框定(弱化 CFD 物理、强调 MT 方法学) + 补 1–2 个 baseline 对比 + 增被测应用 → 较可能达 IST 中等。**但 IST 已桌拒此稿**，需实质改投材料(非原样重投)。
2. **TOSEM/TSE**：需多被测 + 击败 SOTA MT baseline + 理想是真实 DL 系统找到真 bug → 大工作量。decidability 闸门可作理论卖点，但评估必须补强。
3. **RESS**：需 Method-B(可靠性量 P_f/FAR-MDR) → 中等工作量、scope 结构性改造。

**诚实总判**：本文是一篇**有真实方法新点、但实证规模偏小、且诚实到自我降级**的蜕变测试方法稿。它的自然归宿是 **SE 测试刊**(IST/TOSEM)，前提是补评估(baseline+多被测)；冲 TSE 或转 RESS 都需更大改造。当前任何一刊原样投都低于中等。
