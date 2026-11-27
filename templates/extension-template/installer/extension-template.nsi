Unicode true
ManifestDPIAware true

!include "MUI2.nsh"
!define APP_NAME "Alp 示例扩展"
!define EXT_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\Alp Example Extension"
!define EXT_SUBDIR "Example Extension\v1"
!define EXT_VERSION "1.0.0"
!define PAYLOAD_FILE "ExampleExtension.exe"
!ifndef SETUP_OUT
  !define SETUP_OUT "..\dist\Alp-Example-Extension-setup-v1.exe"
!endif

Name "${APP_NAME}"
OutFile "${SETUP_OUT}"
InstallDir "$PROGRAMFILES64\Alp Toolbox Extensions\${EXT_SUBDIR}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"

Section "Install"
  SetRegView 64
  StrCpy $INSTDIR "$PROGRAMFILES64\Alp Toolbox Extensions\${EXT_SUBDIR}"
  SetOutPath "$INSTDIR"
  SetOverwrite on
  ClearErrors
  File "..\payload\${PAYLOAD_FILE}"
  ; 随包带许可证时，补上对应的 File 和 Delete 指令。
  IfErrors install_failed
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  IfErrors install_failed
  WriteRegStr HKLM "${EXT_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "${EXT_KEY}" "DisplayVersion" "${EXT_VERSION}"
  WriteRegStr HKLM "${EXT_KEY}" "Publisher" "Alp Toolbox Community"
  WriteRegStr HKLM "${EXT_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${EXT_KEY}" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegDWORD HKLM "${EXT_KEY}" "NoModify" 1
  WriteRegDWORD HKLM "${EXT_KEY}" "NoRepair" 1
  Goto finished
install_failed:
  MessageBox MB_OK|MB_ICONEXCLAMATION "无法写入扩展文件。请从托盘退出 Alp 工具箱后重试。" /SD IDOK
  SetErrorLevel 1
  Abort
finished:
SectionEnd

Section "Uninstall"
  SetRegView 64
  ClearErrors
  Delete "$INSTDIR\${PAYLOAD_FILE}"
  IfFileExists "$INSTDIR\${PAYLOAD_FILE}" in_use
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  DeleteRegKey HKLM "${EXT_KEY}"
  Goto done
in_use:
  MessageBox MB_OK|MB_ICONEXCLAMATION "请从托盘退出 Alp 工具箱后重新卸载扩展。" /SD IDOK
  SetErrorLevel 1
  Abort
done:
SectionEnd
