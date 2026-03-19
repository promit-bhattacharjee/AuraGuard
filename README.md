# 🛡️ AuraGuard — The Smart Workspace & Hydration Monitor

AuraGuard is a **privacy-first, locally-run** computer vision application that transforms your standard webcam into an ambient productivity coach. Using a lightweight YOLO object detection model, it monitors your workspace in real-time to help you stay focused and hydrated.

---

## 📋 Features

- **Phone Distraction Alerts**: Detects when you're using your phone and provides visual warnings to help you stay on task.
- **Hydration Tracking**: Monitors your water intake and reminds you to drink if no bottle or cup is detected for a period.
- **Privacy-First Design**: Runs entirely on your local machine. No video data ever leaves your computer.
- **Interactive HUD**: Real-time Heads-Up Display overlays status updates, session timers, and alerts directly onto the video feed.
- **Presence Awareness**: Automatically pauses session timers when you step away from your desk.

---

## ⚙️ System States

| State | Condition | UI Feedback |
|-------|-----------|-------------|
| **Empty Desk** | User away for > 5 seconds | Yellow status: *"System Paused: User Away"* |
| **Normal** | User present | White status: *"Status: Active"* |
| **Deep Work**| Continuous focus for > 10 seconds | Green bounding box, *"Status: Focusing"* |
| **Distracted** | Phone detected for > 2 seconds | Red box + flashing *"WARNING: PUT PHONE AWAY"* |
| **Dehydrated** | No cup/bottle for > 30 seconds | Blue status: *"HEALTH ALERT: Drink Water"* |

> [!NOTE]
> For demonstration, thresholds are set to **10 seconds** for focus and **30 seconds** for hydration (instead of the 30-minute standard depicted in diagrams) to ensure smooth grading and testing.

---

## 🏗️ Project Architecture

```
AuraGuard/
├── main.py                  # Entry point — orchestrates all modules
├── yolo26n.pt               # YOLOv26 Nano model weights
├── src/
│   ├── Webcam.py            # Video capture and core logic engine
│   ├── HeadsUpDisplay.py    # Rendering engine for HUD and windows
│   ├── States.py            # State definitions and controller
│   ├── Time.py              # Timer system with session management
│   ├── DrawBox.py           # Object detection and frame annotation
│   ├── WarningScreen.py     # Privacy consent and startup UI
│   └── Colors.py            # Unified color palette (BGR/RGB)
└── TECHNICAL_REPORT.md      # Detailed technical design review
└──Demo-auragard.mp4         # Demo video file
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- A working webcam

### Installation
1. Clone the repository and navigate to the project folder.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App
```bash
python main.py
```

### Controls
- **'q' key**: Quit the application safely.
- **Mouse Click**: Use the **YES/NO** buttons on the startup consent screen.

---

## 🛠️ Verification
You can verify the core logic remains intact after any changes by running the automated test suite:
```bash
python test_project.py
```

---

*Developed for the Module 15 Computer Vision Assignment.*
