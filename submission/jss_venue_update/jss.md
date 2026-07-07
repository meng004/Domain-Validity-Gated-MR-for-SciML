# venues/jss.md — Journal of Systems and Software

> 投稿/改稿前先读本文件，再跑模板目录中的 `precheck_jss.py` 与项目验证脚本。
> 期刊全称：Journal of Systems and Software（JSS）
> 出版商：Elsevier
> 同行评审：**单盲（single-anonymized）**——审稿人看得到作者，作者看不到审稿人
> 投稿系统：**Editorial Manager** — https://www.editorialmanager.com/jss/

---

## 信源（all from 官方）

- ScienceDirect《Guide for Authors — Journal of Systems and Software》
- Elsevier LaTeX instructions（elsarticle）
- Elsevier Highlights / CRediT / Declaration of Competing Interest / Generative-AI 政策页
- 官方模板分发：Elsevier `elsarticle` template package / CTAN `elsarticle`
- 核对日期：2026-07-04

---

## 官方投稿模板（落地 `venues/templates/jss/`）

| 文件 | 说明 |
|---|---|
| `elsarticle.cls` | Elsevier `elsarticle` 类文件；与 IST 模板共用官方 v3.5 系列 |
| `elsarticle-num.bst` | 数字制参考文献 BibTeX 样式 |
| `elsarticle-template-num.tex` | 官方数字制范例稿，供新稿起步 |
| `elsarticle.dtx` / `elsarticle.ins` | 类文件源，可重生 `.cls` |
| `doc/elsdoc.pdf` | 官方使用文档 |
| `elsarticle-official-v3.5.zip` | 官方原始包存档 |
| `main.tex` | JSS regular-paper 项目模板 |
| `precheck_jss.py` | JSS 投稿前硬性检查脚本 |

> 新论文复用：`\documentclass[preprint,12pt]{elsarticle}` + `\journal{Journal of Systems and Software}` + `\bibliographystyle{elsarticle-num}`。
> Elsevier LaTeX instructions 明确提醒：Editorial Manager 不能处理带子文件夹的 LaTeX source。最终 source zip 应把 `main.tex`、`.bib`、`.bbl`、`.cls`、`.bst`、figure 文件放在同一层级，并同步去掉 `figures/...` 路径。

---

## 1. 范围与证据契约

JSS publishes papers covering all aspects of software engineering. 官方要求所有文章必须用证据支持 claims，证据类型可以是 empirical studies、simulation、formal proofs 或 other validation。

当前与软件测试 / SciML 论文最相关的范围项：

- software requirements, design, architecture, verification and validation, testing, maintenance and evolution;
- AI, data analytics and big data applied in software engineering;
- Software Engineering for AI systems;
- methods and tools for empirical software engineering research.

**写作原则：**首屏必须让编辑快速看到：软件工程问题是什么、贡献是什么、证据类型是什么、哪些 inference 被允许、哪些不被允许。

---

## 2. 字数、页数与字符约束

| 项 | 约束 | 备注 |
|---|---|---|
| Title | 官方无硬上限 | concise and informative；尽量避免缩写和公式 |
| **Abstract** | **≤ 250 词** | concise, factual, standalone；通常避免引用 |
| Highlights | **必须单独 editable file；3–5 条，每条 ≤ 85 字符（含空格）** | 文件名含 `highlights` |
| Keywords | **1–7 个 English keywords** | 尽量避免长词组；少用非通用缩写 |
| Length | 建议 full-length paper **<36 页 single-column 或 <18 页 double-column** | 超过需在投稿中解释合理性；这是 recommendation，不是硬 word cap |
| References | 官方无固定条数上限 | 正文引用与参考文献必须互相对应 |
| Figures | 单独提供图文件；矢量图优先 PDF/EPS | 所有图必须正文引用 |

---

## 3. Abstract 风格

JSS abstract 不要求 IST 那种强制结构化标签。要求是：

- concise and factual；
- ≤250 words；
- able to stand alone；
- state purpose, principal results, and major conclusions；
- avoid references；
- avoid non-standard/uncommon abbreviations unless defined at first mention.

项目自检按禁止处理：摘要内出现 `\cite`、`\ref`、未定义缩写、超过 250 词。

---

## 4. 参考文献格式

- JSS Guide 不强制初投稿参考文献样式，但要求格式一致、信息完整。
- LaTeX 模板建议使用 `elsarticle-num`，投稿包保持数字制。
- 数据、软件、代码、模型、notebooks 应按软件/数据引用原则引用：creator、title、repository/archive、date/version、persistent identifier。
- Web references 至少给完整 URL 和访问日期。

---

## 5. 投稿文档格式

| 项 | 要求 |
|---|---|
| 主稿件 | LaTeX 或 Word editable source；PDF 不是 source file |
| LaTeX class | Elsevier `elsarticle.cls` |
| documentclass | `\documentclass[preprint,12pt]{elsarticle}` |
| 编译 | `pdflatex` + `bibtex` + `pdflatex` + `pdflatex` |
| 匿名 | **不匿名**；JSS single-anonymized，保留作者、单位、ORCID、CRediT、Funding |
| LaTeX source zip | **扁平化**：不要子目录；figures 与 `.tex` 同层；不要把 LaTeX source 作为 supplementary item 上传 |

---

## 6. 必备/建议提交项

| 项 | 是否必须 | 备注 |
|---|---|---|
| Main manuscript PDF | ✅ | EM item type: Manuscript |
| LaTeX source files | ✅/按系统要求 | `.tex`, `.bib`/`.bbl`, `.bst`, `.cls`, figures 同层 |
| Highlights | ✅ | 单独 editable file；3–5 条，每条 ≤85 字符 |
| Keywords | ✅ | 1–7 个 |
| CRediT author statement | ✅ | 可在正文或 submission system 中提供 |
| Declaration of competing interest | ✅ | Elsevier declarations tool；无冲突也要声明 |
| Funding statement | ✅ | 说明资助来源及 sponsor role |
| Generative-AI declaration | ✅ 如使用 AI | 放在 reference 前；作者承担全部责任 |
| Data availability statement | ✅ | 仓库/Zenodo DOI/不可共享原因 |
| Author biographies / Vitae | ✅ | 单独 editable file；每位作者 ≤100 words；不要放进主文 |
| Graphical abstract | 可选 | 若有，禁止 AI 生成/修改图像造成不可披露风险 |
| Supplementary material | 可选 | 独立文件；不要把 LaTeX source files 错传为 supplement |

---

## 7. 编译验证清单

```bash
cd <submission_dir>
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex

# 应只看到 Output written 行；不应出现 Overfull/undefined/Citation/Rerun/Warning
rg -n "Output written|Overfull|undefined|Undefined|Citation|Rerun|Warning|LaTeX Warning|Package natbib Warning" main.log
```

---

## 8. 投稿前自检脚本

模板目录提供 `precheck_jss.py`：

```bash
python3 precheck_jss.py main.tex
```

检查项：

- `elsarticle` 与 `Journal of Systems and Software` 元数据；
- Abstract ≤250 词，且无 `\cite`/`\ref`；
- Keywords 1–7；
- Highlights 若在主文中出现，则 3–5 条且每条 ≤85 字符；
- CRediT、competing interest、funding/acknowledgments、generative-AI、data availability；
- author biography 不在 `main.tex`；
- 若 figure 路径含子目录，提示最终 EM source zip 需 flatten。

---

## 9. Cover Letter

Cover letter 应回答编辑最先看的五个问题：

1. Scope：这是给 software engineers / AI engineers 的问题吗？
2. Novelty and impact：相对现有 JSS/SE 文献，新在哪里？
3. Validation：用什么 empirical / simulation / formal / other validation 支撑 claims？
4. Replicability and transparency：数据、代码、脚本、补充材料在哪里？
5. Boundary：哪些 claims 明确不做？

若超过 36 页 single-column / 18 页 double-column，在 cover letter 中解释长度必要性。

---

## 10. 当前 SciML-MR 项目的 JSS 边界提示

可以 claim：

- auditable validity-gated V&V workflow for SciML metamorphic testing；
- numerical-decidability gate under stated operator/mesh assumptions；
- bounded full rubric-to-verdict evidence；
- external issue/PR/commit-linked semantic-witness triangulation。

不能 claim：

- general SciML reliability；
- baseline superiority；
- arbitrary-mesh soundness；
- representative defect sampling；
- real-world defect-detection rates；
- production validation；
- trained-SUT correctness；
- broad framework correctness。

