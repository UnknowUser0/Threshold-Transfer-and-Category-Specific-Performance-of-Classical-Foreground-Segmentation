#!/usr/bin/env python3
"""V4 read-only post-hoc analysis of frozen V3 results.

No training, tuning, detector inference or modification of the original V3 outputs.
CSV, figures and a descriptive report are stored in a separate V4 directory.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

METHODS = {"B1t": "Frame Difference", "B2t": "MOG2", "B3t": "KNN", "B4t": "Farneback"}
DEFAULTS = {"B1t": "B1", "B2t": "B2", "B3t": "B3", "B4t": "B4"}
EXPECT_CATEGORIES = {'PTZ','cameraJitter','intermittentObjectMotion','lowFramerate','thermal','turbulence'}
DEV_CATEGORIES = {'badWeather','baseline','dynamicBackground','nightVideos','shadow'}
CORE_FILES = ['all_per_seq.csv', 'run_info.json', 'table_hypotheses.csv', 'table_by_category.csv']
REQUIRED = {'exp','algo','seq','condition','split','px_tp','px_fp','px_fn','px_tn','px_f','px_fpr','px_fnr','px_precision','px_recall'}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def load_and_validate(conf: Path, dev: Path):
    for f in CORE_FILES:
        if not (conf / f).is_file():
            raise FileNotFoundError(f'Required confirmatory source is missing: {conf / f}')
    d = pd.read_csv(conf / 'all_per_seq.csv')
    z = pd.read_csv(dev / 'all_per_seq.csv')
    missed = REQUIRED - set(d.columns)
    if missed:
        raise ValueError('Missing source columns: '+', '.join(sorted(missed)))
    info = json.loads((conf / 'run_info.json').read_text(encoding='utf-8'))
    if info['cfg']['mode'] != 'confirmatory':
        raise ValueError('Source must be confirmed confirmatory V3 data.')
    if set(info['cfg']['categories']) != EXPECT_CATEGORIES:
        raise ValueError('Source category set differs from frozen V3 confirmatory categories.')
    if info['cfg']['run_tuning'] or info['cfg']['tune_per_category'] != 0:
        raise ValueError('Tuning was enabled; cannot use as frozen confirmatory source.')
    if not (d['split'].eq('test').all()):
        raise ValueError('V3 confirmatory source contains non-test split rows.')
    main = d[d.exp.isin(METHODS)].copy()
    if set(main.condition.unique()) != EXPECT_CATEGORIES or main.seq.nunique() != 27:
        raise ValueError('Unexpected confirmatory categories or sequence count.')
    if main.duplicated(['seq','exp']).any():
        raise ValueError('Duplicate sequence-method observations.')
    if main.groupby('seq').exp.nunique().ne(4).any():
        raise ValueError('Some sequences have missing tuned-method rows.')
    if set(main.seq.unique()) & set(z.seq.unique()):
        raise ValueError('Data leakage: development sequence overlaps confirmatory sequences.')
    if set(z.condition.unique()) != DEV_CATEGORIES:
        raise ValueError('Unexpected categories in development dataset.')
    if info.get('protocol_audit', {}).get('overlap') != 0:
        raise ValueError('V3 protocol reported historical overlap.')
    for seq, g in main.groupby('seq'):
        positives = (g.px_tp + g.px_fn).astype('int64')
        negatives = (g.px_tn + g.px_fp).astype('int64')
        if positives.nunique() != 1 or negatives.nunique() != 1:
            raise ValueError(f'GT pixel-count mismatch across algorithms: {seq}')
        f = np.divide(2*g.px_tp, 2*g.px_tp + g.px_fp + g.px_fn, out=np.zeros(len(g)),where=(2*g.px_tp + g.px_fp + g.px_fn).to_numpy()!=0)
        if not np.allclose(f, g.px_f, rtol=0, atol=1e-8):
            raise ValueError(f'F1 calculation mismatch on {seq}')
    return d, z, main, info


def category_means(main):
    cols = ['px_f','px_precision','px_recall','px_fpr','px_fnr','px_pwc']
    tab = main.groupby(['condition','exp'], observed=True)[cols].mean().reset_index().rename(columns={'condition':'category'})
    tab['method'] = tab.exp.map(METHODS)
    return tab


def sequence_profile(main):
    t = main[['seq','condition','exp','px_f','px_precision','px_recall','px_fpr','px_fnr','px_tp','px_fp','px_fn','px_tn']].copy()
    t = t.rename(columns={'condition':'category','px_f':'f1','px_precision':'precision','px_recall':'recall','px_fpr':'fpr','px_fnr':'fnr'})
    t['method'] = t.exp.map(METHODS)
    t['gt_pixel_prevalence'] = (t.px_tp+t.px_fn)/(t.px_tp+t.px_fp+t.px_fn+t.px_tn)
    t['error_profile'] = np.select([t.fpr > 0.01, t.fnr >= 0.75, t.fnr >= 0.5], ['high_FPR_over_1pct','high_FNR_ge_75pct','FNR_ge_50pct'], default='mixed_or_lower_errors')
    # This label is descriptive/heuristic, not a source of causal diagnosis.
    return t


def category_winners(cat):
    p = cat.pivot(index='category',columns='method',values='px_f')[list(METHODS.values())]
    p['winner'] = p.idxmax(axis=1)
    p['margin_to_runnerup'] = p.apply(lambda r: float(np.sort(r[list(METHODS.values())].to_numpy(dtype=float))[-1] - np.sort(r[list(METHODS.values())].to_numpy(dtype=float))[-2]), axis=1)
    return p.reset_index().sort_values('category')


def tuned_default(d):
    rows=[]
    for tuned, default in DEFAULTS.items():
        a=d[d.exp==tuned][['seq','condition','px_f']].rename(columns={'px_f':'tuned_f1'})
        b=d[d.exp==default][['seq','px_f']].rename(columns={'px_f':'default_f1'})
        m=a.merge(b, on='seq',how='inner',validate='one_to_one')
        if len(m)!=27:
            raise ValueError(f'Missing default/tuned pair: {tuned}')
        m['f1_delta_tuned_minus_default']=m.tuned_f1-m.default_f1
        m['method']=METHODS[tuned]
        rows.append(m.rename(columns={'condition':'category'}))
    allseq=pd.concat(rows,ignore_index=True)
    cat=allseq.groupby(['category','method'],as_index=False)[['tuned_f1','default_f1','f1_delta_tuned_minus_default']].mean()
    return allseq, cat


def failure_cases(main):
    profile = sequence_profile(main)
    # Negative differences are cases in which tuned FD outperforms a nominally stronger method.
    p=profile.pivot(index=['category','seq'], columns='method', values='f1').reset_index()
    p['knn_minus_fd']=p['KNN']-p['Frame Difference']
    p['mog2_minus_fd']=p['MOG2']-p['Frame Difference']
    p['stronger_of_knn_mog2_minus_fd']=p[['knn_minus_fd','mog2_minus_fd']].max(axis=1)
    p['best_method']=p[list(METHODS.values())].idxmax(axis=1)
    p['worst_method']=p[list(METHODS.values())].idxmin(axis=1)
    return p.sort_values(['stronger_of_knn_mog2_minus_fd','category'])


def transfer_descriptive(d, z):
    a=d[d.exp.isin(METHODS)].groupby(['condition','exp'],as_index=False)['px_f'].mean().assign(phase='confirmatory')
    b=z[z.exp.isin(METHODS)].groupby(['condition','exp'],as_index=False)['px_f'].mean().assign(phase='development')
    t=pd.concat([a,b],ignore_index=True).rename(columns={'condition':'category','px_f':'f1'})
    t['method']=t.exp.map(METHODS)
    return t.sort_values(['method','phase','category'])


def save_plot(fig, out, name):
    fig.tight_layout()
    for ext in ['png','pdf']:
        fig.savefig(out / f'{name}.{ext}',dpi=210,bbox_inches='tight')
    plt.close(fig)


def figures(out, winners, cat, bycat_tuning, transfer):
    names=list(METHODS.values())
    p=winners.set_index('category')[names].sort_index()
    fig,ax=plt.subplots(figsize=(10.4,5.6))
    im=ax.imshow(p.to_numpy(),cmap='Greys',vmin=0,vmax=1,aspect='auto')
    ax.set_yticks(range(len(p)),labels=p.index)
    ax.set_xticks(range(len(names)),labels=names,rotation=20,ha='right')
    for i in range(len(p)):
        for j in range(len(names)):
            val=p.iloc[i,j];ax.text(j,i,f'{val:.3f}',va='center',ha='center',color='white' if val>.55 else 'black',fontweight='bold' if val==p.iloc[i].max() else 'normal',fontsize=10)
    fig.colorbar(im,ax=ax,label='Pixel F1 (equal sequence weight within category)')
    ax.set_title('Frozen V3 confirmatory: F1 by category and method')
    save_plot(fig,out,'fig_v4_category_heatmap')

    fig,axes=plt.subplots(1,2,figsize=(12,5),sharey=True)
    for ax,phase in zip(axes,['development','confirmatory']):
        part=transfer[transfer.phase==phase]
        offsets=np.linspace(-.23,.23,4)
        for i,m in enumerate(names):
            x=part[part.method==m].f1.to_numpy(dtype=float)
            ax.scatter(np.ones(len(x))*i+offsets[i],x,s=42,alpha=.75,label=m)
            ax.plot([i-.21,i+.21],[x.mean(),x.mean()],lw=2,color='black')
        ax.set_xticks(range(4),labels=names,rotation=20,ha='right')
        ax.set_ylim(0,1);ax.set_title(f'{phase.title()} categories (n={part.category.nunique()})')
        ax.set_ylabel('Category-level F1')
        ax.grid(axis='y',alpha=.15)
    fig.suptitle('Descriptive category-shift comparison — NOT a paired experiment')
    save_plot(fig,out,'fig_v4_category_shift')

    arr=bycat_tuning.pivot(index='category',columns='method',values='f1_delta_tuned_minus_default').reindex(columns=names).sort_index()
    fig,ax=plt.subplots(figsize=(10.5,5.2))
    vmax=max(abs(arr.to_numpy().min()),abs(arr.to_numpy().max()),.001)
    im=ax.imshow(arr.to_numpy(),vmin=-vmax,vmax=vmax,cmap='coolwarm',aspect='auto')
    ax.set_yticks(range(len(arr)),labels=arr.index);ax.set_xticks(range(len(names)),labels=names,rotation=20,ha='right')
    for i in range(len(arr)):
        for j in range(len(names)):
            ax.text(j,i,f'{arr.iloc[i,j]:+.3f}',va='center',ha='center',fontsize=9)
    fig.colorbar(im,ax=ax,label='Tuned F1 minus default F1')
    ax.set_title('Transfer of frozen threshold tuning to new categories')
    save_plot(fig,out,'fig_v4_tuned_minus_default')

    fig,axes=plt.subplots(1,2,figsize=(13,5.3))
    keys=['px_fpr','px_fnr']
    for ax,metric in zip(axes,keys):
        part=cat.pivot(index='category',columns='method',values=metric).reindex(columns=names).sort_index()
        for m in names:
            ax.plot(range(len(part)),part[m].to_numpy(),marker='o',label=m)
        ax.set_xticks(range(len(part)), labels=part.index,rotation=35,ha='right')
        ax.set_ylabel('FPR' if metric=='px_fpr' else 'FNR')
        ax.set_title('False-positive rate' if metric=='px_fpr' else 'False-negative rate')
        ax.grid(alpha=.18)
    axes[1].legend(loc='best',fontsize=8)
    fig.suptitle('Descriptive error decomposition — category means')
    save_plot(fig,out,'fig_v4_fpr_fnr')


def build_report(out, info, winners, cat, bycat_tuning, transfer, failure, hypotheses, hashes):
    fmt=lambda x: f'{float(x):.3f}'
    cats=winners.set_index('category')
    tab='| Category | FD F1 | MOG2 F1 | KNN F1 | Farneback F1 | Top method |\n|---|---:|---:|---:|---:|---|\n'
    for name,r in cats.iterrows():
        tab+= f'| {name} | {fmt(r["Frame Difference"])} | {fmt(r["MOG2"])} | {fmt(r["KNN"])} | {fmt(r["Farneback"])} | {r.winner} |\n'
    hyp='| Hypothesis | Original p one-sided | Original p Holm | Original decision |\n|---|---:|---:|---|\n'
    for _,r in hypotheses.iterrows():
        hyp+=f'| {r["Hipotesis"]} | {r["p satu sisi kategori"]:.3f} | {r["p Holm"]:.3f} | {r["Keputusan statistik"]} |\n'
    tuned=bycat_tuning.groupby('method')['f1_delta_tuned_minus_default'].mean().reindex(list(METHODS.values()))
    dominant = cat.groupby('method')[['px_fpr','px_fnr']].mean()
    mis= failure[failure.best_method=='Frame Difference']
    worst= failure[['category','seq','knn_minus_fd','mog2_minus_fd']].sort_values('knn_minus_fd').head(7)
    worstt=worst.to_markdown(index=False,floatfmt='.3f')
    report=f'''# V4: Frozen-V3 post-hoc generalization and failure-mode analysis

**Evidence status:** Exploratory, descriptive secondary analysis of the existing V3 confirmatory results. **NO new independent test set or new confirmatory claims.**\n
**Input:** 27 sequences / 6 unseen-by-V2 categories; 320 px width; fixed parameters; 4 tuned algorithms. V3 prior development = 26 sequences / 5 different categories. Source V3 already tested; all V4 plots/tables are post-hoc.\n
## Reproduced V3 hypothesis decisions (original protocol — not re-tested in V4)

{hyp}

Note: p values for H3-H4 use the designated one-sided hypothesis family. The broader exploratory factorial comparisons have DIFFERENT Holm correction families. Do not substitute one for the other. A one-sided claim requires a defensible prior-time-stamped directional hypothesis.

## Category-level outcomes (mean of sequence F1, equal category weight for headline summary)

{tab}

The winner varies by category. The PTZ advantage of FD is not a mechanistic explanation; inspect frame masks and movements to test competing explanations.\n
## Frozen threshold transfer

| Method | Mean category-level tuned minus default F1 |\n|---|---:|\n'''
    for m,val in tuned.items(): report+=f'| {m} | {val:+.4f} |\n'
    report+='''\nMethod-level tuning gains on the development categories cannot guarantee gains in categories with different scene dynamics. Any post-hoc threshold refinement would invalidate a confirmatory-transfer interpretation unless evaluated on a new untouched test set.\n
## Selected sequence-level reversals (exploratory)\n
'''+worstt+'''\n\nA negative KNN-minus-FD value means FD performed better for that sequence. These are ranked for qualitative inspection, not statistical discovery.\n
## Interpretation constraints

1. **Scene-category shift is confounded with scene composition**. Development and confirmatory categories are disjoint and not randomized matched pairs; avoid attributing mean gaps solely to overfitting.\n2. **Aggregated confusion counts lack temporal resolution**. A high FPR/FNR tells what type of pixel error occurred, not whether its cause was camera motion, static foreground absorption, illumination, thermal noise, or another mechanism. Failure-cause claims require frame-by-frame evidence or additional measurements.\n3. **Statistical unit** for hypothesis testing is category (n=6), not 27 independent categories. V4 ranking and plots carry no newly confirmed p-values.\n4. **Metric resolution** is 320px, not native resolution; frame MCC and box F1 are secondary and some MCC observations are missing.\n5. **Numerical comparability** with online leaderboard requires identical training assumptions, evaluation frames, GT interpretation, and pixel resolution. Our within-study scores must not be reported as benchmark leaderboard scores.\n6. **History**: confirmatory status is conditional on these categories never having informed earlier parameter choice. A manifest overlap check cannot prove absence of previous manual inspection.\n
## Suggested evidence acquisition (new study, separately preregistered)\n
- Produce frame-aligned qualitative panels on PTZ and turbulence with the same frame IDs across algorithms, GT and predictions; write the selection rule before review.\n- Record per-frame FP, FN, GT foreground area and camera-motion proxy; analyze temporal trajectories with sequence-level replication. This cannot be reconstructed from the V3 aggregate CSV alone.\n- Run native-resolution sensitivity with frozen algorithms/thresholds, label it follow-up exploratory unless a fresh test set is reserved.\n- Add one modern algorithm baseline with clearly specified adaptation/training assumptions and computational budget.\n
## Original evidence hashes (SHA-256)\n\n'''
    for name,val in hashes.items():report+=f'- `{name}`: `{val}`\n'
    report+='''\nGenerated V4 outputs are derived from unchanged V3 files. No new detector predictions were created.\n'''
    (out/'REPORT_V4.md').write_text(report,encoding='utf-8')


def run(conf:Path,dev:Path,out:Path):
    conf=conf.resolve();dev=dev.resolve();out=out.resolve()
    if out==conf or out==dev or conf in out.parents or dev in out.parents:
        raise ValueError('V4 output must NOT be inside V3 input directories.')
    out.mkdir(parents=True,exist_ok=True)
    d,z,main,info=load_and_validate(conf,dev)
    cat=category_means(main)
    winners=category_winners(cat)
    seq=sequence_profile(main)
    tune_seq,tune_cat=tuned_default(d)
    failure=failure_cases(main)
    transfer=transfer_descriptive(d,z)
    hypotheses=pd.read_csv(conf/'table_hypotheses.csv')
    outputs={'table_v4_category_profile.csv':cat,'table_v4_category_winners.csv':winners,'table_v4_sequence_error_profiles.csv':seq,'table_v4_default_vs_tuned_sequences.csv':tune_seq,'table_v4_default_vs_tuned_category.csv':tune_cat,'table_v4_ranked_failure_cases.csv':failure,'table_v4_category_shift_descriptive.csv':transfer,'table_v4_frozen_v3_hypotheses.csv':hypotheses}
    for filename,df in outputs.items():df.to_csv(out/filename,index=False,float_format='%.9g')
    figures(out,winners,cat,tune_cat,transfer)
    hashes={f'confirmatory/{f}':sha256(conf/f) for f in CORE_FILES}
    for f in ['all_per_seq.csv','table_by_category.csv','run_info.json']:
        hashes[f'development/{f}']=sha256(dev/f)
    manifest={'analysis':'V4 read-only post-hoc','v3_confirmatory_mode':info['cfg']['mode'],'v3_confirmatory_sequences':main.seq.nunique(),'v3_confirmatory_categories':sorted(main.condition.unique().tolist()),'development_categories':sorted(z.condition.unique().tolist()),'overlap_sequences':len(set(main.seq)&set(z.seq)),'confirmatory_parameter_source':info['cfg']['tuned_params_file'],'v3_frozen_tuned_params':info.get('tuned_params'),'source_sha256':hashes,'generated_output_files':sorted([*outputs.keys(),'REPORT_V4.md','fig_v4_category_heatmap.png','fig_v4_category_shift.png','fig_v4_tuned_minus_default.png','fig_v4_fpr_fnr.png'])}
    build_report(out,info,winners,cat,tune_cat,transfer,failure,hypotheses,hashes)
    (out/'V4_PROVENANCE.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'V4 supplementary exploratory analysis complete: {out}')
    print(f'Validated {main.seq.nunique()} confirmatory sequences, {main.condition.nunique()} categories; {len(outputs)} tables and 4 figures.')
    return manifest


def main():
    project=Path(__file__).resolve().parent
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--confirmatory',type=Path,default=project/'working/results-v3-confirmatory')
    cli.add_argument('--development',type=Path,default=project/'working/results-v3-development')
    cli.add_argument('--out',type=Path,default=project/'working/results-v4-posthoc')
    args=cli.parse_args()
    run(args.confirmatory,args.development,args.out)

if __name__=='__main__':main()
