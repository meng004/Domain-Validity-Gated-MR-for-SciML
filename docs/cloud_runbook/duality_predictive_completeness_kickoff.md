# 云端 Kickoff：把 validity-coverage duality 升级为「可证伪的覆盖完备性预言」(FNO + PINN)

> 单文件冷启动 runbook，**云端执行**。执行者是无先验上下文的云端 Claude Code 会话。**先完整读完再动手。**
>
> 版本：2026-06-20 · 分支：`cloud/1q-empirical-expansion`。

---

## 0. 人类如何调用
```
git fetch && git checkout cloud/1q-empirical-expansion && git pull
读取 docs/cloud_runbook/duality_predictive_completeness_kickoff.md
执行任务
```

---

## 1. 任务背景与为什么(必读)

上一轮真实故障实验(claims C48/C49)显示:真实 SciML bug 的可检性按"扰动了哪个被测不变量"涌现成一个 2×2 结构(改 mass→守恒 MR;破对称/平移→对称 MR;两者→both;都不动→blind)。本任务把这个观察升级为 **validity-coverage duality 的可证伪、先验预言**,但**只取其中真正非平凡的部分**。

**必须先分清(决定本实验只证什么):**
- 「故障改 ∫ ⇒ 守恒 MR 抓它」**近乎定义反复**——守恒检测器本身就是"∫ 变了 > 阈值"。**单不变量的检测预测不是本实验的卖点,不得当作发现宣称。**
- **真正非平凡、可证伪的核心只有两条:**
  1. **盲区完备性**:一个故障若保持**全部**被测不变量,则它对**整个 MR 套件**(不只某一个 MR)不可见——即套件**没有隐藏覆盖**。这可被证伪(只要有一个"保全部不变量"的故障被任一 MR 抓到)。
  2. **幅度无关性**:盲是不变量性质,**与故障把场打多烂无关**——一个保全部不变量、却把输出损坏 ~0.5 rel-L2 的大故障,**仍**对整套 MR 不可见。

**本实验只证这两条(定性),不证任何检测率/概率/定量覆盖模型。**

---

## 2. 环境(自检)
- 仓库当前工作目录;云端 shell 不加 `rtk`;sibling 在 `/home/user/`(不需要)。CPU + `torch`(+`numpy`)。无 GPU/凭据。
```bash
python -m pytest tests -q                          # 基线全 passed
python tools/validate_research_assets.py; echo rc=$?
```
**输入(committed):** FNO/PINN checkpoints(`fno-k6-roster/`、`pinn-k6-roster/`+`pinn-cross-family/reference_solution.npz`);上一轮真实故障报告 `research_assets/runs/fno-realistic-fault/...`、`pinn-realistic-fault/...`(含每故障 by-class 与扰动幅度);故障实现 `tools/run_realistic_fault_fno.py`、`tools/run_realistic_fault_pinn.py`。

---

## 3. 硬约束(防循环 + 定性边界,违反即整轮作废)

1. **先验预测必须非循环**:每个故障的"不变量签名"由**故障算子本身的数学性质**决定,在一个**通用测试场**(随机或解析场,**不是模型输出**)上计算:
   - `perturbs_conservation` = 在通用场上 ∫ 相对变化 > 0?
   - `breaks_symmetry_or_translation` = 算子与对称/平移**不**对易(`‖R(F(g)) − F(R(g))‖/‖F(g)‖ > 0`)?
   据此**先验**预测该故障落 2×2 哪格 / 是否盲——**严禁**用上一轮的检测结果来"预测"。
2. **只证两条非平凡命题**(§1):盲区完备性 + 幅度无关性。单不变量检测预测在报告里**明确标注为"near-definitional, not a finding"**。
3. **如实报告 mismatch**:若某故障**先验预测盲但实测被抓**(或反之),这是对 duality 的**证伪**,必须**显著报告**,不得掩盖或调参消除。
4. **阈值 predeclared 不改**(复用现有 runner 阈值)。**幅度逐故障报实测 rel-L2**,大盲故障须真的大(目标 ~0.5),达不到就如实说"该架构光滑场上无法构造大幅度保不变量故障"。
5. **C37 定性边界**:`wording_forbidden` 禁"validated/quantitative predictive coverage model"、"coverage predicted at detection rates/probabilities"、"duality proven for all MRs"。本实验产出只能是**定性类预测 + 完备性/幅度无关性的有界确证**。
6. claim 从 **C50** 起(当前最高 C49)。不主张 superiority;显式报错。提交前敏感扫描(key/真实用户名 `/Users/<真名>`)。

---

## 4. 任务

### Task A — 先验算子分类(非循环)
新建 `tools/run_duality_predictive_completeness.py`。对 FNO 与 PINN 各自故障目录里的每个故障算子 F:
- 在一个**通用结构化测试场**(如 `default_rng` 随机场 + 一个解析场,与模型无关)上,计算 `perturbs_conservation` 与 `breaks_symmetry_or_translation`(定义见 §3.1)。
- 据此先验标注预测类:`conservation` / `symmetry-translation` / `both` / `blind`。
- 输出"先验预测表"(故障 → 两个布尔 → 预测类),**独立于任何检测结果**。

### Task B — predict-then-verify
- 读上一轮 `fno-realistic-fault` / `pinn-realistic-fault` 报告里的**实测** by-class。
- 逐故障对照 **先验预测 vs 实测**,统计一致/mismatch。
- 在报告里**明确分层**:(i) 单不变量检测一致——标 "near-definitional";(ii) **盲区完备性**——所有"先验保全部不变量"的故障是否**实测对全套 MR 不可见**;(iii) 任何 mismatch(证伪)。

### Task C — 大幅度保不变量盲故障(关键,补 FNO 缺口)
- **PINN**:确认上一轮 `spatial_shift`(实测 ~0.63 rel-L2、保 ∫ + 对称/平移、实测全盲)即"大幅度盲"的证据,纳入本报告。
- **FNO**:现有 FNO 盲故障是 no-op(0.000–0.006)。**设计/搜一个保通道和 + 平移等变、但在 FNO 光滑场上仍达 rel-L2 ~0.5 的真实故障**(候选:更大平移 shift=grid/2「半场互换」;或在结构更丰富的 eval case 上评估;或别的保和大结构变换)。先验须预测盲;实测验证是否盲。
- **若 FNO 光滑低分辨场上确实无法构造大幅度保不变量故障** → **如实报告**为该架构的真实局限(blind-completeness 在 FNO 上只能由 no-op 故障弱确证,大幅度确证由 PINN 提供)。不得伪造大幅度。

### Task D — claim + test + PROVENANCE
- claim `C50-duality-predictive-completeness`(先 blocked→observed)。`wording_allowed` 只许:先验不变量签名预测故障**类**(定性);盲区完备性(保全部不变量⇒全套不可见)在 FNO/PINN 上的有界确证;幅度无关性(PINN 0.63 大故障仍盲,FNO 见 Task C 结果)。`wording_forbidden`:定量覆盖模型 / 检测率预测 / 跨架构泛化 / superiority / "duality proven"。
- `tests/test_duality_predictive_completeness.py`:pin 先验预测表 + predict-vs-actual 一致计数 + "near-definitional 标注在场" + "0 处 superiority"。**不得**断言"必须全部一致"——若有 mismatch,test 断言报告**记录**了它。
- `research_assets/runs/duality-predictive-completeness/PROVENANCE.md`(格式照 `pointmlp-cylinder-seeded-fault-detection/PROVENANCE.md`)。

---

## 5. 交回人类时必须明确回答
1. **先验预测 vs 实测一致到什么程度?**(分层:near-definitional 单不变量 / 盲区完备性 / mismatch)
2. **盲区完备性是否成立?** 有没有"保全部不变量却被某 MR 抓"的证伪案例?
3. **幅度无关性**:FNO 上是否找到大幅度(~0.5)保不变量盲故障?PINN 0.63 那个确认盲?还是 FNO 只能 no-op 弱确证(如实说)?
4. **诚实裁决**:duality 作为"先验定性可预测 + 覆盖完备"的命题,在这两架构上**成立 / 部分成立 / 被证伪**?

> 这些答案决定本地改稿:成立→把 coverage/duality 段升级为"先验可预测 + 完备性确证";部分/证伪→如实弱化。云端只产证据 + 答 4 问,**不改 main.tex**。

---

## 6. verification + 提交
```bash
python -m pytest tests -q                          # 全绿(含新 test)
python tools/validate_research_assets.py; python tools/validate_experiment_protocol.py   # rc=0
grep -rIn -E "outperform|superior|better than" research_assets/runs/duality-predictive-completeness | grep -v "%"   # 空
```
- commit:`feat(expansion): duality predictive coverage-completeness (C50)` + 验证;结尾 `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`。push 前 fetch;分叉则 merge(ledger 冲突保留双方 claim)。
- 交回报告含 §5 四问答案 + 先验预测表 + 各盲故障实测幅度。

---

## 附:锚点
| 用途 | 路径 |
|---|---|
| 上轮真实故障报告(实测 by-class + 幅度) | `research_assets/runs/{fno,pinn}-realistic-fault/*.json` |
| 故障算子实现(复用) | `tools/run_realistic_fault_{fno,pinn}.py` |
| checkpoints | `research_assets/runs/{fno-k6-roster,pinn-k6-roster}/` + `pinn-cross-family/reference_solution.npz` |
| claim 真相源(C49 最高,新增 C50) | `research_assets/experiments/claim-ledger.yml` |
| PROVENANCE 模板 | `research_assets/runs/pointmlp-cylinder-seeded-fault-detection/PROVENANCE.md` |
| 完整规则 | `CLAUDE.md` |
