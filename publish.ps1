# Publish Task Management System to GitHub
# Run in PowerShell from this folder after: gh auth login

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "Checking GitHub login..."
gh auth status 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Not logged in. Run this first:"
    Write-Host "  gh auth login"
    Write-Host ""
    Write-Host "Choose: GitHub.com -> HTTPS -> Login with a web browser"
    exit 1
}

$repoName = "task-management-system"
Write-Host "Creating public repo: $repoName"
gh repo create $repoName --public --source=. --remote=origin --push --description "College Task Management System - Flask, MySQL, HTML/CSS/JS"

if ($LASTEXITCODE -eq 0) {
    gh repo view --web
    Write-Host ""
    Write-Host "Done! Your repo URL:"
    gh repo view --json url -q .url
}
