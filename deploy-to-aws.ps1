# TaxWise AWS Deployment Script
# This script deploys the TaxWise application to AWS Elastic Beanstalk

Write-Host "🚀 TaxWise AWS Deployment Script" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if AWS EB CLI is installed
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
try {
    eb --version | Out-Null
    Write-Host "✅ AWS EB CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS EB CLI not found. Installing..." -ForegroundColor Red
    Write-Host "Installing AWS EB CLI via pip..." -ForegroundColor Yellow
    pip install awsebcli
}

# Navigate to backend directory
Set-Location backend

# Step 1: Initialize Elastic Beanstalk (if not already initialized)
Write-Host ""
Write-Host "Step 1: Initializing Elastic Beanstalk..." -ForegroundColor Yellow
if (-not (Test-Path ".elasticbeanstalk/config.yml")) {
    Write-Host "First time setup - please answer the following questions:" -ForegroundColor Cyan
    eb init -p python-3.11 taxwise-backend --region us-east-1
} else {
    Write-Host "✅ Already initialized" -ForegroundColor Green
}

# Step 2: Check if environment exists
Write-Host ""
Write-Host "Step 2: Checking for existing environment..." -ForegroundColor Yellow
$envExists = $false
try {
    $status = eb status 2>&1
    if ($status -match "taxwise-backend-env") {
        $envExists = $true
        Write-Host "✅ Environment exists" -ForegroundColor Green
    }
} catch {
    Write-Host "No existing environment found" -ForegroundColor Yellow
}

# Step 3: Create or update environment
if (-not $envExists) {
    Write-Host ""
    Write-Host "Step 3: Creating new environment..." -ForegroundColor Yellow
    Write-Host "⏳ This may take 5-10 minutes..." -ForegroundColor Cyan
    eb create taxwise-backend-env --instance-type t2.micro --envvars "FLASK_ENV=production"
} else {
    Write-Host ""
    Write-Host "Step 3: Environment already exists, will deploy to it" -ForegroundColor Green
}

# Step 4: Set environment variables
Write-Host ""
Write-Host "Step 4: Setting environment variables..." -ForegroundColor Yellow
Write-Host "Please enter your Supabase credentials:" -ForegroundColor Cyan
$supabaseUrl = Read-Host "SUPABASE_URL"
$supabaseKey = Read-Host "SUPABASE_KEY"
$supabaseServiceKey = Read-Host "SUPABASE_SERVICE_KEY"

if ($supabaseUrl -and $supabaseKey -and $supabaseServiceKey) {
    eb setenv SUPABASE_URL=$supabaseUrl SUPABASE_KEY=$supabaseKey SUPABASE_SERVICE_KEY=$supabaseServiceKey FLASK_ENV=production
    Write-Host "✅ Environment variables set" -ForegroundColor Green
} else {
    Write-Host "⚠️  Skipping environment variables (you can set them later)" -ForegroundColor Yellow
}

# Step 5: Deploy
Write-Host ""
Write-Host "Step 5: Deploying application..." -ForegroundColor Yellow
Write-Host "⏳ Deploying to AWS..." -ForegroundColor Cyan
eb deploy

# Step 6: Get status and URL
Write-Host ""
Write-Host "Step 6: Getting deployment status..." -ForegroundColor Yellow
eb status

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Get your backend URL with: eb status" -ForegroundColor White
Write-Host "2. Update frontend API URL in: frontend/temp/src/utils/supabase/client.tsx" -ForegroundColor White
Write-Host "3. Build and deploy frontend to S3" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  eb status    - Check environment status" -ForegroundColor White
Write-Host "  eb health    - Check application health" -ForegroundColor White
Write-Host "  eb logs      - View application logs" -ForegroundColor White
Write-Host "  eb ssh       - SSH into EC2 instance" -ForegroundColor White
Write-Host "  eb terminate - Delete environment (stop costs)" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Remember to monitor your AWS Free Tier usage!" -ForegroundColor Yellow
Write-Host "Visit: https://console.aws.amazon.com/billing/home#/freetier" -ForegroundColor Cyan
