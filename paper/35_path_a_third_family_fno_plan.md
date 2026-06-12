# 35 — Path A 第三架构家族：FNO roster 计划

Date: 2026-06-11
Decision input: 用户拍板 Path A（补新证据后 v7）；34 号平台期判定。

## 0. 约束与选型

- 本地无 DeepMind cylinder 数据集（仅云端 `/home/user/Minimum-MR-SubSet/` 有），
  Geo-FNO on cylinder（27 号 stretch 项）**本地不可行**，且规则网格插值合法性风险高。
- 选型：**FNO-2D（谱神经算子）在闭式生成的 2D Burgers / heat 数据上**。
  - 第三个真正不同的架构家族：MGN=消息传递 GNN、PINN=坐标 MLP、FNO=谱卷积算子。
  - 数据由 numpy 有限差分参考求解器本地生成（与 PINN 扩展同一 PDE 家族与参考实现谱系，
    family×PDE 矩阵从 2×2 增长到 3×2）。
  - FNO 周期平移等变性是构造性候选关系，恰好测试 admissibility predicate 的区分力：
    非周期边界条件下平移关系应被 rubric **拒绝/降级**而不是直接当作精确 MR——
    这直接回应 v6 glm 的"rubric 验证部分循环"关切（rubric 在新家族上做出非平凡裁决）。
- 诚实边界：闭式合成数据、小网格、K=3 seeds/PDE 起步；是第三个有界家族证据点阵，
  不是 cylinder-flow 跨家族、不是任何 generalization 声明。

## 1. 里程碑

| M | 内容 | 产物 |
|---|---|---|
| M1 | FD 数据生成器（heat/Burgers 2D，周期+Dirichlet 两种 BC 变体）+ FNO-2D 模型 + 训练脚本 + 1-seed smoke | `tools/gen_fd_dataset_2d.py`、`tools/fno2d.py`、`tools/train_fno_2d.py`、smoke manifest |
| M2 | K=6 roster（3 seeds × 2 PDEs）+ rubric 门控 MR runner（平移、镜像、守恒、输出探针） | `research_assets/runs/fno-k6-roster/` + aggregate JSON（bootstrap CI，仿 pinn_k6 模式） |
| M3 | 统一缺陷目录扩展（FNO 输出级闭式探针 ×12/PDE）→ 48+ entries | phase3 catalogue v2 |
| M4 | claim C19 + 稿件集成（§4.1/§5.6.x/摘要边界句）+ 全量测试 + 字数 ≤11000 | manuscript/main.tex 同步 |
| M5 | 面板 v7 | gate 复评 |

## 2. 不做

- 不在本地伪造/下采样 cylinder 数据集；不做 Geo-FNO 插值（合法性风险）。
- 不声明 FNO 结果可比 MGN/PINN 的数值（不同数据分布）；只作 admissibility-gated
  workflow 的第三家族执行证据。
- Zenodo DOI 归档需用户账号（§13.4），单列等待用户。
