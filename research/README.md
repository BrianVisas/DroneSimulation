# Trajectory Extraction Research Utility

This folder surfaces Brian Visas' directly traceable trajectory-extraction work from the collaborative DroneSimulation research repository.

## Provenance

The maintained utility in `trajectory_extraction.py` is derived from Brian's historical commit:

[`8835e7180176cc11edf68a0ce8bcf041199c6c3f`](https://github.com/BrianVisas/DroneSimulation/commit/8835e7180176cc11edf68a0ce8bcf041199c6c3f) — `openCV trajectory extraction`

The original implementation is intentionally preserved in Git history. This version removes machine-specific paths and presents the same experimental ideas as a reusable command-line tool.

## What it does

Two image-space motion extraction strategies are available:

1. **Background subtraction**
   - MOG2 foreground model
   - thresholding and morphological cleanup
   - contour-area filtering
   - centroid and bounding-box extraction

2. **Optical flow**
   - Shi–Tomasi feature selection
   - pyramidal Lucas–Kanade tracking
   - per-frame displacement observations

Both modes produce time-indexed trajectory observations that can be written to CSV. An optional MP4 overlay can be generated for visual inspection.

## Usage

```bash
python research/trajectory_extraction.py path/to/simulation.mp4 \
  --output-csv results/trajectory_observations.csv
```

Optical-flow mode:

```bash
python research/trajectory_extraction.py path/to/simulation.mp4 \
  --method optical_flow \
  --output-csv results/optical_flow_observations.csv
```

Generate an annotated video:

```bash
python research/trajectory_extraction.py path/to/simulation.mp4 \
  --output-csv results/trajectory_observations.csv \
  --overlay results/trajectory_overlay.mp4
```

## Research boundary

This utility extracts image-space motion observations from simulator video. It does not implement the upstream drone simulator, MPC controller, REST API, or Linda Mümken's visualization architecture.

The subsequent simulator-to-BoF/TPT integration is documented in `BrianVisas/TLCAmpcBrian`.
