# Brian Visas — Thesis Extension Contribution Map

## Provenance

This repository is a fork of `linda78/DroneSimulation`, originally authored and maintained by Linda Mümken.

The history on `feature/Drone_Simulation_Updates` is collaborative: it contains Brian-authored commits as well as changes merged from Linda's branches. For that reason, this document distinguishes **directly attributable Brian work** from the surrounding simulation platform instead of treating the entire branch delta as one person's implementation.

Important reference points:

- Linda MPC baseline: `645a28e0cf6bc9563743de46cdc021087a992f01`
- Linda REST/API merge: `73a6bd26ffd7ce82bf2fe42f6da0aa0206a35352`
- Brian OpenCV trajectory extraction: `8835e7180176cc11edf68a0ce8bcf041199c6c3f`
- Presentation branch: `brian/thesis-extension`

## Directly attributable contribution

### OpenCV trajectory extraction

Verified Brian-authored commit:

[`8835e7180176cc11edf68a0ce8bcf041199c6c3f`](https://github.com/BrianVisas/DroneSimulation/commit/8835e7180176cc11edf68a0ce8bcf041199c6c3f) — `openCV trajectory extraction`

This commit adds a `DroneTrajectoryExtractor` workflow for deriving motion observations from recorded simulation video. The implementation includes:

- OpenCV video ingestion
- background-subtraction-based moving-object extraction
- contour filtering and centroid/bounding-box calculation
- Lucas–Kanade optical-flow tracking as an alternative extraction mode
- frame/timestamp trajectory records
- CSV export using pandas
- optional trajectory-overlay video generation
- retained trajectory/result artifacts from an MPC multi-drone experiment

The implementation appears historically under `output/import cv2.py`; the unusual filename is preserved because this branch documents the original research history rather than rewriting authorship or commit history.

### Research integration role

The contribution was used in a larger thesis workflow in which simulated multi-drone motion provided observations for trajectory-prediction experiments. The stronger TPT/BoF integration work is documented separately in `BrianVisas/TLCAmpcBrian` and the BoF project.

## Collaborative / upstream components

The following components are present in this branch but should **not** be presented as solely Brian-authored without commit-level evidence:

- the core 3D simulation architecture
- MPC and collision-avoidance implementation
- REST/Swagger simulation API and `RestServerQuickstart.md`
- mesh/visualization work inherited from Linda's history
- automated simulation test suite

In particular, the REST/API material entered the history through Linda's `linda/rest_api` work and merge commit `73a6bd26ffd7ce82bf2fe42f6da0aa0206a35352`.

## System relationship

```text
Linda's DroneSimulation platform
          |
          | simulated / rendered drone motion
          v
Brian's OpenCV trajectory extraction
          |
          | time-indexed observations / CSV
          v
Trajectory-prediction research workflow
          |
          v
BoF / TPT evaluation and visualization
```

## Why this fork is retained

This fork demonstrates collaboration on an existing research codebase rather than ownership of the complete simulator. It preserves the original platform provenance while making Brian's directly traceable extension visible through commit history and focused documentation.

## Attribution

The original DroneSimulation framework and Linda-authored extensions remain attributed to Linda Mümken and `linda78/DroneSimulation`. No claim in this document transfers authorship of those components to Brian Visas.
