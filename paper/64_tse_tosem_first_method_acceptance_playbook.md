# 64 · 让 TSE/TOSEM 接受"首创/无 SOTA-baseline"方法稿的打法

> 日期：2026-06-30 · 问题：baseline 稀缺恰证明研究紧迫性/必要性——如何让 TSE/TOSEM 编辑接受、审稿人认可？
> 立场：必要性论证**有效且是正确框定**，但它**改变成功判据、不豁免证据门槛**。

## 一、肯定有效部分：TSE/TOSEM 确实收"首创/无 SOTA-baseline"方法稿

实检反例（近 2 年 TOSEM，均"首创、无可击败的 SOTA MT"）：
- **MET-MAPF**(TOSEM24)：自称"首个 MAPF 的 MT"，无 SOTA MT baseline；**靠"MR 发现了 mission-completion oracle 漏掉的违例"** 立住。
- **DRLMutation**(TOSEM25)：首个 DRL 综合变异框架；靠**能力+算子库**立住，非击败分数。
- **CCML/Boosting MT**(TOSEM26)：首个通用 MR 描述语言+工具；靠**新能力**立住。

→ **"缺口未占"在 TSE/TOSEM 不是死刑，反而可作必要性卖点。本文的"complementary"发现其实是正确形状。**

## 二、诚实划界：必要性**改变判据、不豁免门槛**

顶刊对首创稿的判据从「**击败 SOTA 分数**」变成「**令人信服地证明一个真实、独特、必要的能力**」。它**仍然要求**：
- 多被测真实对象（非单 SUT）；
- 可辩护的真实故障（非自造平凡 mutant）；
- **把你能想到的自然 baseline 都建出来**，再展示它们结构性做不到的事（不能说"没 baseline，信我"）；
- 理想是**真实 bug / 真实危害**的证据。

**纯修辞（"gap 紧迫"）拿不到审稿人认可；必须把必要性"演示"出来。**

## 三、编辑接受关（desk-level）的杠杆

编辑问：问题重要吗？在 scope 吗？够格送审吗？
1. **框成 SE 测试问题**（非计算科学）：标题/摘要/引言用 oracle 问题、MT、可采性、故障归因的 SE 语汇；弱化 CFD 物理叙事（这是 IST 桌拒的同一坑）。
2. **把必要性"实证化"地立在首段**：不是"很重要"，而是"SciML 代理已部署于 X，无 oracle，**现有测试(accuracy/generic-MT/UQ)对物理有效性故障结构性失明**——这是一个未被覆盖的真实风险"。一句话既给 significance 又给 gap。
3. **novelty crisp**：一句话锁 numerical-decidability admissibility 闸门是新的可判定性判据（对 Eniser/Duque-Torres/Sun CCML 的精确 delta，本文 §2.2 已有雏形）。
4. **generality**：强调方法**域无关**（admissibility 理论跨 surrogate 类型）——顶刊偏爱可泛化方法。

## 四、审稿人认可关（review-level）的杠杆（决定性）

审稿人对评估最狠。无 SOTA-baseline 稿，认可来自：
1. **把"complementary"重述为"catch what others are blind to"**：现稿"complementarity, not superiority"是弱词。改为**"门控捕获 accuracy 监控/generic-MT/UQ 结构性漏掉的一类物理有效性故障"**——这是**正面必要性结果**，正是 MET-MAPF 的制胜形状。
2. **测量"被预防的危害"**：实证展示——**不做 admissibility 门控时，标准做法在真实 SciML 代理上产生 X% 误警/误归因；门控把它修掉**。一个 measured harm + measured fix = 必要性的硬证据（比任何修辞强）。
3. **把自然 baseline 全建出来**：generic-MR、accuracy/residual 监控、UQ/conformal、Kanewala 式科学软件 MT——全跑，展示各自结构盲区。"我建了所有自然 baseline，缺口在此"远胜"无 baseline"。
4. **多被测真实对象**：≥3–5 个独立训练、跨架构×跨物理域的真实 SciML 代理（本文已有 ~6，须训到位+补域+保独立）。
5. **可辩护故障基准**：弃自造平凡 mutant，建有物理依据、经独立校验的真实 SciML-代理故障分类（paper/63 阶段 2，最稀缺最关键）。
6. **principled 理论 + 可采性 soundness**：TOSEM 尤爱框架——把"容差须压过算子误差地板"形式化（定义、四条件、门控的 soundness 论证）。理论 + 可执行实例 + 多被测演示 = 经典 TOSEM 形状。
7. **(最硬，可选)真实 bug**：在第三方真实 SciML 代理/库里用门控找到一个真实的、被确认的物理有效性缺陷——把"有趣想法"变"必需工具"。

## 五、本文专属的关键重述（一句话级）

| 现稿（弱） | 改为（必要性强） |
|---|---|
| "complementary, not superiority" | "门控捕获标准测试结构性失明的一类物理有效性故障" |
| seeded faults 5/10（自造平凡）| 真实/可辩护故障分类上的 measured 误警率下降 |
| "asserts no reliability/rate" | "首次量化：无可采性门控时 SciML-代理测试的误归因率，及门控的修正" |
| 单 SUT | 跨架构×跨域 ≥3–5 真实代理上的一致门控行为 |

## 六、残余风险（实事求是）

- 必要性框定**能过编辑关**（问题真、gap 真、形状对），但**审稿关仍要 §四的证据**——尤其阶段 2(故障基准)+阶段 4(measured harm/fix)。
- 核心不确定**未消除**：必须真的测出"门控修掉了标准做法的危害"。若实测门控**在真实代理上无显著危害可修**，则必要性叙事落空——这是诚实的下行风险。
- 工作量仍是 paper/63 的 4–6 月级；必要性框定**降的是"必须击败 SOTA 分数"的风险**，**不降**"多被测+真实故障基准+measured harm"的工作量。

## 结论

**必要性论证是正确且可用的战略框定**——TSE/TOSEM 确实收首创无 baseline 稿，本文的"互补"发现是正确形状。**让编辑接受**：SE 化框定 + 实证化的 gap/significance + crisp novelty。**让审稿人认可**：把"互补"重述为"捕获他人结构盲区"，并用 **measured harm + measured fix + 多被测 + 可辩护故障基准 +(可选)真实 bug** 把必要性**演示**出来。修辞开门，证据定生死。这条路可行，但生死手在 paper/63 阶段 2/4 那两项最稀缺工作上。
