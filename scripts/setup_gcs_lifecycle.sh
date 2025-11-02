#!/bin/bash
# Setup GCS bucket with lifecycle policy for auto-cleanup
#
# Usage:
#   ./scripts/setup_gcs_lifecycle.sh YOUR_PROJECT_ID your-bucket-name
#
# This script:
# 1. Creates a GCS bucket in us-central1
# 2. Sets a lifecycle policy to auto-delete files after 7 days
#
# Why 7 days?
# - Videos are deleted immediately after successful download
# - 7-day policy catches orphaned files from failed/interrupted runs
# - Minimizes storage costs with zero manual intervention

set -e

if [ $# -ne 2 ]; then
    echo "Usage: $0 PROJECT_ID BUCKET_NAME"
    echo "Example: $0 my-project veo-videos-myname"
    exit 1
fi

PROJECT_ID=$1
BUCKET_NAME=$2
BUCKET_URI="gs://${BUCKET_NAME}"

echo "📦 Setting up GCS bucket: ${BUCKET_URI}"
echo ""

# Create bucket
echo "1️⃣  Creating bucket..."
if gsutil ls "${BUCKET_URI}" 2>/dev/null; then
    echo "   ✅ Bucket already exists"
else
    gsutil mb -p "${PROJECT_ID}" -l us-central1 "${BUCKET_URI}"
    echo "   ✅ Bucket created"
fi

# Create lifecycle policy JSON
LIFECYCLE_FILE=$(mktemp)
cat > "${LIFECYCLE_FILE}" << 'EOF'
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
EOF

echo ""
echo "2️⃣  Setting lifecycle policy (auto-delete after 7 days)..."
gsutil lifecycle set "${LIFECYCLE_FILE}" "${BUCKET_URI}"
echo "   ✅ Lifecycle policy set"

# Cleanup temp file
rm "${LIFECYCLE_FILE}"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Add this to your .env file:"
echo "VERTEX_VEO_OUTPUT_BUCKET=${BUCKET_URI}/"
echo ""
echo "Storage cleanup:"
echo "  • Videos deleted immediately after download (primary)"
echo "  • Orphaned files auto-deleted after 7 days (backup)"
echo "  • Zero manual intervention needed! 🎉"





