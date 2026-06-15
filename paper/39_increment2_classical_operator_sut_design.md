# 39 — 增量② 设计文档：经典算子-代码 SUT + 可执行守恒判决

> Date: 2026-06-15
> Status: DESIGN / 执行就绪。**执行在云端**（pull 本分支 → 跑工具 → 集成 → 跑 v29）。
> 触发数据：v28=7.89（新峰值）。两张封顶 major 之一是 MethodologyRigor 的
> "守恒 MR 在主 SUT deferred——最硬的门未行使"。本增量正面拆它。

---

## 1. 动机（精确对应的审稿人关切）

| 关切（v28 复现） | 来源 | 本增量如何拆 |
|---|---|---|
| **守恒 MR 在主 SUT deferred,无可执行绝对判决** | MethodologyRigor(major), DevilsAdvocate | 经典守恒算子上守恒 MR **可标定 → 产出可执行 PASS/FAIL** |
| "只是神经网络?" 经验全是学习代理 | EIC, DomainExpert | 加一条**经典算子-代码 SUT**,横跨"学习+经典" |
| 缺陷"任意腐蚀/gross" | 全员 | 缺陷植入**科学家自写的通量函数**(真实缺陷形态) |

**一句话主张（新增,受 §5.9 block 约束,不外推）**：在一个守恒律离散算子上,守恒 MR
通过数值可判定性门并产出**可执行判决**——正确守恒格式 PASS 到机器精度,算子代码缺陷
(非守恒形式/漏通量/重复通量)FAIL;这与圆柱 MGN 上守恒被 **deferred**(地板不可标定)、
airfoil 上不可压连续性被 **rejected**(物理不成立)构成**同一关系的三态 typed verdict**。

---

## 2. SUT 定义（经典算子-代码,非学习代理）

- **物理/方程层**：1D 标量守恒律(Burgers）`∂u/∂t + ∂(u²/2)/∂x = 0`,周期边界 `[0,L)`。
  选 Burgers 而非线性平流的原因：**守恒形式与平流(非守恒)形式在此不同**,使"非守恒形式"
  成为可注入的真实缺陷;线性常系数平流两者重合,无法区分。
- **框架层(成熟库,非缺陷区)**：等距网格、显式时间步进、CFL 选 Δt——纯 numpy,平凡。
- **算子层(科学家自写,缺陷区)**：界面**通量函数** `F_{i+1/2}` 与守恒形式更新
  `u_i^{n+1} = u_i^n − (Δt/Δx)(F_{i+1/2} − F_{i−1/2})`。用 Lax–Friedrichs 通量
  `F_{i+1/2} = ½(f(u_i)+f(u_{i+1})) − ½(Δx/Δt)(u_{i+1}−u_i)`,`f(u)=u²/2`。

> 诚实边界：这是**最小经典算子范例**(textbook FV),非大型生产代码。可执行守恒判决的论点
> 是真实的、原理上可推广,但在此范例上演示。受 §5.9 block：不声明可靠性/泛化/baseline 优越。

---

## 3. 守恒 MR + 可准入性(为何此处可执行,MGN 上 deferred)

- **关系**：总量 `M^n = Σ_i u_i^n Δx`。周期边界 ⇒ 净边界通量 = 0 ⇒ 守恒形式更新使
  `Σ_i(F_{i+1/2}−F_{i−1/2})` **telescope 抵消** ⇒ `M` 守恒到**机器精度**。
- **可准入性(condition iv 数值可判定)**：正确 flux-form 的离散守恒残差 = 浮点舍入 ~1e-15,
  即**算子地板 ≈ 1e-15**;验收容差取 `tol = 1e-12` **dominate 地板** ⇒ 关系 **admissible**,
  产出**可执行 PASS/FAIL**。
- **三态对照(typed verdict,论文最强的统一叙事)**：

  | 任务 | 守恒关系命运 | 原因(在 层×性质 矩阵里) |
  |---|---|---|
  | **经典 FV 算子(本增量)** | **admissible + executable** | flux-form 离散守恒残差=机器精度,tol dominate |
  | 圆柱 MGN | **deferred** | 参考场自带非零散度,地板不可标定(C12/C32) |
  | airfoil MGN | **rejected** | 可压流,不可压连续性物理不成立(C31) |

  同一守恒性质,三层/三任务三态——这正是 typed domain-inadmissibility verdict 的活证据。

---

## 4. 缺陷模型（注入科学家自写的通量/更新算子代码）

| mutant | 算子代码缺陷(真实形态) | 破坏的性质 | 守恒 MR 预期 |
|---|---|---|---|
| `baseline` | 正确守恒 LF 通量 | — | **PASS**(|ΔM|~1e-15) |
| `nonconservative_form` | 写成平流形式 `u_i·(u_{i+1}−u_{i−1})/2Δx` | flux-form 结构 | **FAIL** |
| `drop_boundary_flux` | 某 cell 漏减 `F_{i−1/2}`(误索引) | telescope 结构 | **FAIL** |
| `double_flux` | 单侧界面通量 ×2(非 telescope) | telescope 结构 | **FAIL** |

(可选第 5 个 `inconsistent_interface`：同一界面被相邻两 cell 用不同通量值——界面通量不唯一,
真正破坏 telescope;云端构造时务必核实它确实使 |dM|>tol,否则弃用。先用上表 4 个稳的。)

要点：缺陷全在**通量函数/更新公式**(算子层),框架(网格/步进)不动——真实 CFD bug 正是
"把守恒形式写成平流形式 / 通量记账错"。这也回应覆盖几何：守恒 MR 抓的正是破坏 flux-form
守恒结构的缺陷,对保持该结构的缺陷(如一致的界面通量值错)不灵敏(可作诚实盲区注记)。

可选交叉检查(增量③前哨,非②必须)：reflection/superposition MR——线性平流 SUT 上
`u(αv+βw)=αu(v)+βu(w)` 到机器精度,系数错缺陷破坏之。

---

## 5. 工具代码（云端 `tools/run_classical_operator_conservation.py`,执行就绪）

```python
#!/usr/bin/env python3
"""Classical operator-code SUT: executable conservation MR on a finite-volume
scalar conservation law (1D periodic Burgers). Conservation is ADMISSIBLE here
(flux-form discrete-conservation residual is floating-point roundoff, dominated
by the 1e-12 tolerance), so the MR yields a full executable PASS/FAIL -- unlike
the MGN cylinder case where it is deferred. Faults are injected into the
scientist-written flux/update operator (not the grid/time-stepping framework).

Honesty boundary: one minimal textbook FV exemplar; not a production solver, not
a reliability/generalization/baseline-superiority claim.
"""
from __future__ import annotations
import argparse, hashlib, json
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / "research_assets" / "runs" / "classical-operator-conservation"

L, N, T_STEPS = 2.0, 200, 50
DX = L / N
CFL = 0.4
CONS_TOL = 1e-12   # verdict tolerance; dominates the ~1e-15 flux-form floor

def f(u):            # Burgers flux
    return 0.5 * u * u

def initial_field():
    x = (np.arange(N) + 0.5) * DX
    return 0.5 + 0.4 * np.sin(2 * np.pi * x / L)   # smooth, periodic, Sum != 0

def dt_from_cfl(u):
    amax = float(np.max(np.abs(u))) or 1.0
    return CFL * DX / amax

def lf_flux(u, dt):
    up = np.roll(u, -1)                              # u_{i+1}
    return 0.5 * (f(u) + f(up)) - 0.5 * (DX / dt) * (up - u)

def step(u, mutant):
    dt = dt_from_cfl(u)
    if mutant == "nonconservative_form":            # advective (non-flux) form
        ux = (np.roll(u, -1) - np.roll(u, 1)) / (2 * DX)
        return u - dt * u * ux, dt
    F = lf_flux(u, dt)                               # F_{i+1/2}, i=0..N-1
    Fm = np.roll(F, 1)                               # F_{i-1/2}
    if mutant == "drop_boundary_flux":
        Fm = Fm.copy(); Fm[0] = 0.0                  # mis-indexed: drop one interface -> Sum(F-Fm)=F_{N-1}!=0
    elif mutant == "double_flux":
        F = 2.0 * F                                  # non-telescoping: Sum(2F-roll(F,1))!=0
    return u - (dt / DX) * (F - Fm), dt

def total_mass(u):
    return float(np.sum(u) * DX)

def run_mutant(mutant):
    u = initial_field()
    m0 = total_mass(u)
    max_abs_dM = 0.0
    for _ in range(T_STEPS):
        u, _ = step(u, mutant)
        max_abs_dM = max(max_abs_dM, abs(total_mass(u) - m0))
    detected = max_abs_dM > CONS_TOL
    return {"mutant": mutant, "max_abs_delta_mass": max_abs_dM,
            "conservation_MR_pass": (not detected),
            "conservation_MR_detects_fault": detected}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", default=str(OUTDIR))
    args = ap.parse_args(argv)
    mutants = ["baseline", "nonconservative_form", "drop_boundary_flux",
               "double_flux"]
    rows = [run_mutant(m) for m in mutants]
    base = next(r for r in rows if r["mutant"] == "baseline")
    faults = [r for r in rows if r["mutant"] != "baseline"]
    record = {
        "ledger_id": "classical-operator-conservation",
        "schema_version": "0.1.0",
        "evidence_level": "classical-operator-code-sut-executable-conservation",
        "sut": "1D periodic finite-volume Burgers (flux-form Lax-Friedrichs)",
        "operator_under_test": "scientist-written interface flux + flux-form update",
        "framework_libraries": "uniform grid, explicit time-stepping (not under test)",
        "conservation_mr": {
            "quantity": "total mass M = sum(u)*dx",
            "tolerance": CONS_TOL,
            "operator_floor_estimate": "flux-form telescoping residual ~1e-15 (float roundoff)",
            "admissible": True,
            "admissibility_reason": "tolerance 1e-12 dominates the ~1e-15 flux-form floor",
        },
        "grid": {"L": L, "N": N, "dx": DX, "steps": T_STEPS, "cfl": CFL},
        "results": rows,
        "summary": {
            "baseline_pass": base["conservation_MR_pass"],
            "baseline_max_abs_delta_mass": base["max_abs_delta_mass"],
            "faults_detected": sum(r["conservation_MR_detects_fault"] for r in faults),
            "num_faults": len(faults),
        },
        "typed_verdict_contrast": {
            "classical_fv_operator": "admissible + executable (this run)",
            "cylinder_mgn": "deferred (uncalibratable floor; C12/C32)",
            "airfoil_mgn": "rejected (compressible; C31)",
        },
        "honesty_boundary": ("One minimal textbook FV exemplar; faults are hand-constructed "
                             "operator-code edits. Not a production solver, reliability, "
                             "generalization, or baseline-superiority claim."),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    out = Path(args.outdir); (out / "raw").mkdir(parents=True, exist_ok=True)
    (out / "raw" / "metric_ledger.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"baseline |dM|max={base['max_abs_delta_mass']:.2e} PASS={base['conservation_MR_pass']}")
    for r in faults:
        print(f"  {r['mutant']:22s} |dM|max={r['max_abs_delta_mass']:.3e} "
              f"detected={r['conservation_MR_detects_fault']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

> 云端执行注意：上述 4 个缺陷均在精确算术下确凿破坏 telescope(drop→残 `F_{N-1}`;
> double→残 `ΣF`;nonconservative→平流形式不守恒),baseline 守恒到舍入级。**以真实跑出的
> |dM| 为准**,不得手填数字。若要加第 5 个 `inconsistent_interface`,先在云端验证其 |dM|>tol。

---

## 6. 云端执行步骤（按序,实事求是,数字以真实输出为准）

```bash
# 0. 取分支(云端 sibling 在 /home/user/Minimum-MR-SubSet,本增量不需要它)
git fetch origin claude/youthful-feynman-qy22k2 && git checkout claude/youthful-feynman-qy22k2 && git pull
# 1. 落地工具(§5 代码)并运行
python tools/run_classical_operator_conservation.py
#    期望:baseline PASS(|dM|~1e-15);各 fault detected=True。若某 fault 未 detected,
#    按 §5 注记修正其算子代码缺陷构造,直到它真实破坏守恒(不得调 tol 灌结果,守 §10.3)。
# 2. 复跑确认确定性(无随机源,应逐字节一致,除 generated_at)
# 3. 加 claim C34(用真实数字)、guard tests/test_classical_operator_conservation.py
python -m pytest tests -q                      # 期望全绿
python tools/validate_research_assets.py && python tools/validate_experiment_protocol.py
# 4. 正文集成(见 §7),字数 ≤11800(IST),no-drift 自检
python tools/ist_wordcount.py
# 5. 跑 v29 面板,对比 v28(7.89),看 MethodologyRigor 的"守恒 deferred" major 是否松动
OPENAI_BASE_URL=... OPENAI_API_KEY=... python tools/run_academic_review_panel.py \
  --outdir research_assets/runs/academic-review-panel-v29
# 6. commit + push
```

---

## 7. 正文集成点（云端据真实数字写,净中性或在 11800 内）

- **§4.1 Subject Systems**：新增一类 **Classical operator-code SUT**(1D 周期 FV Burgers,
  flux-form),明确"框架用库 / 通量算子自写、为缺陷注入对象"。
- **§5（新子节,如 §5.5.x 或并入守恒叙事）**：报告**可执行守恒判决**——baseline PASS 到
  机器精度(真实 |dM|),N 个算子代码缺陷被守恒 MR 检出;给出 **三态 typed verdict 对照表**
  (classical=executable / MGN=deferred / airfoil=rejected)。这是 §3.5 typed verdict 的活证据。
- **§3.2 / §3.6**：守恒性质在"计算模型层"的可判定性,在经典算子上 admissible、在 MGN 上 deferred
  ——直接落进已重组的 层×性质 矩阵,无需新框架。
- **claim C34**(sketch,数字待真实跑)：
  ```
  C34-classical-operator-executable-conservation
  scope: one 1D periodic finite-volume Burgers exemplar / flux-form vs operator-code faults
  wording_allowed: On a classical finite-volume conservation-law operator the conservation MR
    passes the numerical-decidability gate (flux-form residual ~1e-15 dominated by the 1e-12
    tolerance) and yields an EXECUTABLE verdict: the correct conservative scheme conserves total
    mass to machine precision (PASS) while operator-code faults (non-conservative form, dropped/
    doubled interface flux) are detected (FAIL). The same conservation relation is admissible-and-
    executable here, deferred on the MGN cylinder (uncalibratable floor), and rejected on the
    compressible airfoil -- a three-task typed verdict for one relation.
  wording_forbidden: production-solver reliability / generalization / baseline-superiority /
    high-recall fault detection.
  ```
- **guard** `tests/test_classical_operator_conservation.py`：校验产物——baseline PASS、
  faults_detected==num_faults、admissible==True、三态对照存在;正文含"executable"守恒判决句。

---

## 8. 风险与守则

- **不得调 tol 灌检出**(§10.3)。tol=1e-12 由"dominate 1e-15 地板"决定,固定;缺陷是否被检出
  必须是真实数值结果。
- **诚实标注**：最小范例、手构缺陷;不外推。三态对照是论文叙事强点,但每态都已有 claim 支撑
  (C34 新 / C12+C32 MGN / C31 airfoil),不新增越界主张。
- **字数**:若 §5/§4.1 新增触 11800,按既有做法先压缩别处或将对照表计为 float;不擅自升 buffer。
- **panel 不确定性**:v29 可能因新增篇幅微动;若守恒 major 松动则净正向,若仅加长则回退——
  以真实 v29 为准决定去留(同 C33 的处置纪律)。
