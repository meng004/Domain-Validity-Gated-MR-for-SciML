# GPU Kickoff:补全 airfoil 的三臂(arm2 accuracy-monitor + arm3 ungated-generic)

> 单文件冷启动 runbook,**有 CUDA GPU 的机器执行**(本地 RTX 或云端皆可;无 physicsnemo/CUDA 的 Mac 跑不了)。执行者是无先验上下文的 GPU 会话,**先完整读完再动手**。
> 版本:2026-06-21 · 分支:`cloud/1q-empirical-expansion` · 这是 EXT-1 所在的同一分支与同一机器栈。

## 0. 人类如何调用
```
git fetch && git checkout cloud/1q-empirical-expansion && git pull
读取 docs/cloud_runbook/ext3_airfoil_three_arm_kickoff.md
执行任务
```

## 1. 背景与为什么(必读)
EXT-1 已把 airfoil 训到收敛(C35,K=6,`.../physicsnemo-mgn-airfoil-primary-roster/checkpoint_k0*.pt`,rollout 0.92)。EXT-3 的**本地整合**(C51,`tools/run_ext3_cross_sut_three_arm.py`)已把三个收敛 SUT 的三臂收成一张 cross-SUT 表,但 **airfoil 只有 arm1(MR 臂,C36)**;arm2(accuracy-monitor)、arm3(ungated-generic gate value)缺,因为需**活的 PhysicsNeMo airfoil 模型**(GPU)。本任务补这两臂,凑齐"三 SUT 各跑三臂"。

**诚实预期(先说清,避免反伤)**:airfoil 是**低保真模型**(rollout 0.92)。所以 arm2 大概率检出很少(故障要把 rollout 推过 2×0.92=1.84 才算检到);arm3 的 gate-rejected 模板在不准的模型上误报率会高。**这些都如实报,本任务价值是"补全 cross-SUT 三臂表",不是"airfoil 强检测"。** 严禁为了好看调参/挑数。

## 2. 环境与数据(复用 EXT-1 已建的 harness)

EXT-1 已把 GPU 环境与 airfoil 数据的搭建脚本提交在 `tools/_ext1_*.sh`。**先自检;不齐就按下序复用,不要从零重搭**:

```bash
# (a) 自检:三者齐 → 直接跳到 §4
python -c "import torch,physicsnemo;print('cuda',torch.cuda.is_available())"   # 期望 True
ls research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/checkpoint_k0*.pt | wc -l   # 期望 6
bash tools/_ext1_verify_gpu.sh        # GPU 可见性自检

# (b) 若 physicsnemo/torch-cuda 缺(非 EXT-1 原机或环境已失效),按序复用:
bash tools/_ext1_venv_setup.sh
bash tools/_ext1_install_torch_cu124.sh    # 或 _ext1_install_torch.sh(按你 CUDA 版本)
bash tools/_ext1_install_stack.sh          # physicsnemo + 依赖栈
bash tools/_ext1_fix_torchvision.sh        # 若 torchvision ABI 报错才需

# (c) 若 airfoil 官方数据未 staged:
bash tools/_ext1_stage_data.sh             # 落 DeepMind airfoil TFRecords

# (d) 基线门(env 齐后)
python -m pytest tests -q                  # 全绿(缺 dep 的 skip 记录,勿当失败)
python tools/validate_research_assets.py; python tools/validate_experiment_protocol.py   # rc=0
```

**输入(committed,checkout 后即有)**:
- converged airfoil checkpoints(C35 roster,6 个 `checkpoint_k0*.pt`);
- **arm1 模板** `tools/run_seeded_fault_detection_physicsnemo_airfoil.py`(+ 一键复跑 `tools/_ext1_seeded_fault.sh`);
- **arm2/arm3 标准做法**参照 `tools/run_three_arm_complementarity_pointmlp.py`(`arms_for` 的 accuracy 臂、`fp_rate` 的 generic 误报臂);
- 本地整合脚本 `tools/run_ext3_cross_sut_three_arm.py`(Task C 跑完刷新它)。

## 3. 硬约束(违反即整轮作废)
1. **实事求是**:不伪造、不挑数;每个数有 run 目录 + ledger。airfoil 检出低就如实低。
2. **claim 纪律**:新 claim 从 **C52** 起(当前最高 C51)。先 `status: blocked`、真跑出转 `observed`;配 `wording_forbidden`。**绝不主张 superiority / outperforms**;**绝不**把 airfoil 三臂写成"强检测/可靠率"。
3. **mirror-y 在 airfoil 不可入**(非零迎角,门已排除)——arm1 不跑 mirror-y;arm3 的 mirror-y 模板按"gate-rejected"处理(它正是 duality 的点)。
4. **accuracy-monitor 阈值** = 2 × airfoil 无故障基线 rollout(≈0.92×2=1.84),与 PointMLP 三臂同口径(`ACCURACY_ROLLOUT_MULT=2.0`)。
5. **最小修改 / 显式报错**;敏感扫描(key、真实 `/Users/<名>`)。

## 4. 任务
### Task A — airfoil arm2 + arm3
扩展 `run_seeded_fault_detection_physicsnemo_airfoil.py`(或新建 `run_airfoil_three_arm.py`),在**收敛 airfoil checkpoints** 上,对与 C36 同一 10-mutant 五类故障目录:
- **arm2 accuracy-monitor**:每故障算 rollout rel-L2,检出 = rollout ≥ 2× 无故障基线;输出 per-fault + 检出计数 + Wilson CI。
- **arm3 ungated-generic gate value**:照 `run_three_arm_complementarity_pointmlp.py` 的 `fp_rate` 做法,对一组 generic MT 模板(node-perm 真不变量 + mirror-y/translation/scaling 等非不变量)算**无故障 SUT 上的 baseline 误报率**;报 gate-admitted vs gate-rejected 的误报对比。
- 输出 `research_assets/runs/.../physicsnemo-mgn-airfoil-three-arm/raw/metric_ledger.json`,schema 对齐 PointMLP 三臂(arm1 可复用 C36 或重算)。

### Task B — claim + test + PROVENANCE
- claim `C52-airfoil-three-arm`(blocked→observed)。`wording_allowed` 只许实跑的 arm2/arm3 数字 + "airfoil 低保真下检出有限"的诚实陈述;`wording_forbidden`:superiority、competitive accuracy、强检测、可靠率。
- `tests/test_airfoil_three_arm.py`:pin arm2/arm3 计数 + "0 superiority" + 低保真诚实标注在场。
- PROVENANCE.md(照 `ext3-cross-sut-three-arm/PROVENANCE.md`)。

### Task C — 刷新 cross-SUT 整合
跑 `python tools/run_ext3_cross_sut_three_arm.py`(它会自动把 airfoil arm2/arm3 从新 ledger 拉进来——**需先改该脚本让 airfoil 段读新三臂 ledger 而非标 GPU-pending**),C51 报告里 airfoil 的 `arms_run` 变成 `[arm1,arm2,arm3]`。

## 5. 交回人类必答
1. airfoil arm2 检出几个 / 总几个(Wilson CI)?arm3 gate-admitted vs rejected 误报率?
2. 与 cylinder/PointMLP 三臂并表后,**cross-SUT 互补结构是否一致**(MR 抓 accuracy 漏的、gate 去误报)?airfoil 因低保真有何差异?
3. duality 是否仍 0 反例(airfoil 上没有"被排除的 mirror-y 却抓到故障"的情况)?

## 6. verification + 提交
```bash
python -m pytest tests -q                         # 全绿(含新 test)
python tools/validate_research_assets.py; python tools/validate_experiment_protocol.py   # rc=0
grep -rIn -E "outperform|better than|state-of-the-art" research_assets/runs/*airfoil-three-arm*   # 空(裸 superior 不查:合规免责语"not a superiority claim"本就含它)
```
- commit:`feat(ext3): airfoil three-arm arm2/arm3 on converged C35 (C52)` + 验证;结尾 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`。push 前 fetch;分叉则 merge(ledger 冲突保留双方 claim)。
- **不改 main.tex**——正文整合由有上下文的本地会话做(收编散落 cell 进一张 cross-SUT 表,降 over-extension)。

## 附:锚点
| 用途 | 路径 |
|---|---|
| converged airfoil checkpoints(C35) | `research_assets/runs/production-grade-sut-extension/physicsnemo-mgn-airfoil-primary-roster/checkpoint_k0*.pt` |
| airfoil seeded-fault runner(arm1 模板) | `tools/run_seeded_fault_detection_physicsnemo_airfoil.py` |
| 三臂参照(arm2/arm3 做法) | `tools/run_three_arm_complementarity_pointmlp.py` |
| 本地整合(跑完刷新它) | `tools/run_ext3_cross_sut_three_arm.py` |
| claim 真相源(C51 最高,新增 C52) | `research_assets/experiments/claim-ledger.yml` |
| 完整规则 | `CLAUDE.md` |
