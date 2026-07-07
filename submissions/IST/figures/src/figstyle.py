"""论文级 matplotlib / seaborn 默认样式 + 双格式保存助手。

把本文件复制到生成的绘图脚本同目录(`<插图目录>/src/`),脚本即可 `import figstyle`。
render.py 在执行 .py 源文件时也会把 skill 的 scripts/ 目录加入 PYTHONPATH。
"""
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # 无显示环境也能渲染
import matplotlib.pyplot as plt

# 论文级 rcParams。字号按投稿排版偏小;某期刊另有要求时在生成脚本里覆盖。
PARAMS = {
    "font.family": "serif",
    "mathtext.fontset": "dejavuserif",
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "legend.frameon": False,
    "lines.linewidth": 1.2,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
}


def apply_style():
    """应用论文级默认样式。装了 seaborn 时用 paper context + whitegrid。"""
    try:
        import seaborn as sns
        sns.set_theme(context="paper", style="whitegrid", font="serif")
    except ImportError:
        pass
    plt.rcParams.update(PARAMS)


def output_target(default_name, default_outdir="figures"):
    """读取 render.py 注入的环境变量;脚本被直接运行时回落到默认值。

    返回 (outdir, name, dpi)。
    """
    return (
        os.environ.get("FIG_OUTDIR", default_outdir),
        os.environ.get("FIG_NAME", default_name),
        int(os.environ.get("FIG_DPI", "300")),
    )


def save_figure(fig, basename, outdir="figures", dpi=300, formats=("pdf", "png")):
    """同一张图存矢量 PDF + 位图 PNG。PDF 无 dpi 概念,PNG 用 300 dpi。"""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for fmt in formats:
        p = out / f"{basename}.{fmt}"
        if fmt == "pdf":
            fig.savefig(p, format="pdf")
        else:
            fig.savefig(p, format=fmt, dpi=dpi)
        saved.append(str(p))
    plt.close(fig)
    print("saved:", "  ".join(saved))
    return saved
