#!/bin/bash

# Configuration - CORRECTED: Using PROJECT_ID, not project number
PROJECT_ID="qwiklabs-gcp-02-b02e3ca6f413"  # This is the PROJECT ID
PROJECT_NUMBER="939854106735"              # This is the PROJECT NUMBER  
POOL_ID="agentic-era-hack-pool" 
PROVIDER_ID="agentic-era-hack-provider"
SERVICE_ACCOUNT="agentic-era-hack-cicd-sa@qwiklabs-gcp-02-b02e3ca6f413.iam.gserviceaccount.com"
REPO="yourusername/agentic-era-hack"  # Replace with your actual GitHub repo

echo "Setting up Workload Identity Federation for GitHub Actions..."

# Step 1: Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com --project=$PROJECT_ID
gcloud services enable sts.googleapis.com --project=$PROJECT_ID

# Step 2: Create Workload Identity Pool
echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create $POOL_ID \
    --project=$PROJECT_ID \
    --location="global" \
    --display-name="GitHub Actions Pool"

# Step 3: Create OIDC Provider for GitHub Actions
echo "Creating GitHub OIDC Provider..."
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
    --project=$PROJECT_ID \
    --location="global" \
    --workload-identity-pool=$POOL_ID \
    --display-name="GitHub Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com"

# Step 4: Allow the GitHub repo to impersonate the service account
echo "Binding service account to GitHub repository..."
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$REPO"

# Step 5: Verify the setup
echo "Verifying Workload Identity Pool..."
gcloud iam workload-identity-pools describe $POOL_ID \
    --project=$PROJECT_ID \
    --location="global"

echo "Verifying Provider..."
gcloud iam workload-identity-pools providers describe $PROVIDER_ID \
    --project=$PROJECT_ID \
    --location="global" \
    --workload-identity-pool=$POOL_ID

echo "Setup complete!"
echo ""
echo "Full workload_identity_provider string:"
echo "projects/$PROJECT_ID/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID"