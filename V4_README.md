# CDnet2014 V4 — Post-hoc failure-mode and generalization analysis

## Scope and academic integrity

V4 **does not alter V3 and does not perform new inference or tuning**. It reads the confirmed `working/results-v3-confirmatory` and `working/results-v3-development`, regenerates descriptive supplementary tables and plots, and logs source hashes. This is explicitly **post-hoc/exploratory** analysis, not a fresh confirmation of H1–H4.

`working/results-v4-posthoc/` is a separately generated directory. Do not overwrite or regenerate the original V3 evidence to change conclusions. The 320px protocol is still the protocol used for reported results.

## In PyCharm — recommended `.ipynb` route

1. Extract the **complete V4 ZIP** preserving the `cdnet_paper_v3` folder hierarchy.
2. Open `analysis_v4.ipynb` from the project folder in PyCharm. Use the Jupyter kernel with pandas, NumPy, matplotlib, nbformat, and pytest from `requirements.txt`.
3. Run the two code cells. The first cell searches for `analyze_v4.py` by walking upwards from the notebook's working directory, or uses `CDNET_V4_PROJECT_DIR` when set. No `CDNET_MODE` setting is needed: V4 is read-only.
4. Inspect `working/results-v4-posthoc/REPORT_V4.md` and the four `fig_v4_*.png` images.

If your V3 source outputs are elsewhere, set `PROJECT_DIR` to the directory containing `analyze_v4.py`, or pass explicit paths to `analyze_v4.run(...)`.

## Via terminal

```powershell
python -m pip install -r requirements.txt
python -m pytest -q tests/test_protocol.py tests/test_v4_analysis.py
python analyze_v4.py
```

Optional explicit paths:

```powershell
python analyze_v4.py --confirmatory "C:\\data\\results-v3-confirmatory" --development "C:\\data\\results-v3-development" --out "C:\\data\\analysis-v4-posthoc"
```

## Main files

- `analyze_v4.py` — independent read-only post-hoc analysis runner
- `analysis_v4.ipynb` — PyCharm-friendly notebook entry point
- `working/results-v4-posthoc/REPORT_V4.md` — findings with honest limitations
- `working/results-v4-posthoc/V4_PROVENANCE.json` — reproducibility manifest + source SHA-256
- `working/results-v4-posthoc/table_v4_category_winners.csv` — category-level ranking
- `working/results-v4-posthoc/table_v4_sequence_error_profiles.csv` — per-sequence FPR/FNR etc.
- `working/results-v4-posthoc/table_v4_ranked_failure_cases.csv` — cases needing visual inspection
- `working/results-v4-posthoc/table_v4_default_vs_tuned_category.csv` — threshold transfer
- `PAPER_V4_DRAFT.md` — text draft with data-backed evidence and explicit TODOs

## Important statistical distinction

The pre-declared H3/H4 one-sided family in frozen V3 yielded Holm-adjusted p = 0.031 for each. A broader exploratory family in `stats_ablation_frame_diff.csv` has other correction factors and must not be selectively mixed. H1/H2's Holm-adjusted p = 0.062 for each (not significant at 0.05).

## What V4 cannot infer from the ZIP

The archived CSV has aggregate counts by video sequence, not frame-aligned masks or per-frame object trajectories. Therefore camera motion **cannot be asserted as the cause** of poor segmentation solely on these results. To make mechanistic claims, use raw video frames, GT, per-frame predictions, and temporal measurements in a separate follow-up experiment.
