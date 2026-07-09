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

# 1. Set environment variables globally for all bash sessions
echo "# Lab specific ENV vars" >> /etc/bash.bashrc
echo "export GOOGLE_CLOUD_PROJECT=${project_id}" >> /etc/bash.bashrc
echo "export GOOGLE_CLOUD_LOCATION=${region}" >> /etc/bash.bashrc
echo 'export PATH=$${PATH}:/opt/google-cloud-sdk/bin' >> /etc/bash.bashrc

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

# 6. Clone the repository and setup local requirements
mkdir -p /opt/db-demo
git clone ${github_repo_url} /opt/db-demo

cd /opt/db-demo
# Set up environment using uv
/usr/local/bin/uv venv .venv
source .venv/bin/activate
/usr/local/bin/uv pip install -r requirements.txt

# 7. Correct permissions so all users can execute/write in the shared folder
chmod -R 777 /opt/db-demo
chown -R ubuntu:ubuntu /opt/google-cloud-sdk

echo "=== Workstation Setup Complete ==="
