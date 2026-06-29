# 54 · RESS 重定位稿 Phase 0–3 评审（按《科研工作流指南》工具）

> 日期：2026-06-29
> 评审对象：`submissions/RESS/main.tex`（RESS 格式转换版，frontmatter 已重定位，正文未动）
> 方法（指南工具）：Phase 0/1 = deep-research socratic 批判；Phase 2 = paper-search MCP 文献核验（子代理）；Phase 3 = synthesis + Devil's Advocate
> 真源：`manuscript/manuscript.md` L43–55（RQ0–4）；`README.md` L54–77（证据边界）；`submissions/RESS/references.bib`

---

## Phase 0 · 研究定位 —— 通过（条件）

| 过关检查 | 判定 | 依据 |
|---|---|---|
| 一句话定位 | ✅ | "为部署学习型代理的复杂系统可靠性/验证工程师，解决代理无 exact oracle 时如何可审计地把故障归因到代理而非无效测试" |
| 候选刊 ≥1 + 知偏好 | ✅ | RESS，`venues/RESS.md` |
| ≥3 篇同一对话近期论文 | △→✅(待补) | 现 bib 锚 SE/MT 对话；RESS 对话缺锚 → Phase 2 已找到 3–4 条可补 |
| Scope 闸门 | ✅框架/△锚定 | 问题表述落 RESS scope（software reliability + automatic fault detection and diagnosis）；对话锚定待补 |

**要点**：Phase 0 是 IST 桌拒死因（SE 受众→超范围）。重定位修好框架；对话锚定靠 Phase 2 补 RESS 谱系。

---

## Phase 1 · 研究问题 —— 通过（两处须落实）

| 过关检查 | 判定 | 依据 |
|---|---|---|
| RQ 可判定/可证伪 | △ | RQ0 为方法型"How can…"，非单一可证伪命题；可证伪点在 RQ1/RQ4 |
| 证伪预期 | ✅未显式 | 操作命题=「validity gating **changes** V&V outcomes（非仅标注）」；论文已正面满足（airfoil reject 了 cylinder 仅 defer 的 continuity）。**应显式立为 thesis** |
| 全文统一叙事系统 | △风险 | 去黑话（paper/53 §I）须**全文一致**，半改即两套（漂移）|
| Importance 闸门 | ✅ | "让学习型代理的故障归因可审计、控误报"——领域级贡献（修好 IST 低新颖死因）|

**待落实**：① 显式写出 thesis 句；② 去黑话保持单一叙事。

---

## Phase 2 · 文献基础 —— 通过（1 条 △ 待 CNKI 清零）

**子代理用 paper-search MCP 核验 47/47（100%）：✓ 46 · △ 1 · ✗ 0。**

| 过关检查 | 判定 | 依据 |
|---|---|---|
| 0 条无法核实 | ✅(近) | 唯一 △ `yang2020hierarchical`（《计算机科学》2020,47(11A),DOI 10.11896/…）——国际库不索引中文增刊，**非伪造**（作者自引）；按 §8.3 走 CNKI 核对卷期页码即升 ✓ |
| ≥2 竞争工作 | ✅ | MetaTrimmer(约束 MR 适用域)、bug-or-not(真故障 vs MR 不适用)、relaxations；+ reichert2024/yang2021hydromt 提供**反向经验**（MR 一致性与精度不相关）构成张力线 |
| 子领域 ≥3 + 经典齐全 | ✅ | MT 奠基 chen1998 + 综述 chen2018/segura2016 + oracle barr2015 + 科学软件 SLR kanewalaBieman2014 + SciML 代理本体 ≥3，全满足 |

**瑕疵（非阻塞，§4 可选清理）**：`zhao2026noether` 键名与首作者(Li,Meng)不符→建议 `li2026noether`；`yang2021hydromt` 缺 `number=9`。

**RESS 谱系缺口（关键）**：现库几乎无 RESS 本刊引用 → 投 RESS 必被问"为何此刊"。子代理已 Crossref 核实 4 条可补（ISSN 0951-8320）：

| 优先 | 文献 | DOI | 用途 |
|---|---|---|---|
| ★必补 | Paterson et al., Safety assurance of ML for autonomous systems, RESS 264:111311 (2025) | 10.1016/j.ress.2025.111311 | 把"MR→可审计验证资产"接到 ML safety assurance |
| ★必补 | Han & Li, OOD-detection-assisted trustworthy fault diagnosis…deep ensembles, RESS 226:108648 (2022) | 10.1016/j.ress.2022.108648 | RESS 内"OOD+可信性"代表作，呼应"不优于 UQ"边界 |
| ★必补 | E. Chen, Bao, Dinh, Evaluating reliability of ML-based predictions in NPP I&C, RESS 250:110266 (2024) | 10.1016/j.ress.2024.110266 | 接作者核能线到 RESS 当代脉络 |
| 可选 | Subramanian & Mahadevan, Probabilistic physics-informed ML for dynamic systems, RESS 230:108899 (2023) | 10.1016/j.ress.2022.108899 | PIML↔可靠性代理验证 |

---

## Phase 3 · 研究必要性 + Devil's Advocate —— ❌ 1 条 CRITICAL（有明确修复路径）

| 过关检查 | 判定 | 依据 |
|---|---|---|
| 缺口↔贡献 1:1 | ✅ | 3 缺口（MR 识别≠可采测试构造／relaxations 不要求数值可判定／约束-归因不绑数值可判定）↔3 贡献 |
| 每缺口"为何值得填" | △ | 现 SE 语汇；须改 RESS 受众"信任学习型代理时的误报/误归因" |
| ≥2 竞争工作讨论差异 | ✅ | MetaTrimmer/bug-or-not/relaxations 已说清差异 |
| **DA 无 CRITICAL** | ❌ | 见 DA-1 |

**Devil's Advocate 最严苛意见：**
- 🔴 **DA-1（CRITICAL · scope-by-convenience）**：当前**只改了 frontmatter，正文仍纯 SE 黑话+物理**，RESS 审稿人会读成"relabel 躲桌拒"。按指南 Phase 3 规则，CRITICAL **必须回 Phase 2 补文献**——Phase 2 已备好 3 条 RESS 谱系；再叠加 paper/53 §H（广度前置）+ §I（去黑话），让**正文真正进入可靠性对话**，DA-1 即解除。
- 🟡 DA-2：单 checkpoint 泛化 → RESS 容许 case study + §H 广度前置（"非 cross-SUT 率"标签）。
- 🟡 DA-3：gate 思想窄 → 以"控误报/可审计故障归因"操作价值领衔。
- 🟢 DA-4：reliability/localization 越claim → 已被漂移检查 G 红线夹死。

---

## 综合结论与放行条件

**已修好**：IST 两大死因（Phase 0 超范围、Phase 1 importance）经重定位解决；文献真实性 Phase 2 通过。

**放行 Phase 3（解除 DA-1 CRITICAL）须完成的最小集**：
1. **补 3 条 RESS 谱系引用**（Paterson 2025、Han&Li 2022、Chen-Bao-Dinh 2024），并在 Related Work 新增一段把贡献接进 ML-assurance/OOD-trustworthy 对话。 → 清 Phase 0 锚定 + Phase 3 DA-1
2. **执行 paper/53 §I 去黑话**（删 MetaPattern/MR-family/sans-serif 记号），全文单一叙事。 → 清 Phase 1 叙事 + DA-1
3. **执行 paper/53 §H 广度前置**（§5.2 后插 cross-arch/cross-eq 表，保留"非 cross-SUT 率"标签）。 → 清 DA-2
4. **缺口 importance 改 RESS 语汇** + **显式 thesis 句**（门控改变 V&V 结果而非仅标注）。 → 清 Phase 1/3 次要项
5. **清零 △**：CNKI 核 `yang2020hierarchical` 卷期页码；修 `zhao2026noether`→`li2026noether`、补 `yang2021hydromt` number=9。 → 清 Phase 2 残留

**1–4 完成前，本稿处于"封面重定位"，不应投 RESS。** 5 为收尾清理。
