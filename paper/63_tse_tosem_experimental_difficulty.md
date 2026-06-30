# 63 · 冲 1 区 TSE/TOSEM 的实验环境难度 + 工作量预估

> 日期：2026-06-30 · 问题：本文冲 TSE/TOSEM 的实验对象稀缺性、baseline 稀缺性、预估工作量。
> 标尺：近 2 年 TSE/TOSEM 实际 MT-of-ML 论文的实验配置（paper/62 实检）。

## 一、TSE/TOSEM MT 论文的实验环境"门槛画像"（实检）

| 论文 | 实验对象规模 | baseline | 制胜货币 |
|---|---|---|---|
| DLLens (TOSEM26) | 2 大库(TF/PyTorch)、200 API | SOTA 差分测试 | **找到 71 真 bug(59 确认)** |
| Word-closure MT (TOSEM24) | 3 个 MT 系统×5 变换 | 现有 MT 方法 | **F1 +29.9% 胜 SOTA** |
| Mimicry 边界测试 (TOSEM26) | 5 个 DL 分类系统 | 2 baseline | **25× 更近边界、统计显著** |
| 复合 MR DNN (TSE26) | 多 DNN 实证 | 单 MR | **复合 MR 提升有效性** |
| AIM 蜕变安全 (TSE24) | 真实系统 | — | 输入集最小化 |
| DRLMutation (TOSEM25) | 5 环境、107 算子 | — | 算子库 |

**提炼门槛**：① **≥3–5 个真实被测系统**（常是主流 DL 库/模型/真实应用）；② **击败 ≥1 SOTA baseline，统计显著**，或 **找到真实 bug**（最硬货币）；③ 配工具/可复现基准。**"互补而非超越"在 TSE/TOSEM 基本不够。**

## 二、实验对象稀缺性（SciML surrogate SUT）—— 中高

**为何稀缺（与主流 DL 测试的根本差异）**：
- 主流 DL 测试有**现成丰沛对象**：TF/PyTorch 库、ImageNet/COCO 模型动物园、Defects4J 式 bug 数据集。
- SciML surrogate **没有**：每个 MeshGraphNets/PINN/FNO checkpoint 需 **GPU 训练 + 领域设置**；**无公开"干净 vs 有 bug"的物理代理模型库**；**无既成故障基准**（本文只能自造 seeded faults——这正是稀缺的直接证据）。

**本文已有（部分缓解）**：MGN(cylinder, airfoil)、PointMLP、PhysicsNeMo、PINN(Burgers/heat 各 15 seeds)、FNO(Burgers/heat)、姊妹库跨程序(OpenMC/point-kinetics/wave…)。**约 6+ 架构/任务，数量上不算空白**。
**短板**：① 多属同一架构族或自训弱模型(airfoil 半废 rel L2 0.92)；② 独立性弱(K=6 roster S0 复用 pilot)；③ 缺跨物理域多样性(主力是不可压 NSE)。
**缺口工作**：把 airfoil 训到位 + 补 2–3 个独立物理域(如反应扩散/弹性/波动)的真实训练代理，确保跨架构×跨域矩阵。

## 三、Baseline 稀缺性 —— 高（且有结构性悖论）

**悖论**：本文的 novelty 卖点是"缺口未占"(无人做 SciML 物理一致性 admissibility 门控)——**这恰恰意味着没有 canonical 竞争方法可击败**。而 TSE/TOSEM **要求击败 SOTA**。
**可构造的 baseline（须自建/改编）**：generic-MR 生成、accuracy/residual 监控、UQ/conformal、Kanewala-式科学软件 MT。本文已含 accuracy-monitor + generic-template + LLM 三个对照。
**致命风险**：本文当前结论是 **"complementarity, not superiority"**——即门控**在共享标量分上不击败** baseline（它是 gate/triage，不是更强 detector）。TSE/TOSEM 要"我们更强"，与方法**本性**(可采性门控)冲突。
**化解路径（须实测支撑）**：换一个门控**确实占优**的指标——如**误警率下降**(gate 把数值伪影正确归类→比 accuracy 监控少误报) 或 **accuracy 监控漏掉而 gate 抓到的故障类**。但这要新证据，且可能跑出负结果。

## 四、工作量预估（现稿 → TSE/TOSEM 中等）

| 阶段 | 内容 | 工作量 | 风险 |
|---|---|---|---|
| 1 多样真实 SUT | airfoil 训到位 + 补 2–3 独立物理域真实代理(GPU)，凑跨架构×跨域 ≥5–8 | **1–2 月 GPU+设置** | 中(训练成本) |
| 2 故障基准 | 弃自造平凡 mutant，建可辩护的真实 SciML-surrogate 故障分类 + 独立校验 | **1–1.5 月** | **高(无现成基准, 最稀缺)** |
| 3 baseline 实现 | 改编/实现 ≥2–3 竞争法跑 head-to-head | 3–4 周 | 中 |
| 4 证明占优 | 选门控占优指标(误警率/漏检互补)做统计显著 | 2–4 周 | **高(可能不占优=核心不确定)** |
| 5(高价值高风险) | 在真实 SciML 代理/库中**找到真 bug**(TSE/TOSEM 最硬货币) | 开放式 | **很高(可能失败)** |
| 6 重写 | 改成"多被测+击败 baseline/真 bug"叙事 | 3–4 周 | 中 |

**总计：约 4–6 个月，HIGH 风险**，主要 GPU 训练 + 故障基准构建（最稀缺）+ 占优叙事（与方法本性冲突的核心风险）。

## 五、净判断

- **实验对象**：中高稀缺——SciML 代理无现成模型库/bug 基准，每个需 GPU 自训；但本文已有 ~6 SUT，非从零，缺口在"独立×多域×真实故障"。
- **baseline**：高稀缺 + 结构悖论——无 canonical 竞争法可打，且方法本性是"互补非超越"，与 TSE/TOSEM"击败 SOTA"要求正面冲突，是**最难一关**。
- **工作量**：4–6 月、HIGH 风险，最大不确定=能否在某指标上真正击败 baseline / 找到真 bug。

**对比另两条路**：
- IST(SE 重框定+补 baseline)：~1–2 月，中风险，可恢复性最高。
- RESS Method-B(可靠性量)：~中等(周到月级)，scope 结构改造但有现成核/PDEM/WDN 资产。
- **TSE/TOSEM：4–6 月、最高风险**，卡在"故障基准稀缺"+"互补非超越悖论"。

**结论**：冲 TSE/TOSEM 的实验环境难度在四条路中**最高**——不是对象绝对为零，而是(a)真实故障基准稀缺须自建并经得起审稿、(b)方法"互补非超越"本性与顶刊"击败 SOTA"硬要求冲突。除非愿投 4–6 月并接受占优叙事可能跑不出来的风险，否则 ROI 低于 IST 重框定或 RESS Method-B。
