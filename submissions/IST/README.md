# submissions/IST/ — IST 投稿专属物

本目录**只放投稿专属物**：cover letter、highlights、自述、稿件 PDF（手稿编译产物）。

手稿 tex 源在 [`manuscript/`](../../manuscript/README.md)。
最终上传压缩包在 [`dist/IST-submission-2026-06-24.zip`](../../dist/IST-submission-2026-06-24.zip)。

## 目录内容

| 文件 | EM 上传位 |
|---|---|
| `main.pdf` | Manuscript（手稿 PDF，与 `manuscript/main.pdf` 字节一致） |
| `cover_letter.md` | Cover Letter |
| `highlights.txt` | Highlights |
| `README.md` | （本文件；不上传） |

## Editorial Manager 上传映射

| EM item type            | File                                  |
|-------------------------|---------------------------------------|
| Manuscript              | `submissions/IST/main.pdf`            |
| Highlights              | `submissions/IST/highlights.txt`      |
| Cover Letter            | `submissions/IST/cover_letter.md`     |
| LaTeX Source (zipped)   | `dist/IST-submission-2026-06-24.zip` 的 `source/` 子目录 |

## 不在本目录的相关物

- **稿件 tex 源**（`main.tex` / `references.bib` / `main.bbl` / `elsarticle.cls` / `elsarticle-num.bst` / `figures/*.pdf`）：在 `manuscript/`
- **supplementary 文档**（`figure_plan.md`、`manuscript.md`）：在 `manuscript/`
- **完整投稿压缩包**：`dist/IST-submission-2026-06-24.zip`

## 期刊与系统

- 期刊全称：Information and Software Technology（Elsevier）
- 文章类型：Regular Paper（≤ 15 000 words；当前 13 020）
- 同行评审：single-anonymized（**不**匿名）
- 投稿系统：<https://www.editorialmanager.com/infsof/>
- 必备声明（已写入 `manuscript/main.tex`）：CRediT、Competing Interest、Generative AI、Data Availability、Funding

## 同步规则

`submissions/IST/main.pdf` 必须与 `manuscript/main.pdf` 字节一致。改动 tex 后：

```bash
cd manuscript/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
cd ..
cp manuscript/main.pdf submissions/IST/main.pdf
```
