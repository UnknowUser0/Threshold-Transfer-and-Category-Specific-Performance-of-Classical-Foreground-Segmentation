# Manuscript development draft — Version 4 (NOT submission-ready)

**Working title**: *Threshold Transfer and Preprocessing Sensitivity in Classical Foreground Segmentation: An Eleven-Category CDnet2014 Study*

**Study type**: controlled empirical assessment and descriptive failure-mode analysis. We have results spanning all eleven CDnet2014 categories, BUT **five categories are development data** and **six categories are a later confirmatory evaluation**, so we must never imply that all 53 sequences were independent held-out test samples.

**Status**: manuscript development; original experimental results remain in V3. Any V4 tables, rankings and failure-case selections are post-hoc analyses, not additional confirmation.

---

## Abstract (working English draft, verify every number against locked V3 tables)

Classical foreground segmentation methods remain relevant in low-complexity video-processing pipelines, but the transferability of threshold choices and preprocessing effects across surveillance conditions requires careful evaluation. This study compares frame differencing, MOG2, KNN background subtraction, and dense Farneback optical flow on CDnet2014, using a fixed 320-pixel evaluation width and category-aware analysis. Parameters were selected using 26 video sequences from five development categories; they were then frozen and applied to 27 sequences from six additional categories. The latter evaluation yielded category-averaged pixel F-measures of 0.230, 0.471, 0.483, and 0.203 for frame differencing, MOG2, KNN, and Farneback, respectively. Although KNN had the largest overall mean, frame differencing was strongest within the PTZ category, demonstrating heterogeneity across scenes. Frozen parameter tuning did not consistently improve performance: for KNN, the default and tuned configurations achieved F-measures of 0.489 and 0.483, respectively, on the new categories. Under the pre-specified directional hypothesis tests, Gaussian blurring reduced the false-positive rate of frame differencing and morphology improved its pixel F-measure (Holm-adjusted p = 0.031 for each), whereas the two primary algorithm-vs-baseline hypotheses were not significant after correction (p = 0.062 each). These results show that preprocessing benefits and threshold transfer should be interpreted in relation to video-condition variability rather than generalised from overall mean scores alone. The study is limited by category-level sample size, its working resolution, and the lack of temporal error annotations for mechanism-level conclusions.

**Keywords**: change detection, background subtraction, CDnet2014, domain generalization, preprocessing, threshold sensitivity, failure analysis.

> Editorial warning: do not call this a new algorithm, a state-of-the-art result, or a complete independent test over all 11 categories.

## 1. Introduction — draft argument

Foreground segmentation is sensitive to real-world video factors including intermittent motion, camera changes, and turbulent backgrounds. Overall performance scores may conceal category-specific reversals in algorithm rankings. A second issue is tuning transfer: the threshold selected on one group of scenes may not improve performance on unfamiliar categories. A third issue is the heterogeneous impact of blur and morphology on false alarms and missed foreground pixels. The CDnet2014 benchmark contains 11 categories designed to challenge change-detection methods (Wang et al., 2014; official dataset website).

This paper tests the robustness of four classical approaches under a shared pipeline and separates parameter-development evidence from later category-level assessment. It does not claim to propose a novel model. Its prospective contribution is a transparent, leakage-aware comparison, paired category-level inference for designated hypotheses, and a documented analysis of category-specific failure cases.

**Explicit research questions:**

- **RQ1:** How consistent are the rank orders of four classical methods across changing categories?
- **RQ2:** Do threshold values tuned on five development categories transfer to six disjoint categories?
- **RQ3:** Under a frozen configuration, does Gaussian Blur reduce the Frame Difference FPR, and does morphology increase Frame Difference F1?
- **RQ4 (exploratory):** Which sequences show ranking reversals, and what additional temporal evidence is needed to attribute their causes?

## 2. Related Work — gaps to fill before submission

- Summarize the CDnet2014 benchmark protocol and its five GT labels, explicitly comparing your treatment of label 50 (hard shadow) and non-ROI/unknown labels with the official evaluation convention.
- Review both classical adaptive background models and **recent** non-classical background subtraction/foreground segmentation research. Do not imply MOG2/KNN/Farneback are representative of current SOTA.
- Compare literature methods only when training, image resolution, evaluation period, and ground-truth interpretation are compatible. Avoid direct leaderboard comparisons otherwise.
- Add a literature matrix: method, unsupervised/supervised, per-scene adaptation, number of categories, resolution, metric aggregation, speed hardware, and generalization protocol.

**Background sources to verify and cite:**

1. Wang et al. (2014), *CDnet 2014: An Expanded Change Detection Benchmark Dataset*. [Open-access paper](https://openaccess.thecvf.com/content_cvpr_workshops_2014/W12/html/Wang_CDnet_2014_An_2014_CVPR_paper.html)
2. [Official CDnet dataset and evaluation website](https://changedetection.net/)
3. *Comparative Study of Supervised Deep Learning Architectures for Background Subtraction and Motion Segmentation on CDnet2014* (2026). [Publisher source](https://www.mdpi.com/2624-6120/7/1/14) — methodological context; verify its exact publication metadata, scope and relevance before citing.
4. *An unsupervised dual-phase framework combining statistical separation and hybrid level set evolution for robust motion detection and segmentation in intelligent video surveillance* (2026). [Publisher source](https://www.nature.com/articles/s41598-026-50215-9) — contextual example of modern background subtraction; **not a directly comparable baseline** without protocol matching.

## 3. Materials and Methods — locked facts

**Data partition:** 26 sequences, five categories, used for development and threshold tuning; 27 different sequences, six categories, evaluated without threshold tuning. This covers the 11 categories across **different phases**, not a single independent test over all categories. Preserve exact sequence IDs and SHA-256 evidence in the appendix.

**Main evaluation:** standardised video width 320 pixels, common preprocessing settings as described in V3: 5×5 Gaussian Blur, fixed foreground threshold, morphological opening (3) and closing (7) with contour filtering. Algorithm specifics and frozen tuned parameters must be copied verbatim from `run_info.json` and `protocol/frozen_v2_params.json`. Report the initialization/warm-up and ROI evaluation frames.

**Pixel labels and evaluation:** GT foreground = 255; background = 0; hard-shadow label 50 handled as negative; out-of-ROI = 85 and unknown = 170 excluded. Compute TP, FP, FN, TN on evaluated pixels; compute per-sequence F1, precision, recall, FPR and FNR. Aggregate over sequences within categories, then average over categories, giving categories equal headline weight. Explicitly document how this differs, if at all, from official benchmarking metrics.

**Statistics:** directional category-level exact sign-flip tests for pre-specified H1–H4 with Holm adjustment **within designated families**; category resampling for hierarchical CIs, as implemented in V3. Disclose n=6 categories for confirmatory category-level inference. Paired per-sequence Wilcoxon tests are *exploratory* and not the primary inferential evidence. Clearly distinguish pre-registered H3/H4 from broader factorial contrasts.

**Reproducibility:** code and data manifest in V3; V4 is read-only and adds SHA-256 of exact CSV/JSON source files. Include CPU, OS, library versions, and timing definitions. Post-hoc ranking does not constitute a separate statistical hypothesis.

## 4. Results — numerical claims supported by uploaded V3 outputs

### 4.1 Held-out-category headline scores

On 27 sequences in the six confirmatory categories, the category-averaged pixel F1 values were **0.230** (Frame Difference), **0.471** (MOG2), **0.483** (KNN), and **0.203** (Farneback). KNN therefore had the highest descriptive mean, with no statistically established superiority over Frame Difference after the designated Holm adjustment. More precisely, the pre-specified category-level one-sided test for KNN versus Frame Difference had Holm-adjusted **p = 0.062**, not below α = 0.05. The MOG2 comparison was likewise not significant after correction (p = 0.062).

### 4.2 Ranking heterogeneity

The six-category ranking differed by category. Frame Difference was highest on **PTZ (F1 = 0.316)**, ahead of MOG2 (0.215) and KNN (0.203). KNN was strongest on cameraJitter (0.709), intermittentObjectMotion (0.372), and thermal (0.573). MOG2 was strongest on lowFramerate (0.486) and turbulence (0.626). This is evidence of **ranking variation**, but not proof of its physical cause.

### 4.3 Threshold transfer

In the six-category confirmatory set, the default and tuned KNN configurations yielded F1 values of **0.489** and **0.483**, respectively. Corresponding mean changes for Frame Difference, MOG2, KNN, and Farneback were approximately **+0.0020**, **+0.0125**, **−0.0056**, and **0**, respectively. These are descriptive out-of-development-category differences, not standalone significance tests.

### 4.4 Preprocessing hypotheses and multiplicity

The original designated one-sided, category-level hypothesis family supported H3 (blur reduces Frame Difference FPR) and H4 (morphology increases Frame Difference F1), with Holm-adjusted **p = 0.031** for each. This does not mean every preprocessing configuration has a significant positive effect: the broad factorial tests have separate multiple-testing families and different adjusted values. The paper must present both without selectively mixing them.

### 4.5 Sequence-level failure cases (post-hoc)

`PTZ/intermittentPan` is a candidate for detailed visual inspection because Frame Difference F1 exceeds KNN by approximately **0.410** and MOG2 by **0.402**. This is a prioritization result derived after the confirmatory stage, not a preregistered hypothesis. Foreground/background predictions and temporal dynamics are needed before explaining the failure mechanism.

## 5. Discussion — hypotheses and falsifiable mechanisms

**Hypothesis for later testing, not a conclusion:** PTZ camera motion may affect background-model adaptation differently from frame differencing. A useful follow-up must compare temporally aligned raw frames, GT, full prediction masks, and per-frame FP/FN time series. It should also track camera-motion magnitude or image registration quality. The V3 sequence-level CSV alone cannot isolate these causes.

**Generalization interpretation:** The lower confirmatory scores than development scores are consistent with a more challenging set of categories, but the two phase cohorts are not randomized matched groups. The term 'performance drop' can describe a descriptive contrast; avoid claiming causal overfitting without controlled transfer evaluation.

**Computational trade-off:** FPS benchmarks are hardware- and implementation-dependent. Avoid claiming real-time end-to-end system latency unless I/O and preprocessing are measured under a specified deployment workload.

## 6. Threats to validity

- Domain differences confound development/confirmatory comparisons.
- Small number of inferential clusters (six categories) limits power.
- Confirmation depends on no previous human access to the additional categories; the manifest alone cannot prove this.
- 320px scores are not native-resolution or necessarily leaderboard-comparable scores.
- Different preprocessing assumptions may disadvantage algorithms differently.
- F1 can hide false-alarm vs missed-object trade-offs; sequence-level FPR/FNR and foreground prevalence are presented separately.
- The reported comparison covers only four classical methods and does not establish superiority to modern models.
- The V4 failure-case inspection is data-driven exploratory selection.

## 7. Conclusion — placeholder for final manuscript

The results emphasize heterogeneous category-level performance and incomplete transfer of selected thresholds. The confirmatory evidence supports the two directional preprocessing hypotheses under the declared testing protocol but does not support the two corrected algorithm superiority hypotheses. Causal explanations of failure mechanisms, native-resolution robustness, external baselines and venue-specific formatting remain open work.

---

## Submission-readiness checklist

- [ ] Verify temporal integrity of the original hypothesis pre-registration (timestamp / commit / archived evidence).
- [ ] Re-run the V3 unit tests and V4 tests in the intended reproducibility environment.
- [ ] Independently inspect five GT label conventions and confirm metric comparability.
- [ ] Add within-paper algorithm schematics, qualitative examples with aligned masks and images, and error trajectories.
- [ ] Add contemporary literature and at least one method from a different algorithm family under fair protocol conditions.
- [ ] Consider native-resolution sensitivity and another dataset; label any follow-up analyses appropriately.
- [ ] Review statistics: hypothesis family definitions, CI procedure, missing MCC cases.
- [ ] Audit language and novelty claims with a research supervisor or coauthor.
- [ ] Select an actual currently accredited SINTA 2 venue and comply with its author template, ethics, reference format, and scope. **SINTA 2 is a journal accreditation category, not an automatic acceptance rule.**
