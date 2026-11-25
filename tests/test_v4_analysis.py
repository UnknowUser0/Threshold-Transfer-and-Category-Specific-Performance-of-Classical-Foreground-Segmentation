"""Non-destructive tests for the V4 post-hoc analysis."""
from pathlib import Path
import shutil
import sys
import json
import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyze_v4 import (load_and_validate, category_means, category_winners, tuned_default, failure_cases, transfer_descriptive, run, METHODS)

CONF = ROOT/'working/results-v3-confirmatory'
DEV = ROOT/'working/results-v3-development'


def test_nonoverlap_and_frozen_mode():
    d,z,m,info=load_and_validate(CONF,DEV)
    assert len(m)==27*4
    assert set(m.seq).isdisjoint(set(z.seq))
    assert info['cfg']['mode']=='confirmatory'
    assert len(m.condition.unique())==6


def test_category_f1_matches_frozen_v3():
    _,_,m,_=load_and_validate(CONF,DEV)
    cat=category_winners(category_means(m))
    original=pd.read_csv(CONF/'table_by_category.csv').set_index('Kategori')
    for method,src_col in zip(METHODS.values(),['B1 Frame Difference','B2 MOG2','B3 KNN','B4 Farneback']):
        # V3 table is rounded to 3 decimals.
        assert np.allclose(cat.set_index('category').loc[original.index,method].to_numpy(),original[src_col].to_numpy(),atol=0.00051)


def test_tuning_effect_has_all_methods_and_six_categories():
    d,_,_,_=load_and_validate(CONF,DEV)
    seq,cat=tuned_default(d)
    assert len(seq)==27*4
    assert len(cat)==6*4
    assert np.isfinite(seq.f1_delta_tuned_minus_default).all()


def test_reversals_independently_recomputed():
    _,_,m,_=load_and_validate(CONF,DEV)
    pairs=failure_cases(m)
    row=pairs.set_index('seq').loc['PTZ/intermittentPan']
    assert row.knn_minus_fd<0
    assert row.mog2_minus_fd<0
    assert row['best_method']=='Frame Difference'


def test_phase_table_is_descriptive():
    d,z,m,_=load_and_validate(CONF,DEV)
    tab=transfer_descriptive(d,z)
    assert tab[tab.phase=='development'].category.nunique()==5
    assert tab[tab.phase=='confirmatory'].category.nunique()==6


def test_wrong_mode_rejected(tmp_path):
    # Test on minimal copied CSV+JSON fixtures without requiring symlink privileges.
    tmp=tmp_path/'wrong'
    tmp.mkdir()
    for f in ['all_per_seq.csv','table_hypotheses.csv','table_by_category.csv']:
        shutil.copy2(CONF/f, tmp/f)
    info=json.loads((CONF/'run_info.json').read_text());info['cfg']['mode']='development'
    (tmp/'run_info.json').write_text(json.dumps(info))
    with pytest.raises(ValueError,match='confirmatory'):
        load_and_validate(tmp,DEV)


def test_cli_output_isolated(tmp_path):
    output=tmp_path/'analysis'
    manifest=run(CONF, DEV, output)
    assert len(list(output.glob('table_v4_*.csv')))==8
    assert len(list(output.glob('fig_v4_*.png')))==4
    assert manifest['overlap_sequences']==0
    assert 'Exploratory' in (output/'REPORT_V4.md').read_text()
    assert not (CONF/'fig_v4_category_heatmap.png').exists()
