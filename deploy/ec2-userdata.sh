#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# EC2 User Data Script — AI Meeting Assistant
# ══════════════════════════════════════════════════════════════════════════════
# This script runs automatically on first boot of the EC2 instance.
# It installs Docker, Docker Compose, and configures the system for
# running the AI Meeting Assistant container 24/7.
# ══════════════════════════════════════════════════════════════════════════════

set -euxo pipefail

LOG_FILE="/var/log/ai-meeting-setup.log"
exec > >(tee -a "${LOG_FILE}") 2>&1

echo "══════════════════════════════════════════════════════════════"
echo "  AI Meeting Assistant — EC2 First Boot Setup"
echo "  Started at: $(date)"
echo "══════════════════════════════════════════════════════════════"

# ── Step 1: System Updates ───────────────────────────────────────────────────
echo "📦 Updating system packages..."
dnf update -y

# ── Step 2: Install Docker ───────────────────────────────────────────────────
echo "🐳 Installing Docker..."
dnf install -y docker

# Start Docker and enable on boot
systemctl start docker
systemctl enable docker

# Add ec2-user to docker group (so we don't need sudo)
usermod -aG docker ec2-user

# ── Step 3: Install Docker Compose Plugin ────────────────────────────────────
echo "🔧 Installing Docker Compose..."
DOCKER_COMPOSE_VERSION="v2.29.1"
DOCKER_CLI_PLUGINS="/usr/local/lib/docker/cli-plugins"

mkdir -p "${DOCKER_CLI_PLUGINS}"
curl -SL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-$(uname -m)" \
    -o "${DOCKER_CLI_PLUGINS}/docker-compose"
chmod +x "${DOCKER_CLI_PLUGINS}/docker-compose"

# Verify installation
docker compose version

# ── Step 4: Install useful utilities ─────────────────────────────────────────
echo "🔧 Installing utilities..."
dnf install -y git htop

# ── Step 5: Configure Docker Daemon for Production ───────────────────────────
echo "⚙️  Configuring Docker daemon..."
cat > /etc/docker/daemon.json <<'DAEMON_JSON'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5"
  },
  "storage-driver": "overlay2",
  "live-restore": true
}
DAEMON_JSON

# Restart Docker to apply daemon config
systemctl restart docker

# ── Step 6: Create App Directory ─────────────────────────────────────────────
echo "📁 Creating application directory..."
APP_DIR="/home/ec2-user/ai-meeting-assistant"
mkdir -p "${APP_DIR}/downloads" "${APP_DIR}/vector_db"
chown -R ec2-user:ec2-user "${APP_DIR}"

# ── Step 7: Set Up Swap Space (helps with PyTorch memory) ────────────────────
echo "💾 Setting up 4GB swap space..."
if [ ! -f /swapfile ]; then
    dd if=/dev/zero of=/swapfile bs=1M count=4096
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
fi

# ── Step 8: Configure system limits ─────────────────────────────────────────
echo "⚙️  Setting system limits..."
cat >> /etc/security/limits.conf <<'LIMITS'
# AI Meeting Assistant — increase limits for Docker
*    soft    nofile    65536
*    hard    nofile    65536
*    soft    nproc     4096
*    hard    nproc     4096
LIMITS

echo ""
echo "══════════════════════════════════════════════════════════════"
echo "  ✅ EC2 Setup Complete!"
echo "  Finished at: $(date)"
echo "══════════════════════════════════════════════════════════════"
echo ""
echo "  Docker:         $(docker --version)"
echo "  Docker Compose: $(docker compose version)"
echo "  Swap:           $(free -h | grep Swap)"
echo ""
echo "  Ready for deployment. Run deploy.sh from your local machine."
echo "══════════════════════════════════════════════════════════════"
