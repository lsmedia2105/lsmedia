param([switch]$EditorOnly, [switch]$InstallOnly)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.UTF8Encoding]::new()
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8:backslashreplace'
$root = $PSScriptRoot
Set-Location -LiteralPath $root
$runtime = Join-Path $root '.runtime'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Get-Studio {
    try { return Invoke-RestMethod 'http://127.0.0.1:8090/api/status' -TimeoutSec 2 } catch { return $null }
}
function Get-OllamaTags {
    try { return Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 } catch { return $null }
}
function Get-VerifiedInstaller($url, $file, $publisher) {
    Write-Host "Downloading official installer: $url"
    Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $file
    $signature = Get-AuthenticodeSignature -FilePath $file
    if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch $publisher) {
        throw "Installer signature/publisher verification failed: $file. File was not executed."
    }
}
function Test-Python($exe, $arguments) {
    try {
        $result = & $exe @arguments -c "import sys,struct;print('LS-PY311-OK' if sys.version_info[:2]==(3,11) and struct.calcsize('P')==8 else 'NO')" 2>$null
        return $LASTEXITCODE -eq 0 -and $result -contains 'LS-PY311-OK'
    } catch { return $false }
}

$failed = $false
try {
    if (-not [Environment]::Is64BitOperatingSystem -or $env:PROCESSOR_ARCHITECTURE -eq 'ARM64') {
        throw 'This package requires Windows 10/11 x64. ARM64 is not supported by this installer.'
    }
    if (-not $InstallOnly) {
        $live = Get-Studio
        if ($live -and $live.application -eq 'LS-PIXEL-STUDIO' -and $live.version -eq 4) {
            Write-Host 'Studio V4 is already running. Opening the existing window.'
            Start-Process 'http://127.0.0.1:8090'
            exit 0
        }
        # Never reinstall/rename the AI environment while an older studio owns the port.
        if ($live) { throw 'Port 8090 is in use. Close the old studio/CMD first, then start V4 again.' }
    }
    $python = $null
    $pythonArgs = @()
    $privatePython = Join-Path $env:LOCALAPPDATA 'LS-Pixel-Studio\Python311\python.exe'
    if (Test-Path -LiteralPath $privatePython) {
        if (Test-Python $privatePython @()) { $python = $privatePython }
    }
    if (-not $python -and (Get-Command py.exe -ErrorAction SilentlyContinue)) {
        if (Test-Python 'py.exe' @('-3.11')) { $python = 'py.exe'; $pythonArgs = @('-3.11') }
    }
    if (-not $python -and (Get-Command python.exe -ErrorAction SilentlyContinue)) {
        if (Test-Python 'python.exe' @()) { $python = 'python.exe' }
    }
    if (-not $python) {
        $installer = Join-Path $runtime 'python-3.11.9-amd64.exe'
        Get-VerifiedInstaller 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' $installer 'Python Software Foundation'
        $target = Split-Path -Parent $privatePython
        $arguments = '/quiet InstallAllUsers=0 Include_launcher=0 Include_test=0 PrependPath=0 Shortcuts=0 TargetDir="' + $target + '"'
        $process = Start-Process -FilePath $installer -ArgumentList $arguments -Wait -PassThru
        if ($process.ExitCode -notin @(0,3010) -or -not (Test-Python $privatePython @())) { throw 'Python installation failed. Install Python 3.11 x64 from python.org, then run again.' }
        $python = $privatePython
    }
    Write-Host 'LS Pixel Studio V4 - checking this computer.'
    Write-Host 'First full setup needs Internet and several GB of downloads. Keep this window open.'
    if (-not $EditorOnly) {
        try {
            $vc = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64' -ErrorAction SilentlyContinue
            if (-not $vc -or $vc.Installed -ne 1) {
                $installer = Join-Path $runtime 'vc_redist.x64.exe'
                Get-VerifiedInstaller 'https://aka.ms/vs/17/release/vc_redist.x64.exe' $installer 'Microsoft Corporation'
                $process = Start-Process -FilePath $installer -ArgumentList '/install /quiet /norestart' -Wait -PassThru
                if ($process.ExitCode -notin @(0,1638,3010)) { throw 'Visual C++ runtime installation failed.' }
            }
        } catch { $failed = $true; Write-Warning ('Visual C++ runtime: ' + $_.Exception.Message) }
        & $python @pythonArgs -X utf8 (Join-Path $root 'photo-3d-ai\setup.py') --download-models
        if ($LASTEXITCODE -ne 0) { $failed = $true; Write-Warning '3D AI setup/download did not complete. The editor can still open. Retry START-STUDIO.bat when the connection is available.' }
        try {
            $tags = Get-OllamaTags
            $ollama = (Get-Command ollama.exe -ErrorAction SilentlyContinue).Source
            if (-not $ollama) {
                $candidate = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
                if (Test-Path -LiteralPath $candidate) { $ollama = $candidate }
            }
            if (-not $tags -and -not $ollama) {
                $installer = Join-Path $runtime 'OllamaSetup.exe'
                Get-VerifiedInstaller 'https://ollama.com/download/OllamaSetup.exe' $installer '(?i)Ollama'
                $process = Start-Process -FilePath $installer -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP-' -Wait -PassThru
                if ($process.ExitCode -ne 0) { throw 'Ollama installer failed.' }
                $ollama = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
            }
            if (-not $tags) {
                if (-not $ollama) { throw 'Ollama executable not found.' }
                Start-Process -FilePath $ollama -ArgumentList 'serve' -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'ollama-out.log') -RedirectStandardError (Join-Path $runtime 'ollama-error.log')
                for ($attempt=0; $attempt -lt 30; $attempt++) {
                    Start-Sleep -Seconds 1
                    $tags = Get-OllamaTags
                    if ($tags) { break }
                }
                if (-not $tags) { throw 'Ollama did not start. Open Ollama manually, then try again.' }
            }
            $model = if ($env:LS_VISION_MODEL) { $env:LS_VISION_MODEL } else { 'qwen2.5vl:3b' }
            $available = @($tags.models | Where-Object { $_.name -eq $model -or $_.model -eq $model })
            if ($available.Count -eq 0) {
                if (-not $ollama) { throw 'Model is missing and ollama.exe was not found.' }
                Write-Host "Downloading local vision/camera model: $model"
                & $ollama pull $model
                if ($LASTEXITCODE -ne 0) { throw 'Ollama model download failed.' }
            }
            Write-Host 'Ollama/model found. Ollama selects its supported GPU/CPU independently of TripoSR.'
        } catch { $failed = $true; Write-Warning ('Vision AI is not ready: ' + $_.Exception.Message + ' Official installer: https://ollama.com/download/windows') }
    }
    if ($InstallOnly) { if ($failed) { exit 1 } else { exit 0 } }
    if ($failed) { Write-Warning 'Some AI components are unavailable. Studio opens with presets, manual cameras and offline storyboard tools. See messages above.' }
    & $python @pythonArgs -X utf8 (Join-Path $root 'scene-studio\server.py')
    exit $LASTEXITCODE
} catch {
    Write-Host ('Startup failed: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'To open only the editor (without heavy AI installation), run START-EDITOR-ONLY.bat.'
    exit 1
}
