; JARVIS AI Windows Installer (NSIS)
; Creates a professional Windows .exe installer for JARVIS AI desktop application
;
; Generated: 2026-02-24
; Version: 0.1.0
; Platform: Windows 7+

; Include required libraries
!include "MUI2.nsh"
!include "x64.nsh"
!include "nsDialogs.nsh"
!include "LogicLib.nsh"

; ─── Application Settings ───────────────────────────────────────
Name "JARVIS AI Desktop"
OutFile "JARVIS-AI-Desktop-Setup.exe"
InstallDir "$PROGRAMFILES\JARVIS AI"
InstallDirRegKey HKCU "Software\JARVIS AI" "InstallPath"

; Require admin privileges for installation
RequestExecutionLevel admin

; ─── Installer Pages ────────────────────────────────────────────
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ─── Installation Sections ──────────────────────────────────────
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Copy application files
  File /r "dist\*.*"
  File /r "..\backend\*.*"
  File "..\backend\.env"
  File "..\RUN_JARVIS.bat"
  File "..\START_JARVIS_BROWSER.bat"
  
  ; Create shortcuts
  SetOutPath "$SMPROGRAMS\JARVIS AI"
  CreateDirectory "$SMPROGRAMS\JARVIS AI"
  CreateShortCut "$SMPROGRAMS\JARVIS AI\JARVIS AI (Browser).lnk" "$INSTDIR\START_JARVIS_BROWSER.bat"
  CreateShortCut "$SMPROGRAMS\JARVIS AI\JARVIS AI (Desktop).lnk" "$INSTDIR\RUN_JARVIS.bat"
  CreateShortCut "$SMPROGRAMS\JARVIS AI\Uninstall.lnk" "$INSTDIR\uninstall.exe"
  
  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\JARVIS AI.lnk" "$INSTDIR\START_JARVIS_BROWSER.bat"
  
  ; Register uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"
  WriteRegStr HKCU "Software\JARVIS AI" "InstallPath" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JARVIS AI" "DisplayName" "JARVIS AI Desktop"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JARVIS AI" "UninstallString" "$INSTDIR\uninstall.exe"
  
SectionEnd

; ─── Uninstall Section ──────────────────────────────────────────
Section "Uninstall"
  Delete "$DESKTOP\JARVIS AI.lnk"
  RMDir /r "$SMPROGRAMS\JARVIS AI"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKCU "Software\JARVIS AI"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\JARVIS AI"
SectionEnd

; ─── Installer Finished ─────────────────────────────────────────
Function .onInstSuccess
  MessageBox MB_OK "JARVIS AI Desktop has been installed successfully!$\n$\nClick 'Finish' to start the application."
  Exec "$INSTDIR\START_JARVIS_BROWSER.bat"
FunctionEnd
