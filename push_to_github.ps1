# Git Push Helper Script for Windows PowerShell
# Run this script to push your code to GitHub

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  CRYPTO TRADING BOT - GITHUB PUSH SCRIPT" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ Git is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Git is installed" -ForegroundColor Green
Write-Host ""

# Check if already in git repository
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git repository already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 1: Checking for sensitive data..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Run verification
python verification_script.py

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 2: Staging files..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

git add .
Write-Host "✓ Files staged" -ForegroundColor Green

Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Yellow
git status --short

Write-Host ""
$confirm = Read-Host "Do you want to continue with the commit? (yes/no)"

if ($confirm -ne "yes") {
    Write-Host "❌ Commit cancelled by user" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 3: Committing..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$commitMessage = @"
Initial commit: Full-stack crypto trading bot

Features:
- FastAPI backend with JWT authentication
- React frontend with TailwindCSS
- Binance Futures Testnet integration
- Market/Limit/Stop-Limit orders
- Real-time price fetching
- Trade history and statistics
- Bot configuration management
- Complete documentation

Tested and verified with live trading on Binance Futures Testnet.
"@

git commit -m $commitMessage
Write-Host "✓ Files committed" -ForegroundColor Green

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 4: Setting up remote..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if remote already exists
$remoteExists = git remote | Select-String -Pattern "origin"

if ($remoteExists) {
    Write-Host "✓ Remote 'origin' already exists" -ForegroundColor Green
} else {
    Write-Host "Adding remote repository..." -ForegroundColor Yellow
    git remote add origin https://github.com/apoorvpandey048/Crypto-Trading-Bot.git
    Write-Host "✓ Remote added" -ForegroundColor Green
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  STEP 5: Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "(You may be prompted for your GitHub username and personal access token)" -ForegroundColor Cyan
Write-Host ""

# Check current branch
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    $currentBranch = "main"
    git branch -M main
}

# Push to GitHub
git push -u origin $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  🎉 SUCCESS! Repository pushed to GitHub!" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your repository is now live at:" -ForegroundColor Cyan
    Write-Host "https://github.com/apoorvpandey048/Crypto-Trading-Bot" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Visit the repository URL above" -ForegroundColor White
    Write-Host "2. Verify all files are present" -ForegroundColor White
    Write-Host "3. Check that README renders correctly" -ForegroundColor White
    Write-Host "4. Share with others!" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host "  ❌ Push failed!" -ForegroundColor Red
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Authentication failed:" -ForegroundColor White
    Write-Host "   - You need a Personal Access Token (not password)" -ForegroundColor Gray
    Write-Host "   - Get one at: https://github.com/settings/tokens" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Repository doesn't exist:" -ForegroundColor White
    Write-Host "   - Create it on GitHub first: https://github.com/new" -ForegroundColor Gray
    Write-Host "   - Repository name: Crypto-Trading-Bot" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Remote URL wrong:" -ForegroundColor White
    Write-Host "   - Run: git remote set-url origin <your-repo-url>" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
