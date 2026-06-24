#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# Deploy Script — AI Meeting Assistant
# ══════════════════════════════════════════════════════════════════════════════
# Transfers the project to EC2, builds the Docker image, and starts the app.
#
# Usage:
#   ./deploy/deploy.sh <EC2_PUBLIC_IP>
#   ./deploy/deploy.sh                     # Auto-reads from .instance-info
#
# Environment variables (set in .env or export before running):
#   MISTRAL_API_KEY   — Required
#   SARVAM_API_KEY    — Optional (for Hinglish support)
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "${SCRIPT_DIR}")"

# ── Load instance info if available ───────────────────────────────────────────
if [ -f "${SCRIPT_DIR}/.instance-info" ]; then
    source "${SCRIPT_DIR}/.instance-info"
fi

# ── Parse arguments ───────────────────────────────────────────────────────────
EC2_HOST="${1:-${PUBLIC_IP:-}}"
SSH_KEY="${KEY_FILE:-${HOME}/.ssh/ai-meeting-assistant-key.pem}"
SSH_USER="ec2-user"
REMOTE_DIR="/home/${SSH_USER}/ai-meeting-assistant"

if [ -z "${EC2_HOST}" ]; then
    echo "❌ Usage: ./deploy/deploy.sh <EC2_PUBLIC_IP>"
    echo "   Or run aws-setup.sh first to auto-populate the IP."
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "  AI Meeting Assistant — Deploying to ${EC2_HOST}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

SSH_CMD="ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no ${SSH_USER}@${EC2_HOST}"

# ── Step 1: Verify SSH connectivity ──────────────────────────────────────────
echo "🔌 Testing SSH connection..."
if ! ${SSH_CMD} "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ Cannot connect to ${EC2_HOST}. Check:"
    echo "   - Is the instance running?"
    echo "   - Is the security group allowing port 22?"
    echo "   - Is the SSH key correct? (${SSH_KEY})"
    exit 1
fi
echo "✅ SSH connected"

# ── Step 2: Verify Docker is installed ───────────────────────────────────────
echo "🐳 Verifying Docker installation..."
if ! ${SSH_CMD} "docker --version" 2>/dev/null; then
    echo "⏳ Docker not ready yet. The user-data script may still be running."
    echo "   Wait 1-2 minutes and try again."
    echo "   You can check progress with:"
    echo "   ${SSH_CMD} 'tail -f /var/log/cloud-init-output.log'"
    exit 1
fi
echo "✅ Docker is ready"

# ── Step 3: Upload project files ─────────────────────────────────────────────
echo "📦 Uploading project files..."
${SSH_CMD} "mkdir -p ${REMOTE_DIR}"

# Use rsync for efficient transfer (only changed files)
rsync -avz --progress \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude 'downloads/*' \
    --exclude 'vector_db/*' \
    --exclude '.DS_Store' \
    --exclude 'node_modules' \
    -e "ssh -i ${SSH_KEY} -o StrictHostKeyChecking=no" \
    "${PROJECT_DIR}/" \
    "${SSH_USER}@${EC2_HOST}:${REMOTE_DIR}/"

echo "✅ Files uploaded"

# ── Step 4: Upload .env file (secrets) ───────────────────────────────────────
echo "🔑 Uploading environment variables..."
if [ -f "${PROJECT_DIR}/.env" ]; then
    scp -i "${SSH_KEY}" -o StrictHostKeyChecking=no \
        "${PROJECT_DIR}/.env" \
        "${SSH_USER}@${EC2_HOST}:${REMOTE_DIR}/.env"
    echo "✅ .env file uploaded"
else
    echo "⚠️  No .env file found. Create one on the server:"
    echo "   ${SSH_CMD}"
    echo "   nano ${REMOTE_DIR}/.env"
    echo ""
    echo "   Required contents:"
    echo "   MISTRAL_API_KEY=your_key_here"
fi

# ── Step 5: Build and start Docker container ─────────────────────────────────
echo "🏗️  Building Docker image (this may take 5-10 minutes on first run)..."
${SSH_CMD} "cd ${REMOTE_DIR} && docker compose down 2>/dev/null || true"
${SSH_CMD} "cd ${REMOTE_DIR} && docker compose up -d --build"

echo ""
echo "⏳ Waiting for health check..."
sleep 15

# ── Step 6: Verify deployment ────────────────────────────────────────────────
echo "🏥 Checking container health..."
CONTAINER_STATUS=$(${SSH_CMD} "docker inspect --format='{{.State.Status}}' ai-meeting-assistant 2>/dev/null" || echo "not found")

if [ "${CONTAINER_STATUS}" = "running" ]; then
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  ✅ Deployment Successful!"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "  🌐 App URL:  http://${EC2_HOST}:8501"
    echo ""
    echo "  ── Useful Commands ─────────────────────────────────────────"
    echo "  View logs:   ${SSH_CMD} 'docker compose -f ${REMOTE_DIR}/docker-compose.yml logs -f'"
    echo "  Restart:     ${SSH_CMD} 'cd ${REMOTE_DIR} && docker compose restart'"
    echo "  Stop:        ${SSH_CMD} 'cd ${REMOTE_DIR} && docker compose down'"
    echo "  SSH:         ${SSH_CMD}"
    echo ""
    echo "  The app will auto-restart on crash and after EC2 reboot."
    echo "═══════════════════════════════════════════════════════════════"
else
    echo "⚠️  Container status: ${CONTAINER_STATUS}"
    echo "   Checking logs..."
    ${SSH_CMD} "cd ${REMOTE_DIR} && docker compose logs --tail=30"
    echo ""
    echo "   The container may still be starting (Whisper model download)."
    echo "   Check again in a minute with:"
    echo "   ${SSH_CMD} 'docker compose -f ${REMOTE_DIR}/docker-compose.yml logs -f'"
fi
