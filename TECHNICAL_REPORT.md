# AuraGuard — Technical Report
### The Smart Workspace & Hydration Monitor
**Author:** [Your Name]  
**Date:** March 2026

---

## 1. Introduction

AuraGuard is a privacy-first, locally-run computer vision application that acts as an ambient productivity coach. Using a standard webcam and a pre-trained YOLO object detection model, it monitors the user's desk environment in real-time, detects smartphone distractions, tracks hydration habits, and provides instant visual feedback through a Heads-Up Display (HUD) overlay.

The fundamental idea is simple: instead of relying on manual timers or rigid schedules, the workspace itself *sees* the user's actual behavior and responds accordingly.

---

## 2. System Architecture

The application follows a modular, object-oriented design where each responsibility is isolated into its own class. The system is composed of seven core modules:

```
AuraGuard/
├── main.py                  # Application entry point & orchestrator
├── yolo26n.pt               # Pre-trained YOLOv26 Nano weights
├── assets/
│   └── warning.png          # Consent screen background
└── src/
    ├── HeadsUpDisplay.py    # OpenCV window & text rendering engine
    ├── WarningScreen.py     # Privacy consent UI (camera access prompt)
    ├── DrawBox.py           # YOLO inference, filtering & annotation
    ├── Webcam.py            # Video capture loop & core state logic
    ├── States.py            # State definitions & controller
    ├── Time.py              # Timer system with pause/resume support
    └── Colors.py            # Color constants (BGR for OpenCV, RGB for Supervision)
```

### Data Flow

The processing pipeline for each frame follows this sequence:

1. **Capture** — `Webcam` reads a frame from `cv2.VideoCapture`.
2. **Inference** — `DrawBox` passes the frame through the YOLO model.
3. **Filtering** — Detections are filtered to only retain relevant classes (person, cell phone, cup, bottle).
4. **State Evaluation** — `Webcam` evaluates temporal logic using `TimeController` and updates `StateController`.
5. **Rendering** — `DrawBox` annotates the frame with bounding boxes and the `HeadsUpDisplay` overlays status text.
6. **Display** — The annotated frame is rendered to the OpenCV window.

## 3. Development Phases (The Milestones)

The development of AuraGuard was structured into four distinct milestones to ensure a progressive and reliable build:

### Milestone 1: The Video Loop
The foundation of the project is a robust video capture system using **OpenCV (`cv2`)**. 
- **Implementation**: The `Webcam` class initializes the camera stream and handles the main loop.
- **Graceful Exit**: The system listens for the `'q'` key to release the camera resources and close the windows safely.

### Milestone 2: The Brain
The project's intelligence is powered by the **Ultralytics** library and a pre-trained **YOLO** nano model.
- **Inference**: Frames are passed from the capture loop to the `DrawBox` class, which handles the model inference.
- **Raw Data**: Detections are extracted as raw data before being passed to the filtering stage.

### Milestone 3: The Filter
To minimize noise, the system filters out all but the four key COCO dataset classes.
- **Relevant Classes**: `person` (0), `cell phone` (67), `cup` (41), and `bottle` (39).
- **Separation**: Person detections are handled separately to enable state-based bounding box coloring.

### Milestone 4: The Timekeepers
The system uses the Python `time` module to transform frame-by-frame detections into meaningful behavioral alerts.
- **Stopwatches**: Variables track continuous phone usage, focus duration, and hydration gaps.
- **Logical Triggers**: If/else statements compare current time against these variables to toggle UI states.

---

## 4. Key Implementation Details

### 3.1 Object Detection — The Brain

The application uses the **YOLO** nano model loaded through the Ultralytics library. The raw detections are converted into `supervision.Detections` objects for convenient downstream filtering and annotation.

### 3.2 Detection Filtering — The Filter

AuraGuard monitors four specific classes:

| Object | COCO Class ID |
|---|---|
| Person | 0 |
| Bottle | 39 |
| Cup | 41 |
| Cell Phone | 67 |

Filtering is done using NumPy's `np.isin()`. Person detections are separated since they trigger dynamic bounding box color changes based on the interactive state.

### 3.3 Temporal Logic — The Timekeepers

A core challenge was moving beyond simple frame-by-frame detection to *time-aware* reasoning. This is handled by the `Time` class, which provides:

- **`threshold_time_start()` / `get_threshold_time_seconds()`** — High-precision stopwatches for measuring distraction duration, focus time, and empty desk periods.
- **`stream_pause()` / `stream_resume()`** — Pauses all clocks when the user leaves the desk.
- **`should_process_frame()`** — Caps inference at a consistent 15 FPS to save resources.

Five independent `Time` instances are managed by `TimeController`: session stream, empty desk, distraction, hydration, and focus duration.

### 3.4 State Machine — System States

| State | Trigger | Threshold | UI Feedback |
|---|---|---|---|
| **Empty Desk** | No `person` detected | > 5s | Yellow text: *"System Paused: User Away"* |
| **Normal** | `person` present | Immediate | White label: *"Status: Active"* |
| **Deep Work** | Continuous focus (no phone) | > 10s | Green box, *"Status: Focusing"* |
| **Distracted** | `cell phone` detected | > 2s | Red box, flashing *"WARNING: PUT PHONE AWAY"* |
| **Dehydrated** | No `cup`/`bottle` detected | > 30s | Blue text: *"HEALTH ALERT: Drink Water"* |

The system uses a **single-variable state model** (`current_state`) with a built-in priority system:
1. **Empty Desk** (Highest)
2. **Distracted**
3. **Dehydrated**
4. **Deep Work**
5. **Normal** (Default)

### 3.5 State Stability (Persistence)
To prevent flickering and ensure meaningful alerts, the system implements a **Stability Buffer**:
- **Persistence**: While waiting for a threshold (e.g., the 2s phone detection or 5s away detection), the system **retains the previous state** instead of reverting to Normal.
- **Immediate Clearance**: Alert states (Distracted, Empty Desk) clear immediately once their trigger condition is gone (e.g., phone is hidden), returning the system to Normal or the next highest priority state.
- **Dehydration Exception**: As requested, Dehydration bypasses the stability persistence and triggers immediately once the 30-minute timer is exceeded, ensuring health alerts are never delayed.

State transitions follow priority rules:
- **Presence**: When a person returns, the Empty Desk state is cleared and timers resume.
- **Focus**: Deep Work is triggered by 10s of continuous presence without a phone.
- **Distraction**: A phone detection immediately resets the focus timer and adds a Distracted alert.
- **Hydration**: Detecting a cup/bottle resets the hydration timer and clears the Dehydrated status.

### 3.5 HUD Design — Visual Feedback

The `HeadsUpDisplay` class wraps OpenCV's `cv2.putText()` with:
- **Flashing text** for attention-grabbing alerts.
- **Session timer** in the top-left corner.
- **Unified status bar** at the bottom.

Bounding box annotation is handled by the `supervision` library's `BoxAnnotator` and `LabelAnnotator`, with the person annotator's color dynamically changed based on the current state (green for Deep Work, red for Distracted, blue for Dehydrated).

### 3.6 Privacy-First Consent Screen

Before accessing the camera, AuraGuard displays a consent screen (`WarningScreen`) that asks the user to explicitly grant camera access. This is implemented using OpenCV's `setMouseCallback` to create interactive YES/NO buttons. The application only proceeds if the user clicks YES; otherwise, it exits gracefully.

---

## 4. Libraries & Tools Used

| Library | Purpose |
|---|---|
| **OpenCV (`cv2`)** | Video capture and UI rendering |
| **Ultralytics** | YOLO model management |
| **Supervision (`sv`)** | Detection processing and annotation |
| **NumPy** | Array filtering |
| **Python `time`** | `perf_counter()` for precision timing |

---

## 5. Challenges & Solutions

| Challenge | Solution |
|---|---|
| False alarms from brief phone visibility | Implemented a 2-second temporal threshold before alerts trigger |
| Session clock advancing while user is away | Built a pause/resume mechanism that offsets the start time by pause duration |
| Multiple simultaneous states (e.g., distracted AND dehydrated) | Used a list-based state stack to display multiple concurrent alerts |

---

## 6. Testing & Demonstration

The system was tested using a live webcam with the following scenarios:

1. **Empty Desk** — Stepped away from the camera for > 5 seconds → Yellow "System Paused" text appeared, timers paused.
2. **Deep Work** — Sat at the desk without a phone visible → Green bounding box with "Status: Focusing" displayed.
3. **Distraction** — Held a cell phone in view for > 2 seconds → Box turned red, flashing "WARNING: PUT PHONE AWAY" appeared.
4. **Dehydration** — Removed the water bottle from view for > 30 seconds → Blue "HEALTH ALERT: Drink Water" appeared.
5. **Recovery** — Put the phone down / picked up the water bottle → System correctly transitioned back to Deep Work.
6. **Concurrent States** — Held phone while dehydrated → Both warnings displayed simultaneously.

The hydration threshold was set to 30 seconds (instead of 30 minutes) for demonstration purposes, as recommended in the assignment brief.

---

## 7. Object-Oriented Design & Scalability

AuraGuard is built entirely around **Object-Oriented Programming (OOP)** principles, making the system easy to maintain, test, and extend. Each class has a single, well-defined responsibility:

### Encapsulation

Every module hides its internal complexity behind a clean interface. For example, `HeadsUpDisplay` encapsulates all OpenCV rendering logic — the rest of the codebase simply calls `hud.draw_text()` without knowing anything about font types, line anti-aliasing, or flashing toggle math. If the rendering engine ever needs to switch from OpenCV to a GPU-accelerated library, only `HeadsUpDisplay` changes — nothing else.

### Separation of Concerns

| Class | Responsibility |
|---|---|
| `Webcam` | Video capture and state evaluation logic |
| `DrawBox` | YOLO inference, detection filtering, and frame annotation |
| `StateController` | Manages which states are currently active |
| `TimeController` | Manages all independent timers |
| `HeadsUpDisplay` | All visual rendering (text, windows) |
| `WarningScreen` | Consent UI — completely decoupled from the main loop |

Because each concern lives in its own class, a developer can modify the detection logic in `DrawBox` without touching the timer system in `Time`, or redesign the HUD without affecting the state machine.

### Data-Driven State Definitions

States are not hardcoded as `if/else` branches. Instead, each state is an instance of `StateProperty` — a reusable data class that holds a category name, time threshold, text color, annotation color, display text, and flashing flag. **Adding a brand-new state requires zero changes to the rendering or detection code** — you simply create a new `StateProperty` object with the desired parameters and add the corresponding trigger logic.

### Dependency Injection

Objects are wired together through **constructor injection** rather than global variables. For example, `Webcam` receives `TimeController`, `StateController`, and `DrawBox` as constructor parameters. This makes it trivial to swap implementations — for instance, replacing the real `Webcam` with a mock for unit testing, or injecting a different `DrawBox` that uses a newer YOLO model.

### How This Enables Future Scaling

The OOP architecture means new features can be added by **extending** the system rather than **modifying** existing code:

- **New state?** → Create a `StateProperty` instance + add trigger logic in `Webcam`.
- **New model?** → Swap the model path in `DrawBox.__init__()`.
- **New UI layer?** → Create a new class that implements the same interface as `HeadsUpDisplay`.
- **Multiple cameras?** → Instantiate multiple `Webcam` objects with shared controllers.

---

## 8. Future Work

| Feature | Description |
|---|---|
| **Posture Detection** | Use pose estimation (e.g., MediaPipe) to detect slouching and alert the user to sit upright |
| **Break Reminder** | Track continuous Deep Work duration and suggest a 5-minute break every 25 minutes (Pomodoro technique) |
| **Session Analytics Dashboard** | Log state transitions with timestamps to a CSV/JSON file and generate daily productivity reports |
| **Multi-Object Hydration Tracking** | Distinguish between a water bottle and a coffee cup to provide more nuanced hydration advice |
| **Configurable Thresholds** | Add a settings file or GUI panel where users can customize thresholds (e.g., hydration timer, distraction delay) without editing code |
| **Sound Alerts** | Play an audio notification alongside the visual warning for stronger feedback |
| **Video File Input** | Allow users to pass a pre-recorded video file via command-line argument for offline analysis and testing |
| **Model Hot-Swapping** | Support loading different YOLO model sizes (Nano, Small, Medium) at runtime based on available hardware |

---

## 9. Conclusion

AuraGuard demonstrates a robust, privacy-respecting computer vision pipeline. The object-oriented, modular architecture ensures that every component — from detection to rendering — can be independently extended, ensuring the system can scale to include features like posture detection or session analytics in the future.
