# Experiment Empirical Protocol

## 1. 实验目标

本文实验部分的目标是建立一个 evidence-gated empirical protocol，用于评价
MeshGraphNets-family cylinder-flow surrogate 的物理约束蜕变关系测试资产是否具备
可执行、可复核、可扩展到真实 SUT 的证据链。当前目标不是报告模型性能，也不是给出
真实 SUT 的通过率或失效率，而是把可观察证据、限定性证据和 blocked 证据分层。

当前可以写入方法部分的核心目标是：以 relation-level verdict coverage and evidence
completeness 为主指标，说明每条 MR 从设计、fixture、运行前置条件到 verdict ledger 的证据门槛。

## 2. 分层实验设计

实验设计分为三层：

1. Fixture asset layer：仅验证 MR 资产路径、fixture transformation 和 metric ledger 是否存在且可追踪。
2. Real SUT execution layer：在记录 dataset、model repository、checkpoint、command 和 raw outputs 后，才允许执行真实 MeshGraphNets 推理。
3. Baseline comparison layer：在每个 baseline 拥有匹配运行产物与 scoring ledger 后，才允许比较。

当前已有 fixture-level node-permutation asset path，可作为 observed asset-plumbing evidence。
此外，已完成一次受限的 single-SUT / single-MR / single-case pilot：在一个真实训练好的
MeshGraphNets 圆柱绕流代理模型上执行了 node permutation 等变性 MR（详见第 3、7 节）。
而三个 METBENCH 计划的真实 SUT execution 仍 blocked，因为当前没有记录
`METBENCH_MGN_DATA_ROOT`、`METBENCH_MGN_REPO`、`METBENCH_MGN_CHECKPOINT`、精确命令和输出产物。

## 3. 实证矩阵

| Layer | Subject | Current Status | Required Evidence Before Claim Upgrade |
|---|---|---|---|
| Fixture asset | Node permutation fixture | observed fixture-only | Existing fixture verdict ledger and fixture case path |
| Real SUT (pilot) | MeshGraphNets cylinder-flow surrogate (Minimum-MR-SubSet PR #103, read-only) | observed pilot (one MR, one case) | Manifest + checkpoint sha256 + raw source/follow-up/mapped outputs + metric ledger (all present) |
| Real SUT | Echowve MeshGraphNets cylinder-flow implementation | blocked | Dataset root, repo, checkpoint, command, raw outputs, metric ledger |
| Real SUT | PhysicsNeMo MeshGraphNets-family implementation | blocked | Dataset root, repo, checkpoint, command, raw outputs, metric ledger |
| Real SUT | Third independent implementation | blocked | Dataset root, repo, checkpoint, command, raw outputs, metric ledger |
| Baseline | Manual expert MR design | protocol commitment | Matched MR set, review ledger, run artifacts |
| Baseline | Generic automatic MR generation scope contrast | protocol commitment | Candidate generation artifact and comparable scoring |
| Baseline | LLM-generated candidate MRs | protocol commitment | Prompt/configuration, candidate ledger, review decisions, run artifacts |
| Baseline | Pure rollout accuracy | protocol commitment | Rollout metrics aligned with the same subject systems and data |

## 4. 指标与判定

Primary metric:

- relation-level verdict coverage and evidence completeness

Secondary metrics:

- completeness of dataset, repository, checkpoint, command, and output artifact records;
- traceability from MR card to source/follow-up case and metric ledger;
- blocked-run transparency;
- reproducibility bundle completeness.

判定规则采用 fail-closed policy：任何真实 SUT claim 缺少 dataset、repo、checkpoint、command 或 output artifact 时，claim 维持 blocked。Fixture verdict 只能支持 asset path observed，不能外推为 SUT behavior。

该 fail-closed 前置条件检查由代码强制执行，而非仅停留在文字层面：`tools/validate_experiment_protocol.py` 中的 `validate_real_sut_preconditions` 在 `METBENCH_MGN_DATA_ROOT`、`METBENCH_MGN_REPO`、`METBENCH_MGN_CHECKPOINT` 任一缺失时，要求所有 `real-sut-*` run 维持 `blocked` 且 `sut_execution: not-run`。

真实 SUT 的最小 run manifest 必须包含：

- required env：`METBENCH_MGN_DATA_ROOT`、`METBENCH_MGN_REPO`、`METBENCH_MGN_CHECKPOINT`；
- command template：`python3 tools/run_real_sut_mr.py --manifest <run-manifest.yml>`；
- seed/env capture：随机种子、deterministic flags、device、Python/framework 版本、git commit；
- source_case_path 与 follow_up_case_path；
- raw output paths：source prediction、follow-up prediction、restored/mapped follow-up output；
- metric ledger fields：`run_id`、`sut_id`、`mr_id`、`source_case_id`、`follow_up_case_id`、`metric_name`、`metric_value`、`tolerance`、`verdict`、`evidence_artifact`；
- claim upgrade rule：只有 manifest、raw outputs、metric ledger、claim ledger 都存在并通过校验，blocked claim 才能升级。

## 5. Baseline

本协议记录四类 baseline，但当前均为 protocol commitment，不是结果：

- Manual expert MR design
- Generic automatic MR generation scope contrast
- LLM-generated candidate MRs
- Pure rollout accuracy

Baseline comparison 必须在 matched run artifacts、scoring ledgers 和 comparable outputs 存在后才能进入 Results。当前不能写 superiority、improvement、effectiveness 或 baseline ranking。

四类 baseline 使用同一组 scoring dimensions：candidate_mr_count、validity_rubric_decision、executable_verdict_coverage、evidence_completeness、review_effort。Manual expert MR design 是候选提出方式的 baseline，不等于本文的 validity-rubric workflow；LLM-generated candidate MRs 只作为候选生成与辅助整理 baseline，不作为 MR 有效性的最终裁判。

## 6. 证据门槛

Claim 升级规则如下：

| Claim Status | Minimum Evidence |
|---|---|
| observed | Artifact exists and directly supports the narrow asset-path statement. |
| qualified | Design-time or rubric evidence exists, but runtime interpretation is explicitly limited. |
| blocked | Required runtime, baseline, or output evidence is missing. |
| speculative | Only future-work framing is allowed. |

Blocked claims 不能写成 Results。它们只能出现在 method/protocol、limitations 或 future experiments 中，并且必须保留缺失证据说明。

## 7. 当前 pilot 结果与 blocked 项

已完成的 single-SUT / single-MR / single-case pilot（可写入 Results，但必须保留限定语）：

- Subject：一个真实训练好的 MeshGraphNets 圆柱绕流代理模型，来自只读仓库 `Minimum-MR-SubSet`（已合并 PR #103），checkpoint sha256 `cf281f85...b04a9`，SUT commit `8c0b7ef`。
- MR：node permutation 等变性。Source case：eval split 第 0 帧（1923 节点、11070 边）。
- 执行：source 推理 → 一致的节点置换 → follow-up 推理 → 逆映射回原节点序 → relative L2。
- 结果：relative L2 = 0.0（容差 1e-6），verdict pass。命令、raw outputs、metric ledger、manifest 均保存在 `research_assets/runs/real-sut-node-permutation-pilot/`，exit code 0。
- 限定：这是一个 SUT、一条 MR、一个 source case 的 pilot evidence，不构成 pass/fail rate、violation rate、model reliability、baseline 优劣或 seeded-fault 检测结论。

当前 blocked 项包括：

- Real Echowve SUT verdicts: missing `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, `METBENCH_MGN_CHECKPOINT`, exact command, and raw outputs.
- Real PhysicsNeMo SUT verdicts: missing `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, `METBENCH_MGN_CHECKPOINT`, exact command, and raw outputs.
- Third implementation SUT verdicts: missing `METBENCH_MGN_DATA_ROOT`, `METBENCH_MGN_REPO`, `METBENCH_MGN_CHECKPOINT`, exact command, and raw outputs.
- Baseline comparison: missing matched baseline artifacts, scoring ledgers, and comparable outputs.
- Seeded-fault effectiveness: missing seeded-fault subjects, commands, and outputs.

前置条件检查记录（可写入 Method/Protocol，不可写入 Results）：2026-06-05 检查 `METBENCH_MGN_DATA_ROOT`、`METBENCH_MGN_REPO`、`METBENCH_MGN_CHECKPOINT` 均为 UNSET，因此上述真实 SUT run 全部维持 blocked。该记录是环境观测，不构成任何 SUT 推理或 verdict 证据，详见 `research_assets/experiments/experiment-ledger.yml` 的 `precondition_check` 与 claim ledger `C5-precondition-check`。

这些 blocked claims 不能写成 Results；只能作为实验协议、证据门槛和后续实验计划来呈现。
