"""Evaluate *externally produced* foreground masks using identical CDnet labels.

Expected root/<model>/<category>/<sequence>/<prefix><frame-number>.png.
No model is included or magically benchmarked. Missing predictions fail closed.
Any new baseline comparison is exploratory on an already inspected test set.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import cv2
import numpy as np
import pandas as pd
from paper_protocol import score_pixel_counts
from .core import numbered_files,load_sequence,groundtruth,metrics

def evaluate_model(dataset,predictions,model,sequence_ids,threshold=127,allow_resize=False):
    cv2.setNumThreads(1)
    rows=[]
    for sid in sequence_ids:
        seq=load_sequence(dataset,sid,320)
        preddir=Path(predictions)/model/sid
        pred_files=numbered_files(preddir)
        expected={k for k in seq.gt if seq.roi_start<=k<=seq.roi_end}
        absent=expected-set(pred_files)
        if absent:
            raise ValueError(f'Incomplete predictions for {sid}: {len(absent)} missing, examples {sorted(absent)[:8]}')
        tp=fp=fn=tn=0
        resized=0
        for n in sorted(expected):
            img=cv2.imread(str(pred_files[n]),cv2.IMREAD_GRAYSCALE)
            if img is None:raise IOError(f'Cannot decode {pred_files[n]}')
            if img.shape[::-1]!=seq.size:
                if not allow_resize:
                    raise ValueError(f'Mask dimension mismatch: {pred_files[n]} {img.shape[::-1]} vs {seq.size}; '
                                     'use --allow-resize explicitly only if this is methodologically justified')
                img=cv2.resize(img,seq.size,interpolation=cv2.INTER_NEAREST)
                resized+=1
            counts=score_pixel_counts((img>threshold).astype(np.uint8)*255,groundtruth(seq,n),seq.roi)
            tp+=counts[0];fp+=counts[1];fn+=counts[2];tn+=counts[3]
        row={'model':model,'seq':sid,'category':seq.category,'n_scored':len(expected),'resized_masks':resized,
             'tp':tp,'fp':fp,'fn':fn,'tn':tn,**metrics(tp,fp,fn,tn)}
        rows.append(row)
    return pd.DataFrame(rows)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset',type=Path,required=True)
    p.add_argument('--predictions',type=Path,required=True)
    p.add_argument('--model',required=True)
    p.add_argument('--threshold',type=int,default=127)
    p.add_argument('--allow-resize',action='store_true')
    p.add_argument('--out',type=Path,default=Path('working/final-external'))
    a=p.parse_args(argv)
    project=Path(__file__).resolve().parents[1]
    source=project/'working/results-v3-confirmatory/splits.csv'
    ids=sorted(pd.read_csv(source).seq.unique())
    data=evaluate_model(a.dataset,a.predictions,a.model,ids,a.threshold,a.allow_resize)
    a.out.mkdir(parents=True,exist_ok=True)
    data.to_csv(a.out/'external_model_per_sequence.csv',index=False)
    cats=data.groupby('category',as_index=False).agg(f1=('f1','mean'),n_sequences=('seq','nunique'))
    cats.to_csv(a.out/'external_model_by_category.csv',index=False)
    summary={'model':a.model,'phase':'EXPLORATORY post-hoc',
             'sequence_count':len(ids),'category_count':len(cats),
             'mean_category_f1':float(cats.f1.mean()),
             'prediction_threshold':a.threshold,'allow_resize':a.allow_resize,
             'resized_prediction_masks':int(data.resized_masks.sum()),
             'warning':'NOT independent validation; validate training scene leakage, adaptation, preprocessing and resolution'}
    (a.out/'external_model_manifest.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
