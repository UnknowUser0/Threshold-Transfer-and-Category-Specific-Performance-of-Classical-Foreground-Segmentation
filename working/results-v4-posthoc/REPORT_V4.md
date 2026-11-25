# V4: Frozen-V3 post-hoc generalization and failure-mode analysis

**Evidence status:** Exploratory, descriptive secondary analysis of the existing V3 confirmatory results. **NO new independent test set or new confirmatory claims.**

**Input:** 27 sequences / 6 unseen-by-V2 categories; 320 px width; fixed parameters; 4 tuned algorithms. V3 prior development = 26 sequences / 5 different categories. Source V3 already tested; all V4 plots/tables are post-hoc.

## Reproduced V3 hypothesis decisions (original protocol — not re-tested in V4)

| Hypothesis | Original p one-sided | Original p Holm | Original decision |
|---|---:|---:|---|
| H1: MOG2 > Frame Difference (F piksel) | 0.047 | 0.062 | tidak signifikan |
| H2: KNN > Frame Difference (F piksel) | 0.031 | 0.062 | tidak signifikan |
| H3: Blur menurunkan FPR Frame Difference | 0.016 | 0.031 | arah didukung |
| H4: Morphology meningkatkan F1 Frame Difference | 0.016 | 0.031 | arah didukung |


Note: p values for H3-H4 use the designated one-sided hypothesis family. The broader exploratory factorial comparisons have DIFFERENT Holm correction families. Do not substitute one for the other. A one-sided claim requires a defensible prior-time-stamped directional hypothesis.

## Category-level outcomes (mean of sequence F1, equal category weight for headline summary)

| Category | FD F1 | MOG2 F1 | KNN F1 | Farneback F1 | Top method |
|---|---:|---:|---:|---:|---|
| PTZ | 0.316 | 0.215 | 0.203 | 0.204 | Frame Difference |
| cameraJitter | 0.154 | 0.667 | 0.709 | 0.128 | KNN |
| intermittentObjectMotion | 0.259 | 0.317 | 0.372 | 0.171 | KNN |
| lowFramerate | 0.279 | 0.486 | 0.474 | 0.220 | MOG2 |
| thermal | 0.339 | 0.517 | 0.573 | 0.394 | KNN |
| turbulence | 0.032 | 0.626 | 0.569 | 0.098 | MOG2 |


The winner varies by category. The PTZ advantage of FD is not a mechanistic explanation; inspect frame masks and movements to test competing explanations.

## Frozen threshold transfer

| Method | Mean category-level tuned minus default F1 |
|---|---:|
| Frame Difference | +0.0020 |
| MOG2 | +0.0125 |
| KNN | -0.0056 |
| Farneback | +0.0000 |

Method-level tuning gains on the development categories cannot guarantee gains in categories with different scene dynamics. Any post-hoc threshold refinement would invalidate a confirmatory-transfer interpretation unless evaluated on a new untouched test set.

## Selected sequence-level reversals (exploratory)

| category                 | seq                                     |   knn_minus_fd |   mog2_minus_fd |
|:-------------------------|:----------------------------------------|---------------:|----------------:|
| PTZ                      | PTZ/intermittentPan                     |         -0.410 |          -0.402 |
| PTZ                      | PTZ/zoomInZoomOut                       |         -0.080 |          -0.052 |
| PTZ                      | PTZ/continuousPan                       |          0.003 |           0.003 |
| PTZ                      | PTZ/twoPositionPTZCam                   |          0.035 |           0.050 |
| lowFramerate             | lowFramerate/port_0_17fps               |          0.050 |           0.260 |
| intermittentObjectMotion | intermittentObjectMotion/tramstop       |          0.051 |           0.023 |
| intermittentObjectMotion | intermittentObjectMotion/winterDriveway |          0.056 |           0.078 |

A negative KNN-minus-FD value means FD performed better for that sequence. These are ranked for qualitative inspection, not statistical discovery.

## Interpretation constraints

1. **Scene-category shift is confounded with scene composition**. Development and confirmatory categories are disjoint and not randomized matched pairs; avoid attributing mean gaps solely to overfitting.
2. **Aggregated confusion counts lack temporal resolution**. A high FPR/FNR tells what type of pixel error occurred, not whether its cause was camera motion, static foreground absorption, illumination, thermal noise, or another mechanism. Failure-cause claims require frame-by-frame evidence or additional measurements.
3. **Statistical unit** for hypothesis testing is category (n=6), not 27 independent categories. V4 ranking and plots carry no newly confirmed p-values.
4. **Metric resolution** is 320px, not native resolution; frame MCC and box F1 are secondary and some MCC observations are missing.
5. **Numerical comparability** with online leaderboard requires identical training assumptions, evaluation frames, GT interpretation, and pixel resolution. Our within-study scores must not be reported as benchmark leaderboard scores.
6. **History**: confirmatory status is conditional on these categories never having informed earlier parameter choice. A manifest overlap check cannot prove absence of previous manual inspection.

## Suggested evidence acquisition (new study, separately preregistered)

- Produce frame-aligned qualitative panels on PTZ and turbulence with the same frame IDs across algorithms, GT and predictions; write the selection rule before review.
- Record per-frame FP, FN, GT foreground area and camera-motion proxy; analyze temporal trajectories with sequence-level replication. This cannot be reconstructed from the V3 aggregate CSV alone.
- Run native-resolution sensitivity with frozen algorithms/thresholds, label it follow-up exploratory unless a fresh test set is reserved.
- Add one modern algorithm baseline with clearly specified adaptation/training assumptions and computational budget.

## Original evidence hashes (SHA-256)

- `confirmatory/all_per_seq.csv`: `b2f7d70702499cf3c97f037b754dd4b82f499ff1b0815f345085ac334cf9bb23`
- `confirmatory/run_info.json`: `94aafcbf7321baf282181399ed87208f2a2d3a0c437860cb8093c296f6fb9fc0`
- `confirmatory/table_hypotheses.csv`: `08f847f193831b5692dca5b2d8b00188469234d8ac748dc78e4ea319ced8f084`
- `confirmatory/table_by_category.csv`: `fc2d6bcca38c11a08400260018207d13a01a4e198391e90c34e659f3fd3e5c10`
- `development/all_per_seq.csv`: `2875a2ec92605f8d27412d2c79cb0e09991b1f9e4e7be6af46f1f04f8bf2cb75`
- `development/table_by_category.csv`: `181802e4019804fe370c4715d7fe32c4a7f701d23fa20d62c68a3cbd9588c628`
- `development/run_info.json`: `a53c7a442e218624588a6c53b90046cce8068bbd7b610822ea0ad199fd55b802`

Generated V4 outputs are derived from unchanged V3 files. No new detector predictions were created.
