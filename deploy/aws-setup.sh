#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════════════════════
# AWS EC2 Setup Script — AI Meeting Assistant
# ══════════════════════════════════════════════════════════════════════════════
# This script provisions an EC2 instance ready to run the Docker container.
#
# Prerequisites:
#   1. AWS CLI installed & configured (`aws configure`)
#   2. Your Mistral API key ready
#
# Usage:
#   chmod +x deploy/aws-setup.sh
#   ./deploy/aws-setup.sh
# ══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ── Configuration (edit these as needed) ──────────────────────────────────────
APP_NAME="ai-meeting-assistant"
REGION="${AWS_REGION:-ap-south-1}"                # Mumbai (closest to India)
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.large}"        # 2 vCPU, 8 GB RAM — good for Whisper
AMI_ID=""                                          # Auto-detected below
KEY_NAME="${APP_NAME}-key"
SECURITY_GROUP_NAME="${APP_NAME}-sg"
VOLUME_SIZE=30                                     # GB — enough for Docker + models

echo "═══════════════════════════════════════════════════════════════"
echo "  AI Meeting Assistant — AWS EC2 Provisioning"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Region:        ${REGION}"
echo "  Instance Type:  ${INSTANCE_TYPE}"
echo "  Volume Size:    ${VOLUME_SIZE} GB"
echo ""

# ── Step 1: Find the latest Amazon Linux 2023 AMI ────────────────────────────
echo "🔍 Finding latest Amazon Linux 2023 AMI..."
AMI_ID=$(aws ec2 describe-images \
    --region "${REGION}" \
    --owners amazon \
    --filters \
        "Name=name,Values=al2023-ami-2023.*-x86_64" \
        "Name=state,Values=available" \
    --query 'sort_by(Images, &CreationDate)[-1].ImageId' \
    --output text)

if [ -z "${AMI_ID}" ] || [ "${AMI_ID}" = "None" ]; then
    echo "❌ Could not find Amazon Linux 2023 AMI in ${REGION}"
    exit 1
fi
echo "✅ AMI: ${AMI_ID}"

# ── Step 2: Create Key Pair ──────────────────────────────────────────────────
KEY_FILE="${HOME}/.ssh/${KEY_NAME}.pem"
if [ -f "${KEY_FILE}" ]; then
    echo "⚠️  Key pair file already exists: ${KEY_FILE}"
    echo "   Using existing key pair."
else
    echo "🔑 Creating key pair: ${KEY_NAME}..."

    # Delete remote key if it exists (ignore errors)
    aws ec2 delete-key-pair --key-name "${KEY_NAME}" --region "${REGION}" 2>/dev/null || true

    aws ec2 create-key-pair \
        --key-name "${KEY_NAME}" \
        --region "${REGION}" \
        --query 'KeyMaterial' \
        --output text > "${KEY_FILE}"

    chmod 400 "${KEY_FILE}"
    echo "✅ Key saved to: ${KEY_FILE}"
fi

# ── Step 3: Create Security Group ────────────────────────────────────────────
echo "🔒 Setting up security group: ${SECURITY_GROUP_NAME}..."

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs \
    --region "${REGION}" \
    --filters "Name=isDefault,Values=true" \
    --query 'Vpcs[0].VpcId' \
    --output text)

# Check if security group already exists
SG_ID=$(aws ec2 describe-security-groups \
    --region "${REGION}" \
    --filters "Name=group-name,Values=${SECURITY_GROUP_NAME}" "Name=vpc-id,Values=${VPC_ID}" \
    --query 'SecurityGroups[0].GroupId' \
    --output text 2>/dev/null || echo "None")

if [ "${SG_ID}" = "None" ] || [ -z "${SG_ID}" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name "${SECURITY_GROUP_NAME}" \
        --description "Security group for AI Meeting Assistant" \
        --vpc-id "${VPC_ID}" \
        --region "${REGION}" \
        --query 'GroupId' \
        --output text)

    # Allow SSH (port 22)
    aws ec2 authorize-security-group-ingress \
        --group-id "${SG_ID}" \
        --protocol tcp --port 22 --cidr 0.0.0.0/0 \
        --region "${REGION}"

    # Allow Streamlit (port 8501)
    aws ec2 authorize-security-group-ingress \
        --group-id "${SG_ID}" \
        --protocol tcp --port 8501 --cidr 0.0.0.0/0 \
        --region "${REGION}"

    echo "✅ Security group created: ${SG_ID}"
else
    echo "✅ Security group already exists: ${SG_ID}"
fi

# ── Step 4: Launch EC2 Instance ──────────────────────────────────────────────
echo "🚀 Launching EC2 instance..."

INSTANCE_ID=$(aws ec2 run-instances \
    --region "${REGION}" \
    --image-id "${AMI_ID}" \
    --instance-type "${INSTANCE_TYPE}" \
    --key-name "${KEY_NAME}" \
    --security-group-ids "${SG_ID}" \
    --block-device-mappings "[{\"DeviceName\":\"/dev/xvda\",\"Ebs\":{\"VolumeSize\":${VOLUME_SIZE},\"VolumeType\":\"gp3\"}}]" \
    --user-data file://deploy/ec2-userdata.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${APP_NAME}}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: ${INSTANCE_ID}"

# ── Step 5: Wait for instance to be running ──────────────────────────────────
echo "⏳ Waiting for instance to be running..."
aws ec2 wait instance-running --instance-ids "${INSTANCE_ID}" --region "${REGION}"

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids "${INSTANCE_ID}" \
    --region "${REGION}" \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ EC2 Instance Ready!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  Instance ID:   ${INSTANCE_ID}"
echo "  Public IP:     ${PUBLIC_IP}"
echo "  SSH Key:       ${KEY_FILE}"
echo ""
echo "  ── Next Steps ──────────────────────────────────────────────"
echo ""
echo "  1. Wait ~2 minutes for Docker to install (user-data script)"
echo ""
echo "  2. SSH into the instance:"
echo "     ssh -i ${KEY_FILE} ec2-user@${PUBLIC_IP}"
echo ""
echo "  3. Deploy the app:"
echo "     ./deploy/deploy.sh ${PUBLIC_IP}"
echo ""
echo "  4. Access the app:"
echo "     http://${PUBLIC_IP}:8501"
echo ""
echo "═══════════════════════════════════════════════════════════════"

# Save instance info for deploy.sh
mkdir -p deploy
cat > deploy/.instance-info <<EOF
INSTANCE_ID=${INSTANCE_ID}
PUBLIC_IP=${PUBLIC_IP}
REGION=${REGION}
KEY_FILE=${KEY_FILE}
EOF

echo "📝 Instance info saved to deploy/.instance-info"
