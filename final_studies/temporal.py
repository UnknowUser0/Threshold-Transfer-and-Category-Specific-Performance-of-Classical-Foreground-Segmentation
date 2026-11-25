"""Frame-by-frame post-hoc error trajectories, descriptive motion proxy, and overlays.

Example: python -m final_studies.temporal --dataset D:\\CDnet2014
All masks and predictions are recalculated from video; requires original dataset.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from paper_protocol import score_pixel_counts
from .core import METHODS,load_frozen, load_sequence, FrozenMotion, bgr_from_path, groundtruth, metrics, shift_proxy

PILOT=('PTZ/intermittentPan','turbulence/turbulence0','cameraJitter/badminton')

def illustration(frame, gt, masks):
    valid=np.isin(gt,(0,50,255))
    target=(gt==255) & valid
    panels=[frame,cv2.cvtColor((target*255).astype(np.uint8),cv2.COLOR_GRAY2BGR)]
    for m in METHODS:
        pred=(masks[m]>0)&valid
        overlay=frame.copy()
        # BGR: blue false positives, red false negatives, green true positives
        overlay[pred & ~target]=(255,80,35)
        overlay[~pred & target]=(35,35,255)
        overlay[pred & target]=(30,200,70)
        panels.append(overlay)
    top=np.concatenate(panels[:3],axis=1)
    bottom=np.concatenate([panels[3],panels[4],panels[5]],axis=1)
    return np.concatenate([top,bottom],axis=0)

def run_one(dataset:Path,sequence_id:str,out:Path,width:int|None=320,max_frames:int|None=None,per_frame_overlay:int=3):
    seq=load_sequence(dataset,sequence_id,width)
    frozen=load_frozen(Path(__file__).resolve().parents[1]/'protocol/frozen_v2_params.json')
    cv2.setNumThreads(1)
    dets={name:FrozenMotion(name,frozen,seq.size) for name in METHODS}
    t0=time.time()
    previous=None
    records=[]
    snapshots=[]
    n_evaluated=0
    for frame_id, path in seq.inputs.items():
        if frame_id>seq.roi_end:break
        frame=bgr_from_path(seq,path)
        previous,displacement,response,_=shift_proxy(previous,frame,seq.roi)
        masks={name:det.process(frame,seq.roi) for name,det in dets.items()}
        if frame_id<seq.roi_start or frame_id not in seq.gt:continue
        gt=groundtruth(seq,frame_id)
        per_method={}
        for name in METHODS:
            tp,fp,fn,tn=score_pixel_counts(masks[name],gt,seq.roi)
            d=metrics(tp,fp,fn,tn)
            rec={'sequence':sequence_id,'category':seq.category,'frame':frame_id,'algorithm':name,
                 'width':seq.size[0],'height':seq.size[1],
                 'tp':tp,'fp':fp,'fn':fn,'tn':tn,'shift_proxy_px':displacement,
                 'shift_response':response,**d}
            records.append(rec)
            per_method[name]=d
        n_evaluated+=1
        # Select frames AFTER seeing the data: illustrations are explicitly exploratory.
        v=per_method['frame_diff']['f1']-per_method['knn']['f1']
        if np.isfinite(v) and (len(snapshots)<per_frame_overlay or v>min(s[0] for s in snapshots)):
            snapshots.append((v,frame_id,frame.copy(),gt.copy(),{k:p.copy() for k,p in masks.items()}))
            snapshots=sorted(snapshots,key=lambda s:s[0],reverse=True)[:per_frame_overlay]
        if max_frames is not None and n_evaluated>=max_frames:break
    if not records:raise ValueError(f'No annotated frames for {sequence_id}')
    folder=out/seq.category/seq.name
    folder.mkdir(parents=True,exist_ok=True)
    df=pd.DataFrame(records)
    df.to_csv(folder/'per_frame.csv',index=False)
    sums=df.groupby('algorithm',sort=False)[['tp','fp','fn','tn']].sum()
    summ=[]
    for method,row in sums.iterrows():
        d=metrics(*[int(row[x]) for x in ('tp','fp','fn','tn')])
        summ.append({'sequence':sequence_id,'algorithm':method,'n_eval_frames':n_evaluated,
                     'width':seq.size[0], 'height':seq.size[1],**row.to_dict(),**d})
    pd.DataFrame(summ).to_csv(folder/'sequence_summary.csv',index=False)
    fig,axs=plt.subplots(2,1,figsize=(12,7),sharex=True,constrained_layout=True)
    for method,g in df.groupby('algorithm',sort=False):
        sub=g.sort_values('frame')
        # Rolling trajectory for visualization only; NaNs retained where undefined.
        trajectory=sub.f1.rolling(101,min_periods=1,center=True).mean()
        axs[0].plot(sub.frame,trajectory,label=method,linewidth=1.1)
    axs[0].set_ylabel('Frame F1 (rolling 101)');axs[0].set_ylim(0,1.02);axs[0].legend(ncol=4,fontsize=8)
    m=df[df.algorithm=='frame_diff'].sort_values('frame')
    axs[1].plot(m.frame,m.shift_proxy_px,linewidth=.7,label='Phase-correlation global displacement proxy (px)')
    axs[1].set_xlabel('CDnet frame index');axs[1].set_ylabel('Estimated shift magnitude (px)')
    axs[1].legend(fontsize=8)
    fig.suptitle(sequence_id+' — exploratory temporal diagnostics')
    fig.savefig(folder/'temporal.png',dpi=170);fig.savefig(folder/'temporal.pdf');plt.close(fig)
    for effect,n,frame,gt,masks in snapshots:
        im=illustration(frame,gt,masks)
        cv2.imwrite(str(folder/f'exploratory_frame_{n:06d}.png'),im)
    metadata={'sequence':sequence_id,'phase':'EXPLORATORY POST-HOC',
              'selection_bias':'snapshots chosen using observed Frame Difference-KNN frame F1 gap',
              'resolution':seq.size,'max_frames':max_frames,'evaluated_frames':n_evaluated,
              'time_seconds':round(time.time()-t0,3),
              'definitions':'GT255=positive; GT0/50=negative; GT85/170=ignored; ROI.bmp applied',
              'methodology':'Each model processes all preceding frames for background-state warm-up; timing is not benchmarked.',
              'motion_proxy_limitation':'phaseCorrelate is descriptive; object motion/texture can confound camera motion.'}
    (folder/'manifest.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    return pd.DataFrame(summ), metadata

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',required=True,type=Path)
    p.add_argument('--out',default=Path('working/final-temporal'),type=Path)
    p.add_argument('--sequences',nargs='+',default=list(PILOT))
    p.add_argument('--width',type=int,default=320)
    p.add_argument('--max-eval-frames',type=int,default=None,
                   help='Optional exploratory quick run; never use truncated output for main claims.')
    a=p.parse_args(argv)
    out=a.out.resolve()
    allsum=[]; manifests=[]
    for seq in a.sequences:
        d,meta=run_one(a.dataset,seq,out,a.width,a.max_eval_frames)
        allsum.append(d);manifests.append(meta)
        print('Completed:',seq,'scored frames',meta['evaluated_frames'],flush=True)
    pd.concat(allsum,ignore_index=True).to_csv(out/'temporal_summary.csv',index=False)
    (out/'ANALYSIS_STATUS.txt').write_text('POST-HOC EXPLORATORY - NOT INDEPENDENT CONFIRMATION\n',encoding='utf-8')
    (out/'run_manifest.json').write_text(json.dumps(manifests,indent=2),encoding='utf-8')
    print('EXPLORATORY TEMPORAL OUTPUT',out)

if __name__=='__main__':main()
