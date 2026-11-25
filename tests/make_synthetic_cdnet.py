"""Generate a tiny fake CDnet-like fixture for integration testing ONLY.

It must never be used to support publication claims. Output is artificial.
"""
from pathlib import Path
import argparse
import cv2
import numpy as np

DEVELOPMENT = ('baseline', 'dynamicBackground', 'nightVideos', 'badWeather', 'shadow')
CONFIRMATORY = ('cameraJitter', 'intermittentObjectMotion', 'lowFramerate', 'PTZ', 'thermal', 'turbulence')


def make_fixture(root: Path, mode='development'):
    cats = CONFIRMATORY if mode == 'confirmatory' else DEVELOPMENT
    count = 4 if mode == 'confirmatory' else 2
    for j, cat in enumerate(cats):
        for i in range(count):
            d = root/cat/f'synthetic_{i+1}'
            for sub in ('input', 'groundtruth'):
                (d/sub).mkdir(parents=True, exist_ok=True)
            (d/'temporalROI.txt').write_text('3 9\n')
            cv2.imwrite(str(d/'ROI.bmp'), np.full((48, 64), 255, dtype=np.uint8))
            for n in range(1, 10):
                raw = np.full((48, 64, 3), 40+j, dtype=np.uint8)
                gt = np.zeros((48, 64), np.uint8)
                x = 8+n+i
                raw[15:26, x:x+11] = 220
                gt[15:26, x:x+11] = 255
                gt[:3] = 85
                gt[3:5] = 170
                gt[-3:] = 50
                cv2.imwrite(str(d/'input'/f'in{n:06d}.jpg'), raw)
                cv2.imwrite(str(d/'groundtruth'/f'gt{n:06d}.png'), gt)
    return len(cats)*count


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('root', type=Path)
    p.add_argument('--mode', choices=('development','confirmatory'), default='development')
    x = p.parse_args()
    print('Created', make_fixture(x.root,x.mode),'synthetic-only sequences')
