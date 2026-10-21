Write-Host "TRACE TEST SCRIPT RUNNING SUCCESSFULLY" -ForegroundColor Green
Write-Host "Working directory: $((Get-Location).Path)"
Write-Host "Python version:"
python --version
Write-Host "Git branch:"
git branch --show-current
