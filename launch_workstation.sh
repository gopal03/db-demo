#!/bin/bash
# ==============================================================================
# GCP Database Demo Engine — Automated VM Workstation Launcher
# ==============================================================================
set -e

ZONE="us-central1-a"
REGION="us-central1"
VM_NAME="db-workstation"

echo "=========================================================="
echo "🛡️ GCP Workstation VM Launcher Initializing..."
echo "=========================================================="

# 1. Verify gcloud CLI installation
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI (gcloud) is not installed on your local Mac."
    echo "👉 Please install it first: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# 2. Check gcloud authentication status
echo "Checking GCP active account..."
ACTIVE_ACCOUNT=$(gcloud config get-value account 2>/dev/null || echo "")
if [ -z "$ACTIVE_ACCOUNT" ]; then
    echo "❌ No active GCP account authenticated."
    echo "👉 Please run the following command to authenticate, then re-run this script:"
    echo "   gcloud auth login"
    exit 1
fi
echo "✔️ Authenticated as: $ACTIVE_ACCOUNT"

# 3. Detect and confirm target GCP Project ID
DETECTED_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
if [ -z "$DETECTED_PROJECT" ]; then
    read -p "❓ Enter GCP Project ID to deploy the workstation VM: " PROJECT_ID
else
    read -p "❓ Confirm target GCP Project ID [$DETECTED_PROJECT]: " input_project
    PROJECT_ID=${input_project:-$DETECTED_PROJECT}
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID cannot be empty."
    exit 1
fi

# Set project locally for session verification
gcloud config set project "$PROJECT_ID" >/dev/null 2>&1

# 4. Resolve Git remote repository URL for VM synchronization
REPO_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")
if [ -z "$REPO_URL" ]; then
    REPO_URL="https://github.com/gopalbhutada/db-demo.git"
else
    # Normalize SSH git URLs to standard HTTPS URLs for VM clone capability
    if [[ "$REPO_URL" == git@* ]]; then
        REPO_URL=$(echo "$REPO_URL" | sed -E 's/git@github.com:(.*)\.git/https:\/\/github.com\/\1/')
    fi
    # Ensure trailing .git suffix
    if [[ "$REPO_URL" != *.git ]]; then
        REPO_URL="${REPO_URL}.git"
    fi
fi

# 5. Silently ensure default IAP firewall ingress rule exists
echo "Verifying firewall ingress rules for IAP SSH access..."
FW_RULE="allow-ssh-from-iap-to-workstation"
if ! gcloud compute firewall-rules describe "$FW_RULE" --project="$PROJECT_ID" &>/dev/null; then
    echo "Creating firewall rule '$FW_RULE' to allow IAP SSH tunneling..."
    gcloud compute firewall-rules create "$FW_RULE" \
        --project="$PROJECT_ID" \
        --network="default" \
        --direction="INGRESS" \
        --priority=1000 \
        --action="ALLOW" \
        --rules=tcp:22 \
        --source-ranges="35.235.240.0/20" \
        --target-tags="db-workstation" >/dev/null
    echo "✔️ Firewall rule successfully deployed."
else
    echo "✔️ Firewall rule verified."
fi

# 6. Spin up the GCE VM Workstation instance
echo "🚀 Provisioning db-workstation VM instance..."
if gcloud compute instances describe "$VM_NAME" --project="$PROJECT_ID" --zone="$ZONE" &>/dev/null; then
    echo "⚠️ VM instance '$VM_NAME' already exists in project '$PROJECT_ID'."
    read -p "Do you want to re-use it and proceed to tunnels? (Y/n): " reuse_confirm
    if [[ "$reuse_confirm" == "n" || "$reuse_confirm" == "N" ]]; then
        echo "Exiting deployment."
        exit 0
    fi
else
    gcloud compute instances create "$VM_NAME" \
        --project="$PROJECT_ID" \
        --zone="$ZONE" \
        --machine-type="e2-standard-4" \
        --scopes="https://www.googleapis.com/auth/cloud-platform" \
        --metadata-from-file="startup-script=terraform/workstation/startup.sh" \
        --metadata="project_id=${PROJECT_ID},region=${REGION},github_repo_url=${REPO_URL}" \
        --image-family="ubuntu-2204-lts" \
        --image-project="ubuntu-os-cloud" \
        --boot-disk-size="50GB" \
        --tags="db-workstation"
    echo "✔️ VM instance created successfully."
fi

# 7. Poll the instance until configuration completes
echo "⏳ Waiting for workstation setup and packages installation (~2-3 minutes)..."
until gcloud compute ssh "$VM_NAME" --project="$PROJECT_ID" --zone="$ZONE" --tunnel-through-iap --command="test -f /tmp/setup_complete" &>/dev/null; do
    echo "   Configuration still in progress, checking again in 10 seconds..."
    sleep 10
done
echo "✔️ Workstation VM is fully initialized!"

# 8. Start Background SSH Port Forwarding Tunnel
echo "🔌 Launching secure connection tunnels..."
gcloud compute ssh "$VM_NAME" \
    --project="$PROJECT_ID" \
    --zone="$ZONE" \
    --tunnel-through-iap \
    -- -N -L 8501:localhost:8501 -L 8504:localhost:8504 &
TUNNEL_PID=$!

# Register exit trap to kill tunnel background process automatically on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down port forwarding tunnels (PID: $TUNNEL_PID)..."
    kill "$TUNNEL_PID" 2>/dev/null || true
    echo "Done."
}
trap cleanup INT TERM EXIT

clear
echo "=========================================================="
echo "🎉 GCP Database Demo Engine is Live & Connected!"
echo "=========================================================="
echo ""
echo "👉 Configurator Portal:   http://localhost:8504"
echo "👉 Demo Explorer Console: http://localhost:8501"
echo ""
echo "💡 Presentation Tips:"
echo "1. Keep this terminal window open to maintain the connection."
echo "2. Open the Configurator Portal (8504) to seed your database."
echo "3. Present your target scenarios via the Console (8501)."
echo ""
echo "Press [Ctrl+C] to disconnect tunnels and exit."
echo "=========================================================="

wait
