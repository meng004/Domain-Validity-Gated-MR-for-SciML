# 云端实证扩张 Kickoff（冲中科院 1 区：TSE / TOSEM）

> 单文件冷启动 runbook。执行者是一个**无先验上下文**的云端 Claude Code 会话。本文件假定你（执行 agent）刚 checkout 本分支、未读过任何历史。**先完整读完本文件再动手。**
>
> 版本：2026-06-20 · 目标分支：`cloud/1q-empirical-expansion` · 基线 commit：见本文件所在分支 HEAD。

---

## 0. 人类如何调用（你不需要做这步，仅供理解）

人类在云端只会输入三句：
1. `git fetch && git checkout cloud/1q-empirical-expansion`
2. `读取 docs/cloud_runbook/1q_empirical_expansion_kickoff.md`
3. `执行任务`

所以**本文件就是全部指令来源**。遇到本文件未覆盖的判断，按 §3 硬约束与仓库 `CLAUDE.md` 行事；仍不确定就**停下来问人类**，不要猜。

---

## 1. 任务背景与诚实定位（必读，决定你怎么取舍）

这是论文 *Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates* 的实证扩张。现状：

- 论文已是一篇成熟的 software-V&V 方法论稿（中科院 2 区 Q1 的 IST 可投）。
- 一个固定 5-LLM 评审 panel 的 **EIC 连续三轮判 major**，核心理由始终是 **"contribution partly incremental + 证据 single-SUT / under-trained / fragmented"**。两轮纯写作修订（sharp claim、hedge 瘦身）没能翻动它——经核实这是**稳定上限**，不是可改的写作缺陷。
- 期刊重估 + 中科院分区分析后，人类决定：**为冲真 1 区（TSE/TOSEM）做实证扩张**，用更扎实的实证拆掉 EIC 的"single-SUT / under-trained"前缀。

**本次扩张拆的是「证据前缀」，不是「novelty 不足」。** 必须诚实承认：即便全做完，1 区仍可能因 novelty 立场被拒。但所有 MVP 产物**同时直接强化 2 区 IST 稿**，所以回退也是净收益——**这是先做全 CPU 的 MVP、把 GPU 投入放在 MVP 验证之后的根本原因**。

### 历史反伤教训（务必避开）
仓库 `NEXT_STEPS.md` 记录过两次反伤：airfoil 第二 SUT 因**欠训练**反而把评审分拉低 0.4；C34 绝对守恒因证据不足被撤回两次。**铁律：任何 baseline 对比、duality 论证，只能跑在「已收敛」的 SUT 上，绝不在欠训练 SUT 上做对比**（1 区会直接判无效）。

---

## 2. 环境准备与自检（动手前必须全绿）

### 2.1 仓库与路径（云端）
- 本仓库：当前工作目录（`git remote -v` 应指向本项目 origin）。
- 只读姊妹仓库 `Minimum-MR-SubSet`：云端在 `/home/user/Minimum-MR-SubSet/`（本地是 `../最小完备MR子集/`）。**只读，永不修改**；本仓库可 import 其 `scripts/`、读其 committed `data/`，所有写入落本仓库。
- 云端 shell **不加 `rtk` 前缀**（那是本地 hook，云端无）。

### 2.2 自检命令（逐条跑，全绿才继续）
```bash
# 基线测试套件（应 372 passed，数量可能随新 test 增长）
python -m pytest tests -q

# fail-closed 证据门（改数据/提交前必跑，应 rc=0）
python tools/validate_experiment_protocol.py; echo "protocol rc=$?"
python tools/validate_research_assets.py;     echo "assets rc=$?"

# 字数（单一真相源；当前约 12,545 / 15,000）
python tools/ist_wordcount.py

# GPU 是否可用（决定 EXT-1 能否跑）
python -c "import torch; print('cuda', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-')"
```

### 2.3 真实 SUT 凭据（仅 EXT-1 的 cylinder METBENCH 路径需要；MVP 不需要）
`METBENCH_MGN_DATA_ROOT` / `METBENCH_MGN_REPO` / `METBENCH_MGN_CHECKPOINT` 缺失会 fail-closed——**这是设计行为，不是 bug，不要去"修"它**。MVP / EXT-2 完全不依赖此路径；EXT-1 airfoil 走自己的公开数据下载（HTTP，无需凭据）。

---

## 3. 硬约束（不可违反，违反即整轮作废）

来自仓库 `CLAUDE.md` 与 `0-论文/CLAUDE.md`，逐条遵守：

1. **实事求是 / 反伪造**：绝不伪造实验输出、绝不声称没跑的实验成功。每个结论必须有可复算证据（run 目录 + metric ledger + claim ID）。
2. **claim-ledger 纪律**（`research_assets/experiments/claim-ledger.yml`）：
   - 写依赖某 claim 的 prose **之前**先加 claim ID；
   - 新 claim **先以 `status: blocked` 落地，真跑出数据后才转 `observed`**；
   - **绝不把 `wording_allowed` 写宽超出实跑数字**；每条新 claim 必须有 `wording_forbidden` 红线（见各任务）。
   - 当前最高 claim 是 **C40**，新 claim 从 **C41** 起编号。
3. **回归 guard 不可静默削弱**：`tests/test_*` pin 了 prose / claim 措辞 / 资产 schema。prose 跑赢证据导致 guard 红 → **改 prose 或补证据，绝不偷改 guard**。
4. **姊妹仓库只读**：见 §2.1。
5. **最小修改 / 反自发改写**：只做被要求的事，不顺手重构、不动无关段落、不删未被要求删的内容。
6. **显式报错**：跳过项 / 失败项 / 不确定假设必须明说，不静默吞掉。
7. **STVR 不是候选 venue**；scope 框定为 software V&V 方法（**不**主张"优于 accuracy/UQ"，**不**主张 baseline superiority）。
8. **提交前敏感扫描**（§5）：`git ls-files | xargs grep` 无 API key / 真实 base_url / 个人绝对路径 / 第三方邮箱。

---

## 4. 任务总览与执行顺序

> **本云端文档只做 MVP。EXT 实验（EXT-1 airfoil 收敛 / EXT-2 operator-floor / EXT-3 cross-SUT）已划归本地执行，见 `docs/local_runbook/ext_experiments_kickoff.md`。本文件 §5 的 EXT-1 / EXT-2 章节仅作参考，云端不执行。**

云端唯一任务 = MVP（全本地 CPU，无 GPU/凭据），**严格按序**；末尾 verification gate（§6）+ commit + 向人类报告。

```
MVP（云端唯一任务）
  ├─ MVP-A   PointMLP 端到端 seeded-fault（第二个收敛架构族）
  └─ MVP-B/C 三臂互补矩阵 + ≥20 fault + Wilson CI + knife-edge 曲线
  → verification gate → commit → 报告 → 【完成，交回人类；EXT 由本地做】
```

> **为什么云端只做 MVP**：MVP 全 CPU/零凭据、无论冲几区都净收益；EXT 中 EXT-1 需 GPU、EXT-3 依赖 MVP 结果，已划归本地协调执行（claim 编号 C41-C43 归 MVP，EXT 从 C44 起；见 local 文档 §8）。MVP 交付后由人类（在有 LLM 网关凭据的本地）重跑评审 panel 看分数是否上移。

---

## 5. 逐任务说明（read-first → create → 验收 → claim → test → run）

### 任务 MVP-A — PointMLP 端到端 seeded-fault

**目标**：给已收敛、不同架构族（row-wise，无消息传递）的 PointMLP cylinder SUT 补上 seeded-fault 检测这一环，得到第二个「完全收敛 + 端到端 + 非平凡 seeded-fault」的 SUT。若其 by-class 检测模式与主 MGN 可比，则把"5/10 + by-class"从 1 个架构族扩到 **2 个真正不同的架构族**（闭合 `claim-ledger.yml` 中 `speculative_claims` 被 `blocked_reason: K=6 checkpoints share one architecture family` 卡住的缺口）。

**先读**：
- `tools/run_seeded_fault_detection.py`（主 MGN 的 10-mutant 五类催化剂 + 预声明阈值 + detection_matrix/summary/robustness 结构——**直接复用**，同域 cylinder 故催化剂定义无需新造）。
- `research_assets/runs/pointmlp-cylinder-primary-workflow/pointmlp_cylinder_primary_workflow_report.json`（PointMLP SUT 接口、checkpoint 位置、rollout L2 0.0298 收敛证据）。
- 对应的 PointMLP workflow runner（`tools/` 下，grep `pointmlp`）以理解其 SUT 调用约定。

**创建**：`tools/run_seeded_fault_detection_pointmlp.py`——把现有 mutant 注入逻辑接到 PointMLP 的 predict 接口；阈值/催化剂/输出 schema 对齐主 MGN runner（node-perm tol 1e-5、conservation ratio 1.5、mirror-y rel-change 0.5）。robustness ≥5 frame/trajectory。

**验收门槛**：
- 产出非平凡 `detection_matrix`（baseline rel-L2 ≠ 0，检出率非全 0——若全 0 说明接错了 SUT 或 PointMLP 退化，停下来查）。
- 输出 `summary.union_detection_rate` + by-class 分解，与主 MGN 的 5/10 + by-class 模式可对比。
- **两种结果都诚实可写**：by-class 一致 → 支持"跨架构族结构复现"；不一致 → 诚实写成架构相关边界。**先看数据再定 prose 口径，不预设结论。**

**claim**：新增 `C41-pointmlp-seeded-fault`，先 `status: blocked`，跑出后转 `observed`。
- `wording_allowed`：只能描述实跑的 PointMLP detection 数字 + 与 MGN 的对比。
- `wording_forbidden` 必含：「by-class 检测模式跨架构族泛化已被证明」（除非数据真支持，且即便支持也只能说"在这两个架构族上复现"，不得说"泛化"）。

**test**：`tests/test_seeded_fault_detection_pointmlp_cross_sut.py`——先写断言骨架 + `@unittest.expectedFailure`/xfail 占位；跑出真数据后去 xfail 转硬断言 pin 关键数字。

**run**：
```bash
python tools/run_seeded_fault_detection_pointmlp.py --out research_assets/runs/pointmlp-cylinder-seeded-fault-detection
python tools/validate_research_assets.py
python -m pytest tests/test_seeded_fault_detection_pointmlp_cross_sut.py -q
```

---

### 任务 MVP-B/C — 三臂互补矩阵 + ≥20 fault + Wilson CI + knife-edge 曲线

**目标**：在**收敛**SUT 上量化"validity-gated MR 检测器"相对 baseline 的**互补性（不是优越性）**，并系统化 fault 集。

**先读**：
- `tools/run_seeded_fault_detection.py` 的 `--with-rollout`（C38 已做的 accuracy-monitor 互补，cylinder MGN 上 MR 抓 2 个 accuracy 漏的、accuracy 单独抓 0）。
- `research_assets/runs/detection-vs-accuracy/`（C38 现状）。
- `tools/run_expert_mr_baseline.py` / `run_generic_mr_baseline.py`（第三臂 generic/expert-MR 资产；**纯量化复算不需要 LLM 网关凭据**，只有重跑 `run_llm_mr_baseline.py` 才需要——本任务不重跑 LLM）。

**创建/扩展**：
- 把 accuracy-monitor 升级为**独立 detector**（rollout-L2 阈值化），与 validity-gated MR suite、generic/expert-MR suite 组成**三臂**。
- fault 集从 10 扩到 **≥20、覆盖 ≥4 类**（boundary / scale / physical-channel / adjacency / normalization）。在 PointMLP + cylinder MGN **双收敛 SUT** 各跑 × K=6 checkpoints。
- 产出：每臂 per-fault detection rate + **Wilson 95% CI**（复用仓库已用的 Wilson 方法）；**2×2 互补表**（MR-only / accuracy-only / both / neither，带 McNemar 或集合差）；**knife-edge severity 曲线**（PC_zero_vy 非单调 sweep → detection-vs-severity，证明 accuracy-monitor 在 symmetric-severe fault 上的盲区——**这是别人没有的差异化 finding，比任何 superiority 都值钱**）。

**验收门槛**：
- 三臂各带 Wilson CI；2×2 互补表完整；knife-edge 曲线产出。
- **全部产物与 prose 里 0 句 `superior` / `outperforms` / `better than`**（grep 自检；命中即不合格——这是 C38 等的 `wording_forbidden` 红线，也是论文 scope 的刻意边界）。
- §10 ARS 自检：fault 类是否**预声明**？多重比较是否需要 Bonferroni/FDR 校正？在报告里显式说明。

**claim**：`C42-three-arm-complementarity`（`wording_forbidden` 必含 superior/outperforms/better than accuracy-monitor）；`C43-knife-edge-blind-region`（`wording_forbidden`：禁外推到未测 fault 类）。两者先 `blocked` 后 `observed`。

**test**：`tests/test_three_arm_complementarity.py`——断言「正文 0 处 superiority 措辞」+ pin 2×2 表关键数值。

---

### 任务 EXT-2 — operator-floor ≥2 mesh 拓扑一致性（加固唯一真新原子）

> 【参考章节——已划归本地执行，见 `docs/local_runbook/ext_experiments_kickoff.md` §5 EXT-2；云端不执行本任务。】

**目标**：论文唯一真新原子是 **measurement-floor 容差闸**（以测量算子误差 floor 门控 MR admissibility）。当前只在一种网格上有闭式 floor。本任务**不追** general unstructured bound（那是数学工作，1 区不因此忽略证据碎片化），而是验证：**在 ≥2 种 mesh 拓扑上，floor 估计落同量级（≤2–3×）且「tolerance 须 dominate floor」的 admissibility 判定不翻转**。把这个唯一原子从"单点观察"升级为"有外推证据"。

**先读**：`tools/run_operator_floor_sweep.py` + `tools/run_operator_floor_sweep_extended.py`；claim `C12`（operator-floor resolution）与 `C32`（analytic-bound future-work）。

**创建**：在第二种网格拓扑（如 triangular → polygonal/Voronoi）跑 operator-floor sweep。

**验收门槛**：两拓扑 floor 同量级 + admissibility 判定一致不翻转 → 扩写 `C12` 的 `wording_allowed`（加"holds across ≥2 mesh topologies"）；**绝不碰 `C32` 的 general-bound future-work 措辞**。若判定翻转 → 诚实写成 mesh-specific 边界，不掩盖。

**test**：在现有 operator-floor test 加第二拓扑断言。

---

### 任务 EXT-1 — airfoil 训到收敛（不同物理第三 SUT）【需 GPU · 参考章节，已划归本地执行】

> 【本任务已划归本地执行，见 `docs/local_runbook/ext_experiments_kickoff.md` §5 EXT-1；云端不执行。以下保留作上下文参考。】

**目标**：补一个**不同物理（compressible）+ 不同代码框架（生产级 PhysicsNeMo）**的收敛 SUT，拆掉 MVP 没拆的"不同物理"前缀，并把 C36 从"欠训练负结果"升级为"第二个非平凡端到端 SUT + validity-coverage duality 的 cross-SUT 确证"。

**关键现状**：端到端管线（runner / claim C35-C36 / test）**已全部就位**（commit `f002c80`），`tools/run_seeded_fault_detection_physicsnemo_airfoil.py` 可原样复用。**唯一缺的是把模型训到收敛**——当前 airfoil 卡在 loss≈1.0（z-score 均值预测，rollout rel-L2≈1.0 = 预测无优于基线），seeded-fault 信号因此坍塌（node-perm 检出 0.0）。

**先读**：`research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/`（欠训练铁证：`training.losses` 首轮即 1.00）；airfoil 训练脚本（grep `airfoil` in `tools/`）。

**执行**：
1. **环境自检**：§2.2 的 GPU 检查必须 True（CUDA ≥16GB）。airfoil 公开数据 HTTP Range 自动下载，无需凭据。
2. **训到收敛**：把训练从 15 epoch / 25 trajectory 提升到收敛——**这不是简单续训**（坏起点），可能需要重设配方（全 1000+ 轨迹、数百 epoch、检查归一化）。目标 rollout median rel-L2 进入文献可用区间（≤2–3× 文献值，目安 ≲0.1）。K=6 checkpoint。
3. **原样重跑**现有 roster runner + `run_seeded_fault_detection_physicsnemo_airfoil.py`——此时 node-perm baseline rel-L2 不再为 0，检测信号才非平凡。

**验收门槛**：
- rollout median rel-L2 收敛到 ≲0.1（或文献可用区间）——**没达到就不要往下做**，欠训练上的一切对比都无效（铁律，见 §1）。
- 收敛后 violation 可干净归因于"模型违反不变量"而非 under-fitting。
- airfoil by-class 映射很可能**仍**与 cylinder 不同（compressible interior-masked vs incompressible full-field；mirror-y 在 airfoil 物理上 inadmissible）——**这不是问题，反而是 C37 duality 的 cross-SUT 自然实验**（换物理 → 门恰好移除那条 MR 的覆盖）。

**claim**：升级 `C35/C36/C37` 的 `wording_allowed`（去掉"under-trained / training-state diagnostic"措辞）；**仍禁**"by-class 模式跨 SUT 泛化已证"。

**test**：重跑 `tests/test_physicsnemo_airfoil_primary_roster.py` + `tests/test_seeded_fault_detection_airfoil_cross_sut.py`，让 guard 对齐新（收敛后）数字。

**GPU 环境锁版本**：训练完成后 `pip freeze > requirements-gpu.txt`（或并入 requirements），把产出 artifact 的环境记录入库。

---

## 6. 每阶段 verification gate（必须全绿才能 commit）

```bash
python -m pytest tests -q                      # 全套，应全 passed（含新 test）
python tools/validate_experiment_protocol.py   # rc=0
python tools/validate_research_assets.py       # rc=0
python tools/ist_wordcount.py                  # ≤ 15000；记录数值
# 若改了 main.tex，跑构建（pdflatex 三遍 + bibtex）并确认：
#   0 undefined / 0 "Missing character" / 0 Overfull \hbox（用 LANG=C grep --binary-files=text）
# claim 红线自检：
grep -rIn -E "outperform|superior|better than" paper/ | grep -v "%"   # 期望空（MVP-B/C 红线）
```
任一不绿 → 修，不要 commit。

---

## 7. 提交 / 分支 / 报告纪律

- **分支**：全部工作在 `cloud/1q-empirical-expansion` 上。**不要直接动 main。**
- **commit 粒度**：每个任务（MVP-A / MVP-B-C / EXT-2 / EXT-1）独立 commit。先跑 §5 敏感扫描 + §6 gate。
- **commit message**：`feat(expansion): <任务一句话>` + 动机/改动范围/验证结果（tests/wordcount/validators）。结尾加
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- **每阶段末报告**（给人类）：本阶段做了什么、新 run 目录、新 claim（及 blocked→observed）、新 test、关键数字（detection rate / CI / floor 比值 / rollout L2）、§6 gate 结果、**诚实标注哪些结论数据较弱 / 哪些假设未验证**。
- **MVP 结束后停**：报告完即交回人类；EXT（含 GPU 的 EXT-1）由本地执行，云端不碰（§4 已说明）。

---

## 8. 完成后如何交回本地会话

人类会把本分支带回本地（有 LLM 网关凭据）做两件你做不了的事：
1. 重跑评审 panel（`tools/run_academic_review_panel.py`，需 `.env` 网关）看 EIC 是否从 major 上移；
2. 据评审结果决定 venue（TSE / TOSEM / 回退 IST）与是否需要 EXT-1。

所以你的交付物 = **可复算的实证 + 对齐的 claim-ledger + 全绿 test + 一份诚实报告**，不需要你跑评审 panel、不需要你定 venue。

---

## 附：关键文件锚点速查

| 用途 | 路径 |
|---|---|
| 可复用 mutant 逻辑 | `tools/run_seeded_fault_detection.py` |
| PointMLP 已收敛 SUT（缺 fault 一环） | `research_assets/runs/pointmlp-cylinder-primary-workflow/` |
| airfoil 端到端就绪但欠训练（EXT-1） | `tools/run_seeded_fault_detection_physicsnemo_airfoil.py` + `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/` |
| operator-floor（C12 扩 / 不碰 C32） | `tools/run_operator_floor_sweep.py` + `..._extended.py` |
| 三臂 baseline 资产 | `tools/run_expert_mr_baseline.py` / `run_generic_mr_baseline.py` / `research_assets/runs/detection-vs-accuracy/` |
| claim 真相源（C40 最高，新增从 C41） | `research_assets/experiments/claim-ledger.yml` |
| 证据门 | `tools/validate_research_assets.py` + `tools/validate_experiment_protocol.py` |
| 字数 | `tools/ist_wordcount.py` |
| 稿件主源 / 投稿包 | `paper/manuscript.md` / `paper/ist-submission/main.tex` |
| 完整规则 | 本仓库 `CLAUDE.md` + `0-论文/CLAUDE.md` |
| 任务台账 | `NEXT_STEPS.md`（顶部 2026-06-20 段） |
