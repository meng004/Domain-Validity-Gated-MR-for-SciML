# 云端 Kickoff：真实机制级故障 → 检验 by-class 是否「涌现」(FNO + PINN)

> 单文件冷启动 runbook，**云端执行**。执行者是无先验上下文的云端 Claude Code 会话。**先完整读完再动手。**
>
> 版本：2026-06-20 · 分支：`cloud/1q-empirical-expansion`。

---

## 0. 人类如何调用

```
git fetch && git checkout cloud/1q-empirical-expansion && git pull
读取 docs/cloud_runbook/realistic_fault_emergence_kickoff.md
执行任务
```

---

## 1. 任务背景与为什么(必读)

一次对抗式评估发现:现有 FNO/PINN seeded-fault 实验(claims C45/C46)的「by-class 干净分离」**是构造的,不是涌现的**——故障是按"正交于某个 MR 的零空间/非零空间"**设计**的解析变换(如 `cos(πx)` 专为保持两不变量、`asym_y` 专为破对称),所以"哪个 MR 抓哪个故障"由故障的解析对称性**预先决定**,SUT 几乎不参与判别。这是自洽性演示,不是检测能力的独立证据;跨 SUT 响应零方差,使 Wilson CI 名义化。

**本实验的唯一目的:用真实机制级故障(未按不变量定制)重做,检验 by-class 结构是否真的「涌现」。**

- 若真实故障下 by-class 仍清晰涌现 → 证据从「构造演示」升级为「涌现经验规律」,显著反驳评审的 "incremental/fragmented"。
- 若结果更乱(某些 bug 被两 MR 同抓、或漏检) → **如实报告**;这也是真相,远比"完美但构造"经得起 Reviewer 2。

**诚实风险(必须接受):** 真实故障的检测矩阵**可能不再干净对角**。**不允许**为得到漂亮结果而筛故障、调阈值、或挑幅度。结果是什么报什么。

---

## 2. 环境(动手前自检)

- 仓库在当前工作目录;云端 shell **不加 `rtk`**;只读 sibling 在 `/home/user/Minimum-MR-SubSet/`(本实验**不需要**)。
- 全程 **CPU**,依赖 `torch`(CPU)+ `numpy`(+ `scipy` 若复用 EXT-2 工具,本实验不需要)。无 GPU、无 METBENCH、无网关凭据。

```bash
python -m pytest tests -q                       # 基线应全 passed(当前 404+)
python tools/validate_research_assets.py; echo rc=$?   # 0
python -c "import torch;print('torch',torch.__version__)"
```

**已收敛 SUT(committed,本实验输入):**
- FNO K=6 roster：`research_assets/runs/fno-k6-roster/{burgers,heat}_s{0,1,2}/sut/checkpoint.pt`
- Burgers PINN K=6 roster：`research_assets/runs/pinn-k6-roster/burgers_s{0..5}/sut/checkpoint.pt` + 共享 reference `research_assets/runs/pinn-cross-family/reference_solution.npz`

---

## 3. 硬约束(防自我构造 + 诚实,违反即整轮作废)

1. **故障未按不变量定制**:照 §4 的真实 bug 清单实现;**不得**新增/改造故障使其"恰好"命中某 MR。每条故障是一个真实 surrogate bug,其 MR 响应**由实验发现**。
2. **阈值 predeclared,禁止调**:复用现有 runner 的阈值——FNO `TRANSLATION_TOL=1e-5`、`CONSERVATION_BREAK_TOL=0.05`(见 `tools/run_seeded_fault_detection_fno.py`);PINN `MR_B_FACTOR=3.0`、`MR_C_TOL=0.10`(见 `tools/run_seeded_fault_detection_pinn.py`)。**一个数都不许为凑结果改。**
3. **幅度按"真实损坏量级"设,逐条报实测扰动**:每条故障目标 output rel-L2 ≈ 0.10–0.30(明显损坏场),在 runner 里**固定**该幅度并在报告里记录每条故障的 `output_perturbation_rel_l2`。**禁止**把幅度调到刚好踩阈值。
4. **检测矩阵如实报**:报告**涌现**的 per-fault × per-MR 检测结果,包括(a)被多个 MR 同抓的故障、(b)漏检的故障、(c)各 MR 的 detection rate。**禁止**删除/隐藏"不干净"的条目。
5. **盲区 = 涌现**:报告真实故障中**恰好**逃过全部 MR 的那些(若有),连同其扰动幅度;**不得**为制造盲区而设计专门故障。若没有真实故障逃过两 MR,如实写"无涌现盲区"。
6. **claim-ledger 纪律**:新 claim 先 `status: blocked`,真跑出才转 `observed`;不 widen `wording_allowed`;每条配 `wording_forbidden`(禁 superiority/泛化/real-world rate)。当前最高 claim 是 **C47**,新 claim 从 **C48** 起。
7. **不主张 superiority**;**显式报错**(漏检、N/A、退化都明说)。
8. 提交前敏感扫描(key/真实 base_url/`/Users/<name>` 个人路径)。

---

## 4. 真实故障清单(实现这些,不增不改其 MR 针对性)

每条幅度调到 output rel-L2 ≈ 0.10–0.30(逐条记录实测值)。`channel_swap` 仅适用于 2 通道(Burgers u_x/u_y);heat 标量上记 **not-applicable**(像 MGN 的 MA mutant 那样诚实标注,不算漏检)。

| key | 真实 bug | 实现要点(输出场级) |
|---|---|---|
| `boundary_band_corrupt` | 边界区处理错(BC) | 把最外 2-cell 边带的值置零或大幅扰动 |
| `global_renorm` | 反归一化/标定错(NS) | 整场 × (1+ε),ε 取使 rel-L2 落入目标带 |
| `channel_swap` | 通道索引错(PC,仅 Burgers) | 交换 u_x ↔ u_y |
| `region_dropout` | 掩码/区域失效 | 把一个 1/4 空间 patch 置零 |
| `gaussian_noise` | 数值不稳/噪声 | 加固定 spatial 噪声场(确定性 seed,使 MR-B 在置换/反射下可重算) |
| `mode_truncation` | FNO 高频模截断(over-smooth) | 对输出做 FFT、置零高频半、逆变换(FNO);PINN 上用强低通近似 |
| `spatial_shift` | 输运/相位错(advection 速度错) | 场空间平移 k=grid/6 格(FNO:`np.roll`;PINN:在 x−s 处重查模型) |
| `sharpen` | 过正则/高通放大 | 场 + α·(field − smooth(field)) |

> 注意:`spatial_shift`、`sharpen`、`mode_truncation` 在旧实验里被当作"专为保不变量设计的盲区";这里它们只是**清单里的普通真实 bug**,其 MR 响应由实验发现——这正是检验旧"盲区"是否真盲、还是构造产物的关键。

**检测器(复用现有 MR,不新增):**
- FNO:周期平移等变 MR + 周期通道和(质量)MR。
- PINN:MR-B mirror-y 等变 + MR-C 守恒(∫u_x)。MR-A 置换对逐点 MLP vacuous,**不**当检测器。

---

## 5. 任务步骤

### 任务 A — FNO 真实故障涌现
1. 先读 `tools/run_seeded_fault_detection_fno.py`(复用其 SUT 加载、MR 评估、Wilson CI、报告 schema;**只换故障目录** §4,阈值不动)。
2. 新建 `tools/run_realistic_fault_fno.py`(**不改旧 runner**,旧 C45 实验保留作对照)。
3. 跑 K=6 FNO,产 `research_assets/runs/fno-realistic-fault/fno_realistic_fault_report.json`:per-fault 检测(translation/conservation/both/none)+ detection rate + Wilson CI + **每条 `output_perturbation_rel_l2`** + 涌现盲区(若有)。
4. claim `C48-fno-realistic-fault-emergence`(先 blocked→observed)。

### 任务 B — PINN 真实故障涌现
同 A,基于 `tools/run_seeded_fault_detection_pinn.py` → `tools/run_realistic_fault_pinn.py` → `research_assets/runs/pinn-realistic-fault/...` → claim `C49-pinn-realistic-fault-emergence`。

### 任务 C — 测试 + PROVENANCE
- `tests/test_fno_realistic_fault.py` / `tests/test_pinn_realistic_fault.py`:pin 报告关键数 + 断言「报告含每条故障的 perturbation 幅度」+ 「0 处 superiority 措辞」。**测试不得断言"必须干净对角"**——只断言报告完整、数字与 runner 一致、措辞合规。
- 每个 run 目录写 `PROVENANCE.md`(输入表、环境、命令、pinned 涌现结果、对应 claim),格式照 `research_assets/runs/pointmlp-cylinder-seeded-fault-detection/PROVENANCE.md`。

---

## 6. 涌现结果报告强制(交回人类时必须明确回答)

在每个报告的 `summary` 与最终给人类的报告里,**明确回答**:

1. **by-class 是否涌现?** 对每个真实故障,列出它实际被哪些 MR 抓到。统计:有多少故障**唯一**定位到单个 MR(清晰 by-class)、多少被**多个** MR 同抓(by-class 模糊)、多少**漏检**。
2. **旧"盲区"是否真盲?** `spatial_shift`/`sharpen`/`mode_truncation` 在真实幅度(rel-L2 0.1–0.3)下,是否仍逃过两 MR?给出它们的扰动幅度与检测结果。
3. **诚实裁决**:真实故障下的 by-class 结构 **比构造版更强 / 相当 / 更弱**?一句话。

> 这三问的答案决定本地会话如何改稿:**若涌现清晰**→把 main.tex/manuscript.md 的「4 架构 by-class」从构造证据升级为涌现证据;**若更弱/更乱**→诚实弱化措辞。云端只产证据 + 如实回答,**不改 main.tex**(整合与 panel 在本地)。

---

## 7. verification gate + 提交

```bash
python -m pytest tests -q                     # 全绿(含新 test)
python tools/validate_research_assets.py      # rc=0
python tools/validate_experiment_protocol.py  # rc=0
grep -rIn -E "outperform|superior|better than" research_assets/runs/fno-realistic-fault research_assets/runs/pinn-realistic-fault | grep -v "%"   # 期望空
```

- 每任务独立 commit:`feat(expansion): realistic-fault emergence FNO|PINN (C48|C49)` + 验证结果,结尾 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`。
- push 前 fetch;若分支分叉(本地也在动),merge(claim-ledger 冲突保留双方 claim)。
- **交回人类的报告**必须含 §6 三问的明确答案 + 每条故障的 perturbation 幅度表。

---

## 附:关键文件锚点

| 用途 | 路径 |
|---|---|
| FNO 旧 runner(复用骨架,只换故障) | `tools/run_seeded_fault_detection_fno.py` |
| PINN 旧 runner(复用骨架) | `tools/run_seeded_fault_detection_pinn.py` |
| FNO checkpoints | `research_assets/runs/fno-k6-roster/` |
| PINN checkpoints + 共享 reference | `research_assets/runs/pinn-k6-roster/` + `research_assets/runs/pinn-cross-family/reference_solution.npz` |
| claim 真相源(C47 最高,新增从 C48) | `research_assets/experiments/claim-ledger.yml` |
| PROVENANCE 模板 | `research_assets/runs/pointmlp-cylinder-seeded-fault-detection/PROVENANCE.md` |
| 完整规则 | `CLAUDE.md` |
