# 执行日志 · TOSEM Real-MRDefect-10 种子试点 · SMS-vs-MS 判别力

> 起始：2026-07-01 · 会话：claude-code（10h 自主推进）
> 本文件是种子试点的唯一 live 执行日志。配套计划：`2026-07-01-tosem-real-mrdefect-seed-pilot.md`；
> 候选库：`research/tosem_candidate_libraries.md`；缺陷卡：`data/realdefects/`（或 `research/real_mrdefect_seed_cards.md`）；
> 代码：`code/realdefects/`；测试：`code/tests/realdefects/`。

---

## 阶段 0 · 恢复上下文与建立任务板（2026-07-01）

### 0.1 核心目标（本会话锁定）

- **Real-MRDefect-10**：挖掘 ≤10 张**高质量、可追溯**的真实、MR-可检行为缺陷卡，覆盖数值等价/广播/dtype/排序重排/图同构/dataframe algebra/坐标对齐/编译 JIT 等价/图像变换不变性等 MR family。
- **SMS-vs-MS 判别力**：在真实 MR-可检缺陷上，语义变异分数 SMS 是否比传统语法变异分数 MS 更能判别 MR 测试套件质量，并能否形成 TOSEM 投稿所需的**初步（seed / go-no-go）**证据——**不夸大为最终统计结论**。

### 0.2 禁止范围（不得漂移）

一般 DL testing / LLM testing / API testing / 自动驾驶测试综述 / 泛 benchmark 建设 / 普通缺陷数据集建设——除非该产出**直接**贡献「真实 MR-可检缺陷 + SMS-vs-MS 判别力」。
非-MR-可检行为一律排除：crash-only、API misuse、文档歧义、安装失败、性能-only、仅异常类型变化、用户错误——除非能构造明确 MR oracle（source x、transform T(x)、relation R(f(x),f(T(x)))、violating observation）。

### 0.3 Ground truth 核查（实事求是）

简报点名的 5 个 ground-truth 路径 **在本仓 main 上全部不存在**：

| 简报路径 | 状态 | 最接近的真实文件 |
|---|---|---|
| `manuscript/docs/review_2026-06-30/venue_ceiling_and_improvement_plan.md` | ❌ 不存在 | `paper/65_venue_ceiling_decision.md`（天花板=TOSEM 决策）|
| `docs/superpowers/plans/2026-07-01-tosem-real-mrdefect-seed-pilot.md` | ❌ 不存在 | 本会话创建（见配套计划）|
| `research/tosem_candidate_libraries.md` | ❌ 不存在 | 本会话创建（Phase 1）|
| `code/realdefects/schema.py` | ❌ 不存在 | 无；本仓用 `tools/`+`tests/` 约定，无 `code/` 树 |
| `code/realdefects/power.py` | ❌ 不存在 | 无 |
| `code/tests/realdefects/` | ❌ 不存在 | 无 |

`rtk rg -i "tosem|real.?defect|semantic mutation score|\bSMS\b|mutation score|candidate.librar|numpy|scipy|pandas"` 在 `paper/`、`research_assets/`、全仓（除 PDF）→ **零命中**。即：**SMS-vs-MS / Real-MRDefect-10 这条线在本仓无任何既有痕迹。**

### 0.4 ⚠️ 战略分叉（最高优先级 open question，需用户拍板）

本会话简报方向 与 仓库已拍板方向 **不同源**，必须挑明（CLAUDE.md §5）：

- **仓库已拍板（`NEXT_STEPS.md` 2026-07-01 + `paper/65/67/68`）**：A+B+C 三杆、**理论优先**、TOSEM 稳投。当前 next-action = 拍板 `paper/68` §8 三项 → 启动 **Phase B**（唯一枢轴 = operator-floor bound 一般化到非结构网格 soundness 定理）。论文被测对象 = **SciML 代理**（MeshGraphNets/PointMLP 圆柱绕流、PINN、FNO），头条贡献 = 「数值可判定性 soundness 判据」。
- **本会话简报方向**：Real-MRDefect-10 = 挖掘**通用科学 Python 库**（NumPy/SciPy/pandas/sklearn/NetworkX/xarray/TF/PyTorch/TVM/OpenCV）的真实 MR-可检缺陷，评 SMS-vs-MS 判别力。被测对象是**库函数**，不是训练好的 SciML 代理。

**两者的被测对象总体不同**（库函数 vs 训练代理），SMS-vs-MS 的变异分数框架也不在现稿贡献结构里。若直接把 Real-MRDefect-10 当论文主线，等于把论文从「SciML 代理 soundness 判据」重框定为「真实 MR-可检库缺陷上的 SMS-vs-MS 实证」——这是重大改向，属 `NEXT_STEPS` 已标「待用户拍板」的战略级决策。

**但存在一条诚实的桥**：现计划 `paper/66` Phase 2 的**最稀缺需求**正是「自造平凡 mutant 须换真实、经独立校验的故障基准」、`paper/66` 明写「MS 是否被语法/低层 mutant 噪声误导」。因此**真实 MR-可检缺陷的证据扫描，对已拍板计划本身也是有价值的输入**（可辩护故障基准的可行性证据），无论最终是否采纳 SMS-vs-MS 框架。

**本会话处置（保守、可逆、双向服务）**：
1. 只产出**新增的、加性的研究工件**（候选库 review、真实缺陷证据卡、schema/validator/power 工具），全部落在**新目录**（`research/`、`code/realdefects/`、`data/realdefects/`）。
2. **不碰** manuscript / claim-ledger / 既有 `tests/`——不对论文做任何 SMS-vs-MS 改向或声明。
3. 缺陷卡一律**证据优先、candidate 起步**；URL/版本/修复点/复现缺任一 → 只能 candidate，绝不标 reproducible/verified。
4. 把「是否采纳 SMS-vs-MS 主线、是否与 A+B+C 融合」作为**头号 open question 交用户拍板**，本会话不替用户做此改向决定。

### 0.5 既有测试状态基线（挖缺陷前，未改任何实现代码）

- 环境：Python 3.12.7、numpy 2.5.0、pytest 8.4.2。
- `python -m pytest tests -q` → **9 failed / 435 passed**（444 collected，~1.7s）。
- 9 个失败均为绑定 IST/manuscript prose 的既有回归 guard（RESS 重定位后发散所致），**与本 seed pilot 无关**。基线记录，不修复（简报：挖缺陷前不改实现代码）。失败清单：
  - `test_p2_adversarial_mutants.py`（R4 section × 2）
  - `test_phase14_fno_primary_workflow.py`（fno promote）
  - `test_phase4_clarity_surgery.py`（× 3）
  - `test_stage2p5_submission_readiness.py`（× 2）
  - `test_stage4_revision_readiness.py`（× 1）
- `code/tests/realdefects/` 本会话新建，起始为空。

### 0.6 阶段 0 门（自审）

- [x] 能清楚说明 Real-MRDefect-10 目标（见 0.1）。
- [x] 测试状态已记录（见 0.5，9 failed 均为无关既有 guard，非本线引入）。
- [x] 没有在挖缺陷前修改任何实现代码（仅新建空目录 + 文档）。
- [x] 战略分叉已如实挑明（0.4），未静默混入两套矛盾方案。

**阶段 0 门：PASS**（附头号 open question：SMS-vs-MS 是否采纳为论文主线 / 与 A+B+C 融合——待用户拍板）。

---

## 阶段 1 · 候选库复核（2026-07-01）

交付：`research/tosem_candidate_libraries.md`。seed-core = NumPy/SciPy/pandas/scikit-learn/NetworkX；candidate = xarray；reserve(capped ≤40%) = TensorFlow/PyTorch/TVM/OpenCV。逐库 MR family 预期见该文件。

**阶段 1 门：PASS**（每项有 MR family 预期；无无证据扩张；分类与目标一致；无 needs_pdf 当 verified）。

## 阶段 2 · 真实缺陷挖掘（2026-07-01）

交付：`data/realdefects/seed_cards.json`（9 卡，唯一真相源）+ 人类可读 `research/real_mrdefect_seed_cards.md`。

- 9 卡跨 6 库 8 MR family，DL/tensor 占比 **0**（远在 40% 上限内）。
- 每卡 issue 状态/日期经 `gh issue view` **实时核实**（numpy #20305/#30349、scipy #21876/#15927、pandas #59350/#33732、sklearn #15438、networkx #8093、xarray #7766）。
- **全部 status=candidate**：URL+行为证据存在，但 MR violation **未本地复现**（诚实下限）。版本字段标 (unconfirmed) 处未 checkout 运行。
- 诚实 nuance 已标注：numpy #30349 是差分不一致（优化路径有确定正确值 [18,18,18]，非 crash-only）；scipy #15927 含 FFT NaN 传播的 FP 语义 nuance，MR 限定在应有限的位置。

**阶段 2 门：PASS**（每卡有 URL；≥1 条清楚 MR 可检——#30349 优化等价、#21876 方法等价、#15438 稀疏-稠密等价皆教科书 MR；不能复现只标 candidate；validator 强制无 crash-only/API-misuse 混入）。

## 阶段 3 · TDD 本地工具（2026-07-01）

交付：`code/realdefects/{schema,validator,power}.py` + `code/tests/realdefects/`（conftest 注入 sys.path，规避 `code` 与 stdlib 撞名）。

- `schema.py`：字段/status/MR-oracle/DL-tensor-cap/crash-only-markers 单一真相源。
- `validator.py`：evidence 完整性 + MR-oracle 完整性 + crash-only 拒绝 + status 转移规则（reproducible 需 repro_artifact；verified 需 affected+fixed+repro+full oracle）+ 域上限 + 重复 id。
- 严格 TDD：`test_schema.py`（17）先红（ModuleNotFoundError）后绿；`test_seed_cards_dataset.py`（8）守已提交数据集；`test_power.py`（8）先红后绿。
- 全部 **33 realdefects 测试通过**；既有仓库套件 **9 failed/435 passed 基线不变**（我的工作隔离在新目录，未碰 tests/）。

**阶段 3 门：PASS**（新测试先红后绿；realdefects 全绿；validator 未降标准——含两处修正：candidate 允许空 fixed 版本、power 测试离散性期望修正；无框架膨胀）。

## 阶段 4 · SMS-vs-MS 假设 + 功效（2026-07-01）

交付：`code/realdefects/power.py` + `research/real_mrdefect_seed_cards.md` §2。

- 每假设绑定具体缺陷/family（H-dtype/H-opt/H-method/H-perm/H-sparse/H-relabel/H-align，见 §2.3 表）。
- suite-level 观测指标：`corr(rank(SMS), rank(真实检出))` vs `corr(rank(MS), rank(真实检出))` + MS-高-真实检出-低 的误导诊断。
- 功效（McNemar 精确符号检验，单侧 α=0.05）：9 张全 discordant、p_favor=0.9 乐观上界下 **power≈0.77 < 0.80**，`decision=design-calibration-only`、`confirmatory=False`；达 80% 需 ~8 discordant；Wilson 95% CI(9/9)=[0.70,1.00]。
- **明确**：种子只能 go/no-go + 设计校准，不作「SMS 优于 MS」最终结论。

**阶段 4 门：PASS**（每假设绑定缺陷；统计保守；样本不足写明缺口；未写「已证明 SMS 优于 MS」）。

## 阶段 5 · TOSEM 审稿人视角自审（2026-07-01）

用 TOSEM 标准 + ARS 对抗视角自审，识别 blocker（先例经 WebSearch 核实，非凭记忆）：

- **BLOCKER-1（术语撞名，真实）**：「Semantic Mutation Testing」是既有术语——Clark, Dan, Hierons, *Science of Computer Programming* 2013（SMT-C 工具），指**变异语言语义**（捕捉描述语言误解），**不是**「真实语义缺陷检出分数」。用 "Semantic Mutation Score (SMS)" 会与之直接冲突。**处理**：必须改名（如 real-fault detection score / behavioral-defect detection score），并在 Related Work 显式区分。→ 已记录，改名是投稿前硬动作。
- **BLOCKER-2（新颖性被先例压，真实）**：Just, Jalali, Inozemtseva, Ernst, Holmes, Fraser, *FSE 2014*「Are mutants a valid substitute for real faults」用 357 真实缺陷发现 mutant 检出与真实缺陷检出**显著相关**——即「MS 是真实缺陷检出的合理代理」已被证。SMS-vs-MS 若泛泛做 = 重跑 Just。**唯一可辩护 novelty delta**：范围收窄到**蜕变（MR）测试套件** + **domain-validity gating**——Just 用普通 test suite，未涉 MR oracle 的适用性/健全性。→ novelty 必须锁死在 MR-suite 维度，否则 desk-reject 风险。
- **BLOCKER-3（scope 分叉，战略级，需用户）**：语料是通用库函数级缺陷，与已拍板论文 SciML-代理被测对象**不同总体**。采纳 SMS-vs-MS = 新论文/重框定，非现稿。→ 头号 open question，本会话不替用户决。
- **BLOCKER-4（成熟度，真实）**：当前 = 9-卡目录 + validator + power 模块（设计+工具），实证研究**未执行**（无 suites×mutants×真实缺陷的实测排序）。仍像 dataset/tooling 小修补。→ 需真复现 ≥ 十数张 + 跑一次 SMS/MS 排序对比才够 TOSEM。
- **BLOCKER-5（可复现，真实）**：9 卡全 candidate，0 reproducible/0 verified。TOSEM 要可复现证据。→ 最小下一步：pin 受影响版本 + 写复现脚本，升 ≥3 张到 reproducible。

**Reviewer-2 一句话**：现产出是「一份诚实的、可行性验证级的种子 + 工具」，**不是** TOSEM 稿的实证核心；离 TOSEM 差 = 术语去撞名 + novelty 锁 MR 维度 + 真复现 + 执行 SMS/MS 排序实验 + 解决 scope 分叉。

**阶段 5 门：PASS**（所有 blocker 有处理结果或最小下一步；未夸大当前证据；BLOCKER-3 明确交用户）。

## 🔵 头号 OPEN QUESTION（交用户拍板）

是否把 Real-MRDefect-10 / SMS-vs-MS 提升为论文主线（重框定现稿），还是仅作已拍板 `paper/66` Phase 2「可辩护真实故障基准」的支撑证据？claude 建议：**后者**——保留 A+B+C 理论优先主线（`paper/67/68`），把本会话种子作为「真实缺陷可低成本采集」的可行性证据并入 Phase A/2，因为直接改向要付术语撞名(BLOCKER-1)+ Just 先例(BLOCKER-2)+ 与现稿被测对象换总体(BLOCKER-3)三重代价。

---

## 阶段 6 · 复现 OPEN 缺陷 → 升 reproducible（2026-07-01，接续会话）

目标（承接 Phase 5 BLOCKER-5，最小下一步）：把 candidate 升 reproducible。策略=挑 3 张 **OPEN** 缺陷（当前版本仍存在），**不降级**在本机复现，最便宜且诚实。

- **经验性探测（先跑再判，不复现不标）**：
  - numpy #30349 on numpy 2.5.0 → optimize=True 得 [18,18,18]、optimize=False 抛 ValueError → **复现**。
  - scipy #21876 on scipy 1.18.0 → valid/full 保 batch 维 B=7、same 塌成 1 → **复现**；且 fftconvolve 与 oaconvolve **彼此一致**（都 (1,100)）——**证伪**原卡「跨方法等价」框定。
  - pandas #59350 on pandas 2.2.3 → 乱序 index [1,0] 得 [200,100]，正确 [100,200] → **复现**。
- **诚实修复**：依实测**更正 RMD-SCIPY-0001** 的 mr_family（跨方法等价 → mode-consistency/broadcasting-invariance）+ 全部 oracle 字段 + §2.3 拆 H-mode/H-method。这是「评审发现错误即修，不带病前进」的直接执行。
- **TDD**：`test_repro_open_defects.py` 先红（`ModuleNotFoundError: repro`）→ 实现 `code/realdefects/repro/{__init__,rmd_numpy_0002,rmd_scipy_0001,rmd_pandas_0001}.py`（每模块 `reproduce()` 跑 MR oracle 返回 reproduced 布尔）→ 后绿（6 passed）。
- **升级**：RMD-NUMPY-0002 / RMD-SCIPY-0001 / RMD-PANDAS-0001 → **reproducible**，repro_artifact 指向可重跑脚本；validator 新守「reproducible 卡的 repro_artifact 文件须存在且 reproduce()=True + registry backing」。
- **状态**：dataset 现 **6 candidate + 3 reproducible / 0 verified**。
- **测试**：realdefects **39 passed**（33+6）；既有仓库套件 **9 failed/435 passed 基线不变**（未碰 tests/）。

**阶段 6 门：PASS**（≥1 OPEN 缺陷本地复现——实为 3 张，各有可重跑脚本；TDD 先红后绿；validator 未降标准反而加强；scipy 卡错误框定经实测更正；基线不变；无主题漂移——全部是真实 MR-缺陷复现，核心服务 Real-MRDefect-10 + SMS-vs-MS）。

**下一阶段候选（未启动，交接）**：① 6 张 candidate（含 4 CLOSED）在隔离 venv pin 旧版本复现 → reproducible；CLOSED 卡在修复版验证关系恢复 → verified。② 构造强弱 MR 套件 + 合成 mutant 集，实测 SMS/MS 排序相关性（真正回答核心问题，需 BLOCKER-3 scope 拍板后才值得大投）。③ BLOCKER-1 术语改名 / BLOCKER-2 novelty 锁 MR 维度（写作动作，投稿前）。

---

## 阶段 7 · 第 4 张复现 + 首张 verified 全链（2026-07-01，接续会话）

承接用户「继续推进、TDD、每阶段评审修错、不漂移」指令。

### 7.1 第 4 张 reproducible：networkx #8093（当前版本）
- 洞察：#8093 2026-06-29 才修，本机 networkx 3.4.2（2024）**早于**修复 → 当前版本可复现。
- **实测证伪原卡框定**：干净**双射**重标号在 3.4.2 **无 bug**（copy=True 正确保属性）；真实违例是**非单射合并映射** {1:4,2:4} 下 copy=True（node4={x:4}）vs copy=False（node4={x:2}）**不一致**。
- **诚实更正**（第 2 次实测自更正）：mr_family 改「graph relabeling: copy-flag invariance」+ 全 oracle 字段。TDD：EXPECTED_REPRO_IDS 加该 id 先红（4 failed）→ 写 `repro/rmd_networkx_0001.py` + 注册 → 后绿。

### 7.2 首张 verified：xarray #7766（affected→fixed 全链）
- xarray 纯 Python → 隔离 venv 装 `xarray==2023.4.0 + numpy==1.26.4 + pandas==2.1.4`（钉有 py3.12 wheel 的组合；2.0.3/无 wheel 组合源码构建失败，是真实环境约束）。
- **oracle**：`pandas.cut(coords,bins,labels).value_counts()`（groupby_bins 内部所用）作 ground truth，比对 `len(group[label])`。
  - **affected 2023.4.0**：correspondence_correct=**False**，标签错乱（four=506 应 1、nine=1 应 506，按名排序而非 bin 边界）→ **复现**。
  - **current 2024.11.0**：correspondence_correct=**True**，0 mismatch → **修复确认**。
- TDD：`test_verified_defects.py` 先红（`ModuleNotFoundError: verify_registry`）→ 写 `repro/rmd_xarray_0001.py`（`check_current()` 活体确认 + `AFFECTED_EVIDENCE` 留档真实运行）+ `verify_registry.py` → 升卡 verified → 后绿。
- **诚实标注**：受影响侧旧 wheel 不进 py3.12 CI，作 recorded provenance；当前侧 `check_current()` 可 CI 重跑活体确认修复。

### 7.3 评审与状态
- 测试：realdefects **44 passed**（含 verified 4 + repro 8 + schema 17 + dataset 8 + power 7）；既有仓库套件 **9 failed/435 passed 基线不变**；隔离 venv 已清理。
- dataset：**1 verified + 4 reproducible + 4 candidate / 9**。
- 文档同步：`research/real_mrdefect_seed_cards.md`（状态行/表/§2.3/§2.5）、`data/realdefects/seed_cards.json` `_meta`。

**阶段 7 门：PASS**（TDD 先红后绿×2；两处实测自我更正落地；validator/verify 守护加强未降标准；基线不变；全部真实 MR-缺陷证据，无漂移；env 约束如实记录未粉饰）。

### 7.4 剩余证据缺口（不粉饰）
- 4 张 candidate 仍需隔离 venv 逐一装旧版本复现（numpy #20305 需 numpy 1.21.x——早于 py3.12，恐无 wheel，是**真实环境 blocker**；pandas #33732 / sklearn #15438 / scipy #15927 同类风险）。
- 核心问题（SMS vs MS 排序判别力）**实证仍未执行**——需构造强弱 MR 套件 + 合成 mutant 集实测，且此大投入应在 BLOCKER-3 scope 分叉由用户拍板后再启动（避免为可能不采纳的主线过度建设）。
- 头号 open question（BLOCKER-3）依旧待用户拍板：Real-MRDefect-10/SMS-vs-MS 作论文主线（重框定）还是作已拍板 `paper/66` Phase 2 支撑证据。

---

## 阶段 8 · 最小 SMS-vs-MS 判别力 PoC（2026-07-01，用户选 ②）

目标：用已 reproducible 的真实缺陷做**存在性**证明（n=1，非统计），直接触碰核心问题，但克制不做完整合成 benchmark（避免漂移 + 避免为未拍板主线过度建设）。

- **设计**：锚定 reproducible 缺陷 RMD-PANDAS-0001（#59350）；忠实重建错位行为的参照 reducer（真实缺陷 + 参照 SUT，cf. Just 2014）使 mutation 分析可行。守恒 MR 杀大量算术 mutant（高 MS）但对错位盲（保总和）；index-order 不变性 MR 检出真实缺陷但杀 mutant 少（低 MS）。
- **TDD**：`test_sms_vs_ms_poc.py`（7）先红（ModuleNotFoundError）→ 实现 `sms_vs_ms_poc.py`。
- **评审即修（实测暴露实现缺陷）**：首跑 `real_defect_detected_only_by=None`——根因是原 `_mr_order_invariance_holds` 仅 `reversed(list)` 未重排 idx 值，而 reference 按 idx 值排序故缺陷不显现。**修**：MR 变换改为「重新赋升序 idx 于不同记录序」（正是 #59350 的 index-order 不变性语义）。修实现，非放松测试。
- **结果（harness 实算，非硬编码）**：守恒 MR **MS=0.90**（杀 9/10，仅漏等价 mutant abs）/ 检出真实缺陷=**否**；index-order MR **MS=0.20**（杀 2 order-dependent）/ 检出真实缺陷=**是**。→ **ms_contradicts_real_detection=True**。
- **kill matrix 诚实核验**：等价 mutant `abs_equivalent` 两 MR 皆不杀（正确，正是 MS 虚高经典来源）；守恒杀 9 个非序 mutant，index-inv 只杀 horner/keep_last。
- **诚实标注**：`is_statistical_claim=False`、`n_real_defects=1`、interpretation 明写「existence proof … motivates but does not statistically establish」。

- 测试：realdefects **51 passed**（+7）；既有仓库套件 **9 failed/435 passed 基线不变**；文档 §2.6 记录。

**阶段 8 门：PASS**（TDD 先红后绿；实测暴露的实现缺陷已修并重验；结果由 harness 实算；明确标注非统计/n=1；等价 mutant 处理正确；基线不变；紧扣核心问题无漂移）。

### 8.1 PoC 的意义与边界（实事求是）
- **正面**：这是本试点首次**直接触碰核心问题**并给出可执行、可复现的正面信号——真实存在「MS 排序 ⊥ 真实缺陷检出」的情形，为 SMS 的判别价值提供存在性支点。
- **边界**：n=1、单缺陷、单库、参照 reducer（非直接对 pandas 源码做 mutation）。**不是** confirmatory；要成 TOSEM 实证核心需：多真实缺陷（≥ 十数张 reproducible）、真实库源码 mutation（或经校验的参照集）、多 SUT、SMS/MS 排序相关性的统计检验（Phase 4 power 模块已备）。
- **仍是 BLOCKER-3 之下**：PoC 增强了「值得投入」的证据，但是否作论文主线仍待用户拍板。
