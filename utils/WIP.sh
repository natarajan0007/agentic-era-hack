#!/bin/bash

# Configuration
PROJECT_ID="qwiklabs-gcp-03-bc59c8288afe"
PROJECT_NUMBER="1050008974311"
POOL_ID="agentic-era-hack-pool"
PROVIDER_ID="agentic-era-hack-provider"
SERVICE_ACCOUNT_NAME="agentic-era-hack-cicd-sa"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
REPO="student_02_6fa5ad690017/agentic-era-hack"

echo "Setting up Workload Identity Federation for GitHub Actions..."

# Step 1: Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com sts.googleapis.com --project=$PROJECT_ID

# Step 2: Create or get Service Account
echo "Creating or getting service account..."
gcloud iam service-accounts describe $SERVICE_ACCOUNT --project=$PROJECT_ID >/dev/null 2>&1
if [ $? -ne 0 ]; then
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --project=$PROJECT_ID \
        --display-name="GitHub Actions Service Account"
else
    echo "Service account $SERVICE_ACCOUNT already exists."
fi

# Step 3: Create Workload Identity Pool
echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools describe $POOL_ID --project=$PROJECT_ID --location="global" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    gcloud iam workload-identity-pools create $POOL_ID \
        --project=$PROJECT_ID \
        --location="global" \
        --display-name="GitHub Actions Pool"
else
    echo "Workload Identity Pool $POOL_ID already exists."
fi

# Step 4: Create OIDC Provider for GitHub Actions
echo "Creating GitHub OIDC Provider..."
gcloud iam workload-identity-pools providers describe $PROVIDER_ID --project=$PROJECT_ID --location="global" --workload-identity-pool=$POOL_ID >/dev/null 2>&1
if [ $? -ne 0 ]; then
    gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
        --project=$PROJECT_ID \
        --location="global" \
        --workload-identity-pool=$POOL_ID \
        --display-name="GitHub Provider" \
        --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
        --attribute-condition="assertion.repository == '$REPO'" \
        --issuer-uri="https://token.actions.githubusercontent.com"
else
    echo "Workload Identity Pool Provider $PROVIDER_ID already exists."
fi

# Step 5: Allow the GitHub repo to impersonate the service account
echo "Binding service account to GitHub repository..."
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/attribute.repository/$REPO"

# Step 6: Verify the setup
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
