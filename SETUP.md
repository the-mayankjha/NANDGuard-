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
| **Build**   | `pyinstaller` Error  | Ensure `venv` is active and requirements are installed.  |

---

## 🛠️ Packaging & Distribution

NANDGuard+ uses a unified build system to generate installers for multiple platforms.

### 1. Automated (Recommended)

Use the `./fkinstaller` script to automate binary compilation and packaging.

| Command                                 | Result                                                |
| :-------------------------------------- | :---------------------------------------------------- |
| `./fkinstaller build nandguard mac`     | Generates `.app` (zip) and `.dmg` in `drivers/macos/` |
| `./fkinstaller build nandguard linux`   | Generates `.deb` in `drivers/linux/`                  |
| `./fkinstaller build nandguard windows` | Generates `.exe` in `drivers/windows/`                |
| `./fkinstaller build nandguard all`     | Builds for all platforms sequentially                 |

### 2. Manual Build Process

If you prefer manual control or need to debug specific phases, follow these steps:

####  macOS (DMG)

1. **Build Binary**:
   ```bash
   venv/bin/pyinstaller packaging/nandguard.spec --distpath dist/nandguard/mac --noconfirm
   ```
2. **Create DMG**:
   ```bash
   bash packaging/macos/create_dmg.sh 1.0.8
   ```

#### 🐧 Linux (DEB)

1. **Build Binary**:
   ```bash
   venv/bin/pyinstaller packaging/nandguard.spec --distpath dist/nandguard/linux --noconfirm
   ```
2. **Package DEB**:
   ```bash
   bash packaging/linux/build_deb.sh 1.0.8
   ```

#### 🪟 Windows (EXE)

1. **Build Binary**:
   ```powershell
   .\venv\Scripts\pyinstaller packaging/nandguard_windows.spec --distpath dist/nandguard/windows --noconfirm
   ```
2. **Create Installer (Requires Inno Setup)**:
   ```powershell
   iscc /DAppVersion="1.0.8" packaging/windows/nandguard_installer.iss
   ```

---
