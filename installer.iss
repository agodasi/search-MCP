[Setup]
; App Information
AppName=Search-MCP
AppVersion=1.0
AppPublisher=Solodev
AppPublisherURL=https://github.com/agodasi/search-MCP

; Directories
DefaultDirName={autopf}\Search-MCP
DefaultGroupName=Search-MCP
OutputDir=installer_output
OutputBaseFilename=SearchMCP_Setup

; Compression settings (makes the setup file smaller)
Compression=lzma2
SolidCompression=yes

; Requires admin privileges to install to Program Files
PrivilegesRequired=admin

; Icon for the uninstaller
UninstallDisplayIcon={app}\search_mcp.exe

[Files]
; Copy everything from the PyInstaller output directory
Source: "dist\search_mcp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu Icon
Name: "{group}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"
; Desktop Icon (Optional)
Name: "{autodesktop}\Search-MCP"; Filename: "{app}\search_mcp.exe"; Parameters: "--mode all"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "デスクトップにショートカットを作成する"; GroupDescription: "追加タスク:"; Flags: unchecked
