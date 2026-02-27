' JARVIS AI Hidden Launcher
' This script launches JARVIS AI without showing command windows

Set oShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get script directory
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Run the launcher batch file hidden
oShell.Run """" & scriptPath & "\LAUNCH_JARVIS_HIDDEN.bat""", 0, False

' Open browser to localhost
WScript.Sleep 3000
oShell.Run "start http://localhost:9000/"
