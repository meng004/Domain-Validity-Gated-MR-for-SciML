# venues/ist/ — IST venue layer

本目录只放 IST 相关的 venue-level 材料：cover letter、highlights、自述和构建入口。

全文唯一权威源在 [`manuscript/`](../../manuscript/)。
生成的上传包位于 [`submission/IST/`](../../submission/IST/)。

## 目录内容

| 文件 | EM 上传位 |
|---|---|
| `cover_letter.md` | Cover Letter |
| `highlights.txt` | Highlights |
| `README.md` | （本文件；不上传） |

## Editorial Manager 上传映射

| EM item type            | File                                  |
|-------------------------|---------------------------------------|
| Manuscript              | `submission/IST/main.pdf`             |
| Highlights              | `submission/IST/highlights.txt`       |
| Cover Letter            | `submission/IST/cover_letter.md`      |
| LaTeX Source            | `submission/IST/source/`              |

## 不在本目录的相关物

- **稿件 tex 源**（`main.tex` / `supplementary.tex` / `references.bib` / `figures/*.pdf`）：在 `manuscript/`
- **完整投稿包**：由 `python venues/ist/build.py` 生成到 `submission/IST/`

## 期刊与系统

- 期刊全称：Information and Software Technology（Elsevier）
- 文章类型：Regular Paper（≤ 15 000 words；当前 14 432）
- 同行评审：single-anonymized（**不**匿名）
- 投稿系统：<https://www.editorialmanager.com/infsof/>
- 必备声明（已写入 `manuscript/main.tex`）：CRediT、Competing Interest、Generative AI、Data Availability、Funding

## 同步规则

改动 `manuscript/` 后重新生成 IST 镜像：

```bash
python venues/jss/build.py
python venues/ist/build.py
```
