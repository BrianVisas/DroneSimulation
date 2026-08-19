# Drone Simulation — Thesis Extension

> **Upstream provenance:** this repository is a fork of [`linda78/DroneSimulation`](https://github.com/linda78/DroneSimulation), originally authored and maintained by Linda Mümken. The upstream framework and its original authorship remain unchanged and fully attributed.
>
> **Contribution branch:** `brian/thesis-extension` documents the thesis-oriented extension built on top of Linda's `linda/mpc_approach` baseline.

## Brian Visas — contribution overview

My work in this fork focused on extending the existing multi-drone simulation so it could be controlled, observed, tested, and integrated with an external trajectory-prediction workflow.

The contribution surface on this branch includes:

- extended REST-based simulation control and state access in `api/server.py`
- stepwise/runtime integration changes in `main.py`
- trajectory-data capture used during integration experiments
- additional 3D visualization support and mesh-based drone rendering
- automated tests covering configuration, drone state, routes, environment behaviour, and flight models
- REST API usage and integration documentation

The branch is **17 commits ahead of the `linda/mpc_approach` baseline**. This statement describes the branch delta, not sole authorship of every historical file or commit in the fork.

### Contribution map

| Area | Extension / evidence |
| --- | --- |
| Simulation API | `api/server.py` |
| Runtime integration | `main.py` |
| API usage | `RestServerQuickstart.md` |
| Automated validation | `tests/` and `tests/README.md` |
| 3D/mesh visualization | `gui/` additions on the extension branch |
| Experiment trajectory data | `drone_trajectories.csv` |

For a detailed provenance and implementation map, see [`docs/brian-contribution.md`](docs/brian-contribution.md).

## Relationship to the thesis workflow

This simulator served as one side of the larger multi-drone trajectory-prediction workflow: simulated drone states could be exposed through the API and consumed by external prediction/integration components. The trajectory-prediction and TPT-specific integration is documented separately in the `TLCAmpcBrian` fork.

---

# 3D Drone Simulation

A state-of-the-art 3D drone simulation with physically accurate flight dynamics, interchangeable collision avoidance algorithms and real-time visualisation.

## Features

### Core Functionality
- **3D Simulation** with VisPy for high-performance real-time visualisation
- **Interchangeable Flight Models**:
  - Physical model with realistic acceleration/deceleration
  - Simple model for direct movement
- **Collision Avoidance** with various algorithms:
  - Right Avoidance (right-hand evasion)
  - Repulsive Forces (repulsive forces)
  - Velocity Obstacle (velocity-based)
- **Flexible Route Configuration**:
  - Circular routes
  - Rectangular routes
  - User-defined waypoints
- **Configurable Space**:
  - Adjustable room size
  - Support for photo/video textures (planned)
  - Simple 3D example space

### Visualisation
- Interactive 3D camera (rotation, zoom)
- Flight path display with configurable length
- Camera tracking mode for individual drones
- Real-time performance display (FPS)

### Export & Analysis
- **Data Export** in multiple formats:
  - JSON (complete state history)
  - CSV (flat data structure)
  - Parquet (efficient binary format)
  - Excel (with summaries and metadata)
- **Video Export** of the simulation
- **3D Trajectories** as interactive HTML plots (Plotly)
- **Summary Statistics** for each drone

### API
- **REST API** for remote control:
  - Load and start simulation
  - Real-time state query
  - Step-by-step execution
  - Retrieve history data

## Project Structure

```
PythonProject1/
├── model/              # Core Data Models
│   ├── drone.py           # Drone Class with Physics State
│   ├── route.py           # Routes and Waypoints
│   ├── environment.py     # Space and Environment
│   ├── flight_model.py    # Flight Physics Models
│   └── avoidance_agent.py # Collision Avoidance Algorithms
├── backend/            # Simulation Engine
│   ├── config.py          # YAML Configuration System
│   └── simulation.py      # SimPy-based Simulation
├── gui/                # GUI and Visualisation
│   └── viewer.py          # VisPy 3D Viewer
├── api/                # REST API
│   └── server.py          # Flask Server
├── export/             # Export Functionality
│   ├── data_exporter.py   # Data Export (CSV, JSON, etc.)
│   └── video_exporter.py  # Video Export
├── configs/            # Example Configurations
│   ├── simple_demo.yaml
│   ├── multi_drone.yaml
│   ├── stress_test.yaml
│   └── camera_follow.yaml
├── output/             # Output Directory
├── assets/             # Assets (GIFs, Textures)
├── main.py             # Main Entry Point
├── requirements.txt    # Python Dependencies
└── README.md          # This File
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Step 1: Clone or Download Repository

```bash
cd DroneSimulation
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Running the Simulation

Simple demo with 3D visualisation:
```bash
python main.py run configs/simple_demo.yaml
```

Multi-drone demo:
```bash
python main.py run configs/multi_drone.yaml
```

Headless mode (without GUI):
```bash
python main.py run configs/simple_demo.yaml --headless
```

With video export:
```bash
python main.py run configs/multi_drone.yaml --export-video
```

### 3D Visualisation Controls

When the 3D visualisation is running:
- **Drag mouse**: Rotate camera
- **Mouse wheel**: Zoom
- **Close window**: End simulation

### Creating a Configuration File

Create default configuration:
```bash
python main.py create-config my_config.yaml
```

### Starting the API Server

Start REST API:
```bash
python main.py api --port 5000
```

Access API documentation:
```
http://localhost:5000/
```

### Displaying Available Configurations

```bash
python main.py list-configs
```

## Configuration

Configuration files are in YAML format and define all aspects of the simulation.

### Example Configuration

```yaml
simulation:
  name: "My Simulation"
  duration: 60.0
  time_step: 0.05
  real_time: false

room:
  dimensions: [20.0, 20.0, 10.0]
  texture_path: null
  is_video: false
```

## REST API

See `RestServerQuickstart.md` for the branch-specific API workflow and endpoint examples.

## Development

The upstream simulation remains the architectural base for flight models, routing, simulation state and collision-avoidance experimentation. Extension-specific validation is under `tests/`.

## Technical Details

Technologies used by the project include SimPy, VisPy, NumPy, Flask, Pandas, Plotly and OpenCV.

## Licence

MIT Licence

## Upstream Author

Linda Muemken

## Extension Contributor

Brian Visas — thesis-oriented REST integration, runtime/trajectory integration, visualization additions and automated validation documented on `brian/thesis-extension`.

## Further Development

Possible extensions:
- [ ] Obstacles in the space
- [ ] Photo/video textures for space
- [ ] AI-based control with PyTorch
- [ ] Multi-agent reinforcement learning
- [ ] Sensor simulation (cameras, lidar)
- [ ] Wind effects and turbulence
- [ ] Battery simulation
- [ ] Swarm intelligence algorithms
- [ ] VR support
