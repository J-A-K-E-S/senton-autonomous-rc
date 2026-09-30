# Autonomous RC Car

An autonomous 1/10-scale RC car built with ROS 2 Jazzy on the ARRMA SENTON 223S BLX platform.

The vehicle maps a track, localises on it, plans racing trajectories, avoids obstacles, and overtakes a moving opponent — using a classical robotics stack deployed on physical hardware.

> **Status:** 🚧 Active development
> The URDF/Xacro vehicle model is implemented and visualised in RViz, with four rotating wheels and independently steerable front assemblies. Simulation, SLAM, planning, control and physical deployment follow.

---

## Overview

Development is simulation-first: the autonomy stack is built and validated in Gazebo against a parameterised vehicle model, then transferred to the physical car. This decouples software progress from hardware assembly and allows rapid iteration without battery charges or crash risk.

The autonomy pipeline:

```text
Sensors
   ↓
Perception / SLAM
   ↓
Localisation
   ↓
Track / Obstacle Representation
   ↓
Trajectory Planning
   ↓
Path Tracking
   ↓
Vehicle Control
```

The engineering focus is the planning and control layers, implemented from scratch rather than configured from an existing navigation stack.

---

## Platform

### Vehicle

| Component | Specification |
|---|---|
| Chassis | ARRMA SENTON 223S BLX |
| Scale | 1/10 |
| Drivetrain | 4WD |
| Steering | Ackermann-style front steering |
| Motor | Spektrum 3100Kv brushless |
| Vehicle mass | 3.55 kg |

### Compute and Sensors

| Component | Hardware |
|---|---|
| Compute | NVIDIA Jetson Orin Nano Super |
| LiDAR | Slamtec RPLIDAR S2 |
| Depth Camera | Luxonis OAK-D S2 |
| IMU | Bosch BNO085 |
| Motor Control | VESC 6 |
| Power | Main LiPo with regulated DC-DC supply for compute/sensors |

The LiDAR and camera mount to a single rigid bracket so their extrinsics remain fixed and can be calibrated once.

---

## Vehicle Parameters

| Parameter | Value |
|---|---:|
| Vehicle length | 558 mm |
| Vehicle width | 305 mm |
| Vehicle height | 210 mm |
| Wheelbase | 327 mm |
| Track width | 263 mm |
| Wheel diameter | 104 mm |
| Wheel width | 42 mm |
| Vehicle mass | 3.55 kg |

Dimensions are taken from manufacturer specifications and tyre measurements. Chassis body geometry in the model is a simplified approximation and will be refined against the physical vehicle.

---

## Current Robot Model

The vehicle description is written in Xacro so physical dimensions are maintained as named parameters rather than duplicated throughout the URDF.

Implemented:

- `base_footprint` as the ground reference frame
- `base_link` positioned at wheel-axis height
- Four wheel links generated from a reusable parameterised macro
- Continuous wheel rotation joints
- Separate steering knuckle links for the front wheels, with revolute steering joints
- Simplified chassis geometry
- RViz visualisation and manual joint verification via `joint_state_publisher_gui`

Transform structure:

```text
base_footprint
└── base_link
    ├── front_left_knuckle_link
    │   └── front_left_wheel_link
    │
    ├── front_right_knuckle_link
    │   └── front_right_wheel_link
    │
    ├── rear_left_wheel_link
    └── rear_right_wheel_link
```

The front steering joints are independently controllable for TF verification. Ackermann steering coordination — where the inner wheel turns more sharply than the outer — is handled at the control layer, not in the robot description.

---

## Software Stack

| Component | Technology |
|---|---|
| Middleware | ROS 2 Jazzy |
| Transform system | TF2 |
| Simulation | Gazebo Harmonic |
| Mapping / Localisation | SLAM Toolbox |
| Obstacle representation | `nav2_costmap_2d` |
| Local trajectory planning | Frenet-frame trajectory generation |
| Path tracking | Regulated Pure Pursuit |
| Opponent tracking | LiDAR clustering + state estimation |
| Compute target | NVIDIA Jetson Orin Nano Super |

---

## Design Decisions

### Custom Frenet-frame planner

The local planner is a Frenet optimal trajectory generator written for this project. Candidate trajectories are sampled as lateral offsets from a reference racing line and scored on lateral deviation, curvature, smoothness, obstacle clearance, vehicle constraints and duration.

This representation suits racing because trajectories are expressed relative to the track rather than as arbitrary motions through a global Cartesian map. The time component of each trajectory also provides the foundation for dynamic-opponent avoidance and overtaking.

### Standalone costmap rather than the full Nav2 stack

Nav2's behaviour tree and lifecycle management are designed around differential-drive indoor navigation. For an Ackermann vehicle running a custom planner at speed, that machinery adds complexity without benefit.

`nav2_costmap_2d` is used as a library for obstacle representation while custom planning and control nodes handle racing-specific trajectory generation and tracking — taking advantage of mature ROS infrastructure without inheriting an architecture built for a different problem.

### Classical robotics first

The first version uses classical planning and control rather than learned driving policies. Reinforcement learning for racing requires substantial training infrastructure and transfers poorly from simulation to hardware, whereas classical controllers transfer reliably and remain interpretable — which allows localisation, planning, tracking and control to be evaluated independently.

Learned perception components are scoped as a later phase, where they offer a clear advantage over geometric methods.

---

## Repository Structure

```text
senton-autonomous-rc/
├── README.md
└── src/
    └── senton_description/
        ├── CMakeLists.txt
        ├── package.xml
        ├── launch/
        │   └── display.launch.py
        └── urdf/
            └── senton.urdf.xacro
```

Additional packages for simulation, control, planning and perception will be added as the project grows.

---

## Running the Current Robot Model

### Requirements

- Ubuntu
- ROS 2 Jazzy
- Xacro, RViz2, `robot_state_publisher`, `joint_state_publisher_gui`

### Build and launch

```bash
colcon build --packages-select senton_description --symlink-install
source install/setup.bash
ros2 launch senton_description display.launch.py
```

The Joint State Publisher GUI exposes the wheel and front steering joints, allowing the kinematic structure and TF tree to be verified in RViz.

---

## Roadmap

### V1 — Autonomous Racing (LiDAR)

**Vehicle model**
- [x] Create ROS 2 description package
- [x] Parameterise vehicle dimensions using Xacro
- [x] Model four wheels with a reusable macro
- [x] Add `base_footprint` and `base_link`
- [x] Add front steering knuckles
- [x] Verify steering and wheel joints in RViz
- [x] Add simplified chassis geometry
- [ ] Add collision geometry and inertial properties
- [ ] Add LiDAR, camera and IMU frames
- [ ] Refine chassis dimensions from physical measurements

**Simulation**
- [ ] Create Gazebo world and spawn vehicle
- [ ] Add simulated LiDAR, camera and IMU
- [ ] Implement simulated vehicle actuation

**Mapping and localisation**
- [ ] Build track map using SLAM Toolbox
- [ ] Implement localisation
- [ ] Generate reference racing line

**Planning and control**
- [ ] Implement Frenet trajectory generator and scoring
- [ ] Implement regulated pure pursuit controller
- [ ] Integrate obstacle costmap
- [ ] Static obstacle avoidance

**Dynamic racing**
- [ ] Detect and cluster moving opponent from LiDAR
- [ ] Track opponent state with a Kalman filter
- [ ] Predict opponent trajectory
- [ ] Incorporate dynamic obstacles into trajectory scoring
- [ ] Implement overtaking behaviour

**Physical deployment**
- [ ] Finalise sensor mounting and 3D-printed electronics deck
- [ ] Integrate Jetson compute platform
- [ ] Integrate motor and steering control via VESC
- [ ] Calibrate sensors and transforms
- [ ] Transfer autonomy stack from simulation
- [ ] Closed-course testing and sim-to-real tuning

### V2 — Vision Layer

- [ ] OAK-D stereo depth integration
- [ ] RTAB-Map visual SLAM
- [ ] Object detection on the OAK-D VPU
- [ ] Detection-to-costmap integration
- [ ] Sensor fusion evaluation

---

## References

- F1TENTH autonomous racing research and educational material
- Werling et al., *Optimal Trajectory Generation for Dynamic Street Scenarios in a Frenét Frame*, IEEE ICRA, 2010
- SLAM Toolbox
- ROS 2 and Navigation2 documentation

---

## Author

**Jakes Jacob Mathew**
BSc (Hons) Artificial Intelligence