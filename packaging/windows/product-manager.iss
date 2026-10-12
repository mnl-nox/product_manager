#define MyAppName "Product Manager"
#ifndef MyAppVersion
  #define MyAppVersion "0.4.0"
#endif

[Setup]
AppId={{326936AE-8633-4C52-9C1E-3A205AE2BB59}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Product Manager
DefaultDirName={autopf}\Product Manager
DefaultGroupName=Product Manager
UninstallDisplayIcon={app}\ProductManager.exe
OutputDir=..\..\build\packages
OutputBaseFilename=ProductManager-{#MyAppVersion}-windows-x64-setup
SetupIconFile=product-manager.ico
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin

[Files]
Source: "..\..\dist\ProductManager.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Product Manager"; Filename: "{app}\ProductManager.exe"
Name: "{autodesktop}\Product Manager"; Filename: "{app}\ProductManager.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos adicionais:"

[Run]
Filename: "{app}\ProductManager.exe"; Description: "Abrir Product Manager"; Flags: nowait postinstall skipifsilent runasoriginaluser
