# 计划 · TOSEM Real-MRDefect-10 种子试点 · SMS-vs-MS 判别力

> 2026-07-01 · 本文件在本仓不存在（简报点名为 ground truth），据简报意图 + 实事求是核查创建。
> live 进度见 `2026-07-01-tosem-real-mrdefect-seed-pilot-execution-log.md`。
> ⚠️ 与已拍板 A+B+C 计划的战略分叉见执行日志 §0.4（头号 open question）。

## 目标

在**真实、MR-可检行为缺陷**上，检验语义变异分数 **SMS**（用真实语义缺陷做 mutant）是否比传统语法变异分数 **MS**（用合成语法 mutant）**更能判别 MR 测试套件质量**，并产出 TOSEM 投稿所需的**初步（go/no-go + 设计校准）**证据。

## 核心定义（本试点内锁定）

- **MR-可检缺陷**：存在明确 MR oracle 的行为缺陷——source input x、transformed input T(x)、expected relation R(f(x), f(T(x)))、violating observation（缺陷版下关系被破坏）。
- **MS（传统变异分数）**：MR 测试套件杀死**合成语法 mutant**（AST 级算子变异）的比例。
- **SMS（语义变异分数）**：MR 测试套件检出**真实语义缺陷**（Real-MRDefect 卡）的比例。
- **判别力假设**：MS 会被语法/低层 mutant 噪声误导（等价 mutant、trivial mutant 高分），SMS 更贴合真实 MR-defect 检出能力，故 SMS 对 MR 套件质量的**排序**更接近真实缺陷检出排序。

## 缺陷卡 schema（每张必含）

project · issue/PR/commit URL · affected version · fixed version 或 fixing commit · behavioral symptom · MR family · source input x · transformed input T(x) · expected relation R(f(x),f(T(x))) · violating observation · why-not-crash-only/api-only · reproduction cost · SMS-vs-MS discriminator hypothesis · status（candidate / reproducible / verified）。

## status 三级（不得放松）

- **candidate**：URL + 行为线索存在，尚未复现。
- **reproducible**：已能本地/脚本复现 MR violation。
- **verified**：证据链完整——版本/修复点/复现脚本/预期 MR oracle 全齐。

## 阶段门（简报）

- **P1 候选库复核**：优先列表每项有 MR family 预期；无无证据扩张；分类与 TOSEM/Real-MRDefect-10 一致。
- **P2 真实缺陷挖掘**：每卡有 URL；≥1 条清楚说明为何 MR 可检；不能复现只标 candidate；无普通 bug/crash-only/API misuse 混入。
- **P3 TDD 工具**：新增测试先红后绿；既有 realdefects 测试全绿；validator 不降标准；无与 Real-MRDefect-10 无关的框架膨胀。
- **P4 SMS-vs-MS 假设 + 功效**：每假设绑定具体缺陷/MR family；统计保守；样本不足写明缺口；不写「已证明 SMS 优于 MS」。
- **P5 TOSEM 审稿人自审**：blocker 有处理结果；无法处理者有最小下一步；不夸大。

## 挖掘优先顺序（简报锁定）

NumPy → SciPy → pandas → scikit-learn → NetworkX → xarray → TensorFlow → PyTorch → TVM → OpenCV。
DL/tensor 项目（TF/PyTorch/TVM/OpenCV）设上限，不超计划占比；needs_pdf/未复现不得当 verified。

## 边界

prose ≤ evidence；姊妹库 `../最小完备MR子集/` 只读；不碰 manuscript/ledger/既有 `tests/`；SMS-vs-MS 不入论文正文直到用户拍板主线。
