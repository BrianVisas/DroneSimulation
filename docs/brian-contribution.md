# Brian Visas — Thesis Extension Contribution Map

## Provenance

This repository is a fork of `linda78/DroneSimulation`.

For the thesis-extension work documented here, the technical comparison baseline is the branch `linda/mpc_approach`, whose baseline commit is:

`645a28e0cf6bc9563743de46cdc021087a992f01`

The branch `feature/Drone_Simulation_Updates` is 17 commits ahead of that baseline. The presentation branch `brian/thesis-extension` is based on that feature branch and adds documentation that makes the extension boundaries explicit.

This document describes the extension surface. It does not claim ownership of the upstream simulation architecture or every historical commit contained in the fork.

## Extension surface

### 1. REST-based simulation integration

Relevant files:

- `api/server.py`
- `RestServerQuickstart.md`

The extension branch expands the simulation's REST-facing control and state-access surface so an external process can load/configure a simulation, control execution, step the simulator, and retrieve state/history data.

This API surface is the key integration boundary between the simulation and external trajectory-processing workflows.

### 2. Runtime and execution integration

Relevant file:

- `main.py`

The runtime entry point on the extension branch includes integration changes for simulation execution and visualization selection. This makes the simulator usable both interactively and as a controlled component in a larger experiment workflow.

### 3. Automated validation

Relevant files:

- `tests/test_config.py`
- `tests/test_drone.py`
- `tests/test_environment.py`
- `tests/test_flight_model.py`
- `tests/test_route.py`
- `tests/README.md`

The extension branch adds automated tests covering configuration parsing, drone state/model behaviour, route generation, environment boundaries/collision behaviour, and flight-model dynamics.

These tests provide regression protection around the simulation components used by the integration workflow.

### 4. Visualization extensions

Relevant branch delta includes additions under:

- `gui/`

The extension branch adds additional visualization capabilities, including mesh-oriented drone rendering support, while retaining the upstream visualization architecture.

### 5. Experiment trajectory data

Relevant file:

- `drone_trajectories.csv`

This file is retained as an experiment artifact from the integration work. It is not presented as a reusable benchmark dataset.

## System role in the thesis workflow

At a high level, the simulator provides drone motion/state data and a controllable execution environment:

```text
Drone simulation
      |
      | state / positions
      v
REST integration boundary
      |
      v
External trajectory-prediction workflow
      |
      v
Prediction / evaluation / visualization
```

Trajectory-Prediction-Tube-specific integration is surfaced separately in the `BrianVisas/TLCAmpcBrian` fork.

## What remains upstream

The underlying drone simulation framework, original architecture, flight/collision-avoidance concepts, and upstream project authorship remain attributed to Linda Mümken and the upstream repository.

The purpose of this fork is to make the extension and integration work traceable without obscuring that provenance.
