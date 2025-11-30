; ============================================================
; Inno Setup Script for ImageOrganizer
; ============================================================

[Setup]
AppName=ImageOrganizer
AppVersion=1.0.0
AppPublisher=NEL
DefaultDirName={commonpf}\ImageOrganizer
DefaultGroupName=ImageOrganizer
OutputDir=installer_output
OutputBaseFilename=ImageOrganizerInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; Icon for installer itself
SetupIconFile=resources\icons\image_organizer_main_icon.ico

[Files]
; Include all PyInstaller output
Source: "dist\ImageOrganizer.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ImageOrganizer"; Filename: "{app}\ImageOrganizer.exe"
Name: "{commondesktop}\ImageOrganizer"; Filename: "{app}\ImageOrganizer.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked

[Run]
Filename: "{app}\ImageOrganizer.exe"; Description: "Launch ImageOrganizer"; Flags: nowait postinstall skipifsilent
