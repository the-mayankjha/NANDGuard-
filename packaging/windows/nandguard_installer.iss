; NANDGuard+ Professional Windows Installer
; Built with Inno Setup

[Setup]
AppId={{D3F4B5E6-81CE-44CA-9D92-0CAA5FF84F4C}
AppName=NANDGuard+
AppVersion=1.0.0
AppPublisher=NANDGuard Team
DefaultDirName={autopf}\NANDGuard+
DefaultGroupName=NANDGuard+
AllowNoIcons=yes
; Require admin for service registration
PrivilegesRequired=admin
OutputDir=dist
OutputBaseFilename=NANDGuard+_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=nandguard.ico 
UninstallDisplayIcon={app}\NANDGuard+.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupshortcut"; Description: "Launch NANDGuard+ on system startup"; GroupDescription: "Startup:"; Flags: checked

[Files]
; The main application built by PyInstaller
Source: "dist\NANDGuard+\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Icons and assets
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\NANDGuard+"; FileName: "{app}\NANDGuard+.exe"
Name: "{group}\{cm:UninstallProgram,NANDGuard+}"; FileName: "{uninstallexe}"
Name: "{autodesktop}\NANDGuard+"; FileName: "{app}\NANDGuard+.exe"; Tasks: desktopicon
Name: "{userstartup}\NANDGuard+"; FileName: "{app}\NANDGuard+.exe"; Tasks: startupshortcut

[Run]
; Register the Windows service
FileName: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\packaging\windows\register_service.ps1"""; Flags: runhidden; StatusMsg: "Configuring background monitoring service..."
; Launch the app after install
FileName: "{app}\NANDGuard+.exe"; Description: "{cm:LaunchProgram,NANDGuard+}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop and unregister the service
FileName: "powershell.exe"; Parameters: "-Command ""Stop-Service -Name NANDGuardService -ErrorAction SilentlyContinue; sc.exe delete NANDGuardService"""; Flags: runhidden
