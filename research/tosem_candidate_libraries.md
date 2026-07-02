# TOSEM Real-MRDefect-10 · 候选库复核与挖掘顺序

> 2026-07-01 · 配套 `docs/superpowers/plans/2026-07-01-tosem-real-mrdefect-seed-pilot.md`
> ⚠️ 本文件的「MR family 预期」是**结构性不变量假设**（指导缺陷挖掘方向），**不是**已验证缺陷声明。
> 真实缺陷卡（带 URL / 版本 / 复现）在 Phase 2 产出，落 `data/realdefects/`。
> 边界：不扩大候选库（除非发现明显证据错误）；DL/tensor 项目设占比上限；`needs_pdf`/未复现不得当 verified。

## 分层与挖掘顺序

优先顺序（简报锁定）：NumPy → SciPy → pandas → scikit-learn → NetworkX → xarray → TensorFlow → PyTorch → TVM → OpenCV。

| 层 | 库 | 定位 | MR 结构丰度 | 复现基础设施成本 |
|---|---|---|---|---|
| **seed-core** | NumPy | 纯数值/线代/广播/dtype/排序，MR 最密、复现最轻（纯 CPU、pip、无训练）| 极高 | 极低 |
| **seed-core** | SciPy | 数值积分/特殊函数/稀疏/信号/空间度量，恒等式丰富 | 高 | 低 |
| **seed-core** | pandas | dataframe algebra（groupby/join/concat/sort）| 高 | 低 |
| **seed-core** | scikit-learn | 排列/缩放不变、稀疏-稠密等价、fit-predict 确定性 | 中高 | 低-中 |
| **seed-core** | NetworkX | 图同构/重标号不变（度/连通/最短路/中心性）| 中高 | 极低 |
| **candidate** | xarray | 坐标对齐、维重排/转置不变、labeled reduction | 中 | 低-中 |
| **reserve（capped）** | TensorFlow | graph/eager & XLA 等价、广播、dtype | 中 | 高（GPU/大依赖）|
| **reserve（capped）** | PyTorch | contiguous/非 contiguous、batch 不变、确定性、广播、dtype | 中 | 高 |
| **reserve（capped）** | TVM | 编译/JIT 等价（优化 vs 未优化、跨 target 同结果）| 中 | 高（构建链）|
| **reserve（capped）** | OpenCV | 图像变换不变/等变（旋转/翻转/resize/色彩空间往返）| 中 | 中 |

**DL/tensor 上限**：reserve 四库（TF/PyTorch/TVM/OpenCV）合计缺陷卡 ≤ 总数的 40%（10 张中 ≤ 4 张），且**优先在 seed-core 满额后**才挖，避免被"知名"误导为证据。

## 逐库 MR family 预期（挖掘靶向）

### seed-core

**NumPy**
- 数值等价：reduction 结合律/交换律（`sum`/`add.reduce` 沿轴、pairwise summation）、`matmul` 结合律、`einsum` 与显式积等价。
- 广播/shape：广播规则一致性、`broadcast_to`/`reshape`/`squeeze` 往返、`stack`/`concatenate` 沿轴一致。
- dtype：dtype promotion（`result_type`）、casting（`astype` 往返、整型/浮点提升）、`float32` vs `float64` 判决容差。
- 排序/重排：`sort`/`argsort` 稳定性、`sort` 后置换与原数组一致、`unique` 幂等。
- **oracle 干净度**：★★★（source/transform/relation/violating 都可脚本化，纯 CPU 秒级）。

**SciPy**
- 数值等价：特殊函数恒等式（`gamma(n+1)=n·gamma(n)`、`erf` 奇函数、`logsumexp` 平移律）、数值积分 `quad` 线性、插值 `interp1d` 通过节点。
- 稀疏-稠密等价：`sparse` 矩阵运算 == 稠密等价（`@`、`sum`、`transpose`）。
- 度量对称：`spatial.distance` 对称性 d(x,y)=d(y,x)、三角不等式、`cdist`/`pdist` 一致。
- 信号：`convolve` 交换律、FFT 线性/Parseval。
- **oracle 干净度**：★★★。

**pandas**
- dataframe algebra：`groupby().agg` 对行序不变、inner `merge` 交换律（列序差异可归一）、`concat` 结合律、`sort_values` 后聚合不变。
- 重排不变：行 shuffle 后 `groupby`/`sum`/`mean` 不变（浮点容差内）。
- **oracle 干净度**：★★（浮点聚合需容差；join 列序/索引需归一化）。

**scikit-learn**
- 排列不变：样本行置换后 `fit`→同模型（tree/kNN/线性闭式解）；特征列置换 + 逆置换后预测不变。
- 缩放不变：`StandardScaler` 幂等（fit_transform 两次）；对 scale-invariant 估计器输入缩放不变。
- 稀疏-稠密等价：接受 sparse 的估计器 sparse 与 dense 输入同结果。
- **oracle 干净度**：★★（随机种子/并行归约顺序需控制）。

**NetworkX**
- 图同构/重标号：节点重标号后度序列/连通分量数/最短路长度分布/（未加权）中心性排名不变。
- 边序不变：加边顺序不改变图不变量。
- **oracle 干净度**：★★★（重标号是最干净的 MR：source=G，T=relabel，R=不变量相等）。

### candidate

**xarray**
- 坐标对齐：按坐标广播 == 手工对齐后 numpy 运算；`transpose` 后 reduction 不变；维重排 `.transpose(...)` 往返恒等。
- **oracle 干净度**：★★（依赖 pandas/numpy 后端，复现中等）。

### reserve（capped，DL/tensor）

**TensorFlow** — graph vs eager 等价、`tf.function`(XLA on/off) 数值等价、广播/dtype 一致。**复现成本高**。
**PyTorch** — contiguous vs 非 contiguous 同结果、batch 维不变（逐样本 == 批量）、`deterministic` 模式、广播/dtype。**复现成本高**。
**TVM** — 编译/JIT 等价：优化 pass on/off 同输出、跨 target（llvm/cuda）同结果、量化前后误差地板。**MR = compiler/JIT equivalence**，与本项目 operator-floor 主题最贴，但构建链重。
**OpenCV** — 图像变换等变：`filter2D`/`GaussianBlur` 对旋转/翻转等变、`resize` 与 crop 交换性、色彩空间 `cvtColor` 往返（RGB→YUV→RGB）误差地板。**MR = image-transform invariance/equivariance**。

## 与已拍板计划的相关性（实事求是）

- 本候选库总体（通用科学库）与已拍板论文的被测对象（SciML 代理）**不同**（见执行日志 §0.4）。
- 但 **TVM 的 compiler/JIT-equivalence** 与 **数值容差需压过误差地板** 两点，与现稿 C1「operator-floor soundness 判据」主题**同构**——若采纳，TVM/OpenCV 的「判决容差 vs 数值/量化地板」是最能反哺现稿理论的桥。
- SMS-vs-MS 判别力所需的「真实 MR-可检缺陷」对已拍板 `paper/66` Phase 2「可辩护故障基准」也是有效输入。

## 阶段 1 门自审

- [x] 优先列表每项都有 MR family 预期（上表逐库）。
- [x] 候选库无无证据扩张（严格用简报锁定的 10 库，未新增；DL/tensor 设 ≤40% 上限）。
- [x] 分类与 TOSEM / Real-MRDefect-10 目标一致（seed-core 全为可构造干净 MR oracle 的纯计算库）。
- [x] `needs_pdf` 未当 verified（本文件无任何 verified 声明，全为挖掘假设）。

**阶段 1 门：PASS。**
