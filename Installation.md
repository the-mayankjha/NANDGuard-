# NANDGuard+ Installation Guide

NANDGuard+ is a professional AI-powered storage health utility. Follow the instructions below to install it on your platform.

## 🍎 macOS

1. **Download**: Obtain the `NANDGuard+_1.0.0.dmg` file.
2. **Mount**: Double-click the `.dmg` file to open it.
3. **Install**: Drag the **NANDGuard+** icon into the **Applications** folder link.
4. **Launch**: Open NANDGuard+ from your Applications folder.
5. **Auto-Start**: (Optional) Run the following in your terminal to enable silent background monitoring on boot:
   ```bash
   bash /Applications/NANDGuard+.app/Contents/Resources/packaging/macos/install.sh
   ```

## 🪟 Windows

1. **Download**: Obtain the `NANDGuard+_Setup.exe` installer.
2. **Run**: Double-click the installer and follow the on-screen wizard.
3. **Permissions**: Grant administrative privileges when prompted to allow the background service to register.
4. **Launch**: NANDGuard+ will create a desktop shortcut and a Start Menu entry. The background monitoring service starts automatically.

## 🐧 Linux (Debian/Ubuntu)

1. **Download**: Obtain the `nandguard-plus_1.0.0_amd64.deb` package.
2. **Install**: Run the following command in your terminal:
   ```bash
   sudo dpkg -i nandguard-plus_1.0.0_amd64.deb
   sudo apt-get install -f  # Fix dependencies if necessary
   ```
3. **Launch**: Find NANDGuard+ in your application menu or launch via `nandguard-plus` in the terminal.

---

### 🛠 Troubleshooting

- **Permissions**: NANDGuard+ requires administrative/root access to read low-level S.M.A.R.T. data via `smartctl`.
- **Dependencies**: Ensure `smartmontools` is installed on your system if you are running from source.

---

## 🛠 Development & Packaging

To build the standalone executable for your platform from source:

### 🍎 macOS

1. Build the app: `pyinstaller packaging/nandguard.spec`
2. Create the DMG: `bash packaging/macos/create_dmg.sh`

### 🪟 Windows

1. Install Python 3.13 and dependencies: `pip install -r requirements.txt`
2. Build the EXE: `pyinstaller packaging/nandguard_windows.spec`
3. Create the Installer: Open `packaging/windows/nandguard_installer.iss` in **Inno Setup** and click 'Compile'.

### 🐧 Linux

1. Build the binary: `pyinstaller packaging/nandguard.spec`
2. Create the DEB: `bash packaging/linux/build_deb.sh`
