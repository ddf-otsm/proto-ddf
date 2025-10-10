#!/bin/bash
# OCI Remote Access Script - Cursor IDE Integration
# Provides quasi-one-click access to OCI instances (like AWS SSM for Cursor)

set -euo pipefail

# Source infrastructure inventory middleware for safety
if [[ -f "scripts/cloud/infrastructure_inventory_middleware.sh" ]]; then
    source scripts/cloud/infrastructure_inventory_middleware.sh
else
    echo "Warning: Infrastructure inventory middleware not found"
fi

# Configuration
TERRAFORM_DIR="terraform/oci/standalone-standard"
KEY_NAME="ssh-key-2025-07-31-deployer-ddf-production-standard-a1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[OCI-Remote]${NC} $1"
}

success() {
    echo -e "${GREEN}[OCI-Remote]${NC} ✅ $1"
}

warn() {
    echo -e "${YELLOW}[OCI-Remote]${NC} ⚠️  $1"
}

error() {
    echo -e "${RED}[OCI-Remote]${NC} ❌ $1"
}

# Function to detect instance OCID from Terraform outputs
get_instance_ocid() {
    cd "$TERRAFORM_DIR" 2>/dev/null || {
        error "Terraform directory not found: $TERRAFORM_DIR"
        return 1
    }

    terraform output -raw instance_id 2>/dev/null || {
        warn "No instance found. Run 'make apply' first."
        return 1
    }
}

# Function to get bastion ID
get_bastion_id() {
    cd "$TERRAFORM_DIR" 2>/dev/null || return 1
    terraform output -raw bastion_id 2>/dev/null || return 1
}

# Function to start bastion session
start_bastion_session() {
    local instance_id="$1"
    local bastion_id="$2"

    log "Creating OCI Bastion session..."

    # Create managed SSH session
    local session_id
    session_id=$(oci bastion session create-managed-ssh \
        --bastion-id "$bastion_id" \
        --key-details "file://$HOME/.ssh/$KEY_NAME.key.pub" \
        --target-resource-id "$instance_id" \
        --display-name "cursor-session-$(date +%Y%m%d-%H%M%S)" \
        --query 'data.id' \
        --raw-output 2>/dev/null) || {
        error "Failed to create bastion session"
        return 1
    }

    success "Session created: $session_id"

    # Wait for session to become active
    log "Waiting for session to become active..."
    sleep 10

    # Start connection
    log "Connecting via bastion..."
    oci bastion session connect --session-id "$session_id"
}

# Function to try direct SSH (fallback)
try_direct_ssh() {
    cd "$TERRAFORM_DIR" 2>/dev/null || return 1

    local public_ip
    public_ip=$(terraform output -raw public_ip 2>/dev/null) || {
        warn "No public IP available"
        return 1
    }

    if [[ "$public_ip" == "null" || -z "$public_ip" ]]; then
        warn "Public IP is null or empty"
        return 1
    fi

    log "Attempting direct SSH to $public_ip..."
    ssh -i "$HOME/.ssh/$KEY_NAME.key" \
        -o ConnectTimeout=10 \
        -o StrictHostKeyChecking=no \
        "ubuntu@$public_ip"
}

# Main function - mimics AWS SSM Session Manager experience
main() {
    log "🚀 Starting OCI Remote Access (Cursor IDE Integration)"

    # Get instance information
    local instance_id
    instance_id=$(get_instance_ocid) || {
        error "No OCI instance available"
        echo ""
        echo "💡 To deploy an instance:"
        echo "   cd $TERRAFORM_DIR && make apply"
        exit 1
    }

    success "Found instance: $instance_id"

    # Try bastion access first (preferred method)
    local bastion_id
    if bastion_id=$(get_bastion_id); then
        success "Found bastion: $bastion_id"

        if start_bastion_session "$instance_id" "$bastion_id"; then
            success "Bastion connection successful"
            exit 0
        else
            warn "Bastion connection failed, trying direct SSH..."
        fi
    else
        warn "No bastion service found, trying direct SSH..."
    fi

    # Fallback to direct SSH
    if try_direct_ssh; then
        success "Direct SSH connection successful"
    else
        error "All connection methods failed"
        echo ""
        echo "🔧 Troubleshooting steps:"
        echo "1. Check instance status: cd $TERRAFORM_DIR && make status"
        echo "2. Verify network connectivity: ping \$(terraform output -raw public_ip)"
        echo "3. Check bastion service: oci bastion bastion list --compartment-id \$(terraform output -raw compartment_id)"
        exit 1
    fi
}

# Handle command line arguments
case "${1:-}" in
    "help"|"-h"|"--help")
        echo "OCI Remote Access Script - Cursor IDE Integration"
        echo ""
        echo "Usage:"
        echo "  $0                 Start OCI remote session"
        echo "  $0 help           Show this help"
        echo "  $0 status         Show instance status"
        echo ""
        echo "This script provides AWS SSM-like access to OCI instances:"
        echo "1. Detects instance OCID from Terraform outputs"
        echo "2. Starts OCI Bastion session"
        echo "3. Falls back to direct SSH if bastion fails"
        ;;
    "status")
        log "Checking OCI instance status..."
        cd "$TERRAFORM_DIR" && make status
        ;;
    *)
        main
        ;;
esac
