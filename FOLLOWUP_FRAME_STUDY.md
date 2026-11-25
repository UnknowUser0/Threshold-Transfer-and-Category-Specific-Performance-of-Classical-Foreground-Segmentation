# Follow-up protocol: temporal failure analysis — proposal, NOT yet executed

## Scope

This is a proposed **separate follow-up** from the V3 confirmation. Frame-level diagnosis cannot be recovered from the existing per-sequence aggregate CSV. It requires the original CDnet frames, ground truth and regenerated/saved per-frame foreground masks.

## Pre-analysis logging

- Register the code commit, dataset manifest/hash, sequence selection and metrics **before** producing new frame-level results.
- Declare that candidate cases such as `PTZ/intermittentPan` were selected **post-hoc** from V3; this does not qualify them for independent hypothesis confirmation.
- Use the V3 frozen algorithm parameters exactly. If changing resolution, record this as a separate sensitivity analysis.
- Select time points by a reproducible rule, such as equally spaced quantiles within the annotated ROI, **not frames chosen for appearance**. Separately allow clearly labeled illustrative cases chosen after analysis.

## Collect for each evaluated frame and algorithm

| Measurement | Definition | Why it matters |
|---|---|---|
| Timestamp/frame ID | CDnet index and original timestamp if provided | Reproducibility and alignment |
| GT positives | Number of GT pixels with label 255 in valid ROI | Foreground prevalence |
| FP pixels | Predicted FG where GT is valid background | False alarms |
| FN pixels | Predicted BG where GT is foreground | Missed foreground |
| Precision/Recall/F1 | Derived on valid GT mask; report undefined cases correctly | Accuracy dynamics |
| Predicted foreground pixel count | Number of prediction positives in ROI | Segmentation instability |
| Motion proxy | Robust estimate of global frame-to-frame affine/homography displacement from background features | Test camera-motion explanation |
| Saved masks | Predicted binary mask and valid-GT mask | Human visual audit |
| Config hash | Model parameters and code hash | Integrity |

## Intended analyses

1. Plot FP, FN, GT prevalence, and motion proxy over frame index per chosen sequence.
2. Assess association between measured camera-motion proxy and per-frame FPR/FNR while accounting for serial dependence; avoid treating frames as independent replicates.
3. Compare methods on the same frames in synchronized qualitative panels.
4. Report both supporting and contradicting examples; do not assign a cause to motion or turbulence without evidence.
5. Retain a fixed quantitative/qualitative selection rule and document missing frames.

**Status:** protocol proposal only. Do not write results paragraphs or p-values for these analyses until the experiment has actually been performed.
