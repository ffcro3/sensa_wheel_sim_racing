# <p align="center"><img src="icon.png" width="128"><br>SensaWheel Pro v1.0</p>

<p align="center">
  <strong>Transform your smartphone into a high-precision F1-style steering wheel for PC SimRacing.</strong>
</p>

---

## 🏎️ Overview
**SensaWheel Pro** is an open-source bridge that captures your smartphone's gyroscope data (via UDP) and touch inputs (via HTTP) to emulate a high-precision virtual joystick on Windows. Designed for low latency and professional sim-racing feel.

---

## 🚀 Getting Started (For Users)

### 1. Prerequisites
* **vJoy Driver:** Download and install [vJoy](https://sourceforge.net/projects/vjoystick/).
  * Ensure **Device 1** is enabled with X, Y, and Z axes.
* **Mobile App:** Use any app that sends UDP motion data (e.g., SensaGram) to your PC's IP on port `8080`.

### 2. Launching
* Run `SensaWheel_Pro.exe`.
* Check the **System Tray** for the SensaWheel logo.
* Open your phone's browser at `http://YOUR_PC_IP:5000`.

### 3. Game Mapping
* **Steering:** Map to vJoy **Axis X**.
* **Gas (Throttle):** Map to vJoy **Axis Y**.
* **Brake:** Map to vJoy **Axis Z**.
* **Shifting:** Map to vJoy **Buttons 3 (Down) and 4 (Up)**.

---

## 🎮 Controls & Hotkeys
* **Default Toggle:** Press **Mouse X1** (side button) to enable/disable steering.
* **Assign New:** Right-click the Tray Icon -> **"Assign Hotkey"** to capture a new button.
* **Notifications:** A high-priority popup will notify you of the status (ACTIVE/DISABLED) even during full-screen gameplay.

---

## 🛠 For Developers (Open Source & Customization)

If you want to fork this project or tweak the steering physics, here is the technical breakdown:

### 📂 Architecture
The system uses a multi-threaded approach to prevent input lag:
* **UDP Listener:** High-frequency thread for gyroscope processing.
* **Flask Server:** Handles the Mobile Web UI for pedals/shifters.
* **UI/Tray:** Manages `pystray` and the `Tkinter` config windows.
* **Native Notification:** Uses isolated `WScript.Shell` (VBScript) calls to ensure thread-safe Windows popups without bulky libraries.

### 🔧 Key Calibration Variables
Edit these constants in `server.py` to change the "feel" of the car:
* `CURSO_FISICO_CELULAR = 45.0`: Max degrees to tilt the phone for full steering lock.
* `FATOR_EXPONENCIAL = 1.7`: Steering curve. > 1.0 makes the center stable and the edges aggressive.
* `PESO_SUAVIDADE = 0.5`: The LERP (Linear Interpolation) factor. Lower values increase smoothness; higher values increase raw responsiveness.

### 📦 Setup Environment
```bash
pip install pyvjoy pynput flask Pillow pystray
```

### 🏗 Build Instructions

To compile the standalone .exe with the integrated assets:

```bash
pyinstaller --noconsole --onefile --icon="icon.ico" --add-data "icon.png;." --add-data "icon.ico;." --name "SensaWheel_Pro" server.py
```

### 📄 License

This is free and open-source software. Feel free to fork, modify, and distribute.

#

<p align="center">Developed for the SimRacing Community with ❤️ by FFCRO3.</p>