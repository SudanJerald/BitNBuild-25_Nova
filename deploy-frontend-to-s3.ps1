# TaxWise Frontend S3 Deployment Script

Write-Host "🌐 TaxWise Frontend S3 Deployment" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Get backend URL
Write-Host "First, we need your backend URL from AWS Elastic Beanstalk" -ForegroundColor Yellow
$backendUrl = Read-Host "Enter your backend URL (e.g., http://taxwise-backend-env.xxxxx.elasticbeanstalk.com)"

if (-not $backendUrl) {
    Write-Host "❌ Backend URL is required!" -ForegroundColor Red
    exit 1
}

# Navigate to frontend
Set-Location frontend/temp

# Update API URL in client.tsx
Write-Host ""
Write-Host "Updating API URL in frontend..." -ForegroundColor Yellow
$clientFile = "src/utils/supabase/client.tsx"
$content = Get-Content $clientFile -Raw
$content = $content -replace "http://localhost:5000", $backendUrl
Set-Content $clientFile $content
Write-Host "✅ API URL updated to: $backendUrl" -ForegroundColor Green

# Build frontend
Write-Host ""
Write-Host "Building frontend..." -ForegroundColor Yellow
npm run build

if (-not (Test-Path "build")) {
    Write-Host "❌ Build failed! Check for errors above." -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build completed" -ForegroundColor Green

# Get S3 bucket name
Write-Host ""
Write-Host "AWS S3 Setup" -ForegroundColor Cyan
$bucketName = Read-Host "Enter S3 bucket name (e.g., taxwise-frontend-yourname)"

# Create S3 bucket
Write-Host ""
Write-Host "Creating S3 bucket..." -ForegroundColor Yellow
try {
    aws s3 mb "s3://$bucketName" 2>&1 | Out-Null
    Write-Host "✅ Bucket created: $bucketName" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Bucket might already exist, continuing..." -ForegroundColor Yellow
}

# Configure bucket for static website hosting
Write-Host ""
Write-Host "Configuring static website hosting..." -ForegroundColor Yellow
aws s3 website "s3://$bucketName" --index-document index.html --error-document index.html

# Upload files
Write-Host ""
Write-Host "Uploading files to S3..." -ForegroundColor Yellow
Write-Host "⏳ This may take a few minutes..." -ForegroundColor Cyan
aws s3 sync build/ "s3://$bucketName" --acl public-read --delete

# Create bucket policy for public access
Write-Host ""
Write-Host "Setting bucket policy for public access..." -ForegroundColor Yellow
$policy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$bucketName/*"
    }
  ]
}
"@

$policy | Out-File -FilePath policy.json -Encoding ASCII
aws s3api put-bucket-policy --bucket $bucketName --policy file://policy.json
Remove-Item policy.json

# Get website URL
$region = aws configure get region
if (-not $region) { $region = "us-east-1" }
$websiteUrl = "http://$bucketName.s3-website-$region.amazonaws.com"

Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your application is now live at:" -ForegroundColor Yellow
Write-Host $websiteUrl -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test your application at the URL above" -ForegroundColor White
Write-Host "2. (Optional) Setup CloudFront for HTTPS and faster delivery" -ForegroundColor White
Write-Host "3. (Optional) Configure custom domain" -ForegroundColor White
Write-Host ""
Write-Host "To update your app in the future:" -ForegroundColor Yellow
Write-Host "1. Make changes to your code" -ForegroundColor White
Write-Host "2. Run: npm run build" -ForegroundColor White
Write-Host "3. Run: aws s3 sync build/ s3://$bucketName --acl public-read --delete" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Free Tier Limits:" -ForegroundColor Yellow
Write-Host "  - 5GB storage" -ForegroundColor White
Write-Host "  - 20,000 GET requests/month" -ForegroundColor White
Write-Host "  - 2,000 PUT requests/month" -ForegroundColor White
