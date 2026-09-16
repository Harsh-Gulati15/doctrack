#!/bin/bash
# ============================================================
#  DocTrack — Google Cloud Run Deployment Script
# ============================================================
set -euo pipefail

REGION="${REGION:-asia-south1}"
SERVICE_NAME="doctrack"
REPO_NAME="doctrack-repo"

# ── Prompt for project ID if not set ──
if [ -z "${PROJECT_ID:-}" ]; then
    read -rp "Enter your Google Cloud Project ID: " PROJECT_ID
fi

echo ""
echo "============================================"
echo "  DocTrack — Cloud Run Deployment"
echo "============================================"
echo "  Project:  $PROJECT_ID"
echo "  Region:   $REGION"
echo "  Service:  $SERVICE_NAME"
echo "============================================"
echo ""

# ── Authenticate (skips if already logged in) ──
echo "[1/6] Checking authentication..."
gcloud auth print-access-token > /dev/null 2>&1 || gcloud auth login
gcloud config set project "$PROJECT_ID"

# ── Enable required APIs ──
echo "[2/6] Enabling required APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    storage.googleapis.com \
    --quiet

# ── Create Artifact Registry repository (if not exists) ──
echo "[3/6] Creating Artifact Registry repository..."
gcloud artifacts repositories describe "$REPO_NAME" \
    --location="$REGION" > /dev/null 2>&1 || \
gcloud artifacts repositories create "$REPO_NAME" \
    --repository-format=docker \
    --location="$REGION" \
    --description="DocTrack Docker images" \
    --quiet

# ── Build and push image ──
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/doctrack:latest"
echo "[4/6] Building and pushing Docker image..."
gcloud builds submit --tag "$IMAGE" --quiet

# ── Deploy to Cloud Run ──
echo "[5/6] Deploying to Cloud Run..."

# Check if .env.cloud exists for env vars
ENV_VARS_FLAG=""
if [ -f ".env.cloud" ]; then
    echo "  Found .env.cloud — loading environment variables..."
    # Read .env.cloud and build --set-env-vars string
    ENV_VARS=$(grep -v '^#' .env.cloud | grep -v '^$' | tr '\n' ',' | sed 's/,$//')
    ENV_VARS_FLAG="--set-env-vars=${ENV_VARS}"
fi

gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 2 \
    --timeout 120 \
    $ENV_VARS_FLAG \
    --quiet

# ── Get the service URL ──
echo ""
echo "[6/6] Deployment complete!"
URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format='value(status.url)')
echo ""
echo "============================================"
echo "  ✅ DocTrack is live!"
echo "  URL: $URL"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Set environment variables in Cloud Run console or .env.cloud"
echo "  2. Run: python seed_mock_data.py (with DATABASE_URL pointing to cloud DB)"
echo ""
