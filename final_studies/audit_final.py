"""Fail-closed consistency and provenance audit of existing CDnet2014 V3/V4 source results."""
from __future__ import annotations
import json,hashlib,sys
from pathlib import Path
import numpy as np
import pandas as pd
from paper_audit import audit

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(root:Path):
    root=Path(root).resolve()
    conf=root/'working/results-v3-confirmatory'
    dev=root/'working/results-v3-development'
    v4=root/'working/results-v4-posthoc'
    issues=[]
    original_issues,previous=audit(conf)
    issues.extend(original_issues)
    manifest=json.loads((v4/'V4_PROVENANCE.json').read_text())
    for name,digest in manifest['source_sha256'].items():
        stage,rel=name.split('/',1)
        p=(conf if stage=='confirmatory' else dev)/rel
        if not p.exists() or sha(p)!=digest:issues.append('SHA-256 mismatch: '+name)
    x=pd.read_csv(conf/'all_per_seq.csv')
    y=pd.read_csv(dev/'all_per_seq.csv')
    if set(x.seq)&set(y.seq):issues.append('Development and confirmation overlap')
    if x.seq.nunique()!=27 or y.seq.nunique()!=26:issues.append('Expected 27/26 sequences not found')
    if x.condition.nunique()!=6 or y.condition.nunique()!=5:issues.append('Expected 6/5 categories not found')
    if set(x.split)!= {'test'}:issues.append('All confirmatory rows must be test')
    if any(c not in x.columns for c in ('px_tp','px_fp','px_fn','px_tn','px_f')):
        issues.append('Missing pixel score columns')
    # recompute all four test means from raw per-sequence pixel counts and compare rounded V3 main table
    recalculated={}
    if not issues:
        sel=x[x.exp.isin(('B1t','B2t','B3t','B4t'))].copy()
        a=sel.px_tp.astype(float);b=sel.px_fp.astype(float);c=sel.px_fn.astype(float)
        sel['recalc_f1']=2*a/(2*a+b+c)
        if not np.allclose(sel.recalc_f1,sel.px_f,rtol=0,atol=1e-9,equal_nan=True):
            issues.append('Stored F1 and count-derived F1 mismatch')
        recalculated=sel.groupby(['exp','condition']).recalc_f1.mean().groupby('exp').mean().round(6).to_dict()
        targets={'B1t':0.230,'B2t':0.471,'B3t':0.483,'B4t':0.203}
        for method,v in recalculated.items():
            if abs(v-targets[method])>0.00051:issues.append(f'Reported F1 discrepancy {method}={v}')
    hs=pd.read_csv(conf/'table_hypotheses.csv')
    if len(hs)!=4:issues.append('Expected four hypotheses')
    required={
      'H1':('algoritma',False),'H2':('algoritma',False),
      'H3':('preprocessing',True),'H4':('preprocessing',True)}
    for k,(family,expected_sig) in required.items():
        z=hs[hs['Hipotesis'].str.startswith(k+':')]
        if len(z)!=1 or z.iloc[0]['Keluarga']!=family:
            issues.append('Hypothesis family mismatch '+k)
        elif (float(z.iloc[0]['p Holm'])<0.05)!=expected_sig:
            issues.append('Unexpected original significance decision '+k)
    prereg=root/'protocol/preregistration.json'
    if not prereg.exists():issues.append('No protocol disclosure available')
    temporal_outputs=root/'working/final-temporal'/'temporal_summary.csv'
    resolution_outputs=root/'working/final-resolution'/'resolution_results.csv'
    temporal_rows=None
    if temporal_outputs.exists():
        tf=pd.read_csv(temporal_outputs)
        temporal_rows=len(tf)
        if tf.sequence.nunique()!=3 or tf.algorithm.nunique()!=4:
            issues.append('Unexpected temporal pilot sequence/method coverage')
    resolution_rows=None
    if resolution_outputs.exists():
        rf=pd.read_csv(resolution_outputs)
        resolution_rows=len(rf)
        if len(rf)!=36 or rf.sequence.nunique()!=3 or rf.method.nunique()!=4:
            issues.append('Unexpected resolution pilot row/sequence/method count')
        counts_f1=2*rf.tp/(2*rf.tp+rf.fp+rf.fn)
        if not np.allclose(counts_f1,rf.f1,rtol=0,atol=1e-9,equal_nan=True):
            issues.append('Resolution F1 does not match pooled pixel counts')
    report={
      'technical_audit_passed':not issues,
      'target_journal':'IJCCS',
      'evaluation_phase':'V3 confirmatory metadata; independent preregistration date NOT independently verified',
      'original_audit':previous,
      'recomputed_category_mean_f1':recalculated,
      'hash_checks':len(manifest['source_sha256']),
      'followup_studies':{
       'temporal_pilot':'complete' if temporal_outputs.exists() else 'not_run',
       'temporal_summary_rows':temporal_rows,
       'resolution_pilot':'complete' if resolution_outputs.exists() else 'not_run',
       'resolution_rows':resolution_rows,
       'interpretation':'post-hoc exploratory; three selected sequences; no inferential claims'},
      'unverified':[
       'third-party evidence of preregistration timestamp',
       'independent third-party reproduction from raw video and annotations',
       'publication novelty, author declarations, and external-model training exposure',
       'visual Word pagination against IJCCS 10-12 page requirements',
       'peer-review outcome'],
      'issues':issues}
    return report

def main():
    root=Path(__file__).resolve().parents[1]
    r=run(root)
    (root/'FINAL_AUDIT.json').write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(r,indent=2,ensure_ascii=False))
    raise SystemExit(0 if r['technical_audit_passed'] else 1)
if __name__=='__main__':main()
