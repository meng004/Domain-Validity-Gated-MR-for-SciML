# MeshGraphNets 圆柱绕流仓库使用与运行时资产准备

> 依据文件：`蜕变测试实验方案.md`  
> 上游仓库：`https://github.com/echowve/meshGraphNets_pytorch`  
> 目标：不把完整训练流程放进 MetBench；先在独立环境中得到 MetBench 运行所需的最小运行时资产。  
> 版本：v1.0 / 2026-05-26

---

## 0. 核心结论

原仓库具备 **运行时代码资产**，但不自带完整 **运行时数据资产**。

它已有：`dataset/`、`model/`、`utils/`、`rollout.py`、`train.py`、`train_ddp.py`、`parse_tfrecord.py`、`requirements.txt`。

它通常不自带：`checkpoints/best_model.pth`、`data/test.npz`、`data/test.dat`、可直接放入 MetBench 的 tiny fixture、MetBench runner/input parser/output parser/catalog。

因此：

- 没有 checkpoint 时，需要本地或独立训练环境训练一次。
- 已有兼容 checkpoint 时，不需要本地训练。
- MetBench 默认运行层只需要推理，不应该训练。

---

## 1. 运行时资产最小闭包

| 资产 | 是否必须 | 说明 |
|---|---:|---|
| 上游推理源码 | 必须 | `dataset/`、`model/`、`utils/` |
| runtime venv | 必须 | 可 import `torch`、`torch_geometric`、`torch_scatter`、`numpy`、`scipy` |
| checkpoint | 必须 | 例如 `checkpoints/best_model.pth` |
| 已转换 fixture | 必须 | `.npz + .dat`，至少包含一条可推理样本 |
| MetBench case JSON | 必须 | 指向 fixture、checkpoint、sample index、rollout steps、MR 参数 |
| 完整 TFRecord | 不必须 | 只在重新转换数据时需要 |
| 训练集/验证集全量数据 | 不必须 | 只在训练或复现实验训练曲线时需要 |
| 训练脚本运行 | 不必须 | 已有 checkpoint 时不需要 |
| GIF / 视频 | 不必须 | 只作为人工可视化检查 |

推荐运行时资产目录：

```text
meshgraphnets_runtime/
├── source/
│   └── meshGraphNets_pytorch/
├── venv/
│   └── .venv-mgn/
├── checkpoints/
│   └── best_model.pth
├── fixtures/
│   ├── tiny.npz
│   ├── tiny.dat
│   └── fixture_manifest.json
└── reports/
    ├── training_summary.md
    ├── rollout_smoke.md
    ├── requirements-mgn-runtime-lock.txt
    └── asset_manifest.json
```

---

## 2. 克隆上游仓库

```bash
mkdir -p meshgraphnets_runtime/source meshgraphnets_runtime/reports
cd meshgraphnets_runtime/source
git clone https://github.com/echowve/meshGraphNets_pytorch.git
cd meshGraphNets_pytorch
git rev-parse HEAD
```

必须记录：

```text
upstream_repo = https://github.com/echowve/meshGraphNets_pytorch
upstream_commit = git rev-parse HEAD 的输出
```

后续论文、验收或 MetBench 资产说明中不要只写 `master`。

---

## 3. Runtime venv 配置

推荐 Python 3.10 或 3.11。PyTorch / PyG / torch_scatter 对版本组合敏感，正式资产必须锁版本。

```bash
cd meshgraphnets_runtime
python3.10 -m venv venv/.venv-mgn
source venv/.venv-mgn/bin/activate
python -m pip install --upgrade pip wheel setuptools
cd source/meshGraphNets_pytorch
python -m pip install -r requirements.txt
python -m pip install scipy
```

验证关键依赖：

```bash
python - <<'PY'
import torch
import torch_geometric
import torch_scatter
import numpy
import scipy
print("runtime imports ok")
print("torch", torch.__version__)
print("cuda", torch.version.cuda)
PY
```

生成锁定快照：

```bash
python -m pip freeze > ../../reports/requirements-mgn-runtime-lock.txt
```

如果 `torch_scatter` 安装失败，不要在 CI 中临时编译，应按 PyG 官方 wheel 选择与 `torch`、Python、CUDA/CPU 匹配的 wheel。MetBench 推荐 CPU-only。

---

## 4. 数据准备

完整训练或完整 rollout 需要 DeepMind `cylinder_flow` 数据：

```bash
cd meshgraphnets_runtime/source/meshGraphNets_pytorch
mkdir -p data
aria2c -x 8 -s 8 https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/train.tfrecord -d data
aria2c -x 8 -s 8 https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/valid.tfrecord -d data
aria2c -x 8 -s 8 https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/test.tfrecord -d data
aria2c https://storage.googleapis.com/dm-meshgraphnets/cylinder_flow/meta.json -d data
```

这些文件不进入 MetBench 仓库。如果只做 MetBench smoke，可由他人提供已转换的 tiny fixture，不必下载完整 TFRecord。

---

## 5. TFRecord 转换环境

`parse_tfrecord.py` 可能需要旧 TensorFlow。建议单独建转换环境：

```bash
cd meshgraphnets_runtime
python3.8 -m venv venv/.venv-mgn-convert
source venv/.venv-mgn-convert/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install "tensorflow<1.15" numpy
cd source/meshGraphNets_pytorch
python parse_tfrecord.py
```

转换完成后应得到：

```text
data/train.npz
data/train.dat
data/valid.npz
data/valid.dat
data/test.npz
data/test.dat
```

如果无法安装旧 TensorFlow，替代路线是：在另一台机器转换一次，把 `.npz + .dat` 拷贝到 `meshgraphnets_runtime/fixtures/`。

---

## 6. 是否需要本地训练

不需要训练的条件：

- 已有与当前上游源码兼容的 `best_model.pth`。
- 已有与 checkpoint 对应的 `.npz + .dat` fixture。
- `rollout.py` 或自定义推理脚本可加载 checkpoint 并完成至少一条样本推理。

需要训练的条件：

- 没有 checkpoint。
- checkpoint 与当前 `model/simulator.py` 参数结构不兼容。
- checkpoint 不是 `cylinder_flow` 数据集训练所得。
- MR 需要的物理行为在现有 checkpoint 上明显不合理。

训练命令：

```bash
source meshgraphnets_runtime/venv/.venv-mgn/bin/activate
cd meshgraphnets_runtime/source/meshGraphNets_pytorch
python train.py
```

多 GPU：

```bash
export NGPUS=2
torchrun --nproc_per_node=$NGPUS train_ddp.py --dataset_dir data
```

训练成功后只需要把 `checkpoints/best_model.pth` 纳入运行时资产；`runs/` 不进入 MetBench。

---

## 7. 基线 rollout 验证

训练或拿到 checkpoint 后，必须先做基线推理验证：

```bash
source meshgraphnets_runtime/venv/.venv-mgn/bin/activate
cd meshgraphnets_runtime/source/meshGraphNets_pytorch
python rollout.py --rollout_num 1
python render_results.py
```

验收：

- `rollout.py` 无异常退出。
- 生成 `results/`。
- 可选：`render_results.py` 生成 `videos/`。
- 人工观察：涡街和 ground truth 不应完全失真。

如果基线 rollout 已经明显失真，后续 MR 失败无法有效归因。

---

## 8. 抽取 tiny fixture

MetBench 不应依赖全量 `test.npz/test.dat`。建议抽取 1 到 3 条短轨迹或少量样本，形成 tiny fixture。

tiny fixture 至少保留：

| 字段 | 用途 |
|---|---|
| `pos` | 节点坐标 |
| `node_type` | 区分 NORMAL、OBSTACLE、INFLOW、OUTFLOW、WALL |
| `cells` | 三角单元 |
| `indices` | 轨迹节点切片 |
| `cindices` | 单元切片 |
| `all_velocity_shape` | memmap shape |
| velocity memmap | 当前速度和目标速度 |

为了少改上游读取代码，tiny fixture 仍保留上游 `FpcDataset` 期望的格式：

```text
fixtures/tiny.npz
fixtures/tiny.dat
```

建议另写外部准备脚本 `tools/extract_tiny_fixture.py`，输入 `data/test.npz + data/test.dat`，输出：

```text
meshgraphnets_runtime/fixtures/tiny.npz
meshgraphnets_runtime/fixtures/tiny.dat
meshgraphnets_runtime/fixtures/fixture_manifest.json
```

`fixture_manifest.json` 建议字段：

```json
{
  "source_split": "test",
  "sample_count": 1,
  "time_steps": 2,
  "node_count": 0,
  "cell_count": 0,
  "created_from_upstream_commit": "",
  "checkpoint_expected": "best_model.pth"
}
```

---

## 9. 运行时资产清单

最终交付给 MetBench 接入阶段的是：

```text
meshgraphnets_runtime/
├── source/meshGraphNets_pytorch/
│   ├── dataset/
│   ├── model/
│   ├── utils/
│   ├── rollout.py
│   └── requirements.txt
├── venv/.venv-mgn/
├── checkpoints/best_model.pth
├── fixtures/tiny.npz
├── fixtures/tiny.dat
├── fixtures/fixture_manifest.json
└── reports/
    ├── requirements-mgn-runtime-lock.txt
    ├── rollout_smoke.md
    └── asset_manifest.json
```

`asset_manifest.json` 建议字段：

```json
{
  "upstream_repo": "https://github.com/echowve/meshGraphNets_pytorch",
  "upstream_commit": "",
  "python": "",
  "torch": "",
  "torch_geometric": "",
  "torch_scatter": "",
  "checkpoint_path": "checkpoints/best_model.pth",
  "checkpoint_sha256": "",
  "fixture_npz": "fixtures/tiny.npz",
  "fixture_dat": "fixtures/tiny.dat",
  "fixture_sha256": {
    "npz": "",
    "dat": ""
  },
  "baseline_rollout_status": "pass"
}
```

---

## 10. 本地验证命令

环境验证：

```bash
source meshgraphnets_runtime/venv/.venv-mgn/bin/activate
python - <<'PY'
import torch
import torch_geometric
import torch_scatter
import numpy
import scipy
print("ok")
PY
```

数据验证：

```bash
cd meshgraphnets_runtime/source/meshGraphNets_pytorch
python - <<'PY'
from dataset import FpcDataset
ds = FpcDataset(data_root="data", split="test")
g = ds[0]
print(len(ds))
print(g.x.shape, g.pos.shape, g.face.shape, g.y.shape)
PY
```

期望：

- `g.pos.shape[-1] == 2`
- `g.face.shape[0] == 3`
- `g.x.shape[-1] == 3`，即 `node_type + u + v`
- `g.y.shape[-1] == 2`

checkpoint 验证：

```bash
cd meshgraphnets_runtime/source/meshGraphNets_pytorch
python - <<'PY'
import torch
from model.simulator import Simulator
sim = Simulator(message_passing_num=15, node_input_size=11, edge_input_size=3, device="cpu")
state = torch.load("checkpoints/best_model.pth", map_location="cpu")
sim.load_state_dict(state["model_state_dict"])
sim.eval()
print("checkpoint ok")
PY
```

---

## 11. 常见问题

| 问题 | 原因 | 处理 |
|---|---|---|
| 找不到 `best_model.pth` | 原仓库不自带 checkpoint | 本地训练一次或请求已有 checkpoint |
| 找不到 `test.npz/test.dat` | 原仓库不自带转换后数据 | 下载 TFRecord 后转换，或使用预转换 fixture |
| `torch_scatter` 安装失败 | wheel 与 torch/Python/CUDA 不匹配 | 选择 PyG 对应 wheel；优先 CPU-only |
| TensorFlow 旧版本装不上 | `parse_tfrecord.py` 依赖旧环境 | 单独转换环境或使用别人转换好的 `.npz/.dat` |
| rollout 输出失真 | checkpoint 未收敛或数据不匹配 | 先修正训练/数据，不进入 MetBench MR |

---

## 12. 下一步

本文只解决如何得到运行时资产。下一步见：

```text
MeshGraphNets圆柱绕流MetBench_MR资产编制与验证说明.md
```

该文档负责把运行时资产包装成 MetBench 可执行 MR：`catalog.json`、runner、input parser、output parser、sample case、全部 MR 的指标和验证流程。
