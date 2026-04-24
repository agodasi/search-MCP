[Setup]
; App Information
AppName=Search-MCP
AppVersion=1.01
AppPublisher=agodasi
AppPublisherURL=https://github.com/agodasi/search-MCP

; Directories
DefaultDirName={autopf}\Search-MCP
DefaultGroupName=Search-MCP
OutputDir=installer_output
OutputBaseFilename=SearchMCP_Setup

; Compression
Compression=lzma2
SolidCompression=yes

; Admin privileges required for {autopf}
PrivilegesRequired=admin

; Icon for the setup installer itself
SetupIconFile=icon.ico

; Icon for the uninstaller
UninstallDisplayIcon={app}\icon.ico

; Language Support
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
; Source files from PyInstaller output
Source: "dist\search_mcp.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; IconFilename: "{app}\icon.ico"
; Desktop (Optional task)
Name: "{autodesktop}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; Tasks: desktopicon; IconFilename: "{app}\icon.ico"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Option to launch after installation
Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; Description: "{cm:LaunchProgram,Search-MCP}"; Flags: nowait postinstall skipifsilent
