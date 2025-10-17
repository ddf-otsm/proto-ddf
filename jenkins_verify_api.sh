#!/bin/bash

##############################################################################
# Jenkins API Verification & Pipeline Trigger Script
# This script demonstrates how to interact with Jenkins API for the proto-ddf
# E2E testing pipeline
##############################################################################

set -e

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_USER="${JENKINS_USER:-admin}"
JENKINS_TOKEN="${JENKINS_TOKEN:-}"
JOB_NAME="proto-ddf-e2e"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Jenkins API Verification & Pipeline Trigger         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. Check Jenkins Health
# ============================================================================
echo -e "${YELLOW}[1/5] Checking Jenkins availability...${NC}"

if curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL" >/dev/null 2>&1; then
    HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL")
    if [ "$HEALTH_CODE" = "200" ] || [ "$HEALTH_CODE" = "403" ]; then
        echo -e "${GREEN}✅ Jenkins is running at $JENKINS_URL${NC}"
        echo -e "${GREEN}   Status Code: $HEALTH_CODE${NC}"
    fi
else
    echo -e "${RED}❌ Cannot reach Jenkins at $JENKINS_URL${NC}"
    echo -e "${YELLOW}   Make sure Jenkins is running:${NC}"
    echo -e "${YELLOW}   jenkins --httpPort=8080 &${NC}"
    exit 1
fi

# ============================================================================
# 2. Get Jenkins Version via API
# ============================================================================
echo ""
echo -e "${YELLOW}[2/5] Retrieving Jenkins version from API...${NC}"

VERSION=$(curl -s -I "$JENKINS_URL/api/json" 2>/dev/null | grep -i "X-Jenkins:" | awk '{print $2}' | tr -d '\r')

if [ -z "$VERSION" ]; then
    echo -e "${YELLOW}⚠️  Could not retrieve version (Jenkins may require auth)${NC}"
    echo -e "${YELLOW}   This is normal for fresh Jenkins installations${NC}"
else
    echo -e "${GREEN}✅ Jenkins Version: $VERSION${NC}"
fi

# ============================================================================
# 3. Test API Endpoint
# ============================================================================
echo ""
echo -e "${YELLOW}[3/5] Testing Jenkins API endpoint...${NC}"

API_RESPONSE=$(curl -s "$JENKINS_URL/api/json" 2>/dev/null || echo "")

if [ -n "$API_RESPONSE" ]; then
    echo -e "${GREEN}✅ Jenkins API is responding${NC}"
    
    # Extract job list if available
    JOB_COUNT=$(echo "$API_RESPONSE" | grep -o '"name"' | wc -l 2>/dev/null || echo "0")
    echo -e "${BLUE}   Jobs in queue/running: $JOB_COUNT${NC}"
else
    echo -e "${YELLOW}⚠️  API endpoint requires authentication${NC}"
    echo -e "${YELLOW}   This is expected for production Jenkins${NC}"
fi

# ============================================================================
# 4. Display Pipeline Configuration
# ============================================================================
echo ""
echo -e "${YELLOW}[4/5] Pipeline Configuration for proto-ddf-e2e${NC}"

cat <<EOF
${BLUE}Job Details:${NC}
  Job Name:       $JOB_NAME
  Jenkins URL:    $JENKINS_URL
  Pipeline File:  Jenkinsfile.e2e
  Repository:     /Users/luismartins/local_repos/proto-ddf
  
${BLUE}Expected Stages:${NC}
  1️⃣  Setup           - Environment preparation (5-10 min)
  2️⃣  Start Generator - Launch Proto-DDF server (2-3 min)
  3️⃣  Run E2E Tests   - Playwright tests (10-15 min)
  4️⃣  Unit Tests      - Python unit tests (1-2 min)
  5️⃣  Cleanup         - Resource cleanup (30 sec)

${BLUE}Expected Results:${NC}
  ✅ 18/18 Unit Tests Passing
  ✅ 13/13 E2E Tests Passing
  ✅ 100% Success Rate
EOF

# ============================================================================
# 5. Show How to Trigger Pipeline
# ============================================================================
echo ""
echo -e "${YELLOW}[5/5] Pipeline Trigger Instructions${NC}"

cat <<EOF

${GREEN}Method 1: Via Jenkins CLI${NC}
  Prerequisites:
    - Download jenkins-cli.jar from: $JENKINS_URL/jnlpJars/jenkins-cli.jar
    - (Already available in repo as jenkins-cli.jar)
  
  Command:
    java -jar jenkins-cli.jar -s $JENKINS_URL build $JOB_NAME -s

${GREEN}Method 2: Via Browser UI${NC}
  1. Navigate to: $JENKINS_URL/job/$JOB_NAME
  2. Click "Build Now"
  3. Watch console output in real-time

${GREEN}Method 3: Via Webhook/API${NC}
  Endpoint: $JENKINS_URL/job/$JOB_NAME/build
  Method: POST
  Headers: 
    - Crumb: (get from $JENKINS_URL/crumbIssuer/api/json)
    - Content-Type: application/x-www-form-urlencoded

${GREEN}Method 4: Via Pipeline Script${NC}
  pipeline {
      stage('Trigger E2E') {
          steps {
              build job: '$JOB_NAME', wait: true
          }
      }
  }

EOF

# ============================================================================
# 6. Provide Curl Command Examples
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              API Commands (with auth if needed)            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cat <<'EOF'
# Get Jenkins info
curl -s http://localhost:8080/api/json | jq '.' 2>/dev/null || echo "Requires authentication"

# Get all jobs
curl -s http://localhost:8080/api/json?tree=jobs[name] | jq '.jobs' 2>/dev/null

# Get specific job info
curl -s http://localhost:8080/job/proto-ddf-e2e/api/json | jq '.' 2>/dev/null

# Get last build info
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/api/json | jq '.' 2>/dev/null

# View build console output
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/consoleText

# Queue a new build (requires CSRF token in production)
curl -X POST http://localhost:8080/job/proto-ddf-e2e/build

EOF

# ============================================================================
# 7. Show Test Expectations
# ============================================================================
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Expected Test Execution & Results               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

cat <<'EOF'
🧪 E2E Test Scenarios (13 total):

  Auto-Start Tests (3):
    ✅ test_open_app_when_down_auto_starts
    ✅ test_open_app_when_running_redirects_immediately
    ✅ test_open_app_preview_button_auto_starts

  Process Control (2):
    ✅ test_stop_button_stops_running_app
    ✅ test_restart_button_restarts_app

  Health Dashboard (5):
    ✅ test_health_dashboard_shows_generator_ports
    ✅ test_health_dashboard_shows_app_count
    ✅ test_health_dashboard_shows_running_count
    ✅ test_health_badges_show_app_status
    ✅ test_refresh_health_button_updates_status

  Port Stability (2):
    ✅ test_ports_remain_stable_after_restart
    ✅ test_ports_remain_stable_after_generator_restart

  Error Handling (1):
    ✅ test_shows_error_when_app_fails_to_start

🧪 Unit Tests (18 total):
    ✅ 9 config tests (port management)
    ✅ 5 generator tests (functionality)
    ✅ 4 structure tests (generated apps)

📊 Expected Totals:
    • Duration: ~30-40 minutes
    • Success Rate: 100%
    • Tests Passing: 31/31

EOF

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Jenkins API Verification Complete - Ready to Run     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

exit 0
