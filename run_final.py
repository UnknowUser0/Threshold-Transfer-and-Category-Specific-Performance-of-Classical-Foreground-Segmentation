"""One entry point to the integrated CDnet2014 FINAL research materials.

    python run_final.py audit
    python run_final.py temporal --dataset D:\\SkySet
    python run_final.py resolution --dataset D:\\SkySet
    python run_final.py external --dataset D:\\SkySet --predictions D:\\Masks --model model_id

Outputs under working/final-* are exploratory unless explicitly described otherwise.
"""
from __future__ import annotations
import subprocess,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def main():
    args=sys.argv[1:]
    mode=args[0] if args else 'audit'
    names={
       'audit':'final_studies.audit_final',
       'compile':'final_studies.compile_results',
       'temporal':'final_studies.temporal',
       'resolution':'final_studies.resolution',
       'external':'final_studies.external_masks'}
    if mode=='tests':
        return subprocess.call([sys.executable,'-m','pytest','-q','tests'],cwd=ROOT)
    if mode not in names:
        raise SystemExit(f'Unknown action: {mode}. Choose: {", ".join(names)}, tests')
    return subprocess.call([sys.executable,'-m',names[mode],*args[1:]],cwd=ROOT)
if __name__=='__main__':raise SystemExit(main())
