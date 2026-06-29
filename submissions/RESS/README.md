# submissions/RESS/ — Reliability Engineering & System Safety 投稿包

Elsevier `elsarticle` 包，numbered Vancouver 参考文献。由 IST 投稿源
（`dist/IST-submission-2026-06-27/source/`）转换而来；转换规则见 `paper/53_ress_repositioning_draft.md`。

## 文件
| 文件 | 说明 |
|---|---|
| `main.tex` | 主稿（`\documentclass[preprint,12pt]{elsarticle}`）|
| `references.bib` | 参考文献（与 IST 同，elsarticle-num）|
| `highlights.txt` | Highlights，5 条，每条 ≤85 字符 |
| `elsarticle.cls` / `elsarticle-num.bst` | 官方类与样式（vendored）|
| `figures/` | 图源 |

## 相对 IST 的改动（仅 frontmatter / 声明 / 格式，正文未动）
1. 标题 → reliability 引导（Auditable Fault Attribution for OOD Use）
2. 摘要 → **非结构化单段，199 词（≤200 硬上限）**，去 Context/Objective/… 标签
3. Highlights → reliability 框架（≤85 字符）
4. Keywords → RESS 受众 7 个
5. GenAI 声明节标题 → RESS 固定措辞「…in the manuscript preparation process」
6. `\journal{}` → RESS；preamble 加 `\sloppy`
- 单一通讯作者（Meng Li，本就单一，符合 RESS）

## 构建
```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
python ../../../venues/templates/RESS/precheck_RESS.py main.tex highlights.txt
```

## 投稿前仍需做（正文级，见 paper/53 §H/§I，本次未做）
- 去 SE 黑话（MetaPattern / MR-family / sans-serif 记号）
- 广度前置（cross-architecture / cross-equation 提到结果主线，保留"非 cross-SUT 率"标签）
- Related Work 补 1–2 条 RESS 谱系引用
- Funding/Data availability 已含；Declaration of Competing Interest 用 declarations tool 另出 .doc

## 字数说明
RESS 硬上限 13,000 词。`precheck` 的 13,173 是**含 LaTeX 命令 token 的全文件粗估**（高估）；
按 RESS 口径（正文 ~9,119 + 参考 ~1,913 ≈ 11k，无 IST 的 200/float 附加）**有余量**。
投稿当下以 Editorial Manager 字数为准。
