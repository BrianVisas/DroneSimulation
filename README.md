# DroneSimulation — Research Contribution by Brian Visas

> **Upstream:** [`linda78/DroneSimulation`](https://github.com/linda78/DroneSimulation), authored and maintained by Linda Mümken.
>
> This branch does **not** claim ownership of the upstream simulator, MPC implementation, REST API, visualization framework, or other Linda-authored components. It exists to make Brian Visas' directly traceable research contribution visible while preserving the collaborative history.

## Verified contribution

### OpenCV trajectory extraction

Brian-authored commit:

[`8835e7180176cc11edf68a0ce8bcf041199c6c3f`](https://github.com/BrianVisas/DroneSimulation/commit/8835e7180176cc11edf68a0ce8bcf041199c6c3f) — `openCV trajectory extraction`

The implementation adds a video-based trajectory extraction workflow using OpenCV, including:

- video ingestion and frame processing
- background subtraction for moving-object extraction
- contour filtering, centroids, and bounding boxes
- Lucas–Kanade optical-flow tracking as an alternative mode
- timestamped trajectory records
- CSV export with pandas
- optional trajectory-overlay video generation
- retained trajectory/result artifacts from a multi-drone simulation experiment

### Maintained research utility

The original implementation remains preserved in Git history. A cleaned, reusable version is available at:

- [`research/trajectory_extraction.py`](research/trajectory_extraction.py)
- [`research/README.md`](research/README.md)

The maintained version removes machine-specific paths and exposes the experiment as a command-line tool while preserving the two original extraction approaches.

Example:

```bash
python research/trajectory_extraction.py path/to/simulation.mp4 \
  --output-csv results/trajectory_observations.csv \
  --overlay results/trajectory_overlay.mp4
```

## Role in the wider research workflow

```text
Linda's DroneSimulation platform
          |
          | rendered / simulated drone motion
          v
Brian's OpenCV trajectory extraction
          |
          | time-indexed observations
          v
Trajectory-prediction workflow
          |
          v
BoF / TPT evaluation
```

The more substantial simulator-to-BoF / TPT integration is documented in [`BrianVisas/TLCAmpcBrian`](https://github.com/BrianVisas/TLCAmpcBrian) and the BoF project.

## Provenance and collaboration

The feature-branch history contains work from both Brian and Linda. For example, the REST/Swagger API entered the history through Linda's `linda/rest_api` work, so it is intentionally **not** listed as Brian's personal contribution here.

See [`docs/brian-contribution.md`](docs/brian-contribution.md) for the detailed commit-level responsibility map.

Linda's original repository documentation is preserved at [`UPSTREAM_README.md`](UPSTREAM_README.md).
