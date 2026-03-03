# Fix whisper.cpp submodule when "not our ref" or fetch fails.
# Run from repo root: .\script\fix-whisper-submodule.ps1
# Then: git add whisper.cpp; git commit -m "fix: point whisper.cpp submodule to v1.8.3"

$ErrorActionPreference = "Stop"
$RepoRoot = (Get-Item $PSScriptRoot).Parent.FullName
$SubmodulePath = Join-Path $RepoRoot "whisper.cpp"
$WhisperRef = "v1.8.3"

Set-Location $RepoRoot

if (Test-Path $SubmodulePath) {
    Write-Host "Removing existing whisper.cpp ..."
    Remove-Item -Recurse -Force $SubmodulePath
}

# Remove stale submodule entry in .git if present
$GitModulesPath = Join-Path $RepoRoot ".git\modules\whisper.cpp"
if (Test-Path $GitModulesPath) {
    Write-Host "Removing .git\modules\whisper.cpp ..."
    Remove-Item -Recurse -Force $GitModulesPath
}

Write-Host "Cloning whisper.cpp and checking out $WhisperRef ..."
git clone --depth 1 --branch $WhisperRef https://github.com/ggerganov/whisper.cpp.git whisper.cpp
if ($LASTEXITCODE -ne 0) {
    Write-Host "Clone failed. Trying without branch (will use default branch)..."
    git clone https://github.com/ggerganov/whisper.cpp.git whisper.cpp
    Set-Location whisper.cpp
    git fetch --tags
    git checkout $WhisperRef
    Set-Location $RepoRoot
}

Write-Host "Done. To update the repo's submodule pointer, run:"
Write-Host "  git add whisper.cpp"
Write-Host "  git commit -m `"fix: point whisper.cpp submodule to $WhisperRef`""
