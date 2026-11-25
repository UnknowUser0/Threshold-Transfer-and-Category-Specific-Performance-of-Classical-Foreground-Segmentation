"""Frozen-parameter resolution sensitivity. Reruns video; requires original CDnet.

Outcomes are exploratory. Thresholds intentionally stay constant across sizes.
To avoid pretending upsampling is native data, requested width is capped at native.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from paper_protocol import score_pixel_counts
from .core import METHODS,FrozenMotion,load_frozen,load_sequence,bgr_from_path,groundtruth,metrics
from .temporal import PILOT

def evaluate(dataset,seqid,width,frozen,max_eval_frames=None):
    native=load_sequence(dataset,seqid,None).size[0]
    effective=min(width,native) if width else native
    seq=load_sequence(dataset,seqid,effective)
    det={m:FrozenMotion(m,frozen,seq.size) for m in METHODS}
    counts={m:np.zeros(4,dtype=np.int64) for m in METHODS}
    scored=0
    for n,fp in seq.inputs.items():
        if n>seq.roi_end:break
        frame=bgr_from_path(seq,fp)
        outputs={m:det[m].process(frame,seq.roi) for m in METHODS}
        if n<seq.roi_start or n not in seq.gt:continue
        gt=groundtruth(seq,n)
        for m in METHODS: counts[m]+=score_pixel_counts(outputs[m],gt,seq.roi)
        scored+=1
        if max_eval_frames is not None and scored>=max_eval_frames:break
    if not scored:raise ValueError(f'No scoring frames: {seqid}')
    result=[]
    for m,c in counts.items():
        result.append({'sequence':seqid,'category':seq.category,'method':m,'requested_width':width or 'native',
                       'actual_width':effective,'native_width':native,'evaluated_frames':scored,
                       **dict(zip(('tp','fp','fn','tn'),map(int,c))),**metrics(*c)})
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',required=True,type=Path)
    p.add_argument('--out',type=Path,default=Path('working/final-resolution'))
    p.add_argument('--sequences',nargs='+',default=list(PILOT))
    p.add_argument('--widths',nargs='+',default=['320','640','native'])
    p.add_argument('--max-eval-frames',type=int)
    a=p.parse_args(argv)
    frozen=load_frozen(Path(__file__).resolve().parents[1]/'protocol/frozen_v2_params.json')
    cv2.setNumThreads(1)
    widths=[None if str(x).lower()=='native' else int(x) for x in a.widths]
    allrows=[]
    for s in a.sequences:
        for w in widths:
            allrows.extend(evaluate(a.dataset,s,w,frozen,a.max_eval_frames))
            print(s,'width',w,'completed',flush=True)
    a.out.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(allrows)
    df.to_csv(a.out/'resolution_results.csv',index=False)
    for seq,g in df.groupby('sequence'):
        fig,ax=plt.subplots(figsize=(8.5,4.5))
        for method,sub in g.groupby('method'):
            sub=sub.sort_values('actual_width')
            ax.plot(sub.actual_width,sub.f1,marker='o',label=method)
        ax.set_xlabel('Actual frame width (px)');ax.set_ylabel('Pixel F1 (pooled counts)')
        ax.set_ylim(0,1);ax.legend(fontsize=8)
        ax.set_title(seq+' / EXPLORATORY')
        fig.tight_layout()
        fig.savefig(a.out/(seq.replace('/','__')+'.png'),dpi=160);plt.close(fig)
    (a.out/'run_manifest.json').write_text(json.dumps({
        'analysis_phase':'POST-HOC EXPLORATORY',
        'dataset':'user-supplied CDnet2014; local path omitted','sequences':a.sequences,'widths':a.widths,
        'max_eval_frames':a.max_eval_frames,
        'threshold_policy':'Frozen numeric 320px params reused across all widths; not rescaled',
        'comparison_limitation':'Native dimensions vary; requested 640 capped at native width; 640 and native coincide for PTZ/intermittentPan',
        'no_new_confirmation':True},indent=2),encoding='utf-8')
    print('EXPLORATORY RESOLUTION OUTPUT',a.out)
if __name__=='__main__':main()
