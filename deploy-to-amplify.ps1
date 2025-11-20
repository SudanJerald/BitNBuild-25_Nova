# TaxWise - AWS Amplify Deployment Script

Write-Host "🚀 Deploying TaxWise to AWS Amplify" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit for Amplify deployment"
}

# Check current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Cyan

# Check if Amplify CLI is installed
Write-Host ""
Write-Host "Checking for Amplify CLI..." -ForegroundColor Yellow
try {
    amplify --version | Out-Null
    Write-Host "✅ Amplify CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ Amplify CLI not found. Installing..." -ForegroundColor Red
    npm install -g @aws-amplify/cli
    Write-Host "✅ Amplify CLI installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  Choose Deployment Method" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 🌐 Deploy via Amplify Console (Recommended - Easiest)" -ForegroundColor White
Write-Host "   - One-click deployment from GitHub" -ForegroundColor Gray
Write-Host "   - Automatic CI/CD" -ForegroundColor Gray
Write-Host "   - Preview deployments for PRs" -ForegroundColor Gray
Write-Host ""
Write-Host "2. 💻 Deploy via Amplify CLI (More Control)" -ForegroundColor White
Write-Host "   - Command-line deployment" -ForegroundColor Gray
Write-Host "   - Direct from local machine" -ForegroundColor Gray
Write-Host "   - Manual configuration" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Enter choice (1 or 2)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "🌐 Deploying via Amplify Console" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check if code is on GitHub
    $remoteUrl = git remote get-url origin 2>$null
    
    if (-not $remoteUrl) {
        Write-Host "⚠️  Your code is not connected to GitHub yet." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Steps to deploy:" -ForegroundColor Cyan
        Write-Host "1. Create a new repository on GitHub: https://github.com/new" -ForegroundColor White
        Write-Host "2. Run these commands:" -ForegroundColor White
        Write-Host ""
        Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git" -ForegroundColor Yellow
        Write-Host "   git branch -M main" -ForegroundColor Yellow
        Write-Host "   git push -u origin main" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "3. Then visit: https://console.aws.amazon.com/amplify/" -ForegroundColor White
        Write-Host "4. Click 'New app' → 'Host web app'" -ForegroundColor White
        Write-Host "5. Connect your GitHub repository" -ForegroundColor White
        Write-Host "6. Add environment variables:" -ForegroundColor White
        Write-Host "   - SUPABASE_URL" -ForegroundColor Gray
        Write-Host "   - SUPABASE_KEY" -ForegroundColor Gray
        Write-Host "   - SUPABASE_SERVICE_KEY" -ForegroundColor Gray
        Write-Host "7. Click 'Save and deploy'" -ForegroundColor White
    } else {
        Write-Host "✅ GitHub repository found: $remoteUrl" -ForegroundColor Green
        Write-Host ""
        Write-Host "Pushing latest changes to GitHub..." -ForegroundColor Yellow
        git add .
        git commit -m "Prepare for Amplify deployment" 2>$null
        git push
        
        Write-Host ""
        Write-Host "✅ Code pushed to GitHub!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Open Amplify Console: https://console.aws.amazon.com/amplify/" -ForegroundColor White
        Write-Host "2. Click 'New app' → 'Host web app'" -ForegroundColor White
        Write-Host "3. Choose 'GitHub' and authorize" -ForegroundColor White
        Write-Host "4. Select your repository and branch: $currentBranch" -ForegroundColor White
        Write-Host "5. Amplify will auto-detect amplify.yml configuration ✅" -ForegroundColor White
        Write-Host "6. Add environment variables in 'Advanced settings':" -ForegroundColor White
        Write-Host ""
        Write-Host "   Environment Variables to Add:" -ForegroundColor Cyan
        Write-Host "   ────────────────────────────" -ForegroundColor Cyan
        
        # Prompt for environment variables
        Write-Host ""
        $supabaseUrl = Read-Host "   SUPABASE_URL"
        $supabaseKey = Read-Host "   SUPABASE_KEY"
        $supabaseServiceKey = Read-Host "   SUPABASE_SERVICE_KEY"
        
        Write-Host ""
        Write-Host "   Copy these values when adding environment variables in Amplify:" -ForegroundColor Yellow
        Write-Host "   ─────────────────────────────────────────────────────────────" -ForegroundColor Gray
        Write-Host "   SUPABASE_URL = $supabaseUrl" -ForegroundColor White
        Write-Host "   SUPABASE_KEY = $supabaseKey" -ForegroundColor White
        Write-Host "   SUPABASE_SERVICE_KEY = $supabaseServiceKey" -ForegroundColor White
        Write-Host ""
        Write-Host "7. Click 'Save and deploy'" -ForegroundColor White
        Write-Host "8. Wait 5-10 minutes for build to complete" -ForegroundColor White
        Write-Host "9. Your app will be live at: https://$currentBranch.xxxxxx.amplifyapp.com" -ForegroundColor White
        Write-Host ""
        
        # Ask if they want to open Amplify Console
        $openConsole = Read-Host "Open Amplify Console in browser? (y/n)"
        if ($openConsole -eq "y") {
            Start-Process "https://console.aws.amazon.com/amplify/"
        }
    }
    
} elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "💻 Deploying via Amplify CLI" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host ""
    
    # Configure Amplify
    Write-Host "Configuring Amplify..." -ForegroundColor Yellow
    Write-Host "You'll need to log in to your AWS account" -ForegroundColor Cyan
    amplify configure
    
    # Initialize Amplify
    Write-Host ""
    Write-Host "Initializing Amplify project..." -ForegroundColor Yellow
    
    if (-not (Test-Path "amplify")) {
        amplify init
    } else {
        Write-Host "✅ Amplify already initialized" -ForegroundColor Green
    }
    
    # Add hosting
    Write-Host ""
    Write-Host "Adding hosting..." -ForegroundColor Yellow
    amplify add hosting
    
    # Publish
    Write-Host ""
    Write-Host "Publishing to Amplify..." -ForegroundColor Yellow
    Write-Host "⏳ This may take 5-10 minutes..." -ForegroundColor Cyan
    amplify publish
    
    Write-Host ""
    Write-Host "🎉 Deployment complete!" -ForegroundColor Green
    
} else {
    Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  ✅ Setup Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 Useful Resources:" -ForegroundColor Yellow
Write-Host "  • Amplify Console: https://console.aws.amazon.com/amplify/" -ForegroundColor White
Write-Host "  • Documentation: https://docs.amplify.aws/" -ForegroundColor White
Write-Host "  • Full Guide: See AMPLIFY_DEPLOYMENT.md" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "  • Every git push will auto-deploy your app" -ForegroundColor White
Write-Host "  • SSL certificate is automatically provisioned" -ForegroundColor White
Write-Host "  • Add custom domain in Amplify Console" -ForegroundColor White
Write-Host "  • Monitor builds in Amplify Console" -ForegroundColor White
Write-Host ""
Write-Host "💰 Cost: $0/month (Free Tier)" -ForegroundColor Green
Write-Host ""
