[Setup]
; App Information
AppName=Search-MCP
AppVersion=1.1
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

; Icon for the uninstaller
UninstallDisplayIcon={app}\search_mcp.exe

; Language Support
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Files]
; Source files from PyInstaller output
Source: "dist\search_mcp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"
; Desktop (Optional task)
Name: "{autodesktop}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
; Option to launch after installation
Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; Description: "{cm:LaunchProgram,Search-MCP}"; Flags: nowait postinstall skipifsilent
