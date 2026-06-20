# NEXT_STEPS — MR识别/圆柱绕流 (IST submission)

> Last updated: 2026-06-20 by claude-code (实证扩张:MVP+EXT-2/FNO/PINN 全完成,by-class+盲区在 4 架构族复现 C41-C46;下一步=整合进 main.tex → 重跑 panel)

## 🟡 2026-06-20 冲中科院1区实证扩张计划(目标 TSE/TOSEM,根治 incremental+单SUT)

> 背景:F-1 sharp claim(commit `42b6f41`)+ hedge 瘦身(commit `1944e5d`)后,gate-1/gate-2 真实 5-LLM panel EIC 仍 major(accept 0.65→0.58,clarity 7→6),三轮 major 经核实是**稳定上限**(分数波动是 LLM 噪声,非可改缺陷)。期刊重估(deep-research + CAS 分区):**2区Q1 的 IST 是高分区∩可发表甜点**;真1区 TSE/TOSEM(1区Top)需先补第二收敛SUT+量化baseline。用户拍板:**为冲1区做实证扩张**。
> 关键战略:**整个 MVP 全本地 CPU/MPS、零 GPU、零新凭据**(第二SUT直接用已收敛的 PointMLP);GPU 只在 EXT-1 airfoil 续训需要,且放在 MVP 验证有效之后(避免重蹈 airfoil −0.4 / C34 撤回的历史反伤)。完整计划:本会话工作流 `wcqn9zm0f` 输出。

### ✅ Done — MVP(云端)+ EXT 本地部分(2026-06-20,全 CPU/MPS,399 tests pass)
- [x] **MVP-A** PointMLP 端到端 seeded-fault — `C41`(by-class 与 MGN 一致,union 4/8)— 云端,merge `917c5f5`
- [x] **MVP-B/C** 三臂互补 + gate value + knife-edge — `C42`/`C43` — 云端,merge `a10fa23`
- [x] **EXT-2** operator-floor 跨拓扑(非结构 Delaunay)— `C44`(slope 0.983 vs 结构 0.984,floor 比值 1.06/1.33,topology-stable)— commit `ac92eef`
- [x] **B-FNO** 端到端 seeded-fault — `C45`(by-class + 盲区 0/24,transport-shift 27% 场变化仍漏)— commit `45999c3`
- [x] **B-PINN** 端到端 seeded-fault — `C46`(by-class + 盲区 0/6,cos(πx) 70% 场变化仍漏)— commit `65ff515`
- [x] **airfoil cuda 修复** — `_select_device` 加 cuda→mps→cpu,EXT-1 在 CUDA 机器就绪 — commit `e3f16a3`
- **里程碑**: by-class 检测 + 结构性盲区已在 **4 架构族**复现(MGN/PointMLP/FNO/PINN,跨谱方法/逐点/消息传递 + cylinder/Burgers/heat)→ 直接拆掉 EIC 的 single-SUT/fragmented 前缀。

### 🟡 In Progress — 把证据整合进稿件(最该做,本地)
- [ ] **整合 C41–C46 进 `main.tex`**(claim-ledger 授权边界内:4 架构 by-class + operator-floor 跨拓扑 + 三臂互补 CI)
  - **硬约束**: ID-free(`\bC\d+`≤10,当前 9,**不能逐个引 C4x**,用描述 + appendix claim 名);`not a `≤28;word budget headroom ~2,455(每图/表 200 词,谨慎加 float);phase8/9 guard 串保留;0 句 superior/outperforms/better
  - next-action: 工作流定位落点 + ID-free 措辞 + guard/budget 核对 → 执行编辑 → pytest/wordcount/build 验证
- [ ] 整合后**重跑 gate panel**,看 EIC 是否从 major 上移(这才是改判关键)

### 🔴 Blockers — EXT-1(需 Windows/WSL2 或云端 CUDA)
- [ ] **EXT-1** airfoil 训到收敛(不同物理 compressible)— 代码已就绪(cuda 分支已补);唯缺训练配方 + GPU 时间;风险:配方问题可能仍训不收敛

### 🟢 Backlog
- [ ] **EXT-3** 三臂互补 + duality 跨全部收敛 SUT(MGN/PointMLP/FNO/PINN 已可立做,airfoil 收敛后更全)

### 🔵 Open Questions
- [ ] 目标锁 **TSE** 还是 **TOSEM**?TSE=IEEEtran 单栏单盲(`venues/IEEE-TSE.md` 已有);TOSEM=acmart 双盲(需新建 `venues/TOSEM.md` + §15 双盲化审计);回退 IST 零切换成本。**venue 未定前不要双盲化**(过早匿名化反伤)。
- [ ] 诚实风险: 即便 MVP+EXT 全做完,**1区 仍可能因 novelty 立场(incremental)被拒**——扩张拆的是 evidence 前缀(single-SUT/under-trained/fragmented),不是 novelty 不足。兜底: MVP 资产全部直接强化 IST 稿(把模拟评审从 major↔minor 上移),回退2区净收益;**GPU 投入放在 MVP 验证有效之后**。

## 🟢 2026-06-17 真实多厂商网关面板 (v37+v38) + deep-research 学术评估 + 成熟度复评
- **✅ 真实多厂商网关面板首次跑通(历史一直被"key 耗尽"阻塞)**:`tools/run_academic_review_panel.py` 在两个独立网关各跑一次,5 厂商(gpt-5.5/glm-5.1/deepseek-v4-flash/qwen3-max/kimi-k2.6),5/5 reviewer、0 失败。**v38**(用户提供网关,OpenAI 兼容,需 `/v1` 后缀)overall **7.86** / accept **0.604** / 多数 **major**(3M/2m);**v37**(兄弟 bltcy 网关)overall **7.6** / accept **0.67** / 多数 **minor**(2M/3m)。记录 `research_assets/runs/academic-review-panel-v37|v38/`。
- **边界铁证**:5 reviewer 中 4 个跨网关 verdict 一致(EIC gpt-5.5 / kimi = major;glm / qwen = minor),整体 verdict 仅靠 **deepseek 一票**翻转(v37 minor 0.65 → v38 major 0.40)→ 论文恰处 **major↔minor 边界**;两网关维度均值高度一致(clarity 仍最弱 6.8/7.0)。
- **deep-research 学术定级**(paper-search-mcp):新颖性=增量重组 + 1 个真新原子(**measurement-floor 容差闸**,文献未见以测量算子误差地板门控 MR admissibility)。最大新颖性威胁=duality vs **Kanewala 覆盖簇**:Srinivasan & Kanewala 2022 STVR `10.1002/stvr.1807` + Saha & Kanewala 2019 `1904.07348`——**均核实真实且确实不在 35 条 bib 中**(deep-research 另报的 Olsen validity-TR / Lin-Simon-Niu 经 bib 复核已引,系误报)。IST 适配强(Spieker 2025 同刊先例)。
- **凭据**:用户提供网关 base_url + key 已存 **gitignored `.env`**(域名不入库,§5)(同时补 `.gitignore` secrets 基线);`git check-ignore .env` 确认不入库。**绝不 commit**。
- **成熟度裁决**:机制 submission-ready(IST 14/14)、科学 major/minor 边界(历史天花板,无新 blocker)。唯一新增·便宜·对症的杠杆=**P0 补 Kanewala 覆盖簇 2 条引用并与 duality 对比**(同时缓解共识关切 #1 tautology + #5 novelty)。其余 P1 body 层 duality 软化 / P2 密度(已近底) / P3 synthetic-fault 边界。详见 `docs/review_presubmission/maturity_assessment.md`(本会话已更新为真实网关版)。**未改动 manuscript。**

## 🟢 2026-06-17 投稿前流水线(§11 终稿 / §15 投稿审计 / §12 IST 合规)
- **✅ bib 真实性校验(§8.5 hard-block)→ 修 7 处引用完整性缺陷**(commit `adad46b`):逐条 crossref 亲验(子代理在 lin/reichert 漏报作者错,已全复核纠正)。`kanewala2019scientific` **按原样不存在**(DOI=Codabux 技术债文)→ 换真实 Kanewala & Chen 2019 CiSE;`olsen2019simulation` 死 DOI + 标题/作者/期/页全错 → 正确版 Olsen & Raunak TR 68(1):91-108;`duqueTorres2023bugornot` DOI 指向 HFCommunity → `...00109`+页 905-912;`raunak2021continuum`/`lin2020exploratory`/`reichert2024hess` 作者/页/期校正;`hiremath` 页。键名 + 首作者姓不变(正文 \cite 与著者-年内联均不受影响)。报告 `docs/review_presubmission/reference_verification.md`。
- **✅ proofread / humanizer / §15 grep+编译 audit → 全清**:全文无拼写语法错、关键数字 Results/Threats/Appendix 三处自洽、符号先定义后用;prose em-dash 0、无 delve/leverage/throat-clearing(仅 1 处合规 "notably");reviewer-speak/process-mark/placeholder/版本叙事/悬空 §X.Y.Z 全 0;0 undefined / 0 multiply-defined / 0 Missing character / 0 overfull>50pt;bib 全引用 33/33;内联枚举各系列一致、`\clearpage`+`\appendix` 正确。
- **✅ §12 IST 合规**:结构化 abstract 五段 296≤300;Highlights 5 条均 ≤85(已抽出单独文件 `paper/ist-submission/highlights.txt`);Keywords 7;Title 7 词;Data avail / CRediT / CoI / GenAI 声明 / Funding(NSFC 12575176 等)全在;wordcount **12158 ≤ 15000**(余 2842)。
- **✅ 参考文献样式切换 elsarticle-harv → elsarticle-num(数字制,用户拍板)**(commit `1eac1a3`):去 `authoryear`、bibstyle 改 num、清 Related Work 手写"(year)";渲染 [1][2]…;372 tests、45pp 全 0。
- **✅ cover letter 初稿**:`paper/ist-submission/cover_letter.md`(突出 novelty + industrial relevance + 诚实 scope;作者信息/建议审稿人留占位)。剩余投稿系统逻辑项:Editorial Manager 元数据、可选 graphical abstract(禁 AI 生成图)。
- **✅ 模拟评审 + 成熟度评估(本会话真实网关 v37+v38 已跑通,见顶部 2026-06-17 网关面板小节;以下为当时 Claude Council 替代记录,已被真实面板超越)**:bltcy 多厂商网关**不可用**(`OPENAI_BASE_URL`/`OPENAI_API_KEY` 未设、历史 key 耗尽,脚本 fail-closed)→ 改跑 §10.9 **Claude Council**(5 角色 EIC/MethRigor/DomainExpert/Perspective/DevilsAdvocate,记录 `research_assets/runs/academic-review-panel-claude-council/`)。结果 overall **7.0** / accept **0.478** / 多数 **major_revision**(3 major/2 minor),与 v36 网关基线(7.37/0.664/同结构)在 **verdict 结构 + clarity 最弱(5.8)** 上一致。评估 `docs/review_presubmission/maturity_assessment.md`:**机制上 submission-ready,科学上 major-revision-ready 边界**(历史天花板,无新 blocker)。可选改进:**P1** 密度手术(C39/C40+OpenMC 降入附录,直击 clarity 绑定约束)/**P2** 加 Spieker 漏引(已核实真实:MET 2024 `10.1145/3679006.3685071` + 同刊 IST 2025 `10.1016/j.infsof.2025.107890`)/**P3** OpenMC "multi-group"→"1-group infinite-medium" 措辞/**P4** precision-recall 描述性标注/**P5** abstract duality 软化。**需真实多厂商面板:提供并轮换网关凭据后重跑 `tools/run_academic_review_panel.py`。**
- **✅ 评审修订轮 P1-P5 + 共识关切全执行**(commits `5cf0d97` + `aee8dad`):**P1**(#1 clarity/dilution)C39+C40 全文移入新 **Appendix B "Cross-program breadth"**,Results 留单句指针 + §4 ref 改指附录;**P2**(#5)加 Spieker 两条(MET 2024 + 同刊 IST 2025,均 crossref 核实)并 cite §2.3;**P3** OpenMC 正文"multi-group"→"single-energy-group infinite medium";**P4**(#4)precision/recall 标注为非独立 checkpoint×seed 描述性率;**P5**(#2)abstract "confirms"→"consistent with a cross-SUT test"(去 overclaim,296 词);#3 airfoil "primary-scale"→"deliberately under-trained gate-discrimination"。**额外修一处历史 bug**:`Appendix~\ref{app:X}` 在 elsarticle 渲染双重"Appendix Appendix",去冗余前缀(连既有 app:claim-evidence)。**同步 `citation_audit.md`**:补登 Spieker + 修正段覆盖 adad46b 修过的 7 条旧 DOI。验证:**372 tests / bib 35-35 / abstract 296 / em-dash 0 / validators rc=0 / 45pp 全 0 / wordcount 12343**。manuscript 修订后仍 submission-ready;如需量化修订收益,提供网关凭据可重跑真实面板对比。

## 🟢 2026-06-17 连贯性终审 + 端到端广度 runbook(GPU 答案)
- **✅ fresh-eyes coherence 审查**(agent 通读全稿):唯一真矛盾 = closest-prior 表把 by-class 当已交付能力、缺限定 → **已修**(caption 加 "(a SUT-specific stress test, not a validated localization model)")。
- **✅ coherence follow-ups 本地已执行(commit 02b49a6 / 63cfd93)**:① duality 去冗(intro novelty 段精简 + abstract Results/Conclusion 去重,~55 词);② §4 subject 列表 + Threats 已补 C39 跨程序语料(OpenMC/wave/PKE);④ 加 tautology 防御(物理有效性谓词≠调参检测,反"检测器测什么抓什么"同义反复指控);⑤ airfoil rollout L2=1.0 "moderate"→"high/low";+ closest-prior 表 caption 加 "(SUT-specific, not a validated localization model)"。44pp / abstract 295 / 总 12725 / 361 tests。
  - **留作可选(你定)**:③ "principle/keystone" bold 词汇(你选的中心论点 framing,保留);§5.7 "Aggregate reading" 段相对位置(flow,重排有破测试风险);§3.6 D-score 五重 hedge(诚实,保留)。
- **✅ 大杠杆 = C40 端到端跨程序(GPU-free)已执行 + 已并(merge `f50b530`)= `paper/46`**。**GPU 答案:不依赖**——P-series 经典解算器纯 numpy、OpenMC 纯 CPU;仅神经 surrogate 需 GPU(已覆盖)。云端在 **E1-E4(heat/wave/PKE/burgers)** 端到端跑通本文 gate+typed-verdict(把 C39 只读复用升级为端到端执行):**33 MR admit / 5 reject / 0 defer 跨 4 SUT;检出 heat 0.75、其余 0.20**;claim **C40**(status observed)+ guard `tests/test_endtoend_pipeline_pseries.py`。本地解决 §4 + Threats 两处 merge 冲突——§4 合为单一 "Cross-program breadth subjects" 组(覆盖 C39 只读 7 类型 + C40 端到端 4 经典,ref 修正 subsec:fault-robustness);Threats 保 coherence 修正 "low surrogate accuracy, L2=1.0" + 采云端更全跨程序句。**验证:371 tests / wordcount 12990≤13050(≤15000 硬限)/ validators rc=0 / §15 grep 全 0 / prose em-dash 0 / abstract 296≤300 / 45pp 0 undefined·0 missing char·0 overfull>50pt**。已 push origin/claude/youthful-feynman-qy22k2。
- **✅ E5 OpenMC 已完成(云端真实跑通)+ 已并(merge `6e1973e`)**:云端用**真实 OpenMC Monte-Carlo k-eigenvalue 解算器**(v0.15.2,multi-group、1-group 无限介质,对照闭式 k∞ 验证)端到端跑通**第 5 程序类型(Monte-Carlo transport)**。C40 现升级为 **5 SUT / 5 程序类型**:gate **38 admit / 7 reject(2 wave+3 PKE+2 OpenMC)/ 0 defer**;检出 0.75 heat·0.20 其余三经典·**0.56 OpenMC**;5/5 结构盲区、映射 program-specific。诚实边界:1-group 无限介质临界 PUT、自生 MGXS、无连续能量/全堆芯/反应堆物理结果;MR+mutant 仍为兄弟仓库资产,仅 gate+verdict 新执行。claim C40 加宽(wording_forbidden 同步:禁"连续能量/全堆芯/反应堆物理")+ guard 升级 + `tools/build_openmc_e5.sh` 可复现脚本 + `endtoend-pseries/PROVENANCE.md`。本地手工解 §4 + Threats(保单一 cross-program 组结构 + 正确 ref subsec:fault-robustness + coherence "low L2=1.0";逗号替云端 prose em-dash)。**验证:372 tests / wordcount 13038≤13050 / validators rc=0 / §15 grep 全 0 / prose em-dash 0 / abstract 296≤300 / 45pp 0 undefined·0 missing char·0 overfull>50pt / §5 机密扫描 0**。已 push origin/claude/youthful-feynman-qy22k2。**至此 C40 端到端跨程序广度全部完成(5 程序类型 × 3 族,含真实生产级 Monte-Carlo 码)。**


## 🟢 2026-06-17 新实验执行(强化"无对比" + "实证广度")
- **✅ Step 1 = C38 互补**:cylinder MGN 上 MR-detection vs rollout-accuracy。harness 加可选 `--with-rollout`(默认关、C10 证据字节不变)。结果:symmetry MR 抓 MA_permute_edges + PC_swap_xy,而它们 rollout error 仅 1.3× baseline(0.0216,< 2× 阈值)——**MR 抓 accuracy 漏的关系违背**;互补非优越。commit `374355c`。
- **✅ Step 2 = C39 跨程序泛化**:读兄弟仓库**已提交 kill matrix**(只读、零重训),在 **7 程序类型 × 3 族**(神经 surrogate / 经典解算器 wave·PKE·Burgers / 生产码 OpenMC)测 coverage-geometry。6/7 有结构盲区、映射 program-specific(SUT-specificity 从 2→7)、检出率 10-100% 随 MR 集变。诚实:非端到端跑 pipeline。fixtures + PROVENANCE + 分析脚本 + 守卫。commit `fed25d9`。
- **✅ 正文集成**:seeded-fault 段加 C38 互补句;falsifiable 段后加 "Cross-program generalization" 段(C39)。buffer 12650→12750、43pp、**361 tests**、§15 复审干净(em-dash 0/reviewer-speak 0)。commit `4f3538f`。
- 计划文档 `paper/45`(已执行)。



## 🟢 2026-06-17 deep-research 评审 + R2-1 跨-SUT（诚实负结果）
- **✅ paper/41 评审**：deep-research（paper-search-mcp）+ §10/§11 结构化 + Reviewer-2。3 篇 closest-prior crossref 核实、novelty gap 真实、3 处漏引（ying2025 同刊 / najafi2026 物理一致性 / Eniser k-safety）。裁决 borderline minor/major，R2-1 为唯一 blocker。commit `ba2a220`。
- **✅ R2-1 策略 (a) 执行 → 诚实负结果**：在第二 SUT（primary-scale airfoil，5 轨）复刻 seeded-fault。**by-class 模式 SUT-specific**：仅 NS_skip_denorm 跨 5 轨稳健；mirror-y domain-inadmissible（gate 排除）；BC/MA/PC/sign 全测不到；跨 SUT 唯一共享=continuity→归一化。新建 harness + **C36** + 多轨 ledger + 5 断言守卫；6 处正文重构；buffer 11800→12100。347 tests / 41pp / 0 undefined。commit `f002c80`。
- **✅ P1/P2 文献**：najafi2026（L173 物理一致性对比）+ ying2025（L129 同刊 MT4ML）。crossref 核验 + citation_audit 入账。
- **📋 response-letter 草稿**：`paper/42_response_to_simulated_review.md`（R2-1 已解 + P1/P2 + 剩余 R2-2/2-3/2-4）。

## ✅ 提升 suggestive 卖点 → validity–coverage 二象性中心论点（已完成）
- **结果（两步落地）**：① coverage-geometry 正文升级（`b624425`）；② 按用户"全力·中心论点"指示升为**中心论点 validity–coverage duality**——abstract+intro+§Results 重构、新增 "Falsifiable predictions, and what would refute them" 段、claim **C37**（status qualified，许"提出+确证"、封"validated quantitative model"）、airfoil 从"SUT-specific 限制"重构为 **keystone 确证实验**（`e1ef055`）。诚实 pins 全留、abstract≤300、buffer 12300→12500、**352 tests 绿**、42pp。
- **用户方法论纠正（已内化）**：诚实≠防守;最有勇气的姿态是 Popper 式"提强命题+用证据辩护+划边界+主动递靶子"。"实事求是"约束的是"不超出证据",不是"不敢下判断"。
- **剩余 review 项**：✅ 全部已解。R2-3 跨类校准——在诚实边界内把模糊"future work"升级为**具体 recipe**(按各类 admissibility 边界归一→D_cal=1),C15 禁止项 + 三条 pin 句逐字保留,不 overclaim;R2-4 highlight 的 O(h) 过度概括已 scope 到 divergence。paper/41 五项(R2-1~R2-4 + P1/P2)全部 ADDRESSED。

### （存档）原始 coverage-geometry 思路
- **思路（诚实升级，非 overclaim）**：把"by-class 定位（suggestive，SUT-specific）"升级为 **coverage-geometry 原理**——*故障被检出 ⟺ 它扰动某个 admissible MR 所测的不变量；admissibility gate 因此预测 detector 套件的盲区*。
- **已有 4 条独立证据支撑**（2 条是可证伪的已确认预测）：R1 K=6 跨-checkpoint 复现 / **R3 knife-edge**（PC_zero_vy 在 p=1.0 同时 permutation-invariant + mirror-symmetric 时检测精确坍塌）/ R4 adversarial（盲区=子空间）/ **C36 跨-SUT**（移除 inadmissible 的 mirror-y 恰好移除其覆盖）。
- **动作**：把现埋在 §Results 的 coverage-geometry 句提为一级贡献/卖点；abstract+contributions+novelty 以"gate 不仅 type verdict，还预测 detector 覆盖与盲区，经 knife-edge + 跨-SUT 两个可证伪预测确认"为主线。**不新增实验**（复用 R1/R3/R4/C36）。**风险**：动 contributions/abstract framing，先给具体改写方案再落。

## 🟢 2026-06-16 本地会话（teleport）小结
- **✅ DOI→concept**：Zenodo v1.1.0 已发布；`CITATION.cff` + `main.tex` Data-availability 改引 **concept DOI 10.5281/zenodo.20702952**（始终指向最新版），弃用 version DOI ...953。commit `5f5b370`。
- **✅ clarity + humanizer**：em-dash 全清（main.tex 16→0；manuscript.md 41 散文行，表格内保留）；OOD 首用定义 + K=6 加注"(six checkpoints)"；itemize 三层级长句；R1 缺陷检测段去密度（数字全留）。337 tests / 40pp / IST 11,438。commits `5f5b370`+`8ef1ba6`。
- **✅ 面板 v34/v35（OpenAI 兼容网关）**：v34=7.49/major(5人)；v35=7.64/minor(4人,kimi 502 掉线)；**clarity 6.6→6.25 未升**（噪声+缺一人）。commit `197a30a`。诚实结论：散文/结构杠杆基本用尽（Tier1 表述正文已写过；Tier2 防御性 caveat 被 `test_stage2p5` pin、删不得）。
- **📋 计划文档**：`docs/superpowers/plans/2026-06-16-clarity-density-revision.md` + `2026-06-16-substantive-strengthening-plan.md`（reviewer 共识 5 项+根因+修复）。

## 🟡 批次 2 = Tier 3 airfoil 主级轮（治 5/5 single-task；用户授权本地 Metal）
- **可行性 ✓**：deps(torch/torch_geometric/physicsnemo/tfrecord)+MPS=True；`~/.cache/dvgmr/airfoil_staged/` 已暂存 6 train+10 test(771MB)+K=6 ckpt；数据源 `gs://dm-meshgraphnets/airfoil`（runner range-download；补更多轨迹需 GCS+dangerouslyDisableSandbox）。bounded C31=172s（但 2-epoch 玩具、rollout L2=2.66）。
- **🔴 拦路点**：`run_physicsnemo_mgn_airfoil_workflow.py` 的 `OUT_DIR` **硬编码到 C31 已提交目录**、无 `--out`；`test_physicsnemo_airfoil_workflow` pin 了 C31 bounded 值 → 放大跑会**覆盖 C31+破测试**。须先：(1) runner 加 `--out`/新目录 `physicsnemo-mgn-airfoil-primary-roster`、(2) 新 ledger 条目(C35)、(3) 新测试，再跑(下载+训练)+整合正文。
- **🔵 待拍板**：主级规模 n_train/n_test/epochs（乘性成本：hidden128/proc15≈9h；n_train20/n_test30/epochs10/hidden64≈47min+~2.5GB 下载）。

## 🟢 增量② 云端执行结果（C34 经典算子-代码可执行守恒；正文撤下，工具/产物留仓库）

> 执行方案 `paper/40_increment2_cloud_execution_plan.md`，分支 `claude/youthful-feynman-qy22k2`。

- **工具真实跑通**：`tools/run_classical_operator_conservation.py` →
  baseline `|dM|max=2.22e-16` PASS；3/3 算子代码缺陷检出（FAIL）：迎风原始变量非守恒
  `1.78e-3`、漏界面通量 `2.34e-2`、重复通量 `1.00`。确定性（除 `generated_at` 逐字节一致）。
  产物 `research_assets/runs/classical-operator-conservation/raw/metric_ledger.json`。
- **诚实修正（守铁律，不动 tol）**：paper/39 §4 原拟的**中心**平流非守恒形式在周期边界下
  `Σu_i(u_{i+1}-u_{i-1})≡0`，恰好守恒一阶矩（实测 |dM|=舍入级，**未检出**）。按"只修缺陷构造、
  不动 tol"改为**迎风原始变量平流** `u_i(u_i-u_{i-1})/Δx`（同为真实非守恒 CFD bug），真实丢质量。
  已在工具注释与 paper/39 §4 记录。`CONS_TOL=1e-12` 未动。
- **claim C34 入账**（真实数字）；guard `tests/test_classical_operator_conservation.py` skip→PASS；
  `pytest` 313 全绿；两 validator exit 0。
- **用户中途指示（本会话）**：以 **LaTeX (main.tex) 为唯一文档**，不再 md/tex 双维护；
  **评审面板目标改为 main.tex**（`tools/run_academic_review_panel.py` 的 `PAPER`）。
  → manuscript.md 已回退至 HEAD（冻结/弃用，不再同步）。
- **v29 三方对照面板（均经网关真实跑出，温度0）**：
  | | v28(md,无增量) | 对照(tex,无增量) | v29(tex,+增量) |
  |---|---:|---:|---:|
  | overall | 7.89 | **7.49** | **7.31** |
  | accept | 0.664 | 0.634 | 0.60 |
  | clarity | 7.4 | 6.8 | 6.2 |
  产物：`research_assets/runs/academic-review-panel-v29/`、`.../academic-review-panel-v29-control-pretex/`。
- **判读（实事求是）**：
  - md→tex 格式切换独立造成 overall **-0.40**（评审读原始 LaTeX：clarity/reproducibility/
    related_work 下滑，参考文献在 .bbl 不内联、`\ref` 未解析）——格式伪信号。
  - 增量净效应（对照→v29，同 tex）= overall **-0.18**、accept -0.034、**clarity -0.6**，仅 scope +0.2。
  - 守恒 major：v28 由 glm(major)+kimi 提出；但**对照（无增量）中也已 0/5 消失**——故 v29 守恒关切
    缺席**不能归因于增量**（格式/噪声所致）。增量无可证收益、且净负向。
  - **结论=撤下正文新增**（plan 纪律"仅加长无收益/回退→撤下"）：main.tex 仅在 §5.6 留**一句**
    "经典算子上守恒 MR 可执行（指向 C34）"作 backup；§4.1/§5.5.1/§3.2/§6.1 等完整集成已撤。
    C34 工具/产物/claim/guard 留仓库作 **revision 备用证据**（类比 C33 覆盖几何处置）。
- **遗留**：(1) `main.pdf` 未重编译（容器无 texlive；源为准，投稿前 `apt-get install texlive-*` 重编）；
  (2) 同步守卫 `test_stage2p5`/`test_phase8` 仍要求 md+tex 双含锚点——md 冻结后它们靠 md@HEAD 通过，
  建议后续重构为 **tex-only**（单文档化的收尾，本会话未改测试以免越界）。

---

## 🟡 进行中：密度优先手术（plan paper/40 Part A；打 v29 readability 5/5）

> 依据：v29 五评审 5/5 提 density/overextended（最被反复提、且是面板 score 绑定约束）；
> 加 SUT 反伤 EIC（已两次实证：airfoil −0.4、C34 撤）。故砍散文密度优先。
> 锚点纪律：守卫逐文件钉 main.tex 的 token 逐字保（combined/md-only 的因 md 冻结安全）；
> §6.4/§6.9 honesty 声明当证据保，不当对冲删。

- **A1 已做（本次 commit）**：删 §Fault-robustness 孤儿 Wilson-CI 表（无 \ref、零守卫、
  逐行复述 R1）+ R2 三机制括号并一句。IST 11787→11355（−432，float 12→10）；证据零损失
  （CI 仍在 R1 散文 + metric_ledger）。pytest 313 全绿、两 validator exit 0。
- **A2 至地板**：原拟 −80，实得 −3（仅一处 filler）；其余经核为 §6.4/§6.9 honesty，保留不删。
- **A3 = N/A（实测）**：§Claim-to-evidence（L337）几乎全是被 \ref 的 21 行 ledger 表 + 1 句散文，
  无"散文复述表格"可删（先前 587w 误把表行文本计入）；表是核心证据 ledger，删行=删 claim，不可动。
- **A5 已做（−41w）**：删 Results-intro 子节指引句（throat-clearing）+ §Boundary-of-evidence 冗余
  第二句（其"comparators=诊断/audit=次要/executions widen within rosters"在 Threats+Results-intro 已有）；
  含 `canonical blocked`（1 守卫）的 blocked-list 句保留。
- **关键 meta-finding（实事求是）**：正文散文密度已近"守卫+honesty 地板"——回归守卫逐字钉了多数证据
  散文，§6.4/§6.9 钉了 caveat，prose-only 去密空间已尽。A1 删孤儿 float（−432）是本轮唯一大净 win；
  v29 的 5/5 readability **不能靠再砍散文解决**。
- **(a) 已做 + 编译验证**：移 21 行 claim-evidence 大表 → 新建 `\appendix`（Appendix A，表 A1），
  子节留指针（守卫要求的 `\subsection{Claim-to-evidence map}` 标题保留）。**本地 xelatex/pdflatex 全循环
  编译通过**：39 页、undefined refs=0、Missing character=0、LaTeX Error=0、bibtex 全解析、无 >50pt Overfull。
  同时清掉"main.pdf 未重编译"遗留（byproduct main.pdf/bbl/log 工作树重生，未提交）。
  踩坑记录：`re.sub` 替换串会解释 `\r`/`\t`，写指针时致 `\ref`/`\texttt` 损坏，已改 str 切片修复（见 PITFALLS 候选）。
- **(b) 已做**：Part B FNO(C23) co-primary reframe —— abstract Results 把 FNO 升格为"second PDE family
  full admit/reject/execute"、Conclusion "Within-architecture-family" → "spanning two CFD tasks and a
  second PDE family"、intro L85 broaden（airfoil + FNO/PINN）。把 abstract headline 对齐正文**已有** scope
  （Threats 早写 "two CFD tasks on two official datasets"），非灌水。abstract trim 回 ≤300 词、保留锁定句
  （second CFD task / Broader generalization is future work / machine precision / non-regression guard）、
  编译 undefined/Missing/Error=0、313 全绿。打 4/5 单任务 + 软化 3/5 novelty。
- **✅ 已修（预存版面 bug）**：两张超大表（MR-card-to-verdict、claim-evidence）转 `xltabular` 分页
  （加载 `xltabular` 包；`Y`=tabularx `X` 列，xltabular 原生支持）；"OOD/conservation" 加 `\allowbreak`
  清 3.93pt 单元 overfull。**完整编译循环全 0**：Overfull=0 / Float-too-large=0 / undefined=0 /
  Missing=0 / LaTeX Error=0（40 页）。`test_stage4` 现在在**新鲜干净 main.log** 上诚实通过、313 全绿；
  守卫字面量（`\small` / `tabcolsep 3pt`）保留。
- **✅ byproduct 治理（commit 0879cc2）**：`.bbl`/`.log` 已 gitignore + `git rm --cached`；fresh main.pdf
  （40pp）保留跟踪并提交（已扫无 `/Users` 路径）。ist-submission 现只跟踪 main.pdf + 源图。
- **✅ v30 面板（本会话改动的同基线验证，均读 main.tex）= overall 7.40 / accept 0.636 / clarity 6.8 /
  scope 8.6 / majority major(3:2)**。vs v29(7.31)：**clarity +0.60（6.2→6.8）是唯一移动维度**，overall
  的 +0.09 几乎全来自它 —— 去密（Part A + 移表）真有效、坐实"密度是绑定约束"；MethodologyRigor accept
  0.65→0.85。**B（abstract 双任务 reframe）面板净中性**：scope_match 8.6→8.6、novelty 6.8→6.8 纹丝不动
  （诚实负结果；framing 价值在真人外部效度观感，不在模拟面板）。产物 `research_assets/runs/academic-review-panel-v30/`。
- **天花板结论**：3 个 major（EIC/DomainExpert/DevilsAdvocate）卡在 prose/framing 改不动的硬伤——增量性(3/5)、
  单族窄经验(3/5)、缺陷目录薄、可复现(DOI/容器)。唯一不加篇幅又命中 major 的杠杆 = **DevilsAdvocate 可复现**
  （Zenodo DOI + 容器化复现包，§13/§14）。其余需真实新证据，与篇幅/密度冲突（airfoil −0.4、增量② 撤 两次实证）。
- **✅ 可复现包第一增量（闭 DevilsAdvocate 可复现关切）**：新建 `CITATION.cff`（DOI 占位待 Zenodo）、`LICENSE`
  （MIT，§13.6）、`requirements.txt`（可验证档 numpy/pyyaml pin + SUT 档注记）、`REPRODUCIBILITY.md`（三档
  smoke/cache-replay/full）、`Dockerfile`+`.dockerignore`（容器跑 compile-independent CI 子集）。容器 CMD 内容
  本地实跑全绿（CI 子集 82 tests OK + 两 validator 0）；docker daemon 未运行，镜像本地未实测构建。
- **test_stage4 × gitignore 冲突 → 选 (d) 文档化（用户拍板）**：不改测试、不重新跟踪 byproduct；README +
  REPRODUCIBILITY 注明"干净 clone 跑整套前须先编译生成 bbl/log，否则 test_stage4 那一条报错"。**CI 不受影响**
  （实测 `validate.yml` 只跑 compile-independent 子集、不含 test_stage4）。
- **可复现包收尾（✅ 完成）**：Zenodo 已归档，DOI=`10.5281/zenodo.20702953`；已回填 `CITATION.cff` 的 `doi:` + 论文 Data-availability（`\url{https://doi.org/10.5281/zenodo.20702953}`，重编译 undefined/Missing/Overfull=0、pytest 313）；✅ `docker build` 已实测：关 Docker 手动代理 + daocloud 镜像源后镜像构建成功，容器跑 CI 子集 **82 tests OK + 两 validator exit 0**（image `dvg-mr-sciml:latest`）。根因记录：Docker 的 HTTPS 代理被写成 `https://…:7890`（对明文代理做 TLS→EOF），且 7890 链路对 Docker 不通；关代理后直连/镜像即通。
- **✅ v31 面板（DOI 回填后）= overall 7.83 / accept 0.694 / majority minor(2:3，翻盘)**。vs v30(7.40)：**reproducibility +1.60(7.2→8.8) 是真信号**——DevilsAdvocate 的"no DOI/container/promised-upon-acceptance"关切在 v31 消失(可复现包 + DOI 命中)。**但** related_work+0.6 / scope+0.4 / novelty+0.2 / technical+0.2 及 DomainExpert major→minor 与单行 Data-availability 改动无关 = 面板 run-to-run 噪声。诚实读：repro 真升、DevilsAdvocate 真软化；+0.43/翻盘**部分是噪声**，论文处于 minor/major 噪声边界(同 v18=7.83)。剩余天花板未动：增量性(EIC/DA/DomainExpert)、密度(EIC/MethRigor)、单任务(EIC/MethRigor/DA/Perspective)、缺陷目录薄、D 未校准。2 个 major=EIC(0.62)、MethRigor(0.55)。产物 `research_assets/runs/academic-review-panel-v31/`。
- **✅ v32 确认轮(与 v31 同稿,纯噪声测试)= overall 7.74 / accept 0.656 / majority major(3:2)**。三轮 v30/v31/v32:**reproducibility 7.2 / 8.8 / 8.6 —— DOI+可复现包的增益真实且稳定(已确认)**;但 **v31 的"翻盘 minor"未复现**:overall 7.40/7.83/7.74、majority major/minor/major、DevilsAdvocate major/minor/major —— v31 的 minor 是幸运 roll。**真状态:overall ~7.7-7.8、accept ~0.65-0.69、majority major、处 minor/major 边界偏 major(3 轮 2 次 major)**;EIC+MethRigor 两轮恒 major(0.6-0.68)。repro 已成确认强项,其余天花板(增量/密度/单任务/目录薄/D 未校准)未动。产物 `research_assets/runs/academic-review-panel-v32/`。
- **🟢 选项2-A:FNO roster 功效深化(TDD + sonnet workflow/agent 提效)**——回应"FNO 跨家族 n=3 欠功效"。设计 workflow(sonnet 并行 A/B 设计 + 对抗审查)**抓出**原拟的跨 PDE Wilcoxon 是"幅值差伪装可靠性检验"(已弃,§10.3)。执行:`run_fno_k6_roster` SEEDS[0,1,2]→range(15) + per-PDE Wilson CI;**真实数:平移 30/30 admitted、各 PDE 15/15、Wilson 95% CI [0.796,1.0]**(原 n=3 为 [0.44,1.0])。TDD 守卫 `test_fno_deepened_roster` + `test_fno_roster_prose_binding`;C19 ledger + main.tex §FNO 同步(真实均值/CI)。**未动 C23 workflow(24/24 保留作执行证据)**——避免 md-冻结跨文件守卫 churn,roster 的 n=15 已是充分的功效答案。318 passed、编译 0 错、两 validator 0、IST 11453(headroom 3547)。
- **🟡 选项2-B:airfoil 延后**——对抗审查判本地不可行(隔夜 + `/workspace` 路径 + ~2.5GB 下载)且未必实质解单任务;留你 GPU/云。PINN 的 p=0.5(C16)同属欠功效,可用同法(`run_pinn_k6_roster`)深化,待定。

---

## 🟡 进行中：方案 B（airfoil 进正文）+ 聚焦压缩（用户拍板，本会话）

- **决策已定**：用户选 B —— airfoil 进正文（main.tex §445 与 manuscript.md §5.4.1 均已含），
  目标把 airfoil 版密度压回 v18 紧度以追回篇幅惩罚分。
- **本会话已做（manuscript.md，面板复评读此文件）**：12329→11944 词（削 385）；
  固定论点不漂移、未改任何数字、数字前缀术语集不变、295 测试全绿。手术点：
  §2.7 novelty run-on 去膨胀（290→165 词）、§6.2 去 3× "must not claim" 重复、
  §5.4 去 §4.1 roster 复述、§5.3 各 bullet 去嵌套对冲、§5.1 表 4 个最长 Boundary 单元、
  §2.4 去过程性叙事("our debates could not pre-empt")、§2.1/2.5/2.6 背景去 throat-clearing。
  pinned 锚点（[0.69,1.00]、calibrated in-distribution magnitude 等）逐字保留。
- **面板复评结果（用户提供网关凭据后跑）**：
  - v23（第一轮压缩）：overall 7.60、accept 0.636、clarity 7.0、**major→minor**（真实增益）。
  - v24（第二轮压缩）：overall 7.54、clarity 6.4——平台/噪声，EIC+MethodologyRigor clarity 仍卡 6，
    坐实"prose-only 已到天花板"。
  - **结论**：压缩第一轮有效（v22 7.43→v23 7.60，保住 airfoil 同时达 minor），第二轮平台。

- **C32 实质增强（measurement-floor 解析地板界，本会话 Phase 21）**：
  - 回应 DevilsAdvocate/EIC/DomainExpert 核心技术质疑"O(h) 扫描只验证斜率不验证绝对地板"。
  - 推导：P1 散度算子对仿射场精确 + 解析场 div≡0 ⇒ 测得地板 = 二阶 Lagrange 余项的几何加权和（精确）。
  - 闭式预测（格心 Hessian）在部署网格 h0 匹配测得地板到 0.5%（1.337 vs 1.343，ratio 0.996），
    细化后 ratio→1.000；严格 a-priori 上界（Hessian 全局谱范数）RMS+pointwise 全 dominate。
  - 产物 `research_assets/runs/operator-floor-analytic-bound/`、工具 `tools/run_operator_floor_analytic_bound.py`、
    claim **C32**、guard `tests/test_operator_floor_analytic_bound.py`（302 测试全绿）。
  - 正文集成：§5.5 新段 + §1.2/§2.4 措辞从"经验估计/future work"改为"具体网格闭式"，main.tex 同步。
  - 诚实边界：仅该结构网格 + 解析场；任意非结构网格的一般界仍 future work。
  - **待办**：跑 v25 面板验证 C32 是否抬 technical_soundness/clarity（凭据在手）。

- **Phase 21 续（已 commit ad70ff3：压缩两轮 + C32）**。

- **(a) §5.1 表格结构性瘦身（已做）**：21 行 ledger 表拆为正文 9 行 headline（无文件路径）
  + Appendix A 完整表。直击 EIC/DomainExpert"artifact references obscure contribution"。
  - **v26 = overall 7.80**（v25 7.60→7.80，clarity 7.0→7.2，accept 0.668）：**airfoil 版追平
    v18 峰值 7.83，且保住 airfoil**。表格瘦身真实有效。

- **(b) B1+B2 扩展缺陷目录 + 真实 bug 见证（C33，已做）**：
  - B1：11 个真实分级工程缺陷注入真实 MeshGraphNet 前向（图构造/归一化/边特征/输出尺度/符号/timestep）。
  - B2：重建 PhysicsNeMo `VortexSheddingDataset.__getitem__` 原地改图真实 bug（doc 37），
    **被 node-perm MR 捕获**（rel L2 1.44）。
  - 诚实结果：11 个真实缺陷只检出 3（union 3/11，Wilson [0.10,0.57]）——均匀幅值缺陷被结构性漏掉。
    框定为"MR 是**结构检测器**"而非灌水 recall（未调阈值，守 §10.3）。目录总量 60→71。
  - 工具 `tools/run_seeded_fault_catalog_v2.py`、产物 `research_assets/runs/seeded-fault-catalog-v2/`、
    claim **C33**、guard `tests/test_seeded_fault_catalog_v2.py`（308 测试全绿）。
  - phase4 clarity buffer 按既定政策 11800→12000（C32+C33 load-bearing；真实上限 15000，余量 3192）。
  - **待办**：v27 面板验证 C33 是否撬动 5/5"目录薄"关切（凭据在手，本地真实 SUT 可跑：
    `PYTHONPATH=../最小完备MR子集/scripts` + torch 2.12）。

- **未 commit**：(a)+(b) 改动停在工作树（commit ad70ff3 之后的新改动）。

## 🚚 本地迁移备忘（在本地继续前先看这段）

**仓库状态**：单一 `main` 分支（2026-06-17 投稿工作已全部并入 main、feature/codex 分支已清理删除），本地=远端完全同步，
工作树干净。最新 commit 见 `git log -1`。

**1. 拉取分支**
```
git fetch origin main
git checkout main
git pull origin main
```

**2. 本地需要重装的依赖**（容器临时装的，不在 git 里）
```
# 仅跑测试只需 torch：
pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision
# 复跑 PhysicsNeMo 工作流（圆柱 scaled / 翼型 airfoil）还需要：
pip install --ignore-installed packaging nvidia-physicsnemo==2.1.1 torch_geometric tfrecord
pip install torch_scatter
# 重编译投稿 PDF：
#   apt-get install -y texlive-latex-extra texlive-bibtex-extra
```

**3. 不在 git 里、需要时自动重下的数据**（按设计放仓库外，约 1–2 GB）
- 圆柱：`tools/run_physicsnemo_mgn_scaled_workflow.py` 自动从官方 DeepMind 数据集
  ranged 下载到 `STAGE_DIR`（常量在文件顶部，本地可改）。
- 翼型：`tools/run_physicsnemo_mgn_airfoil_workflow.py` 同样自动 staging。

**4. 评审面板凭据**（跑 `tools/run_academic_review_panel.py` 才需要）
```
export OPENAI_BASE_URL="<GATEWAY_BASE_URL>"   # OpenAI-compatible gateway
export OPENAI_API_KEY="<gateway key>"     # 不要提交进仓库
```

**5. 验证迁移成功**
```
python -m pytest tests -q        # 应 295 passed
```

## 📌 当前最佳投稿稿件 = v18 版

- **最佳面板分稿件 prose = commit `9446634` 恢复的状态**：overall 7.83、四项
  Phase-5 门槛全过、accept≈0.69。
- 之后加的 airfoil 第二任务（commit `d2f8000` / `ece58bd`）+ 精简（`d333125`）
  是**真实证据**，但面板因篇幅惩罚降到 **v22 = 7.43**（详见下方轨迹与提交信息）。
- **待用户拍板的最后一步**：投稿稿件要不要含 airfoil。
  - 方案 A（推荐）：用 v18 prose 投，airfoil 留作仓库支撑证据、不进正文。
  - 方案 B：含 airfoil 进正文（真实科学更强、外部有效性更好，面板分 7.43）。

## 🔬 真正提升质量的四件事（对真人审稿人，不只追面板分）

按性价比排序，来自 v21/v22 评审里**真实有意义**的意见：
1. **狠砍对冲和篇幅**（EIC/glm 一致："过长、重复、对冲把贡献埋了"）——纯写作。
2. **把测量地板 measurement-floor 从"经验估计"做到"解析推导"一个具体网格的
   绝对地板界**（DomainExpert/kimi："O(h) 扫描只验证斜率不验证绝对地板"）——
   直接强化最核心的新颖点。
3. **D-score 域违反轴做跨 MR 类校准**（3 位提："二维判决核心思想仍未校准"）。
4. **更大 / 更真实的缺陷目录**（4 位提："10 个合成粗暴缺陷太薄"）。

被判定为面板伪信号 / 意义较弱的：分数本身的 ±0.3 噪声、"无 DOI/非开箱即用复现"
（已承诺录用时 Zenodo 归档）、"新颖性是组织性的"（魔鬼代言人角色设定）、
"未对比人类专家"（论文已明确限定为 LLM 模拟专家）。

## 📈 完整 post-gate 量分轨迹（同一套门槛）

| 版本 | overall | accept | clarity | empirical | 裁决 | 说明 |
|---|---:|---:|---:|---:|---|---|
| **v18（精简,无airfoil）** | **7.83** | **0.686** | **7.2** | **8.0** | 4min/1maj | ✅四门槛全过=峰值 |
| v20（≈v18 复核） | 7.74 | 0.676 | 7.0 | 8.0 | 3maj/2min | 噪声边界复核 |
| v19（+novelty 重写） | 7.54 | 0.548 | 6.4 | 7.2 | 4maj/1min | 已回退 |
| v21（+airfoil） | 7.37 | 0.590 | 6.4 | 7.4 | 1rej/1maj/3min | |
| v22（+airfoil+精简） | 7.43 | 0.558 | 6.6 | 7.0 | 4maj/1min | 精简只追回一小部分 |

**结论：面板的约束是篇幅/密度，不是缺证据。v18 是峰值稿件。**

---

## 🎯 里程碑：Phase-5 四项门槛全部达标（v18，2026-06-12）

| 维度 | v16 | v17 | v18 | v19(B轮,已回退) | 门槛 | 状态 |
|---|---:|---:|---:|---:|---:|:--:|
| overall | 7.31 | 7.66 | **7.83** | 7.54 | ≥7.8 | ✅(v18) |
| accept | 0.572 | 0.666 | **0.686** | 0.548 | ≥0.65 | ✅(v18) |
| clarity | 6.0 | 7.0 | **7.2** | 6.4 | ≥7.0 | ✅(v18) |
| empirical | 7.2 | 7.6 | **8.0** | 7.2 | ≥8.0 | ✅(v18) |
| novelty | 6.8 | 7.0 | 7.2 | 7.4 | — | — |

裁决 v18: 4×minor/1×major。**B 轮（v19，commit 486fa1b）尝试用 novelty 重定位
再加码，结果四项门槛全回退、裁决翻成多数 major**：novelty +0.2（噪声内），
但加长的"类别区分"论证段拉低 clarity（EIC/kimi 给 5），且把理论 distinction
拉满反招"floor 实为经验估计"的反击。已 revert 到 v18 达标 prose（commit
9446634），保留 v19 报告为证据。
**结论坐实：prose-only 加码已到天花板（32/34 号文档预判），门槛是被
PhysicsNeMo 规模化实证 + v17 clarity 工作清掉的，不是 prose 挤出来的。**

## 🟡 待用户拍板：是否投稿
当前 HEAD 稿件 = v18 达标版（overall 7.83、四项全过、accept≈0.69）。建议：
- A（推荐）：按当前稿件走投稿流水线投 IST，预期 minor revision
- B 已验证为负收益，不再重试 prose 加码

## 🟢 Backlog（投稿前可选项）
- [ ] v18 残余共性意见（非门槛阻塞，可在 minor-revision 阶段回应）：
  单任务外部效度（5/5 仍提）、D-score 跨类未校准（3/5）、seeded-fault
  目录合成粗粒度（4/5）、glm 建议正文再压缩 30–40%
- [ ] P2: Zenodo DOI（稿件已承诺 acceptance 时归档）

## ✅ Done（本会话 2026-06-12/13）
- [x] 环境恢复 + 286 测试全绿；D-score 时间戳污染修复（73025e9）
- [x] Phase 17 clarity 手术 + 新颖性重定位（9de2d9d, ac3c856）
- [x] PhysicsNeMo smoke→scaled 官方架构工作流（25+40 官方轨迹，node-perm
  40/40 精确、mirror 40/40 OOD）+ C30 claim + 数据管道 bug 修复（8903e71）
- [x] v17 panel（7.66）+ triage（守恒 deferral 重构、跨家族整合、caveat
  去重）（bf8aca6, 9c047e6）
- [x] v18 panel：四项门槛全过（036ff5d）

## 📌 历史 provenance（守卫钉死，勿删）
- P0c Task 3 minimal Object-A smoke workflow 已完成（smoke 子集，已被 scaled
  工作流取代为主要证据，但 smoke 产物与 claim 仍保留）；full-scale Object-A
  与 Task 4-5 仍 blocked。
- P0c Task 2.8 complete DeepMind TFRecord staging 已记录。
