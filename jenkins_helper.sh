#!/bin/bash
# Jenkins Helper Script for proto-ddf
# Sources shared Jenkins configuration and provides local utilities

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load shared Jenkins configuration
JENKINS_CONFIG="$HOME/vars/jenkins_config.sh"

if [ -f "$JENKINS_CONFIG" ]; then
    echo -e "${BLUE}🔗 Loading shared Jenkins configuration...${NC}"
    source "$JENKINS_CONFIG"
else
    echo -e "${RED}❌ Jenkins configuration not found at: $JENKINS_CONFIG${NC}"
    echo -e "${YELLOW}   Please ensure Jenkins is set up according to JENKINS_LOCAL_HANDOFF.md${NC}"
    exit 1
fi

# Project-specific variables
export PROJECT_NAME="proto-ddf"
export PROJECT_PATH="/Users/luismartins/local_repos/proto-ddf"
export PIPELINE_NAME="proto-ddf-local"
export JENKINSFILE="Jenkinsfile.local"

# Functions
function jenkins_status() {
    echo -e "${BLUE}📊 Jenkins Status${NC}"
    echo "===================="
    
    if lsof -i :${JENKINS_PORT} | grep LISTEN > /dev/null; then
        echo -e "${GREEN}✅ Jenkins is running${NC}"
        echo "   URL: ${JENKINS_URL}"
        echo "   Port: ${JENKINS_PORT}"
        
        # Check if process ID file exists
        if [ -f "$HOME/vars/jenkins.pid" ]; then
            PID=$(cat "$HOME/vars/jenkins.pid")
            echo "   PID: ${PID}"
        fi
    else
        echo -e "${RED}❌ Jenkins is not running${NC}"
        echo "   Start it with: jenkins_start"
    fi
}

function jenkins_start() {
    echo -e "${BLUE}🚀 Starting Jenkins...${NC}"
    
    # Check if already running
    if lsof -i :${JENKINS_PORT} | grep LISTEN > /dev/null; then
        echo -e "${YELLOW}⚠️  Jenkins is already running on port ${JENKINS_PORT}${NC}"
        return 1
    fi
    
    # Start Jenkins
    /opt/homebrew/opt/openjdk@21/bin/java \
        -Dmail.smtp.starttls.enable=true \
        -jar /opt/homebrew/opt/jenkins-lts/libexec/jenkins.war \
        --httpListenAddress=127.0.0.1 \
        --httpPort=${JENKINS_PORT} \
        > "$HOME/vars/jenkins.log" 2>&1 &
    
    # Save PID
    echo $! > "$HOME/vars/jenkins.pid"
    
    echo -e "${GREEN}✅ Jenkins started${NC}"
    echo "   URL: ${JENKINS_URL}"
    echo "   PID: $(cat $HOME/vars/jenkins.pid)"
    echo ""
    echo "   Waiting for Jenkins to be ready..."
    sleep 10
    
    # Wait for Jenkins to be accessible
    for i in {1..30}; do
        if curl -s -o /dev/null -w "%{http_code}" "${JENKINS_URL}" | grep -q "200\|403"; then
            echo -e "${GREEN}   ✅ Jenkins is ready!${NC}"
            break
        fi
        echo "   Waiting... ($i/30)"
        sleep 2
    done
}

function jenkins_stop() {
    echo -e "${BLUE}🛑 Stopping Jenkins...${NC}"
    
    if [ -f "$HOME/vars/jenkins.pid" ]; then
        PID=$(cat "$HOME/vars/jenkins.pid")
        if kill "$PID" 2>/dev/null; then
            echo -e "${GREEN}✅ Jenkins stopped (PID: ${PID})${NC}"
            rm "$HOME/vars/jenkins.pid"
        else
            echo -e "${YELLOW}⚠️  Process ${PID} not found, cleaning up...${NC}"
            rm "$HOME/vars/jenkins.pid"
        fi
    else
        echo -e "${YELLOW}⚠️  No PID file found${NC}"
        
        # Try to find and kill Jenkins process
        JENKINS_PID=$(lsof -ti :${JENKINS_PORT})
        if [ ! -z "$JENKINS_PID" ]; then
            echo "   Found Jenkins on port ${JENKINS_PORT} (PID: ${JENKINS_PID})"
            kill "$JENKINS_PID"
            echo -e "${GREEN}✅ Jenkins stopped${NC}"
        else
            echo -e "${YELLOW}⚠️  No Jenkins process found on port ${JENKINS_PORT}${NC}"
        fi
    fi
}

function jenkins_restart() {
    echo -e "${BLUE}🔄 Restarting Jenkins...${NC}"
    jenkins_stop
    sleep 3
    jenkins_start
}

function jenkins_logs() {
    echo -e "${BLUE}📄 Showing Jenkins logs (Ctrl+C to exit)...${NC}"
    tail -f "$HOME/vars/jenkins.log"
}

function jenkins_open() {
    echo -e "${BLUE}🌐 Opening Jenkins in browser...${NC}"
    open "${JENKINS_URL}"
}

function jenkins_password() {
    echo -e "${BLUE}🔐 Jenkins Admin Password${NC}"
    if [ -f "$HOME/vars/jenkins_admin_password_port17843.txt" ]; then
        echo "===================="
        cat "$HOME/vars/jenkins_admin_password_port17843.txt"
        echo ""
        echo "===================="
    else
        echo -e "${YELLOW}⚠️  Password file not found${NC}"
        echo "   Expected location: $HOME/vars/jenkins_admin_password_port17843.txt"
    fi
}

function jenkins_build() {
    echo -e "${BLUE}🔨 Triggering build for ${PROJECT_NAME}...${NC}"
    
    # Check if Jenkins is running
    if ! lsof -i :${JENKINS_PORT} | grep LISTEN > /dev/null; then
        echo -e "${RED}❌ Jenkins is not running${NC}"
        echo "   Start it with: jenkins_start"
        return 1
    fi
    
    echo "   Pipeline: ${PIPELINE_NAME}"
    echo "   This requires authentication - use Jenkins UI or API token"
    echo ""
    echo "   URL: ${JENKINS_URL}/job/${PIPELINE_NAME}/build"
    
    # Open the build page
    open "${JENKINS_URL}/job/${PIPELINE_NAME}/"
}

function jenkins_help() {
    echo -e "${BLUE}Jenkins Helper - proto-ddf${NC}"
    echo "===================="
    echo ""
    echo "Configuration:"
    echo "  Jenkins URL:  ${JENKINS_URL}"
    echo "  Project:      ${PROJECT_NAME}"
    echo "  Pipeline:     ${PIPELINE_NAME}"
    echo ""
    echo "Commands:"
    echo "  jenkins_status     - Check if Jenkins is running"
    echo "  jenkins_start      - Start Jenkins"
    echo "  jenkins_stop       - Stop Jenkins"
    echo "  jenkins_restart    - Restart Jenkins"
    echo "  jenkins_logs       - View Jenkins logs (live)"
    echo "  jenkins_open       - Open Jenkins UI in browser"
    echo "  jenkins_password   - Show admin password"
    echo "  jenkins_build      - Trigger a build for this project"
    echo "  jenkins_help       - Show this help"
    echo ""
    echo "Quick Start:"
    echo "  1. jenkins_status     # Check status"
    echo "  2. jenkins_start      # Start if not running"
    echo "  3. jenkins_open       # Open in browser"
    echo "  4. jenkins_password   # Get admin password"
    echo "  5. jenkins_build      # Trigger a build"
}

# If script is sourced, just load functions
# If executed directly, show help
if [[ "${BASH_SOURCE[0]}" == "${0}" ]] || [[ "${ZSH_ARGZERO}" == "${0}" ]]; then
    jenkins_help
else
    echo -e "${GREEN}✅ Jenkins helper loaded for ${PROJECT_NAME}${NC}"
    echo "   Type 'jenkins_help' for available commands"
fi

