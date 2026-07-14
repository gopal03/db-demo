#!/bin/bash
set -e

echo "=== Starting Workstation Setup ==="

# Wait for internet connectivity (DNS and routing) to establish
echo "Waiting for internet connectivity..."
until curl -sSf https://www.google.com > /dev/null 2>&1; do
  echo "Network not ready yet, sleeping 3 seconds..."
  sleep 3
done
echo "Internet connectivity established!"

# 1. Resolve variables (support both Terraform templatefile and raw gcloud metadata)
PROJECT_ID="${project_id}"
REGION="${region}"
GITHUB_REPO_URL="${github_repo_url}"

if [[ "$PROJECT_ID" == *"project_id"* || -z "$PROJECT_ID" ]]; then
  get_metadata() {
    curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/$1" || echo ""
  }
  PROJECT_ID=$(get_metadata "project_id")
  REGION=$(get_metadata "region")
  GITHUB_REPO_URL=$(get_metadata "github_repo_url")
fi

echo "# Lab specific ENV vars" >> /etc/bash.bashrc
echo "export GOOGLE_CLOUD_PROJECT=$PROJECT_ID" >> /etc/bash.bashrc
echo "export GOOGLE_CLOUD_LOCATION=$REGION" >> /etc/bash.bashrc
echo 'export PATH=$PATH:/opt/google-cloud-sdk/bin' >> /etc/bash.bashrc


# 2. Increase open files limit for benchmark throughput
echo "# Increase open files for running benchmarks" >> /etc/security/limits.conf
echo "* soft nofile 65535" >> /etc/security/limits.conf
echo "* hard nofile 65535" >> /etc/security/limits.conf

# 3. Install packages
apt-get update
apt-get install -y git curl

# 4. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
cp /root/.local/bin/uv /usr/local/bin/uv
chmod 755 /usr/local/bin/uv
rm -rf /root/.local/bin

# 5. Install Terraform
cd /tmp
curl -LO https://releases.hashicorp.com/terraform/1.5.7/terraform_1.5.7_linux_amd64.zip
apt-get install -y unzip
unzip terraform_1.5.7_linux_amd64.zip
mv terraform /usr/local/bin/
chmod +x /usr/local/bin/terraform
rm -f terraform_1.5.7_linux_amd64.zip

# 5. Clean up old snap gcloud and install the latest google-cloud-sdk
if snap list | grep -q google-cloud-cli; then
  snap remove google-cloud-cli || true
fi

cd /tmp
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-x86_64.tar.gz
mkdir -p /opt
tar -xf google-cloud-cli-linux-x86_64.tar.gz -C /opt
/opt/google-cloud-sdk/install.sh --quiet --path-update true

export PATH=$${PATH}:/opt/google-cloud-sdk/bin
gcloud components install cbt bq -q

# Symlink gcloud binaries to /usr/local/bin so they are globally accessible in PATH
ln -sf /opt/google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud
ln -sf /opt/google-cloud-sdk/bin/cbt /usr/local/bin/cbt
ln -sf /opt/google-cloud-sdk/bin/bq /usr/local/bin/bq

# 6. Clone the repository and setup local requirements
mkdir -p /opt/db-demo
if [ -z "$GITHUB_REPO_URL" ]; then
  GITHUB_REPO_URL="https://github.com/gopalbhutada/db-demo.git"
fi
git clone "$GITHUB_REPO_URL" /opt/db-demo

cd /opt/db-demo
# Set up environment using uv
/usr/local/bin/uv venv .venv
source .venv/bin/activate
/usr/local/bin/uv pip install -r requirements.txt

# 7. Correct permissions so all users can execute/write in the shared folder
chmod -R 777 /opt/db-demo
chown -R ubuntu:ubuntu /opt/google-cloud-sdk

echo "=== Workstation Setup Complete ==="
touch /tmp/setup_complete

