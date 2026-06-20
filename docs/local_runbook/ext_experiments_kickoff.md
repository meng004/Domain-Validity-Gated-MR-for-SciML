# 本地 EXT 实验 Kickoff（冲中科院 1 区：扩张的第二批 / 加固层）

> 单文件冷启动 runbook，**本地执行**。与云端 MVP 文档（`docs/cloud_runbook/1q_empirical_expansion_kickoff.md`）配对：**云端做 MVP（PointMLP seeded-fault + 三臂互补），本地做 EXT（本文件）**。两者非重叠。
>
> 版本：2026-06-20 · 分支：`cloud/1q-empirical-expansion`（或从它派生的本地子分支）。

---

## 0. 本地如何调用

```
git fetch && git checkout cloud/1q-empirical-expansion      # 或派生本地子分支
读取 docs/local_runbook/ext_experiments_kickoff.md
执行任务
```
本文件即全部指令来源。本地 shell 的 `git/grep` 等会被 rtk hook 透明改写，**正常敲命令即可**（无需手动加 rtk）。

---

## 1. 任务背景与定位（必读）

论文 *Domain-Validity-Gated Metamorphic Testing of Scientific ML Surrogates* 正为冲真 1 区（TSE/TOSEM）做实证扩张，根因是评审 EIC 三轮 major 的"contribution incremental + 证据 single-SUT/under-trained/fragmented"。完整背景见 `NEXT_STEPS.md` 顶部 2026-06-20 段。

**分工**：
- **MVP（云端）**：第二个收敛架构族（PointMLP）seeded-fault + 三臂互补矩阵——拆"single-SUT / fragmented"前缀。全 CPU。
- **EXT（本文件，本地）**：拆 MVP 没拆的更硬前缀——
  - **EXT-1** = "不同物理"（airfoil 收敛，compressible 第三 SUT）；
  - **EXT-2** = operator-floor 唯一真新原子的"外推证据"（≥2 mesh 拓扑）；
  - **EXT-3** = 三臂互补 + duality 跨**全部**收敛 SUT。

**铁律（历史反伤教训）**：任何 baseline 对比 / duality 论证只能跑在**已收敛**的 SUT 上。airfoil 不收敛就**绝不**在它上面做对比（仓库 `NEXT_STEPS.md` 记录过 airfoil 欠训练反拉低评审 0.4、C34 被撤两次）。

**诚实定位**：EXT 拆的是"证据前缀"，不是"novelty 不足"。即便全做完，1 区仍可能因 novelty 立场被拒；但产物同时强化 2 区 IST 稿，回退净收益。

---

## 2. 本地环境与自检（动手前必须全绿）

### 2.1 路径
- 本仓库：当前工作目录。
- 只读姊妹仓库 `Minimum-MR-SubSet`：本地 `../最小完备MR子集/`。**只读，永不修改**。

### 2.2 自检命令
```bash
python -m pytest tests -q                          # 基线全 passed
python tools/validate_experiment_protocol.py; echo "rc=$?"   # 0
python tools/validate_research_assets.py;     echo "rc=$?"   # 0
python tools/ist_wordcount.py                      # ≤15000，记录数值
python -c "import torch;print('cuda',torch.cuda.is_available())"   # EXT-1 用
```

### 2.3 ⚠️ EXT-1 的 GPU 现实（必读）
EXT-1（airfoil 训到收敛）**需要 CUDA GPU（≥16GB）**。**若你的本地机是 Mac（仅 MPS），EXT-1 跑不出 CFD 收敛**（仓库可行性分析实测：MPS 能跑完整生产架构 3.9h 但训不收敛）。三种处理：
- (a) 本地有独立 CUDA GPU 工作站 → 在该机跑 EXT-1；
- (b) 无本地 GPU → **把 EXT-1 交回云端 GPU**（云端文档已有 EXT-1 章节可复用），本地只做 EXT-2 / EXT-3；
- (c) 先只做 EXT-2（纯 CPU，独立、零依赖），EXT-1/EXT-3 视算力再定。
**不要在 MPS/Mac 上硬训 airfoil 然后在欠训练结果上做对比——违反 §1 铁律。**

---

## 3. 硬约束（不可违反）

与仓库 `CLAUDE.md` 一致，逐条遵守：
1. **实事求是 / 反伪造**：不伪造输出、不声称没跑的实验成功；每个结论有 run 目录 + metric ledger + claim ID。
2. **claim-ledger 纪律**（`research_assets/experiments/claim-ledger.yml`）：写依赖某 claim 的 prose 前先加 ID；新 claim 先 `status: blocked`、真跑出才转 `observed`；**绝不 widen `wording_allowed` 超出实跑数字**；每条新 claim 配 `wording_forbidden`。当前最高 claim **C40**（云端 MVP 会占用 C41-C43；本地 EXT 新 claim 从 **C44** 起，**先与云端协调编号避免撞号**——见 §8）。
3. **回归 guard 不可静默削弱**；prose 跑赢证据 → 改 prose 或补证据。
4. **姊妹仓库只读**。
5. **最小修改**；**显式报错**；**不主张 superiority**（EXT-3 同 MVP 红线：0 句 outperforms/superior/better）。
6. 提交前**敏感扫描**（key/真实 base_url/个人绝对路径/第三方邮箱）。

---

## 4. 任务顺序与依赖

```
EXT-2  operator-floor ≥2 mesh   —— 纯 CPU、完全独立、零依赖 → 建议先做
EXT-1  airfoil 训到收敛          —— 需 GPU（见 §2.3）；独立于 MVP
EXT-3  三臂互补+duality 跨全 SUT  —— 依赖 MVP（PointMLP+三臂）已合入 + EXT-1 收敛 → 最后做
```
**依赖提示**：EXT-3 需要云端 MVP 的产物（PointMLP seeded-fault + 三臂框架 + 收敛 SUT 清单）已合并到本分支，且 EXT-1 收敛后才有"全部收敛 SUT"。所以 EXT-3 **必须等 MVP 分支合并 + EXT-1 完成**。EXT-2 可立即开始。

---

## 5. 逐任务说明

### EXT-2 — operator-floor ≥2 mesh 拓扑一致性【纯 CPU · 可立即做 · 加固唯一真新原子】

**目标**：论文唯一真新原子 = measurement-floor 容差闸（以测量算子误差 floor 门控 MR admissibility）。当前只在一种网格有闭式 floor。**不追** general unstructured bound（数学工作，1 区不因此忽略证据碎片化），而是验证：**≥2 种 mesh 拓扑上 floor 估计落同量级（≤2–3×）且「tolerance 须 dominate floor」的 admissibility 判定不翻转**——把这个唯一原子从"单点观察"升级为"有外推证据"。

**先读**：`tools/run_operator_floor_sweep.py` + `tools/run_operator_floor_sweep_extended.py`；claim `C12`（operator-floor resolution）与 `C32`（analytic-bound future-work）。

**创建**：在第二种 mesh 拓扑（如 triangular → polygonal/Voronoi，或结构化→非结构化）跑 operator-floor sweep。复用现有 sweep 框架，只换网格生成。

**验收门槛**：
- 两拓扑 floor 落同量级（比值 ≤2–3×）+ admissibility 判定一致不翻转 → 扩写 `C12` 的 `wording_allowed`（加 "floor estimate and admissibility decision hold across ≥2 mesh topologies"）。
- **绝不碰 `C32` 的 general-bound future-work 措辞**（那仍是 future work）。
- 若判定**翻转** → 诚实写成 mesh-specific 边界，不掩盖、不删负结果。

**claim**：扩写 `C12`（非新建）。**test**：在现有 operator-floor test 加第二拓扑断言。

**run**：
```bash
python tools/run_operator_floor_sweep_extended.py --mesh <第二拓扑> --out research_assets/runs/operator-floor-sweep-mesh2
python tools/validate_research_assets.py
python -m pytest tests/ -k operator_floor -q
```

---

### EXT-1 — airfoil 训到收敛（不同物理第三 SUT）【需 GPU · 见 §2.3】

**目标**：补"不同物理（compressible）+ 不同代码框架（生产级 PhysicsNeMo）"的收敛 SUT，把 C36 从"欠训练负结果"升级为"第二个非平凡端到端 SUT + validity-coverage duality 的 cross-SUT 确证"。

**关键现状**：端到端管线（runner / claim C35-C36 / test）**已全部就位**（commit `f002c80`），`tools/run_seeded_fault_detection_physicsnemo_airfoil.py` 可原样复用。**唯一缺的是训到收敛**——当前 airfoil 卡 loss≈1.0（z-score 均值预测，rollout rel-L2≈1.0），seeded-fault 信号坍塌（node-perm 检出 0.0）。

**先读**：`research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/`（欠训练铁证 `training.losses` 首轮即 1.00）；airfoil 训练脚本（`grep -ril airfoil tools/`）。

**执行**：
1. GPU 自检 True；airfoil 公开数据 HTTP Range 自动下载（本机可能已缓存 ~361MB），无需凭据；可选 `METBENCH_AIRFOIL_STAGE_DIR`。
2. **训到收敛**：这**不是简单续训**（坏起点）——可能要重设配方（全 1000+ 轨迹、数百 epoch、检查归一化）。目标 rollout median rel-L2 ≲0.1（或文献可用区间 ≤2–3× 文献值）。K=6 checkpoint。
3. **原样重跑** roster runner + `run_seeded_fault_detection_physicsnemo_airfoil.py`——收敛后 node-perm baseline rel-L2 ≠ 0，检测信号才非平凡。

**验收门槛**：
- rollout median rel-L2 收敛到 ≲0.1——**没达到就停**，欠训练上一切对比无效（§1 铁律）。
- 收敛后 violation 可干净归因于"模型违反不变量"而非 under-fitting。
- airfoil by-class 映射很可能**仍**与 cylinder 不同（compressible interior-masked vs incompressible full-field；mirror-y 物理上 inadmissible）——**这是 C37 duality 的 cross-SUT 自然实验，不是问题**。

**claim**：升级 `C35/C36/C37` 的 `wording_allowed`（去 "under-trained/training-state diagnostic"）；**仍禁** "by-class 模式跨 SUT 泛化已证"。
**test**：重跑 `tests/test_physicsnemo_airfoil_primary_roster.py` + `tests/test_seeded_fault_detection_airfoil_cross_sut.py` 对齐收敛后数字。
**锁版本**：训完 `pip freeze`（GPU 环境）并入 requirements。

---

### EXT-3 — 三臂互补 + duality 跨全部收敛 SUT【依赖 MVP 合并 + EXT-1 · 最后做】

**目标**：把 MVP 在单/双 SUT 上的三臂互补矩阵 + validity-coverage duality 扩到**全部收敛 SUT**（cylinder MGN + PointMLP + 收敛后 airfoil），形成 cross-SUT 的系统化证据。

**前置条件（缺一不可）**：① 云端 MVP（PointMLP seeded-fault `C41` + 三臂互补 `C42/C43`）已合入本分支；② EXT-1 airfoil 已收敛。**两者未齐不要开 EXT-3。**

**做什么**：在三个收敛 SUT 上各跑三臂互补（validity-gated MR / accuracy-monitor / generic-expert MR）+ Wilson CI；产 cross-SUT 互补汇总 + duality 跨 SUT 验证（"换 SUT/物理 → 门移除某条 MR → 覆盖随之变化"的可证伪预测在 ≥3 SUT 上的表现）。

**验收门槛**：cross-SUT 互补表每臂带 CI；**全文 0 句 superior/outperforms/better**（grep 自检）；duality 写成"在 N 个收敛 SUT 上的可证伪预测表现"，不外推为定律。

**claim**：`C44-cross-sut-three-arm`（与云端 C41-C43 协调后编号）；`wording_forbidden`：禁 superiority、禁外推为通用 coverage law。
**test**：`tests/test_cross_sut_complementarity.py`。

---

## 6. verification gate（每任务后，全绿才 commit）

```bash
python -m pytest tests -q
python tools/validate_experiment_protocol.py   # rc=0
python tools/validate_research_assets.py       # rc=0
python tools/ist_wordcount.py                  # ≤15000
# 改了 main.tex 则跑 pdflatex 三遍 + bibtex，确认 0 undefined / 0 Missing character / 0 Overfull
grep -rIn -E "outperform|superior|better than" paper/ | grep -v "%"   # 期望空
```

---

## 7. 提交 / 分支 / 报告纪律

- 工作在 `cloud/1q-empirical-expansion` 或其本地子分支；**不直接动 main**。
- 每任务独立 commit，先跑 §6 gate + 敏感扫描。message：`feat(expansion): EXT-N <一句话>` + 验证结果，结尾
  `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`。
- 每任务末报告：新 run 目录、新/扩 claim（blocked→observed）、新 test、关键数字（floor 比值 / rollout L2 / detection CI）、gate 结果、**诚实标注弱证据点**。

---

## 8. 与云端 MVP 的协调（关键，避免撞号/冲突）

- **claim 编号**：云端 MVP 占 **C41（PointMLP seeded-fault）/ C42（三臂互补）/ C43（knife-edge）**；本地 EXT 的 `C12` 是**扩写**（不撞号），新 claim 从 **C44** 起。**开工前先 `git log`/读 claim-ledger 确认云端是否已占用 C41-C43**，避免两边撞号。
- **合并顺序**：EXT-2 独立可先合；EXT-3 依赖云端 MVP + EXT-1，**等 MVP 分支合并后再做**。
- **交回**：所有 EXT 产物（run + claim + test + 报告）留在本分支；最终由人类整合 MVP+EXT 后，在有 LLM 网关凭据的本地会话重跑评审 panel（`tools/run_academic_review_panel.py`）看 EIC 是否上移，并据此定 venue（TSE/TOSEM/回退 IST）。

---

## 附：关键文件锚点

| 用途 | 路径 |
|---|---|
| operator-floor（C12 扩 / 不碰 C32） | `tools/run_operator_floor_sweep.py` + `..._extended.py` |
| airfoil 端到端就绪但欠训练（EXT-1） | `tools/run_seeded_fault_detection_physicsnemo_airfoil.py` + `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/` |
| 三臂 baseline 资产 | `tools/run_expert_mr_baseline.py` / `run_generic_mr_baseline.py` / `research_assets/runs/detection-vs-accuracy/` |
| claim 真相源 | `research_assets/experiments/claim-ledger.yml` |
| 证据门 | `tools/validate_research_assets.py` + `tools/validate_experiment_protocol.py` |
| 姊妹仓库（只读，本地） | `../最小完备MR子集/` |
| 云端 MVP 配对文档 | `docs/cloud_runbook/1q_empirical_expansion_kickoff.md` |
| 完整规则 / 任务台账 | `CLAUDE.md` / `NEXT_STEPS.md`（顶部 2026-06-20 段） |
