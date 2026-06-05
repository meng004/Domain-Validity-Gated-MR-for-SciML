# MeshGraphNets 圆柱绕流 MetBench MR 资产编制与验证说明

> 前置文档：`MeshGraphNets圆柱绕流仓库使用与运行时资产准备.md`  
> 实验依据：`蜕变测试实验方案.md`  
> 目标：把 MeshGraphNets 圆柱绕流运行时资产包装成 MetBench System MT 可执行的 MR 资产。  
> 版本：v1.0 / 2026-05-26

---

## 0. 前置条件

开始编制 MetBench MR 资产前，必须已经具备：

- 上游源码：`meshGraphNets_pytorch`
- runtime venv：可 import `torch`、`torch_geometric`、`torch_scatter`
- checkpoint：`best_model.pth`
- tiny fixture：`tiny.npz + tiny.dat`
- asset manifest：记录上游 commit、依赖版本、checkpoint hash、fixture hash
- 至少一次本地 rollout smoke 通过

如果缺少 checkpoint 或 fixture，不要开始 MetBench 接入；此时只能写 parser smoke，不能声称 MR 可运行。

---

## 1. MetBench 资产目录

在 MetBench 仓库中新增：

```text
SUT/meshgraphnets_cylinder_flow/
├── catalog.json
├── README.md
├── meshgraphnets_cylinder_runner.py
├── meshgraphnets_cylinder_input_parser.py
├── meshgraphnets_cylinder_output_parser.py
├── meshgraphnets_cylinder_common.py
└── sample/
    ├── identity_case.json
    ├── perturbation_case.json
    ├── divergence_case.json
    ├── mirror_y_case.json
    ├── scale_similarity_case.json
    ├── re_st_case.json
    ├── node_permutation_case.json
    ├── face_order_case.json
    ├── translation_case.json
    └── rollout_prefix_case.json
```

不要把完整数据和大型 checkpoint 直接放入 MetBench 仓库。MetBench sample case 只引用外部运行时资产路径或环境变量。

---

## 2. 环境变量契约

推荐 runner 读取以下环境变量：

```text
METBENCH_MGN_REPO=/absolute/path/to/meshgraphnets_runtime/source/meshGraphNets_pytorch
METBENCH_MGN_DATA_ROOT=/absolute/path/to/meshgraphnets_runtime/fixtures
METBENCH_MGN_CHECKPOINT=/absolute/path/to/meshgraphnets_runtime/checkpoints/best_model.pth
METBENCH_MGN_DEVICE=cpu
METBENCH_MGN_ENABLE_INTEGRATION=1
```

行为规则：

- 未设置 `METBENCH_MGN_ENABLE_INTEGRATION=1` 时，重依赖 integration test 应 clean skip。
- parser contract tests 不依赖这些环境变量。
- runner 如果缺 checkpoint 或 fixture，应返回明确错误，测试层根据 profile 决定 skip 或 fail。

---

## 3. 输入 case JSON 规范

每个 sample case 采用统一结构：

```json
{
  "dataset": {
    "root": "${METBENCH_MGN_DATA_ROOT}",
    "split": "tiny",
    "sample_index": 0,
    "rollout_steps": 1
  },
  "model": {
    "repo_root": "${METBENCH_MGN_REPO}",
    "checkpoint": "${METBENCH_MGN_CHECKPOINT}",
    "device": "cpu",
    "deterministic": true
  },
  "transform": {
    "kind": "identity",
    "seed": 0,
    "parameters": {}
  },
  "metrics": {
    "dt_seconds": 0.01,
    "cylinder_diameter": 0.0508,
    "u_ref": 1.0,
    "probe_offsets": [[3.0, 0.0], [4.0, 0.3], [5.0, -0.3]]
  }
}
```

runner 负责展开环境变量。input parser 不展开环境变量，只读写 JSON。

---

## 4. 全部 MR 资产清单

### 4.1 来自实验方案的 MR

| MR id | MR 名称 | `transform.kind` | 指标 | 阈值 | MetBench assertion |
|---|---|---|---|---|---|
| `mgn-identity-determinism` | MR1 基础恒等 | `identity` | `max_abs_diff` | `<= 1e-12` | `approx` |
| `mgn-velocity-perturbation-stability` | MR2 输入扰动稳定性 | `velocity_noise` | `relative_l2_error` | `<= 0.05` | `less` |
| `mgn-incompressible-divergence` | MR3 连续性 / 质量守恒 | `divergence_check` | `relative_divergence` | `<= 0.05` | `less` |
| `mgn-mirror-y-equivariance` | MR4 对称性保持 | `mirror_y` | `mirror_relative_l2_error` | `<= 0.05` | `less` |
| `mgn-scale-similarity` | MR5 尺度相似 | `scale_similarity` | `scale_relative_l2_error` | `<= 0.05` | `less` |
| `mgn-re-st-invariance` | Re-St 不变性 | `re_st_scale` | `strouhal_delta` | `<= 0.002` | `less` |

### 4.2 建议补充的 GNN 专属 MR

| MR id | MR 名称 | `transform.kind` | 指标 | 阈值 | MetBench assertion |
|---|---|---|---|---|---|
| `mgn-node-permutation-equivariance` | 节点置换等变 | `node_permutation` | `permutation_relative_l2_error` | `<= 1e-6` | `less` |
| `mgn-face-order-invariance` | face / cell 顺序不变 | `face_order_shuffle` | `face_order_relative_l2_error` | `<= 1e-6` | `less` |
| `mgn-rigid-translation-invariance` | 刚体平移不变 | `rigid_translation` | `translation_relative_l2_error` | `<= 1e-5` | `less` |
| `mgn-rollout-prefix-consistency` | rollout 前缀一致 | `rollout_prefix` | `prefix_relative_l2_error` | `<= 1e-6` | `less` |

### 4.3 推荐落地批次

第一批：

- `mgn-identity-determinism`
- `mgn-node-permutation-equivariance`
- `mgn-face-order-invariance`
- `mgn-mirror-y-equivariance`

第二批：

- `mgn-velocity-perturbation-stability`
- `mgn-incompressible-divergence`
- `mgn-rigid-translation-invariance`
- `mgn-rollout-prefix-consistency`

第三批：

- `mgn-scale-similarity`
- `mgn-re-st-invariance`

第三批需要更长 rollout 和更严格物理解释，不适合作为第一批 smoke。

---

## 5. input parser

文件：

```text
SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_input_parser.py
```

职责：

- `parse --input`：读取 case JSON，原样输出 dict。
- `write --dict-file --output`：把 MetBench transformation 后的 dict 写回 JSON。
- 不 import torch。
- 不访问 checkpoint。
- 不访问 fixture。

验证：

```bash
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_input_parser.py parse --input SUT/meshgraphnets_cylinder_flow/sample/identity_case.json
```

---

## 6. output parser

文件：

```text
SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_output_parser.py
```

职责：

- 读取 runner 输出 JSON。
- 抽取数值指标到 `values`。
- 把 checkpoint hash、sample index、device 等写入 `metadata`。
- 不 import torch。

必须识别的数值 key：

```text
max_abs_diff
relative_l2_error
relative_divergence
mirror_relative_l2_error
scale_relative_l2_error
strouhal_delta
main_peak_ratio
permutation_relative_l2_error
face_order_relative_l2_error
translation_relative_l2_error
prefix_relative_l2_error
```

验证：

```bash
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_output_parser.py parse --output-file /tmp/mgn-result.json
```

---

## 7. runner

文件：

```text
SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_runner.py
```

职责：

- 支持 `--input` / `--output`。
- 展开环境变量。
- 动态加入上游源码路径。
- 加载 checkpoint。
- 加载 tiny fixture。
- 根据 `transform.kind` 调用对应 MR 计算。
- 输出稳定 JSON。

runner 必须设置确定性：

```python
import random
import numpy as np
import torch

random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.use_deterministic_algorithms(True, warn_only=True)
model.eval()
```

runner 主流程：

```text
read case
resolve env vars
import upstream modules
load graph sample
load simulator checkpoint
dispatch transform.kind
compute metric
write output JSON
```

---

## 8. common 变换与指标函数

文件：

```text
SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_common.py
```

必须提供：

```text
load_model()
load_graph_sample()
infer_one_step()
rollout()
mirror_y()
add_velocity_noise()
scale_similarity()
node_permutation()
face_order_shuffle()
rigid_translation()
relative_l2()
max_abs_diff()
cell_divergence()
estimate_strouhal()
```

关键实现约束：

- 所有 graph 变换必须 deep copy。
- permutation 必须同步处理 `x`、`pos`、`y` 和 `face`。
- mirror 输出比较时必须对原输出做同样 mirror。
- scale similarity 需要同时缩放 `pos` 与 velocity。
- Re-St 必须记录探针、主峰能量占比和 `St`。

---

## 9. 全部 MR 的计算说明

### 9.1 MR1 基础恒等

```text
y1 = infer_one_step(model, graph)
y2 = infer_one_step(model, graph)
max_abs_diff = max(abs(y1 - y2))
```

MetBench：

```text
value_name = max_abs_diff
assertion = approx equal to 0
tolerance_abs = 1e-12
```

如果 MR1 不通过，后续所有 MR 都不可解释。

### 9.2 MR2 输入扰动稳定性

```text
y0 = infer_one_step(model, graph)
y1 = infer_one_step(model, add_velocity_noise(graph, std=1e-4, seed=fixed))
relative_l2_error = norm(y1 - y0) / (norm(y0) + eps)
```

MetBench：

```text
value_name = relative_l2_error
assertion = less
threshold = 0.05
```

### 9.3 MR3 连续性 / 质量守恒

```text
y = infer_one_step(model, graph)
relative_divergence = sum(abs(cell_flux)) / velocity_area_norm
```

MetBench：

```text
value_name = relative_divergence
assertion = less
threshold = 0.05
```

这是 property-like MR，可作为 source/followup 同 case 的指标约束。

### 9.4 MR4 y 轴镜像等变

```text
y0 = infer_one_step(model, graph)
y0_mirror = mirror_velocity_y(y0)
y1 = infer_one_step(model, mirror_y(graph))
mirror_relative_l2_error = norm(y1 - y0_mirror) / norm(y0)
```

MetBench：

```text
value_name = mirror_relative_l2_error
assertion = less
threshold = 0.05
```

### 9.5 MR5 尺度相似

```text
y0 = infer_one_step(model, graph)
y1 = infer_one_step(model, scale_similarity(graph, k))
expected = k * y0
scale_relative_l2_error = norm(y1 - expected) / norm(expected)
```

MetBench：

```text
value_name = scale_relative_l2_error
assertion = less
threshold = 0.05
```

### 9.6 Re-St 不变性

```text
rollout base and scaled cases
extract v_y time series at wake probes
FFT
St = f_s * L / U
strouhal_delta = abs(St_scaled - St_base)
main_peak_ratio = peak_power / total_power
```

MetBench：

```text
value_name = strouhal_delta
assertion = less
threshold = 0.002
```

验收：

- `main_peak_ratio > 0.85`
- `strouhal_delta <= 0.002`

该 MR 默认不进入快速 CI。

### 9.7 节点置换等变

```text
y0 = infer_one_step(model, graph)
g_perm, inv_perm = permute_nodes(graph)
y_perm = infer_one_step(model, g_perm)
y1 = inverse_permute(y_perm, inv_perm)
permutation_relative_l2_error = norm(y1 - y0) / norm(y0)
```

MetBench：

```text
value_name = permutation_relative_l2_error
assertion = less
threshold = 1e-6
```

### 9.8 face 顺序不变

```text
y0 = infer_one_step(model, graph)
g2 = shuffle_face_order(graph)
y1 = infer_one_step(model, g2)
face_order_relative_l2_error = norm(y1 - y0) / norm(y0)
```

MetBench：

```text
value_name = face_order_relative_l2_error
assertion = less
threshold = 1e-6
```

### 9.9 刚体平移不变

```text
y0 = infer_one_step(model, graph)
g2 = translate_pos(graph, offset)
y1 = infer_one_step(model, g2)
translation_relative_l2_error = norm(y1 - y0) / norm(y0)
```

MetBench：

```text
value_name = translation_relative_l2_error
assertion = less
threshold = 1e-5
```

### 9.10 rollout 前缀一致

```text
ys_short = rollout(model, graph, short_steps)
ys_long = rollout(model, graph, long_steps)
prefix_relative_l2_error = norm(ys_short - ys_long[:short_steps+1]) / norm(ys_short)
```

MetBench：

```text
value_name = prefix_relative_l2_error
assertion = less
threshold = 1e-6
```

---

## 10. catalog.json 编制规则

每条 MR 必填：

```text
mr_id
sut_name
display_name
description
mr_family
transformation_name
assertion_type_code
assertion_name
value_name
default_parameters
transform_steps
tolerance_rel
tolerance_abs
equation_key
equation
program_type
meta_pattern
sample_case_relative_path
work_root_name
timeout_seconds
```

注意：

- `assertion_type_code = less` 适合误差上界类 MR。
- `assertion_type_code = approx` 适合恒等类 MR。
- 当前 MetBench transformation 若无 `SetField`，可先用 `ScaleField` 修改 `/transform/seed` 或 `/transform/parameters/k`，但必须在文档中说明这是过渡方案。
- 长期应新增语义更清晰的 `SetField` 或 `SetTransformKind`。

---

## 11. sample case 编制步骤

每个 MR 一份 sample：

```text
sample/identity_case.json
sample/node_permutation_case.json
...
```

步骤：

1. 复制统一 case 模板。
2. 设置 `dataset.sample_index`。
3. 设置 `dataset.rollout_steps`。
4. 设置 `transform.kind`。
5. 设置 `transform.parameters`。
6. 设置 `metrics`。
7. 用 input parser 验证 JSON 可读。
8. 用 runner 验证可输出 result JSON。
9. 用 output parser 验证可输出 MetBench `{values, metadata}`。

---

## 12. 本地手工验证

parser：

```bash
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_input_parser.py parse --input SUT/meshgraphnets_cylinder_flow/sample/identity_case.json
```

runner：

```bash
export METBENCH_MGN_REPO=/absolute/path/to/meshgraphnets_runtime/source/meshGraphNets_pytorch
export METBENCH_MGN_DATA_ROOT=/absolute/path/to/meshgraphnets_runtime/fixtures
export METBENCH_MGN_CHECKPOINT=/absolute/path/to/meshgraphnets_runtime/checkpoints/best_model.pth
export METBENCH_MGN_DEVICE=cpu
export METBENCH_MGN_ENABLE_INTEGRATION=1

python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_runner.py \
  --input SUT/meshgraphnets_cylinder_flow/sample/identity_case.json \
  --output /tmp/mgn-identity-result.json
```

output parser：

```bash
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_output_parser.py parse --output-file /tmp/mgn-identity-result.json
```

期望输出包含：

```json
{
  "values": {
    "max_abs_diff": 0.0
  },
  "metadata": {
    "program": "meshgraphnets_cylinder_flow"
  }
}
```

---

## 13. MetBench 测试

建议新增：

```text
MetBench_SystemMT.Tests/Launcher/LauncherEndToEndMeshGraphNetsCylinderTests.cs
```

测试分层：

| 测试 | 依赖 torch/checkpoint | 默认 CI |
|---|---:|---:|
| catalog descriptor test | 否 | 是 |
| parser contract test | 否 | 是 |
| runner smoke test | 是 | 可 skip |
| launcher end-to-end MR test | 是 | 可 skip |

skip reason：

```text
MeshGraphNets runtime fixture not configured.
Set METBENCH_MGN_ENABLE_INTEGRATION=1, METBENCH_MGN_REPO, METBENCH_MGN_DATA_ROOT, and METBENCH_MGN_CHECKPOINT.
```

focused test：

```bash
dotnet test MetBench_SystemMT.Tests --no-restore --filter "FullyQualifiedName~MeshGraphNetsCylinder|FullyQualifiedName~SystemMtLauncherTests"
```

full test：

```bash
dotnet test MetBench_SystemMT.Tests --no-restore
```

---

## 14. MetBench 代码登记

首批实现 PR 需要修改：

```text
SUT/meshgraphnets_cylinder_flow/*
MetBench_BLL.Core/SystemMT/Metadata/SystemMtMetadataCatalog.cs
MetBench_BLL.Core/SystemMT/Launcher/LegacyCatalogFactory.cs
MetBench_SystemMT.Tests/Launcher/SystemMtLauncherTests.cs
MetBench_SystemMT.Tests/Launcher/LauncherEndToEndMeshGraphNetsCylinderTests.cs
docs/status/current.md
docs/requirements.md
docs/PROJECT-STRUCTURE.md
```

如果暂不新增 `PythonExecutableKinds.MeshGraphNets`，catalog 中先用：

```json
"python_executable_kind": "system"
```

测试中让 `LauncherOptions.SystemPython` 指向 `.venv-mgn/bin/python`。

---

## 15. PR 分解建议

### PR-MGN-1：资产骨架

范围：

- `SUT/meshgraphnets_cylinder_flow/`
- input parser
- output parser
- sample cases
- catalog descriptor
- parser contract tests

验收：

- 不需要 torch。
- 不需要 checkpoint。
- catalog 可读。

### PR-MGN-2：runner + 第一批 MR

范围：

- runner
- common
- MR1 identity
- node permutation
- face order
- mirror-y
- optional integration tests

验收：

- 缺运行时资产时 clean skip。
- 有运行时资产时 4 条 MR 可跑。

### PR-MGN-3：物理与长 rollout MR

范围：

- perturbation
- divergence
- scale similarity
- rollout prefix
- Re-St
- 报告输出

验收：

- Re-St 只在 integration profile 下跑。
- 输出 `main_peak_ratio`、`strouhal_delta`、探针位置和 FFT 诊断。

---

## 16. 完成定义

MR 资产接入完成需要满足：

- 全部 MR 都有明确 `mr_id`、sample case、指标和阈值。
- 第一批 smoke MR 能在 tiny fixture 上运行。
- parser tests 默认 CI 可跑。
- 重依赖 integration tests 可配置、可跳过、可复现。
- `requirements.md`、`PROJECT-STRUCTURE.md`、`status/current.md` 同步更新。
- 不修改 Method MT。
- 不修改 Typed Semantic Catalog runtime，除非另开验证语义 PR。
- 不触及 WPF；若后续触及 WPF，必须走 Windows SSH/RDP 验证。
