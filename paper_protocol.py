"""Protocol safeguards, CDnet label handling and category-unit inference.

This module does not load dataset files or evaluate trained models. It can be
unit-tested independently from the heavyweight notebook/experiment runner.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

KNOWN_LABELS = frozenset((0, 50, 85, 170, 255))
DEV_CATEGORIES = ('baseline', 'dynamicBackground', 'nightVideos', 'badWeather', 'shadow')
UNSEEN_CATEGORIES = ('cameraJitter', 'intermittentObjectMotion', 'lowFramerate', 'PTZ', 'thermal', 'turbulence')


def load_seen(path: str | Path) -> set[str]:
    obj = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(obj, dict) or not isinstance(obj.get('seen_sequences'), list):
        raise ValueError('Historical manifest must contain seen_sequences array')
    if not obj['seen_sequences']:
        raise ValueError('Historical manifest must not be empty')
    return set(obj['seen_sequences'])


def validate_protocol(cfg: dict, sequences: list[dict], seen_path: str | Path) -> dict:
    """Fail closed: no old sequence, parameter retuning or incomplete category coverage.

    The 'confirmatory' phase is ONLY valid when evaluated on still-unseen data.
    It does NOT grant independence if its results have already been inspected.
    """
    mode = cfg['mode']
    if mode not in {'development', 'confirmatory'}:
        raise ValueError('mode must be development or confirmatory')
    ids = [s['id'] for s in sequences]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('Sequence list must be nonempty and unique')
    observed = {s['category'] for s in sequences}
    report = {'mode': mode, 'total_sequences': len(sequences), 'categories': sorted(observed)}
    if mode == 'development':
        report['interpretation'] = 'EXPLORATORY; prior v2 test results have been inspected'
        return report

    seen = load_seen(seen_path)
    overlap = sorted(seen.intersection(ids))
    if overlap:
        raise ValueError('CONFIRMATORY LEAKAGE: previously seen sequences: ' + ', '.join(overlap))
    required = set(UNSEEN_CATEGORIES)
    if observed != required:
        raise ValueError(f'CONFIRMATORY COVERAGE: required {sorted(required)}, found {sorted(observed)}')
    if set(cfg['categories']) != required:
        raise ValueError('Confirmatory configuration must include all six preregistered unseen categories')
    category_counts = {c: sum(s['category'] == c for s in sequences) for c in required}
    if any(n < 4 for n in category_counts.values()):
        raise ValueError('CONFIRMATORY COVERAGE: require >=4 sequences in each category; found ' + str(category_counts))
    if cfg['run_tuning'] or int(cfg['tune_per_category']) != 0:
        raise ValueError('CONFIRMATORY LEAKAGE: tuning is forbidden')
    if not cfg['tuned_params_file'] or not Path(cfg['tuned_params_file']).is_file():
        raise ValueError('CONFIRMATORY LEAKAGE: frozen parameters file required')
    if cfg['max_seqs_per_category'] is not None or cfg['max_eval_frames'] is not None or cfg['sequences'] is not None:
        raise ValueError('CONFIRMATORY COVERAGE: no subsets or frame truncation permitted')
    if cfg['resize_width'] != 320:
        raise ValueError('Frozen v2 thresholds were tuned at 320px; run native resolution as a separate sensitivity study')
    for s in sequences:
        if s.get('n_scored', 0) < 1:
            raise ValueError('Sequence missing annotated frames: ' + s['id'])
    report.update(interpretation='CONFIRMATORY ON PREVIOUSLY UNSEEN CATEGORIES (conditional on no prior access)',
                  historically_seen=len(seen), overlap=0, category_counts=category_counts)
    return report


def score_pixel_counts(pred_mask: np.ndarray, gt: np.ndarray, roi: np.ndarray | None = None) -> tuple[int,int,int,int]:
    """GT255 foreground, GT0/50 negative, GT85/170 excluded; enforce ROI.bmp on *both* masks.

    Counts are returned (TP, FP, FN, TN) and aggregated before calculating metrics.
    """
    if pred_mask.shape != gt.shape:
        raise ValueError(f'Prediction and GT shapes differ: {pred_mask.shape} != {gt.shape}')
    labels = set(map(int, np.unique(gt)))
    if not labels.issubset(KNOWN_LABELS):
        raise ValueError(f'Unexpected GT labels: {sorted(labels - KNOWN_LABELS)}; resize masks using NEAREST')
    included = np.ones(gt.shape, dtype=bool) if roi is None else roi != 0
    if included.shape != gt.shape:
        raise ValueError('ROI and GT shapes differ')
    foreground = (gt == 255) & included
    background = ((gt == 0) | (gt == 50)) & included
    prediction = pred_mask != 0
    tp = int(np.count_nonzero(prediction & foreground))
    fp = int(np.count_nonzero(prediction & background))
    fn = int(np.count_nonzero(~prediction & foreground))
    tn = int(np.count_nonzero(~prediction & background))
    return tp, fp, fn, tn


def category_signflip_p(category_effects: np.ndarray, alternative: str = 'two-sided') -> float:
    """Two-sided exact paired sign-flip permutation test on category mean differences.

    Category is the independent unit; avoids pseudoreplication of adjacent video
    frames and repeated sequences from the same challenge category.
    Not a universal solution for within-category dependence or dataset selection.
    """
    v = np.asarray(category_effects, dtype=float)
    v = v[np.isfinite(v)]
    if not len(v) or np.any(~np.isfinite(v)):
        return float('nan')
    if not np.any(v):
        return 1.0
    if len(v) > 18:
        raise ValueError('Exact sign-flip is limited to <=18 categories')
    if alternative not in ('two-sided', 'greater', 'less'):
        raise ValueError('alternative must be two-sided/greater/less')
    observed = float(v.mean())
    count = 0
    total = 1 << len(v)
    for signs in itertools.product((-1.0, 1.0), repeat=len(v)):
        sim = float(np.mean(v * signs))
        extreme = (abs(sim) >= abs(observed) - 1e-12 if alternative == 'two-sided'
                   else sim >= observed - 1e-12 if alternative == 'greater'
                   else sim <= observed + 1e-12)
        if extreme:
            count += 1
    return count / total
