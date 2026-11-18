# Opens the active UE5.9 project; MCP8001 autostarts from project settings.
$ErrorActionPreference = 'Stop'
$workspaceRoot = Split-Path -Parent $PSScriptRoot
$projectPath = Join-Path $workspaceRoot 'VehicleStudio_UE59\VehicleStudio.uproject'
$editorPath = 'C:\Program Files\Epic Games\UE_5.9\Engine\Binaries\Win64\UnrealEditor.exe'
if (!(Test-Path -LiteralPath $projectPath) -or !(Test-Path -LiteralPath $editorPath)) { throw 'Active project or UE5.9 editor is missing.' }
Start-Process -FilePath $editorPath -ArgumentList ('"' + $projectPath + '"')
