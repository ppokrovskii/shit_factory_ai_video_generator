# Setup GCS bucket with lifecycle policy for auto-cleanup
#
# Usage:
#   .\scripts\setup_gcs_lifecycle.ps1 YOUR_PROJECT_ID your-bucket-name
#
# This script:
# 1. Creates a GCS bucket in us-central1
# 2. Sets a lifecycle policy to auto-delete files after 7 days
#
# Why 7 days?
# - Videos are deleted immediately after successful download
# - 7-day policy catches orphaned files from failed/interrupted runs
# - Minimizes storage costs with zero manual intervention

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$BucketName
)

$BucketUri = "gs://$BucketName"

Write-Host "📦 Setting up GCS bucket: $BucketUri" -ForegroundColor Cyan
Write-Host ""

# Create bucket
Write-Host "1️⃣  Creating bucket..." -ForegroundColor Yellow
try {
    $null = gsutil ls $BucketUri 2>$null
    Write-Host "   ✅ Bucket already exists" -ForegroundColor Green
} catch {
    gsutil mb -p $ProjectId -l us-central1 $BucketUri
    Write-Host "   ✅ Bucket created" -ForegroundColor Green
}

# Create lifecycle policy JSON
$LifecycleJson = @"
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 7}
      }
    ]
  }
}
"@

$TempFile = [System.IO.Path]::GetTempFileName()
$LifecycleJson | Out-File -FilePath $TempFile -Encoding UTF8

Write-Host ""
Write-Host "2️⃣  Setting lifecycle policy (auto-delete after 7 days)..." -ForegroundColor Yellow
gsutil lifecycle set $TempFile $BucketUri
Write-Host "   ✅ Lifecycle policy set" -ForegroundColor Green

# Cleanup temp file
Remove-Item $TempFile

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Add this to your .env file:" -ForegroundColor Cyan
Write-Host "VERTEX_VEO_OUTPUT_BUCKET=$BucketUri/" -ForegroundColor White
Write-Host ""
Write-Host "Storage cleanup:" -ForegroundColor Cyan
Write-Host "  • Videos deleted immediately after download (primary)" -ForegroundColor White
Write-Host "  • Orphaned files auto-deleted after 7 days (backup)" -ForegroundColor White
Write-Host "  • Zero manual intervention needed! 🎉" -ForegroundColor White







