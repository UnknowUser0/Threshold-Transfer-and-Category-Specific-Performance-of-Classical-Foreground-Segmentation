"""Synthetic-only integration; under no circumstances cite fixture scores as study outcomes."""
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import pytest
from tests.make_synthetic_cdnet import make_fixture
from final_studies.core import (load_sequence, score_pixel_counts, load_frozen, FrozenMotion, metrics)
from final_studies.temporal import run_one
from final_studies.resolution import evaluate
from final_studies.external_masks import evaluate_model

@pytest.fixture
def mini(tmp_path):
    d=tmp_path/'dataset'
    make_fixture(d,mode='confirmatory')
    return d

def test_label_and_roi(mini):
    s=load_sequence(mini,'PTZ/synthetic_1',32)
    assert s.size==(32,24)
    gt=np.array([[255,0,50,85,170]],dtype=np.uint8)
    mask=np.array([[255,255,255,255,255]],dtype=np.uint8)
    assert score_pixel_counts(mask,gt)==(1,2,0,0)
    assert score_pixel_counts(mask,gt,np.array([[255,0,255,255,255]],dtype=np.uint8))==(1,1,0,0)

def test_frozen_guard(tmp_path):
    p=tmp_path/'p.json';p.write_text('{"frame_diff":{"fixed_thr":33}}')
    with pytest.raises(ValueError,match='Frozen'):
        load_frozen(p)

def test_diagnostics_mini(mini,tmp_path):
    res,meta=run_one(mini,'PTZ/synthetic_1',tmp_path/'temporal',32)
    assert meta['evaluated_frames']==7
    assert set(res.algorithm)=={'frame_diff','mog2','knn','farneback'}
    assert (tmp_path/'temporal/PTZ/synthetic_1/per_frame.csv').exists()
    assert (tmp_path/'temporal/PTZ/synthetic_1/temporal.png').exists()
    assert (tmp_path/'temporal/PTZ/synthetic_1/manifest.json').exists()
    full=load_frozen(Path(__file__).resolve().parents[1]/'protocol/frozen_v2_params.json')
    a=evaluate(mini,'PTZ/synthetic_1',32,full,max_eval_frames=3)
    assert all(z['evaluated_frames']==3 for z in a)
    assert len(a)==4

def test_external_strict_coverage(mini,tmp_path):
    root=tmp_path/'predictions';seq='PTZ/synthetic_1';d=root/'new_model'/seq
    d.mkdir(parents=True)
    for n in range(3,10):
        cv2.imwrite(str(d/f'fg{n:06d}.png'),np.zeros((24,32),dtype=np.uint8))
    with pytest.raises(ValueError,match='dimension mismatch'):
        evaluate_model(mini,root,'new_model',[seq])
    data=evaluate_model(mini,root,'new_model',[seq],allow_resize=True)
    assert len(data)==1 and data.iloc[0]['resized_masks']==7
    (d/'fg000006.png').unlink()
    with pytest.raises(ValueError,match='Incomplete predictions'):
        evaluate_model(mini,root,'new_model',[seq],allow_resize=True)
