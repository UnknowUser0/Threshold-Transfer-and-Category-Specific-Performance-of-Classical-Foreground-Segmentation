# Master evidence: integrated CDnet2014 phases

The archive contains **26 development sequences across five categories** (10 tune/16 development test) and **27 disjoint subsequent evaluation sequences across six categories**. All eleven CDnet categories appear, but the full 53 are **NOT** 53 independent confirmatory test observations. The two phases cannot be pooled without flagging prior outcome inspection.

The original evaluation was at a working width of 320 pixels with category-level inference; supplementary studies require original videos.

## Phase inventory

| phase        |   total_sequences |   tune_sequences |   test_sequences | categories                                                                                   |
|:-------------|------------------:|-----------------:|-----------------:|:---------------------------------------------------------------------------------------------|
| development  |                26 |               10 |               16 | ['badWeather', 'baseline', 'dynamicBackground', 'nightVideos', 'shadow']                     |
| confirmatory |                27 |                0 |               27 | ['PTZ', 'cameraJitter', 'intermittentObjectMotion', 'lowFramerate', 'thermal', 'turbulence'] |

## Category-level F1 (phase labeled)

| phase                        | category                 |   Farneback |   Frame Difference |   KNN |   MOG2 |
|:-----------------------------|:-------------------------|------------:|-------------------:|------:|-------:|
| development_test_inspected   | badWeather               |       0.592 |              0.329 | 0.502 |  0.450 |
| development_test_inspected   | baseline                 |       0.514 |              0.795 | 0.840 |  0.815 |
| development_test_inspected   | dynamicBackground        |       0.310 |              0.136 | 0.508 |  0.523 |
| development_test_inspected   | nightVideos              |       0.355 |              0.405 | 0.377 |  0.368 |
| development_test_inspected   | shadow                   |       0.528 |              0.574 | 0.702 |  0.705 |
| later_category_disjoint_test | PTZ                      |       0.204 |              0.316 | 0.203 |  0.215 |
| later_category_disjoint_test | cameraJitter             |       0.128 |              0.154 | 0.709 |  0.667 |
| later_category_disjoint_test | intermittentObjectMotion |       0.171 |              0.259 | 0.372 |  0.317 |
| later_category_disjoint_test | lowFramerate             |       0.220 |              0.279 | 0.474 |  0.486 |
| later_category_disjoint_test | thermal                  |       0.394 |              0.339 | 0.573 |  0.517 |
| later_category_disjoint_test | turbulence               |       0.098 |              0.032 | 0.569 |  0.626 |

### Scientific disclosure

* The development test was inspected during threshold-grid iterations.
* One-sided preprocessing hypothesis findings rely on prior, externally provable directional hypothesis timing.
* Full 53-sequence performance must not be advertised as an independently held-out result.
* Modern comparator, temporal trajectories, and native-resolution outputs cannot be claimed until real videos/predictions are processed.
