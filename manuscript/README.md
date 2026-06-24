# manuscript/ — 手稿唯一源 (single source of truth)

本目录是论文的**唯一手稿源**：tex、参考文献、figures、supplementary 文档全部在这里。
投稿专属物（cover letter、highlights、PDF 派生件等）在 `submissions/IST/`，
最终上传压缩包在 `dist/IST-submission-2026-06-24.zip`。

## 目录内容

| 文件 | 角色 |
|---|---|
| `main.tex` | **稿件 master**（Elsevier `elsarticle.cls`，`preprint,12pt`） |
| `references.bib` | 文献库（47 条，45 含 DOI） |
| `main.bbl` | 预编译 bibliography |
| `elsarticle.cls` / `elsarticle-num.bst` | 类文件 v3.5 + bst v2.1（vendored, byte-identical to CTAN） |
| `figures/*.pdf` | 4 张图 |
| `manuscript.md` | 早期 prose 源 + 30 个回归 guard 硬绑定靶；**不可删/改名** |
| `figure_plan.md` | 插图规划 supplementary 文档 |
| `main.pdf` | 编译产物（与 `submissions/IST/main.pdf` 字节一致） |
| `main.{aux,bbl,blg,log,spl}` | LaTeX 编译副产物 |

## 编译

```bash
cd manuscript/
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

健康指标（2026-06-24）：50 pages / 542 738 bytes / 0 undefined / 0 Missing character / 0 LaTeX Warning / 0 LaTeX Error / 0 Overfull。

## 同步给投稿包

修改 `main.tex` 后，把新的 PDF cp 到投稿目录、并重新打包：

```bash
cp manuscript/main.pdf submissions/IST/main.pdf

PKG="IST-submission-2026-06-24"
PKGDIR="dist/$PKG"
rm -rf "$PKGDIR" "dist/$PKG.zip"
mkdir -p "$PKGDIR/source/figures"
cp submissions/IST/{main.pdf,cover_letter.md,highlights.txt} "$PKGDIR/"
cp manuscript/{main.tex,references.bib,main.bbl,elsarticle.cls,elsarticle-num.bst} "$PKGDIR/source/"
cp manuscript/figures/*.pdf "$PKGDIR/source/figures/"
cd dist && zip -qr "$PKG.zip" "$PKG"
```

## 工具/测试钉死的入口

`tools/ist_wordcount.py`、`tools/run_ist_maturity_panel.py`、`tools/run_academic_review_panel.py`、
`tests/test_phase6_*` 等 23 个文件硬编码 `Path("manuscript/main.tex")` 或
`Path("manuscript/main.bbl")` 入口。改路径会同时破坏 23 个文件的常量；改前请全文搜索确认。
