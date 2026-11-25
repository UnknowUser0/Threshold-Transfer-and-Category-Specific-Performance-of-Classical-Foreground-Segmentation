from pathlib import Path
import json
import numpy as np
import pytest
from paper_protocol import (score_pixel_counts, category_signflip_p,
                            validate_protocol, DEV_CATEGORIES, UNSEEN_CATEGORIES, load_seen)


def test_ignore_unknown_and_outside_roi():
    # GT labels 255 foreground; 50 shadow = background; 85/170 excluded
    gt = np.array([[255, 0, 50], [85, 170, 255]], dtype=np.uint8)
    pred = np.array([[255, 255, 0], [255, 255, 0]], dtype=np.uint8)
    roi = np.array([[255, 255, 0], [255, 255, 255]], dtype=np.uint8)
    # Pixel 50 is outside ROI and therefore not counted.
    assert score_pixel_counts(pred, gt, roi) == (1, 1, 1, 0)


def test_roi_filters_gt_and_prediction():
    gt = np.array([[255, 255], [0, 0]], np.uint8)
    pred = np.array([[0, 255], [255, 255]], np.uint8)
    roi = np.array([[0, 255], [255, 0]], np.uint8)
    assert score_pixel_counts(pred, gt, roi) == (1, 1, 0, 0)


def test_gt_unknown_class_fail_fast():
    with pytest.raises(ValueError, match='Unexpected GT labels'):
        score_pixel_counts(np.zeros((2, 2), np.uint8), np.full((2, 2), 99, np.uint8))


def test_exact_category_signflip():
    assert category_signflip_p(np.array([1., 1., 1., 1., 1., 1.])) == pytest.approx(2/64)
    assert category_signflip_p(np.array([0., 0., 0., 0., 0., 0.])) == 1.0
    assert category_signflip_p(np.array([2., -2.])) == 1.0
    assert category_signflip_p(np.ones(6), alternative='greater') == pytest.approx(1/64)
    assert category_signflip_p(-np.ones(6), alternative='less') == pytest.approx(1/64)
    assert category_signflip_p(-np.ones(6), alternative='greater') == 1.0


def get_cfg(tmp_path, mode='confirmatory'):
    p = tmp_path/'params.json'
    p.write_text('{"frame_diff":{"fixed_thr":5}}')
    h = tmp_path/'seen.json'
    h.write_text(json.dumps({'seen_sequences': ['baseline/highway']}))
    cfg = dict(mode=mode, categories=list(UNSEEN_CATEGORIES if mode == 'confirmatory' else DEV_CATEGORIES),
               run_tuning=False, tune_per_category=0, tuned_params_file=str(p),
               max_seqs_per_category=None, max_eval_frames=None, sequences=None, resize_width=320)
    seqs = [{'id': f'{cat}/fresh_{i}', 'category': cat, 'n_scored': 5}
            for cat in UNSEEN_CATEGORIES for i in range(4)]
    return cfg, seqs, h


def test_seen_sequence_blocked(tmp_path):
    cfg, seqs, seen = get_cfg(tmp_path)
    seqs[0]['id'] = 'baseline/highway'
    with pytest.raises(ValueError, match='LEAKAGE'):
        validate_protocol(cfg, seqs, seen)


def test_tuning_blocked(tmp_path):
    cfg, seqs, seen = get_cfg(tmp_path)
    cfg['run_tuning'] = True
    with pytest.raises(ValueError, match='tuning is forbidden'):
        validate_protocol(cfg, seqs, seen)


def test_partial_categories_blocked(tmp_path):
    cfg, seqs, seen = get_cfg(tmp_path)
    with pytest.raises(ValueError, match='COVERAGE'):
        validate_protocol(cfg, seqs[:-4], seen)


def test_resolution_mismatch_blocked(tmp_path):
    cfg, seqs, seen = get_cfg(tmp_path)
    cfg['resize_width'] = None
    with pytest.raises(ValueError, match='320px'):
        validate_protocol(cfg, seqs, seen)


def test_confirmatory_valid(tmp_path):
    cfg, seqs, seen = get_cfg(tmp_path)
    audit = validate_protocol(cfg, seqs, seen)
    assert audit['overlap'] == 0
    assert audit['total_sequences'] == 24
    assert len(audit['category_counts']) == 6


def test_original_manifest_exists():
    seen = load_seen(Path(__file__).parents[1]/'protocol'/'seen_v2.json')
    assert len(seen) == 26
    assert 'baseline/highway' in seen
