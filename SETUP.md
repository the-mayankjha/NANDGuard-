# Setup Guide - NANDGuard

NANDGuard is a cross-platform AI storage health monitor. Follow the instructions below for your specific operating system.

---

##  macOS Setup

### 1. Prerequisites

- **Homebrew**: [Install Homebrew](https://brew.sh/)
- **Command Line Tools**: `xcode-select --install`

### 2. Install Dependencies

```bash
brew install smartmontools python-tk@3.13
```

### 3. Setup & Execution

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Compile Native Bridge (For Apple Silicon)
bash telemetry/native/build_native.sh

# Run as Sudo (Required for hardware access)
sudo ./venv/bin/python main.py
```

---

## � Linux Setup (Ubuntu/Debian/Fedora)

### 1. Prerequisites

- **Ubuntu/Debian**: `sudo apt update && sudo apt install smartmontools python3-tk`
- **Fedora**: `sudo dnf install smartmontools python3-tkinter`
- **Arch**: `sudo pacman -S smartmontools tk`

### 2. Setup & Execution

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run as Sudo (Required for hardware access)
sudo ./venv/bin/python3 main.py
```

_Note: Native C bridge is currently macOS exclusive. Linux uses high-fidelity `smartctl` parsing._

---

## 🪟 Windows Setup

### 1. Prerequisites

- **Python**: [Python 3.10+](https://www.python.org/downloads/windows/) (Ensure "Add to PATH" is checked)
- **smartmontools**: [Download Windows Installer](https://www.smartmontools.org/wiki/Download#Windows)

### 2. Setup & Execution

1. Open **PowerShell** or **Command Prompt** as Administrator.
2. Navigate to project folder:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Run as Administrator (Required for hardware access)
python main.py
```

---

## 🧪 Development & Training (All Platforms)

### Generate Dataset

```bash
python data/synthetic_generator.py
```

### Train AI Models

```bash
python models/train_rul.py
python models/train_classifier.py
python models/train_anomaly.py
```

## 🔧 Troubleshooting

| Platform    | Issue                | Fix                                                      |
| :---------- | :------------------- | :------------------------------------------------------- |
| **macOS**   | `_tkinter` not found | `brew install python-tk@3.13`                            |
| **Linux**   | `Permission Denied`  | Always run `main.py` with `sudo`.                        |
| **Windows** | `smartctl` not found | Add `C:\Program Files\smartmontools\bin` to System PATH. |
| **All**     | Error Loading Models | Ensure you ran the Training scripts first.               |
