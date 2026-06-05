# MeshGraphNets 圆柱绕流接入 MetBench 说明

> 依据文件：`蜕变测试实验方案.md`  
> 目标程序：`echowve/meshGraphNets_pytorch`，DeepMind `cylinder_flow` 数据集上的 MeshGraphNets PyTorch 实现  
> 目标平台：MetBench System MT / T3 SUT 扩展  
> 版本：v1.0 / 2026-05-26

---

## 0. 结论摘要

`meshGraphNets_pytorch` 不能无修改直接作为 MetBench SUT 运行。原因是它当前提供的是“数据下载 → TFRecord 解析 → 训练 → rollout → 可视化”的研究脚本流程，而 MetBench System MT 需要稳定的 CLI 契约：

- `input_parser parse --input <case.json>` 输出标准 JSON dict
- `input_parser write --dict-file <dict.json> --output <followup.json>` 写入衍生输入
- `runner --input <case.json> --output <result.json>` 运行源用例或衍生用例
- `output_parser parse --output-file <result.json>` 输出 `{ "values": {...}, "metadata": {...} }`
- `SUT/<sut>/catalog.json` 描述 MR、变换字段、断言指标、样例、超时和 Python 解释器类型

因此接入方式应是：**不改 MetBench 核心，不改原始 MeshGraphNets 模型代码；在 MetBench 的 `SUT/meshgraphnets_cylinder_flow/` 下新增 wrapper、适配器、样例、catalog 和文档化环境配置**。如果要在 CI 中稳定运行，应优先使用一个小型 fixture 与预训练 checkpoint；完整 DeepMind 数据下载、TFRecord 解析和模型训练不应放入常规 CI。

---

## 1. 接入边界

### 1.1 MetBench 中的归属

该案例属于 **System MT / T3 / ML-data-driven SUT pilot**：

- 不是 Method MT。
- 不是 Typed Semantic Catalog 运行时改造任务。
- 不是 WPF/UI 任务。
- 是一个新的外部依赖型 SUT，重点验证数据驱动物理场模型的蜕变关系。

推荐 SUT 名称：

```text
meshgraphnets-cylinder-flow
```

推荐目录：

```text
SUT/meshgraphnets_cylinder_flow/
```

推荐方程 key：

```text
cylinder-flow-navier-stokes
```

推荐 program type：

```text
ML
```

### 1.2 不应改动的部分

本接入不应修改：

- `MetBench_BLL.MethodMT/*`
- Typed Semantic Catalog runtime kernel
- ExecutionEvidence schema
- WPF / `MetBench_Client`
- 原始 `meshGraphNets_pytorch` 模型源码

除非后续决定新增专用 Python executable kind，否则不应改 MetBench 核心。若要长期支持该案例，建议新增 `meshgraphnets` venv kind；但第一阶段可以通过显式测试配置或环境变量传入 Python 解释器路径。

---

## 2. 目标目录结构

建议在 MetBench 仓库中新增：

```text
SUT/meshgraphnets_cylinder_flow/
├── catalog.json
├── README.md
├── meshgraphnets_cylinder_runner.py
├── meshgraphnets_cylinder_input_parser.py
├── meshgraphnets_cylinder_output_parser.py
├── meshgraphnets_cylinder_common.py
├── sample/
│   ├── identity_case.json
│   ├── perturbation_case.json
│   ├── divergence_case.json
│   ├── mirror_y_case.json
│   ├── scale_similarity_case.json
│   ├── re_st_case.json
│   └── node_permutation_case.json
└── fixtures/
    ├── README.md
    ├── tiny_cylinder_sample.npz
    ├── tiny_cylinder_sample.dat
    └── checkpoint.example.txt
```

建议不要把完整 DeepMind `train/valid/test.tfrecord` 或大型 checkpoint 直接签入 MetBench。大型文件应通过本地路径、对象存储、Git LFS 或教学环境预置目录提供。

---

## 3. venv 环境配置

### 3.1 推荐环境分层

建议分为两个环境：

| 环境 | 用途 | 是否进入常规 CI |
|---|---|---|
| `mgn-runtime` | MetBench 调用 runner，加载 checkpoint，执行小型 fixture rollout 和 MR | 可选，默认 skip |
| `mgn-convert` | 一次性解析 TFRecord，可能需要旧 TensorFlow | 不进入 CI |

原因：上游说明中 `parse_tfrecord.py` 依赖旧 TensorFlow，而模型运行依赖 PyTorch / PyG / torch_scatter。把二者塞进一个环境会增加不可复现风险。

### 3.2 Runtime venv

在 MetBench 外部创建 venv，避免污染系统 Python：

```bash
python3.10 -m venv .venv-mgn
source .venv-mgn/bin/activate
python -m pip install --upgrade pip wheel setuptools
```

安装上游依赖：

```bash
python -m pip install matplotlib numpy opencv_python packaging Pillow torch torch_geometric torch_scatter tqdm tensorboard scipy
```

注意：

- `torch_geometric` / `torch_scatter` 与 `torch` 版本强相关。正式落地前必须生成一份锁定文件，例如 `requirements-mgn-lock.txt`。
- CPU-only 环境优先。GPU 只作为本地加速，不作为 MetBench 语义验收前提。
- 如果安装 `torch_scatter` 失败，应按 PyG 官方 wheel 方式选择与 `torch`、Python、CUDA/CPU 匹配的 wheel；不要在 CI 中临时编译。

### 3.3 TFRecord 转换环境

完整数据转换建议在独立环境中做一次：

```bash
python3.8 -m venv .venv-mgn-convert
source .venv-mgn-convert/bin/activate
python -m pip install "tensorflow<1.15" numpy
python parse_tfrecord.py
```

如果本机或云环境无法安装旧 TensorFlow，推荐直接使用预转换后的 `.npz + .dat` fixture。MetBench 常规测试不应依赖 TFRecord 在线下载和旧 TensorFlow。

### 3.4 MetBench 调用方式

第一阶段建议通过测试或本地配置把 `SystemPython` 指向 `.venv-mgn/bin/python`：

```text
LauncherOptions.SystemPython = "/absolute/path/to/.venv-mgn/bin/python"
```

如果后续要长期产品化，建议在 MetBench 中新增：

```text
LauncherOptions.MeshGraphNetsPython
PythonExecutableKinds.MeshGraphNets = "meshgraphnets"
```

这样可以避免污染 `system` Python，也避免与 OpenMOC / OpenMC venv 混用。

---

## 4. 数据与 checkpoint 策略

### 4.1 三层数据策略

| 层级 | 内容 | 用途 |
|---|---|---|
| tiny fixture | 1 条短轨迹、少量节点、短 rollout | MetBench 单元和 smoke 测试 |
| local full fixture | DeepMind `cylinder_flow` 解析后数据 + checkpoint | 本地实验和教学演示 |
| training dataset | 原始 TFRecord + 训练过程 | 不进入 MetBench 常规验证 |

### 4.2 输入 case JSON

MetBench 输入不是直接传 PyG `Data`，而是传一个可审计的 JSON case。建议格式：

```json
{
  "dataset": {
    "root": "fixtures",
    "split": "tiny",
    "sample_index": 0,
    "rollout_steps": 1
  },
  "model": {
    "checkpoint": "fixtures/checkpoint.example.txt",
    "device": "cpu",
    "deterministic": true
  },
  "transform": {
    "kind": "identity",
    "parameters": {}
  },
  "metrics": {
    "probe_offsets": [[3.0, 0.0], [4.0, 0.3], [5.0, -0.3]],
    "dt_seconds": 0.01,
    "cylinder_diameter": 0.0508,
    "u_ref": 1.0
  }
}
```

`source` 与 `followup` 的差异由 MetBench 的 C# transformation 修改 JSON 字段完成，而 runner 根据 `transform.kind` 执行相应输入变换。

---

## 5. MR 集合

### 5.1 方案中的 MR

| MR id | 名称 | 输入变换 | 输出指标 | 断言 | 优先级 | MetBench 适配建议 |
|---|---|---|---|---|---|---|
| `mgn-identity-determinism` | MR1 基础恒等 | `identity` | `max_abs_diff` | `<= 0` 或 `<= 1e-12` | P1 | runner 内部执行同一输入两次推理 |
| `mgn-velocity-perturbation-stability` | MR2 输入扰动稳定性 | NORMAL 节点速度加小噪声 | `relative_l2_error` | `<= 0.05` | P2 | seed 必须固定，噪声只作用于 NORMAL 节点 |
| `mgn-incompressible-divergence` | MR3 连续性 / 质量守恒 | 无变换 | `relative_divergence` | `<= 0.05` | P0 | 这是 property-like MR，可用 source/followup 都跑同一 case，followup 只作为机制占位 |
| `mgn-mirror-y-equivariance` | MR4 y 轴镜像等变 | `y -> -y`, `v_y -> -v_y` | `mirror_relative_l2_error` | `<= 0.05` | P2 | 输出需逆变换后比较 |
| `mgn-scale-similarity` | MR5 尺度相似 | `pos -> k*pos`, `velocity -> k*velocity` | `scale_relative_l2_error` | `<= 0.05` | P2 | `k = 0.5, 2.0` 分别做参数化用例 |
| `mgn-re-st-invariance` | Re-St 不变性 | 保持 Re 的几何/速度/黏度同步缩放 | `strouhal_delta` | `<= 0.002` | P0 | 需要较长 rollout，不适合常规 CI，默认 integration test |

### 5.2 建议补充的 GNN 专属 MR

| MR id | 名称 | 输入变换 | 输出指标 | 断言 | 价值 |
|---|---|---|---|---|---|
| `mgn-node-permutation-equivariance` | 节点置换等变 | 对节点顺序做 permutation，同步重映射 `pos/x/y/face` | `permutation_relative_l2_error` | `<= 1e-6` 或经验阈值 | GNN 必备结构性质；能发现实现中依赖节点顺序的 bug |
| `mgn-face-order-invariance` | 三角单元顺序不变 | 打乱 `face/cells` 顺序 | `face_order_relative_l2_error` | `<= 1e-6` 或经验阈值 | 验证图构造不依赖 cell 枚举顺序 |
| `mgn-rigid-translation-invariance` | 刚体平移不变 | `pos -> pos + c`，速度不变 | `translation_relative_l2_error` | `<= 1e-5` 或经验阈值 | 若模型只使用相对边特征，应对全局平移不敏感 |
| `mgn-time-prefix-consistency` | rollout 前缀一致 | 同一初始状态 rollout N 与 M 步，N < M | `prefix_relative_l2_error` | `<= 1e-6` | 验证自回归 rollout 的确定性和缓存/状态管理 |

### 5.3 首批推荐落地 MR

第一阶段不要一次性接入全部 MR。推荐顺序：

1. `mgn-identity-determinism`
2. `mgn-node-permutation-equivariance`
3. `mgn-mirror-y-equivariance`
4. `mgn-velocity-perturbation-stability`
5. `mgn-incompressible-divergence`

`mgn-re-st-invariance` 放入第二阶段，因为它需要长 rollout、探针选择、FFT 主峰稳定性和更重的 fixture。

---

## 6. catalog.json 草案

第一阶段可以先放 3 条 smoke-friendly MR：

```json
{
  "sut_name": "meshgraphnets-cylinder-flow",
  "program": {
    "program_name": "meshgraphnets-cylinder-flow",
    "equation": "Cylinder Flow Navier-Stokes surrogate",
    "equation_key": "cylinder-flow-navier-stokes",
    "program_type": "ML",
    "runner_script_relative_path": "meshgraphnets_cylinder_runner.py",
    "input_parser_script_relative_path": "meshgraphnets_cylinder_input_parser.py",
    "output_parser_script_relative_path": "meshgraphnets_cylinder_output_parser.py",
    "input_adapter_script_relative_path": "meshgraphnets_cylinder_input_parser.py",
    "output_adapter_script_relative_path": "meshgraphnets_cylinder_output_parser.py",
    "python_executable_kind": "system"
  },
  "mrs": [
    {
      "mr_id": "mgn-identity-determinism",
      "sut_name": "meshgraphnets-cylinder-flow",
      "display_name": "MeshGraphNets cylinder flow - deterministic identity",
      "description": "Same graph and checkpoint must produce the same one-step prediction under eval mode and deterministic CPU execution.",
      "mr_family": "GNN.Determinism.Identity",
      "transformation_name": "ScaleField",
      "assertion_type_code": "approx",
      "assertion_name": "ApproxEqual",
      "value_name": "max_abs_diff",
      "default_parameters": { "factor": "1" },
      "transform_steps": [
        { "transformation_name": "ScaleField", "target_field_path": "/noop" }
      ],
      "tolerance_rel": 0,
      "tolerance_abs": 1e-12,
      "noise_aware": false,
      "equation_key": "cylinder-flow-navier-stokes",
      "equation": "Cylinder Flow Navier-Stokes surrogate",
      "program_type": "ML",
      "meta_pattern": "Inv",
      "source_level": "Manual",
      "failure_correlation": "None",
      "sample_case_relative_path": "sample/identity_case.json",
      "work_root_name": "MetBenchMeshGraphNetsCylinder",
      "timeout_seconds": 120
    },
    {
      "mr_id": "mgn-node-permutation-equivariance",
      "sut_name": "meshgraphnets-cylinder-flow",
      "display_name": "MeshGraphNets cylinder flow - node permutation equivariance",
      "description": "Permuting graph node order and remapping faces must not change predictions after inverse permutation.",
      "mr_family": "GNN.Equivariance.NodePermutation",
      "transformation_name": "ScaleField",
      "assertion_type_code": "approx",
      "assertion_name": "ApproxEqual",
      "value_name": "permutation_relative_l2_error",
      "default_parameters": { "factor": "1" },
      "transform_steps": [
        { "transformation_name": "ScaleField", "target_field_path": "/transform/seed" }
      ],
      "tolerance_rel": 0,
      "tolerance_abs": 1e-6,
      "noise_aware": false,
      "equation_key": "cylinder-flow-navier-stokes",
      "equation": "Cylinder Flow Navier-Stokes surrogate",
      "program_type": "ML",
      "meta_pattern": "Inv",
      "source_level": "Manual",
      "failure_correlation": "None",
      "sample_case_relative_path": "sample/node_permutation_case.json",
      "work_root_name": "MetBenchMeshGraphNetsCylinder",
      "timeout_seconds": 120
    },
    {
      "mr_id": "mgn-mirror-y-equivariance",
      "sut_name": "meshgraphnets-cylinder-flow",
      "display_name": "MeshGraphNets cylinder flow - mirror-y equivariance",
      "description": "Mirroring geometry and vertical velocity must mirror the predicted velocity field.",
      "mr_family": "CFD.Symmetry.MirrorY",
      "transformation_name": "ScaleField",
      "assertion_type_code": "approx",
      "assertion_name": "ApproxEqual",
      "value_name": "mirror_relative_l2_error",
      "default_parameters": { "factor": "1" },
      "transform_steps": [
        { "transformation_name": "ScaleField", "target_field_path": "/transform/enabled" }
      ],
      "tolerance_rel": 0,
      "tolerance_abs": 0.05,
      "noise_aware": false,
      "equation_key": "cylinder-flow-navier-stokes",
      "equation": "Cylinder Flow Navier-Stokes surrogate",
      "program_type": "ML",
      "meta_pattern": "Inv",
      "source_level": "Manual",
      "failure_correlation": "None",
      "sample_case_relative_path": "sample/mirror_y_case.json",
      "work_root_name": "MetBenchMeshGraphNetsCylinder",
      "timeout_seconds": 120
    }
  ]
}
```

说明：

- 上面使用 `ScaleField` 作为 MetBench 现有 transformation 的占位式触发。更干净的长期方案是新增 `SetField` / `SetTransformKind` 或支持 identity transformation。
- `source` 和 `followup` 的真实差异由 case JSON 中的 `transform.kind` 控制，runner 读取后执行对应 GNN 变换。
- 如果不希望使用这种“字段触发”方式，应先补 MetBench transformation 能力，再接入该 SUT。

---

## 7. 运行适配器设计

### 7.1 runner 职责

`meshgraphnets_cylinder_runner.py` 的职责：

1. 读取 MetBench case JSON。
2. 加载 tiny/full fixture。
3. 加载 checkpoint，设定 `eval()`。
4. 根据 `transform.kind` 执行输入变换。
5. 执行 one-step inference 或 rollout。
6. 计算 MR 所需指标。
7. 写出稳定 JSON。

CLI：

```bash
python meshgraphnets_cylinder_runner.py --input case.json --output result.json
```

输出 JSON 示例：

```json
{
  "max_abs_diff": 0.0,
  "permutation_relative_l2_error": 2.3e-8,
  "mirror_relative_l2_error": 0.018,
  "relative_l2_error": 0.012,
  "relative_divergence": 0.041,
  "strouhal_delta": 0.0014,
  "main_peak_ratio": 0.91,
  "sample_index": 0,
  "rollout_steps": 1,
  "device": "cpu",
  "checkpoint_sha256": "..."
}
```

### 7.2 runner skeleton

```python
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def load_case(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def run_case(case: dict) -> dict:
    # Import torch / PyG lazily so parser tests can run without heavy deps.
    # from meshgraphnets_cylinder_common import ...
    kind = case.get("transform", {}).get("kind", "identity")

    # Phase 1 smoke implementation should support tiny fixture mode.
    # Full MGN loading is enabled only when checkpoint + data are present.
    if kind == "identity":
        return {
            "max_abs_diff": 0.0,
            "device": case.get("model", {}).get("device", "cpu"),
            "checkpoint_sha256": sha256_file(Path(case["model"]["checkpoint"]))
        }

    raise NotImplementedError(f"unsupported transform kind: {kind}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    case = load_case(args.input)
    result = run_case(case)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 8. 输入适配器设计

MetBench 当前 pipeline 会调用：

```bash
python meshgraphnets_cylinder_input_parser.py parse --input source.json
python meshgraphnets_cylinder_input_parser.py write --dict-file followup.dict.json --output followup.in.json
```

因此 input parser 应保持轻量，不导入 torch：

```python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse(input_file: str) -> dict:
    return json.loads(Path(input_file).read_text(encoding="utf-8"))


def write(data: dict, output_file: str) -> None:
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p_parse = sub.add_parser("parse")
    p_parse.add_argument("--input", required=True)
    p_write = sub.add_parser("write")
    p_write.add_argument("--dict-file", required=True)
    p_write.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.command == "parse":
        json.dump(parse(args.input), sys.stdout, ensure_ascii=False)
        return 0
    if args.command == "write":
        data = json.loads(Path(args.dict_file).read_text(encoding="utf-8"))
        write(data, args.output)
        print(json.dumps({"output": str(Path(args.output).resolve())}, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 9. 输出适配器设计

MetBench 当前 pipeline 会调用：

```bash
python meshgraphnets_cylinder_output_parser.py parse --output-file result.json
```

输出 parser 必须返回 `values` 和 `metadata`：

```python
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


NUMERIC_KEYS = (
    "max_abs_diff",
    "permutation_relative_l2_error",
    "face_order_relative_l2_error",
    "translation_relative_l2_error",
    "mirror_relative_l2_error",
    "relative_l2_error",
    "relative_divergence",
    "scale_relative_l2_error",
    "strouhal_delta",
    "main_peak_ratio",
)


def parse(output_file: str) -> dict:
    payload = json.loads(Path(output_file).read_text(encoding="utf-8"))
    values = {
        key: float(payload[key])
        for key in NUMERIC_KEYS
        if key in payload and payload[key] is not None
    }
    if not values:
        raise KeyError("meshgraphnets output contains no numeric MetBench values")
    return {
        "values": values,
        "metadata": {
            "program": "meshgraphnets_cylinder_flow",
            "device": str(payload.get("device", "unknown")),
            "sample_index": str(payload.get("sample_index", "")),
            "rollout_steps": str(payload.get("rollout_steps", "")),
            "checkpoint_sha256": str(payload.get("checkpoint_sha256", "")),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    p_parse = sub.add_parser("parse")
    p_parse.add_argument("--output-file", required=True)
    args = parser.parse_args()

    if args.command == "parse":
        json.dump(parse(args.output_file), sys.stdout, ensure_ascii=False)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 10. 输入变换实现建议

在 runner/common 层实现以下变换：

| `transform.kind` | 作用 | 注意事项 |
|---|---|---|
| `identity` | 同输入重复推理 | 必须 `model.eval()`，固定随机源 |
| `velocity_noise` | NORMAL 节点速度加噪 | seed 固定，只改 NORMAL |
| `mirror_y` | y 坐标和 `v_y` 取反 | 输出比较前也要对原输出做 mirror |
| `scale_similarity` | 几何和速度同步缩放 | 记录 `k`；Re-St 时还需记录黏度缩放 |
| `node_permutation` | 节点顺序置换，face 重映射 | 输出需 inverse permutation 后比较 |
| `face_order_shuffle` | 单元顺序打乱 | 验证 graph construction 的顺序无关性 |
| `rigid_translation` | 坐标平移，速度不变 | 仅在模型使用相对几何特征时成立 |

MetBench 第一阶段可以让 C# `ScaleField` 修改 `/transform/seed`、`/transform/enabled` 或 `/transform/parameters/k`，由 runner 根据 JSON 字段完成真实 GNN 变换。长期应补专用 transformation，避免语义不美观。

---

## 11. MetBench 代码侧最小改动清单

### 11.1 必需

- 新增 `SUT/meshgraphnets_cylinder_flow/` 目录。
- 新增 `catalog.json`、runner、input parser、output parser、sample cases。
- 新增 launcher end-to-end 测试，例如：

```text
MetBench_SystemMT.Tests/Launcher/LauncherEndToEndMeshGraphNetsCylinderTests.cs
```

- 新增 `SystemMtMetadataCatalog` equation/MR rows。
- 新增 `LegacyCatalogFactory` blueprint rows。
- 更新 `SystemMtLauncherTests` pinned count。
- 更新 `docs/status/current.md`、`docs/requirements.md`、`docs/PROJECT-STRUCTURE.md`。

### 11.2 条件性

如果不想复用 `system` Python，应新增：

- `LauncherOptions.MeshGraphNetsPython`
- `PythonExecutableKinds.MeshGraphNets`
- `ManifestMrCatalogProvider` 中的 executable 解析分支
- WPF 配置接线。若触及 WPF，必须走 Windows SSH/RDP 验证。

第一阶段建议先不做这项，避免把“接入 SUT”变成“改 launcher runtime 配置”的大 PR。

---

## 12. 测试策略

### 12.1 快速测试

不加载 torch，只测试 parser contract：

```bash
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_input_parser.py parse --input SUT/meshgraphnets_cylinder_flow/sample/identity_case.json
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_input_parser.py write --dict-file /tmp/followup.dict.json --output /tmp/followup.json
python SUT/meshgraphnets_cylinder_flow/meshgraphnets_cylinder_output_parser.py parse --output-file /tmp/result.json
```

### 12.2 MetBench focused tests

```bash
dotnet test MetBench_SystemMT.Tests --no-restore --filter "FullyQualifiedName~MeshGraphNetsCylinder|FullyQualifiedName~SystemMtLauncherTests"
```

### 12.3 完整 System MT 测试

```bash
dotnet test MetBench_SystemMT.Tests --no-restore
```

### 12.4 Skip 策略

如果 `.venv-mgn`、checkpoint 或 fixture 不存在，integration test 必须 clean skip，而不是 fail。skip reason 应明确：

```text
MeshGraphNets runtime fixture not configured. Set METBENCH_MGN_PYTHON, METBENCH_MGN_DATA_ROOT and METBENCH_MGN_CHECKPOINT.
```

---

## 13. CI 与可复现性

常规 CI 默认不下载 DeepMind 数据、不训练模型、不安装 GPU 依赖。CI 可分两层：

| CI 层 | 内容 | 触发 |
|---|---|---|
| default | catalog/schema/parser tests + tiny fixture smoke | 每个 PR |
| optional integration | 真实 checkpoint + tiny/full fixture rollout | 手动或 nightly |

建议环境变量：

```text
METBENCH_MGN_PYTHON=/absolute/path/to/.venv-mgn/bin/python
METBENCH_MGN_DATA_ROOT=/absolute/path/to/meshGraphNets_pytorch/data
METBENCH_MGN_CHECKPOINT=/absolute/path/to/checkpoints/best_model.pth
METBENCH_MGN_ENABLE_INTEGRATION=1
```

---

## 14. 分阶段实施计划

### PR-MGN-0：决策与设计

输出：

- T3 decision record 更新：MeshGraphNets Cylinder Flow 被选为 ML/data-driven SUT pilot。
- 本文档或等价设计文档进入仓库 docs。

验收：

- 明确不改 Method MT。
- 明确是否新增 `meshgraphnets` Python kind。
- 明确哪些 MR 进入第一阶段。

### PR-MGN-1：parser + catalog + tiny fixture

输出：

- `SUT/meshgraphnets_cylinder_flow/catalog.json`
- input/output parser
- sample case
- parser contract tests

验收：

- 不依赖 torch 也能跑 parser tests。
- catalog 能被 `ManifestMrCatalogProvider` 读取。

### PR-MGN-2：runner smoke + 首批 MR

输出：

- runner
- tiny fixture smoke
- MR1 identity
- node permutation MR
- mirror-y MR

验收：

- focused launcher tests 通过。
- 缺 venv/checkpoint 时 clean skip。
- 有 venv/checkpoint 时至少 3 条 MR 可运行。

### PR-MGN-3：完整实验 MR

输出：

- perturbation stability
- divergence / conservation
- scale similarity
- Re-St invariance
- 实验报告模板输出

验收：

- Re-St 输出 `St_mean`、`main_peak_ratio`、`strouhal_delta`。
- 长 rollout 只在 integration profile 下运行。

---

## 15. 风险与控制

| 风险 | 后果 | 控制 |
|---|---|---|
| PyTorch/PyG/torch_scatter 安装不稳定 | CI 红、环境不可复现 | 锁版本；默认 skip 重依赖 integration |
| checkpoint 缺失 | runner 无法运行 | tiny fixture + explicit skip reason |
| TFRecord 转换依赖旧 TensorFlow | 现代环境无法安装 | 转换环境与 runtime 环境分离；预转换 fixture |
| MR 容差过严 | 数据驱动模型大量误报 | 先记录 baseline，再固化阈值 |
| Re-St 需要长 rollout | 测试慢且不稳定 | 放 optional integration，不进默认 PR gate |
| 使用 `ScaleField` 承载 GNN 变换语义不自然 | 文档和实现容易失真 | 第一阶段可接受，长期补专用 transformation |

---

## 16. 最小验收标准

首个可合并版本至少满足：

- `catalog.json` 可被 MetBench 读取。
- input parser / output parser 不依赖 torch，能快速测试。
- runner 支持 `--input` / `--output`。
- 至少 1 条 MR 在 tiny fixture 下可运行。
- 缺少重依赖时测试 clean skip。
- 文档明确环境变量、数据位置、checkpoint 位置、MR 容差。
- 不修改 Method MT、不修改 WPF、不修改 Typed Semantic Catalog runtime。

---

## 17. 参考来源

- 本地实验方案：`蜕变测试实验方案.md`
- 上游仓库：`https://github.com/echowve/meshGraphNets_pytorch`
- 上游依赖：`requirements.txt` 当前包含 `matplotlib numpy opencv_python packaging Pillow torch torch_geometric torch_scatter tqdm tensorboard`
- MetBench 当前接入契约：`SUT/<sut>/catalog.json` + `input_parser` + `runner` + `output_parser` + launcher end-to-end tests
