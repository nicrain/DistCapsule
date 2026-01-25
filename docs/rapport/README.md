# DistCapsule Rapport (LaTeX)

Ce dossier contient le rapport technique en LaTeX (version fran\c{c}aise, compatible pdflatex).

## Compilation (pdflatex)

```bash
cd docs/rapport
pdflatex main.tex
pdflatex main.tex
```

Avec `latexmk` :

```bash
latexmk -pdf -interaction=nonstopmode -file-line-error main.tex
```

## Images

Le rapport r\'eutilise les images du support de slides via :

```tex
\graphicspath{{../slides/pic/}}
```
