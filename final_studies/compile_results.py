"""Consolidate *existing* results with explicit phase labels; no experiments are rerun."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

METHODS={'B1t':'Frame Difference','B2t':'MOG2','B3t':'KNN','B4t':'Farneback'}

def build(root:Path):
    root=Path(root)
    paper=root/'paper'
    paper.mkdir(exist_ok=True)
    records=[]; phases=[]
    for phase in ('development','confirmatory'):
        base=root/'working'/f'results-v3-{phase}'
        x=pd.read_csv(base/'all_per_seq.csv')
        splits=pd.read_csv(base/'splits.csv')
        selected=x[(x.exp.isin(METHODS)) & (x.split=='test')].copy()
        for (cat,method),sub in selected.groupby(['condition','exp']):
            records.append({'phase':'development_test_inspected' if phase=='development' else 'later_category_disjoint_test',
                            'category':cat,'method':METHODS[method],'experiment':method,
                            'n_sequences':sub.seq.nunique(),'category_mean_pixel_f1':sub.px_f.mean(),
                            'mean_sequence_fpr':sub.px_fpr.mean(), 'mean_sequence_fnr':sub.px_fnr.mean()})
        phases.append({'phase':phase,'total_sequences':splits.seq.nunique(),
                       'tune_sequences':int((splits.split=='tune').sum()),
                       'test_sequences':int((splits.split=='test').sum()),
                       'categories':sorted(splits.category.unique().tolist())})
    d=pd.DataFrame(records)
    d.to_csv(paper/'COMBINED_CATEGORY_RESULTS_PHASE_LABELED.csv',index=False)
    pivot=d.pivot_table(index=['phase','category'],columns='method',values='category_mean_pixel_f1').reset_index()
    pivot.to_csv(paper/'COMBINED_F1_11_CATEGORIES_PHASE_LABELED.csv',index=False)
    pivot=pivot.sort_values(['phase','category'])
    methods=list(METHODS.values())
    fig,ax=plt.subplots(figsize=(12,7.4))
    matrix=pivot[methods].values
    chart=ax.imshow(matrix,cmap='viridis',vmin=0,vmax=1,aspect='auto')
    ax.set_xticks(np.arange(len(methods)),methods)
    ax.set_yticks(np.arange(len(pivot)),[f"{str(row.phase).split('_')[0]} · {row.category}" for row in pivot.itertuples()])
    for i in range(len(pivot)):
        for j in range(len(methods)):
            ax.text(j,i,f'{matrix[i,j]:.3f}',ha='center',va='center',fontsize=8,
                    color='white' if matrix[i,j]<.47 else 'black')
    dev_n=int((pivot.phase=='development_test_inspected').sum())
    ax.axhline(dev_n-.5,color='white',linewidth=3)
    ax.set_title('Eleven CDnet2014 categories, TWO different data phases (not one held-out test)')
    fig.colorbar(chart,ax=ax,shrink=.6,label='Category mean pixel F1')
    fig.tight_layout();fig.savefig(paper/'FIG_ALL_11_CATEGORIES_PHASED.png',dpi=175)
    fig.savefig(paper/'FIG_ALL_11_CATEGORIES_PHASED.pdf');plt.close(fig)
    narrative='''# Master evidence: integrated CDnet2014 phases\n\n'''
    narrative+='The archive contains **26 development sequences across five categories** (10 tune/16 development test) and **27 disjoint subsequent evaluation sequences across six categories**. All eleven CDnet categories appear, but the full 53 are **NOT** 53 independent confirmatory test observations. The two phases cannot be pooled without flagging prior outcome inspection.\n\n'
    narrative+='The original evaluation was at a working width of 320 pixels with category-level inference; supplementary studies require original videos.\n\n'
    narrative+='## Phase inventory\n\n'+pd.DataFrame(phases).to_markdown(index=False)+'\n\n'
    narrative+='## Category-level F1 (phase labeled)\n\n'+pivot.to_markdown(index=False,floatfmt='.3f')+'\n\n'
    narrative+='### Scientific disclosure\n\n* The development test was inspected during threshold-grid iterations.\n* One-sided preprocessing hypothesis findings rely on prior, externally provable directional hypothesis timing.\n* Full 53-sequence performance must not be advertised as an independently held-out result.\n* Modern comparator, temporal trajectories, and native-resolution outputs cannot be claimed until real videos/predictions are processed.\n'
    (paper/'EVIDENCE_MASTER.md').write_text(narrative,encoding='utf-8')
    info={'phases':phases,'category_result_rows':len(records),
          'figure':'FIG_ALL_11_CATEGORIES_PHASED.png',
          'claim_policy':'Development and confirmatory result sets remain separate; exploratory analyses carry no new p values.'}
    (paper/'EVIDENCE_MANIFEST.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    return info
if __name__=='__main__':
    print(json.dumps(build(Path(__file__).resolve().parents[1]),indent=2))
