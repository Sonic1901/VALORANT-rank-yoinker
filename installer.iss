#define MyAppName "VALORANT Rank Yoinker"
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif
#define MyAppExeName "vry.exe"

[Setup]
AppId={{217f0fa8-4152-43b2-9326-2b0428940dc0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher=Sonic1901
AppPublisherURL=https://github.com/Sonic1901
AppSupportURL=https://github.com/Sonic1901
AppUpdatesURL=https://github.com/Sonic1901
AppComments=Community VALORANT tracker by Sonic1901
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=vry-{#MyAppVersion}-setup
SetupIconFile=assets\Logo.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern dynamic windows11 includetitlebar
WizardResizable=yes
WizardSizePercent=100

[Files]
Source: "dist\vry\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch vry"; Flags: nowait postinstall skipifsilent

[Code]
const
  WebView2BootstrapperUrl = 'https://go.microsoft.com/fwlink/?linkid=2124703';
  VisualCppRedistributableUrl = 'https://aka.ms/vs/17/release/vc_redist.x64.exe';

function IsWebView2Installed: Boolean;
var
  Version: String;
begin
  Result :=
    RegQueryStringValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and
    (Version <> '') and (Version <> '0.0.0.0');

  if not Result then
    Result :=
      RegQueryStringValue(HKCU, 'SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}', 'pv', Version) and
      (Version <> '') and (Version <> '0.0.0.0');
end;

function IsVisualCppInstalled: Boolean;
var
  Installed: Cardinal;
begin
  Result :=
    RegQueryDWordValue(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) and
    (Installed = 1);

  if not Result then
    Result :=
      RegQueryDWordValue(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64', 'Installed', Installed) and
      (Installed = 1);
end;

function InstallPrerequisite(const Name, Url, FileName, Parameters: String): Boolean;
var
  TempFile: String;
  ResultCode: Integer;
begin
  TempFile := ExpandConstant('{tmp}\' + FileName);
  WizardForm.StatusLabel.Caption := 'Downloading ' + Name + '...';
  try
    DownloadTemporaryFile(Url, FileName, '', nil);
  except
    MsgBox('Could not download ' + Name + '. Please install it manually and run this installer again.' + #13#10 + Url, mbError, MB_OK);
    Result := False;
    exit;
  end;

  if not FileExists(TempFile) then
  begin
    MsgBox('The downloaded ' + Name + ' installer could not be found. Please install it manually and run this installer again.', mbError, MB_OK);
    Result := False;
    exit;
  end;

  WizardForm.StatusLabel.Caption := 'Installing ' + Name + '...';
  Result := Exec(TempFile, Parameters, '', SW_SHOWNORMAL, ewWaitUntilTerminated, ResultCode) and
    (ResultCode = 0);
  if not Result then
    MsgBox(Name + ' installation did not complete successfully. Please install it manually and run this installer again.', mbError, MB_OK);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  Result := '';
  if not IsWebView2Installed then
    if not InstallPrerequisite('Microsoft Edge WebView2 Runtime', WebView2BootstrapperUrl, 'MicrosoftEdgeWebView2Setup.exe', '/silent /install') then
    begin
      Result := 'Microsoft Edge WebView2 Runtime is required.';
      exit;
    end;

  if not IsVisualCppInstalled then
    if not InstallPrerequisite('Microsoft Visual C++ Redistributable', VisualCppRedistributableUrl, 'vc_redist.x64.exe', '/install /quiet /norestart') then
      Result := 'Microsoft Visual C++ Redistributable is required.';
end;