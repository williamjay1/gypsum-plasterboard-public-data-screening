# Public data decision support tool for gypsum plasterboard recycling

This repository contains the reproducibility materials for a public data computational study of batch level triage and pretreatment routing for post consumer gypsum plasterboard.

The study uses public official datasets, public research data and published technical records. It does not contain field sampling, laboratory experiments, human participants or unpublished facility data. The reported scenarios are transparent researcher defined parameter bundles, not an EU wide empirical contamination distribution.

## Contents

- `paper/` contains the Springer Nature LaTeX manuscript, bibliography files, figures and compiled PDF. The files in this directory are kept at one level so that `Manuscript.tex` can be compiled directly.
- `data/` contains public working tables, parameter registers and provenance records. Third party publisher PDFs are not redistributed.
- `results/` contains derived scenario tables, audits and generated figures.
- `code/` contains the analysis and figure scripts used for the public data calculations.

## Reproduce the main outputs

From the repository root, install the Python dependencies listed in `requirements.txt`, then run the scripts in `code/`. The scripts write derived tables to `results/` and figures to `results/figures/`.

The manuscript PDF can be rebuilt with XeLaTeX and BibTeX from the `paper/` directory:

```text
xelatex -interaction=nonstopmode Manuscript.tex
bibtex Manuscript
xelatex -interaction=nonstopmode Manuscript.tex
xelatex -interaction=nonstopmode Manuscript.tex
```

## Interpretation boundary

The repository supports an interval based screening and measurement prioritization analysis. It is not a complete ISO life cycle assessment, life cycle costing study, legal end of waste determination, product certification or empirical EU prevalence estimate.

## Data and licence

Public source URLs, variable roles and limitations are recorded in `data/data_availability_audit.csv` and `data/DATA_SOURCES.md`. Source data remain subject to the terms of their original providers.

The original analysis code and derived materials in this repository are released under the MIT License. The manuscript remains subject to the publisher's terms if submitted or published.
