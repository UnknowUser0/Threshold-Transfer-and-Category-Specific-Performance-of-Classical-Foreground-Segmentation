"""Common exact-label, frozen-parameter CDnet2014 evaluation utilities.

Supplementary exploratory evaluation only; not the V3 preregistered analysis.
Processing reproduces the V3 configured pipeline, but numerical equivalence on the
original dataset must be checked by an actual full-data rerun on the same environment.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from dataclasses import dataclass
import cv2
import numpy as np

from paper_protocol import score_pixel_counts

FROZEN = {'frame_diff': {'fixed_thr':5},'mog2':{'var_threshold':25},
          'knn':{'dist2_threshold':600.0},'farneback':{'flow_thr':1.0}}
DEFAULT = {
 'frame_diff':{'fixed_thr':25, 'otsu_floor':10},
 'mog2':{'history':500,'var_threshold':16,'detect_shadows':True},
 'knn':{'history':500,'dist2_threshold':400.0,'detect_shadows':True},
 'farneback':{'pyr_scale':0.5,'levels':3,'winsize':15,'iterations':3,
              'poly_n':5,'poly_sigma':1.2,'flow_thr':1.0,'mag_scale':32.0,'otsu_floor':10},
}
METHODS = tuple(DEFAULT)

def load_frozen(path: Path):
    params = json.loads(Path(path).read_text(encoding='utf-8'))
    if params != FROZEN:
        raise ValueError('Frozen V2 hyperparameters changed. Stop: this is not the locked experiment.')
    return params

def numbered_files(folder: Path):
    if not folder.is_dir():
        raise FileNotFoundError(str(folder))
    files={}
    for f in folder.iterdir():
        if f.suffix.lower() not in ('.png','.bmp','.jpg','.jpeg'):
            continue
        match=re.search(r'(\d+)',f.stem)
        if match:
            key=int(match.group(1))
            if key in files:
                raise ValueError(f'Duplicate frame index {key}: {folder}')
            files[key]=f
    return dict(sorted(files.items()))

@dataclass
class Sequence:
    category:str
    name:str
    path:Path
    inputs:dict
    gt:dict
    roi_start:int
    roi_end:int
    size:tuple
    roi:np.ndarray|None
    resize_width:int|None
    @property
    def sequence_id(self):return f'{self.category}/{self.name}'

def load_sequence(dataset:Path, id:str, width:int|None=320)->Sequence:
    category,name=id.split('/',1)
    d=Path(dataset)/category/name
    input_paths=numbered_files(d/'input')
    gt_paths=numbered_files(d/'groundtruth')
    if not input_paths or not gt_paths: raise ValueError(f'No images: {d}')
    matches=re.findall(r'\d+', (d/'temporalROI.txt').read_text())
    if len(matches)<2: raise ValueError(f'Invalid temporalROI: {d}')
    roi_start,roi_end=map(int,matches[:2])
    missing=[n for n in gt_paths if roi_start<=n<=roi_end and n not in input_paths]
    if missing: raise ValueError(f'Unmatched GT frames in {id}: {missing[:6]}')
    sample=cv2.imread(str(next(iter(input_paths.values()))),cv2.IMREAD_COLOR)
    if sample is None:raise IOError(f'Invalid image: {d}')
    h,w=sample.shape[:2]
    target=(int(width),int(round(h*width/w))) if width else (w,h)
    if min(target)<=0:raise ValueError('Invalid scale')
    roipath=d/'ROI.bmp'
    roiimg=cv2.imread(str(roipath),cv2.IMREAD_GRAYSCALE) if roipath.exists() else None
    roi=(cv2.resize(roiimg,target,interpolation=cv2.INTER_NEAREST)>0).astype(np.uint8)*255 if roiimg is not None else None
    return Sequence(category,name,d,input_paths,gt_paths,roi_start,roi_end,target,roi,width)

def bgr_from_path(seq:Sequence,path:Path):
    im=cv2.imread(str(path), cv2.IMREAD_COLOR)
    if im is None:raise IOError(f'Unreadable input: {path}')
    if im.shape[:2][::-1]!=seq.size:
        im=cv2.resize(im,seq.size,interpolation=cv2.INTER_AREA)
    return im

def groundtruth(seq:Sequence,n:int):
    im=cv2.imread(str(seq.gt[n]),cv2.IMREAD_GRAYSCALE)
    if im is None:raise IOError(f'Unreadable ground truth: {seq.gt[n]}')
    if im.shape[:2][::-1]!=seq.size:
        im=cv2.resize(im,seq.size,interpolation=cv2.INTER_NEAREST)
    return im

def metrics(tp,fp,fn,tn):
    precision=tp/(tp+fp) if (tp+fp) else float('nan')
    recall=tp/(tp+fn) if (tp+fn) else float('nan')
    f1=2*tp/(2*tp+fp+fn) if (2*tp+fp+fn) else float('nan')
    fpr=fp/(fp+tn) if (fp+tn) else float('nan')
    fnr=fn/(fn+tp) if (fn+tp) else float('nan')
    return {'precision':precision, 'recall':recall, 'f1':f1,'fpr':fpr,'fnr':fnr,
            'pwc':100*(fp+fn)/(tp+fp+fn+tn) if (tp+fp+fn+tn) else float('nan')}

class FrozenMotion:
    """V3 baseline algorithm settings, including V3 per-call RNG re-seeding.

    At a different spatial scale the same numerical thresholds are *not* physically
    scale-invariant; this is a deliberate fixed-parameter sensitivity experiment.
    """
    def __init__(self,method:str,frozen:dict,size:tuple,seed:int=42):
        if method not in METHODS:raise ValueError(method)
        self.method=method
        self.p={**DEFAULT[method],**frozen[method]}
        self.prev=None
        self.n_calls=0
        self.seed=seed
        self.kopen=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        self.kclose=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
        self.bg=None
        if method=='mog2':
            self.bg=cv2.createBackgroundSubtractorMOG2(history=self.p['history'],
              varThreshold=self.p['var_threshold'],detectShadows=self.p['detect_shadows'])
        elif method=='knn':
            self.bg=cv2.createBackgroundSubtractorKNN(history=self.p['history'],
              dist2Threshold=self.p['dist2_threshold'],detectShadows=self.p['detect_shadows'])
    def process(self,frame:np.ndarray,roi:np.ndarray|None):
        img=cv2.GaussianBlur(frame,(5,5),0)
        if self.bg is not None:
            self.n_calls+=1
            cv2.setRNGSeed(self.seed+self.n_calls)
            fg=self.bg.apply(img)
            mask=np.where(fg==255,255,0).astype(np.uint8)
        else:
            gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            prev,self.prev=self.prev,gray
            if prev is None:return np.zeros(gray.shape,dtype=np.uint8)
            if self.method=='frame_diff':
                strength=cv2.absdiff(gray,prev)
                thr=self.p['fixed_thr']
            else:
                p=self.p
                flow=cv2.calcOpticalFlowFarneback(prev,gray,None,p['pyr_scale'],p['levels'],
                       p['winsize'],p['iterations'],p['poly_n'],p['poly_sigma'],0)
                strength=np.clip(cv2.magnitude(flow[:,:,0],flow[:,:,1])*p['mag_scale'],0,255).astype(np.uint8)
                thr=p['flow_thr']*p['mag_scale']
            mask=cv2.threshold(strength,thr,255,cv2.THRESH_BINARY)[1]
        if roi is not None:
            mask=cv2.bitwise_and(mask,roi)
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,self.kopen)
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,self.kclose)
        return mask

def shift_proxy(previous, frame, valid_roi=None):
    """Global phase-correlation displacement proxy, NOT a calibrated camera-motion estimate."""
    cur=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY).astype(np.float32)
    if previous is None:return cur,float('nan'),float('nan'),float('nan')
    a,b=previous,cur
    if valid_roi is not None:
        mask=(valid_roi>0).astype(np.float32)
        a=a*mask; b=b*mask
    try:
        (dx,dy),response=cv2.phaseCorrelate(a,b)
        mag=float(np.hypot(dx,dy))
        return cur,mag,float(response),float(dx)
    except cv2.error:
        return cur,float('nan'),float('nan'),float('nan')

def overlap(row_list, expected):
    missing=sorted(set(expected)-set(row_list))
    unexpected=sorted(set(row_list)-set(expected))
    return {'missing':missing,'unexpected':unexpected}
