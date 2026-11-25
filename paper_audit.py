"""Audit whether a real experiment produced expected outputs and respected the phase.

Does not certify scientific novelty, independence beyond metadata, or SINTA eligibility.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from paper_protocol import UNSEEN_CATEGORIES, load_seen

REQUIRED = ('run_info.json', 'splits.csv', 'all_per_seq.csv', 'report.md',
            'table_main.csv', 'table_by_category.csv', 'table_hypotheses.csv',
            'stats_primary.csv', 'fig_main.pdf', 'fig_ablation.pdf', 'table_fps.csv')


def audit(path: Path):
    issues = []
    for x in REQUIRED:
        if not (path/x).is_file() or (path/x).stat().st_size == 0:
            issues.append('Missing/empty: ' + x)
    if issues:
        return issues, None
    info = json.loads((path/'run_info.json').read_text(encoding='utf-8'))
    splits = pd.read_csv(path/'splits.csv')
    scores = pd.read_csv(path/'all_per_seq.csv')
    mode = info['cfg']['mode']
    if sorted(splits['seq'].unique()) != sorted(scores['seq'].unique()):
        issues.append('Sequence mismatch between splits.csv and all_per_seq.csv')
    if any('/synthetic_' in s for s in splits['seq']):
        issues.append('SYNTHETIC FIXTURE DETECTED: never use synthetic integration tests as evidence for a paper')
    if mode == 'confirmatory':
        if set(splits['category']) != set(UNSEEN_CATEGORIES):
            issues.append('Unexpected confirmatory category selection')
        if set(splits['split']) != {'test'}:
            issues.append('Confirmatory cannot have tune split')
        seen = load_seen(Path(__file__).resolve().parent/'protocol'/'seen_v2.json')
        overlap = sorted(seen & set(splits['seq']))
        if overlap:
            issues.append('Previously seen sequences found: ' + ', '.join(overlap))
        if info['tuned_params'] != json.loads((Path(__file__).resolve().parent/'protocol'/'frozen_v2_params.json').read_text()):
            issues.append('Thresholds differ from frozen v2 values')
        if info['cfg']['resize_width'] != 320 or info['cfg']['run_tuning']:
            issues.append('Confirmatory threshold or resolution guard failed')
        if not info['cfg'].get('run_ablation'):
            issues.append('Preregistered preprocessing ablation was disabled')
        if info['cfg'].get('n_boot', 0) < 5000:
            issues.append('Publication run requires >=5000 bootstrap resamples')
        if info['cfg'].get('bench_repeats', 0) < 5:
            issues.append('Publication run requires >=5 independent benchmark repetitions')
        if splits.groupby('category')['seq'].nunique().min() < 4:
            issues.append('Incomplete category coverage')
    else:
        issues.append('This is a DEVELOPMENT/EXPLORATORY run, not independent confirmation')
    for col in ('px_f', 'px_precision', 'px_recall'):
        if scores[col].isna().any():
            issues.append(f'Missing {col} in {int(scores[col].isna().sum())} per-sequence experiments')
    return issues, {'phase': mode, 'sequences': splits.seq.nunique(),
                    'categories': sorted(splits.category.unique()),
                    'methods': scores.algo.nunique(), 'rows': len(scores)}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('result_dir', type=Path)
    args = p.parse_args()
    issues, summary = audit(args.result_dir)
    print(json.dumps({'audit_passed': not issues, 'summary': summary, 'issues': issues}, indent=2))
    sys.exit(0 if not issues else 1)
