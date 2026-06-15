# 40 — 增量② 云端执行实施方案（自包含,云端读此文件照做）

> Date: 2026-06-15
> 角色：你是云端 Claude Code 会话,在 "Domain-Validity-Gated MR for SciML" 仓库执行本方案。
> 权威设计：`paper/39_increment2_classical_operator_sut_design.md`（深层设计与论证）。本文件是**可执行步骤**。
> 已就绪（已提交）：工具 `tools/run_classical_operator_conservation.py`、guard
> `tests/test_classical_operator_conservation.py`（skip-until-generated）。
> 目标：执行经典算子-代码 SUT,产出**可执行守恒判决**,集成进正文,跑 v29 验证,提交。
> 正面拆 MethodologyRigor 的 major："守恒 MR 在主 SUT deferred,无可执行绝对判决"。

---

## 铁律（全程,违则停）

- **实事求是**：所有数字必须来自真实跑出的 `metric_ledger.json` / 面板报告;缺则问,不猜不填。
- **不调 tol 灌检出**（§10.3）：`CONS_TOL=1e-12` 由"dominate ~1e-15 flux-form 地板"固定;
  缺陷是否被检出必须是真实数值结果。要让某缺陷被检出,只能修**算子代码缺陷构造**,不能动 tol。
- **诚实边界**（§5.9 block）：最小 textbook FV 范例、手构算子代码缺陷;**不写**可靠性/泛化/
  baseline 优越/高 recall。
- **反虚假执行**（§3）：每个"已完成/已修改/已加入"后紧跟工具验证（Read 显示改动 / pytest / git log）。
- **峰值不回退**：当前面板峰值 v28 = overall 7.89（minor,含 airfoil）。本增量净正向才留正文（见第 5 步判读）。
- 云端：shell 不加 `rtk`;sibling 仓库 `/home/user/Minimum-MR-SubSet`（本增量不需要）。

---

## 第 0 步：对齐状态

```bash
git fetch origin claude/youthful-feynman-qy22k2
git checkout claude/youthful-feynman-qy22k2 && git pull
git log --oneline -3      # 期望顶部为 edcf7c4 或更新
```
被动读取并在回复开头一句话总结：`CLAUDE.md`、`NEXT_STEPS.md`、`paper/39_increment2_classical_operator_sut_design.md`。

## 第 1 步：执行工具,生成真实证据

```bash
python tools/run_classical_operator_conservation.py
```
- 期望：`baseline |dM|max ~1e-15 PASS=True`;`nonconservative_form` / `drop_boundary_flux` /
  `double_flux` 三者 `detected=True`;末行 `faults detected: 3/3`。
- 复跑一次,确认除 `generated_at` 外逐字节一致（无随机源）。
- 若某 fault 未检出：按 `paper/39` §4 修正其算子代码缺陷使其真实破坏守恒（**不动 tol**）。
- 产物落在 `research_assets/runs/classical-operator-conservation/raw/metric_ledger.json`。

## 第 2 步：claim C34（用真实数字）

在 `research_assets/experiments/claim-ledger.yml` 的最后一条 C 类 claim 之后、`speculative_claims:` 之前,
新增（把 `<...>` 换成产物里的真实值）：

```yaml
  - claim_id: "C34-classical-operator-executable-conservation"
    status: "observed"
    scope: "one 1D periodic finite-volume Burgers exemplar (flux-form Lax-Friedrichs) / correct conservative scheme vs hand-constructed operator-code faults / conservation MR with machine-precision-scale tolerance"
    evidence:
      - "tools/run_classical_operator_conservation.py"
      - "tests/test_classical_operator_conservation.py"
      - "research_assets/runs/classical-operator-conservation/raw/metric_ledger.json"
      - "paper/39_increment2_classical_operator_sut_design.md"
    wording_allowed: >
      On a classical finite-volume conservation-law operator (1D periodic Burgers,
      flux-form), the conservation MR passes the numerical-decidability gate -- the
      flux-form discrete-conservation residual is floating-point roundoff
      (baseline |dM|max = <BASELINE_DM>), dominated by the 1e-12 verdict tolerance --
      and yields an EXECUTABLE verdict: the correct conservative scheme conserves
      total mass to machine precision (PASS) while <NFAULTS> operator-code faults
      (non-conservative form, dropped interface flux, doubled interface flux) are
      detected (FAIL). The same conservation relation is admissible-and-executable
      here, deferred on the MGN cylinder (uncalibratable floor; C12, C32), and
      rejected on the compressible airfoil (C31) -- a three-task typed verdict for
      one relation.
    wording_forbidden:
      - "A production-solver reliability, generalization, or baseline-superiority claim."
      - "High or general fault-detection recall."
      - "Any claim beyond the single textbook finite-volume exemplar."
    blocked_reason: null
```

## 第 3 步：校验门

```bash
python -m pytest tests -q                          # C34 guard 应从 skip 变 PASS;全绿
python tools/validate_research_assets.py; echo $?  # 0
python tools/validate_experiment_protocol.py; echo $?  # 0
```

## 第 4 步：正文集成（manuscript.md 与 main.tex 同步;数字只来自产物）

1. **§4.1 Subject Systems** 新增一类：
   > **Classical operator-code SUT.** A 1D periodic finite-volume Burgers solver in
   > flux form; the grid and explicit time-stepping use standard library patterns,
   > while the interface flux and conservative update are the scientist-written
   > operator under test and the target of injected operator-code faults.
2. **§5 新子节**（如 §5.5.1 "Executable conservation on a classical operator"）：
   报告 baseline PASS 到机器精度的真实 |dM|;3 个算子代码缺陷被守恒 MR 检出（FAIL）;给出
   **三态对照**：classical = admissible+executable / 圆柱 MGN = deferred / airfoil = rejected。
   一句话点题：这是 §3.5 typed verdict 的活证据——同一守恒关系跨三任务三态。
3. **§3.2 / §3.6**：在已重组的"算子代数 × Yang 三层"叙事里加一句——守恒性质在**计算模型层**的
   可判定性在经典算子上成立（admissible）、在 MGN 上不成立（deferred）。不新增框架。
4. **约束**：
   ```bash
   python tools/ist_wordcount.py     # total ≤ 11800（硬）。超了：先压别处，或把三态对照表计为 float;
                                     # 不擅自升 phase4 buffer（保持 11800）。
   diff <(git show HEAD:paper/manuscript.md | grep -oP '\b\d+[-–]\w+' | sort -u) \
        <(grep -oP '\b\d+[-–]\w+' paper/manuscript.md | sort -u)   # 数字前缀术语集应不变
   ```

## 第 5 步：面板验证 v29 + 判读纪律

```bash
export OPENAI_BASE_URL=<gateway base_url>; export OPENAI_API_KEY=<gateway key>   # 用户提供,勿写入仓库
python tools/run_academic_review_panel.py --outdir research_assets/runs/academic-review-panel-v29
```
提取 overall / accept / per-reviewer,对比 **v28=7.89**,重点看 MethodologyRigor 的
"conservation MR deferred on primary SUT" major 是否松动。

**判读纪律（同 C33 先例,以真实 v29 为准,不硬留）**：
- 若守恒 major 松动 或 overall ≥ 7.89 → **净正向,保留正文新增**。
- 若仅加长无收益 或 回退 → **撤下正文新增**,只把"经典算子上守恒 MR 可执行"**一句**沉淀进 §5,
  C34 工具/产物/claim/guard 留仓库作 revision 备用证据（类比 C33 覆盖几何的处置）。

## 第 6 步：提交（按逻辑分步）

```bash
git grep -nI "sk-" -- . | grep -v ".env.example"   # 敏感扫描,应无输出
# commit A: 工具产物 + C34 + guard 转 PASS
# commit B: 正文集成（§4.1/§5/§3.2）
# commit C: v29 面板 + 判读结论（保留/撤下）
git push origin claude/youthful-feynman-qy22k2
```
每条 commit 消息含 动机 → 改动范围 → 验证结果;尾行：
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`

---

## 验收标准（全绿才算完成）

- [ ] `metric_ledger.json` 生成,baseline PASS、3/3 faults detected（真实数字）。
- [ ] claim C34 入账（真实数字填好 `<...>`）。
- [ ] `pytest` 全绿（C34 guard 由 skip 转 PASS）;两 validators exit 0。
- [ ] 正文集成完成,IST ≤ 11800,no-drift 自检通过,manuscript.md 与 main.tex 同步。
- [ ] v29 跑完,判读结论明确（保留或撤下,有真实分数支撑）。
- [ ] 分步 commit + push;敏感扫描无命中。
- [ ] `NEXT_STEPS.md` 更新本增量结果。
