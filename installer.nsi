; NSIS Installer Script for Searcher Browser
; This creates a professional Windows installer

!include "MUI2.nsh"
!include "x64.nsh"

; Application Information
Name "Searcher Browser"
OutFile "SearcherBrowserInstaller.exe"
InstallDir "$PROGRAMFILES64\Searcher"
InstallDirRegKey HKCU "Software\Searcher" "Install_Dir"

; Request admin privileges
RequestExecutionLevel admin

; UI Settings
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Installer Section
Section "Install"
  SetOutPath "$INSTDIR"
  
  ; Check if Searcher.exe exists
  ${If} ${FileExists} "dist\Searcher.exe"
    File "dist\Searcher.exe"
  ${Else}
    MessageBox MB_OK "Error: Searcher.exe not found in dist\ folder"
    Abort
  ${EndIf}
  
  ; Copy assets folder
  ${If} ${FileExists} "assets"
    SetOutPath "$INSTDIR\assets"
    File /r "assets\*.*"
  ${EndIf}
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\Searcher"
  CreateShortCut "$SMPROGRAMS\Searcher\Searcher Browser.lnk" "$INSTDIR\Searcher.exe" "" "$INSTDIR\Searcher.exe" 0
  CreateShortCut "$SMPROGRAMS\Searcher\Uninstall.lnk" "$INSTDIR\Uninstall.exe" "" "$INSTDIR\Uninstall.exe" 0
  CreateShortCut "$DESKTOP\Searcher Browser.lnk" "$INSTDIR\Searcher.exe" "" "$INSTDIR\Searcher.exe" 0
  
  ; Store installation folder in registry
  WriteRegStr HKCU "Software\Searcher" "Install_Dir" "$INSTDIR"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Write registry entries for Add/Remove Programs
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher" "DisplayName" "Searcher Browser"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher" "UninstallString" "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher" "InstallLocation" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher" "Publisher" "Searcher Team"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher" "DisplayVersion" "1.0.0"
  
SectionEnd

; Uninstaller Section
Section "Uninstall"
  ; Remove files
  Delete "$INSTDIR\Searcher.exe"
  Delete "$INSTDIR\Uninstall.exe"
  
  ; Remove assets folder
  RMDir /r "$INSTDIR\assets"
  RMDir /r "$INSTDIR\_internal"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\Searcher\Searcher Browser.lnk"
  Delete "$SMPROGRAMS\Searcher\Uninstall.lnk"
  Delete "$DESKTOP\Searcher Browser.lnk"
  RMDir "$SMPROGRAMS\Searcher"
  
  ; Remove directory
  RMDir "$INSTDIR"
  
  ; Remove registry entries
  DeleteRegKey HKCU "Software\Searcher"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\Searcher"
  
SectionEnd
