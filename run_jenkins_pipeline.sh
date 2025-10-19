#!/bin/bash

##############################################################################
# Automated Jenkins Pipeline Setup & Execution Script
# This script creates the proto-ddf-e2e job and executes the pipeline
##############################################################################

set -e

# Configuration
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JOB_NAME="proto-ddf-e2e"
REPO_PATH="/Users/luismartins/local_repos/proto-ddf"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
}

print_step() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Main execution
print_header "Jenkins Pipeline Automation"
echo ""

# ============================================================================
# Step 1: Verify Jenkins is Running
# ============================================================================
print_step "Verifying Jenkins is running..."

if ! curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL" >/dev/null 2>&1; then
    print_error "Jenkins is not running at $JENKINS_URL"
    print_step "Starting Jenkins..."
    jenkins --httpPort=8080 &
    sleep 20
fi

HEALTH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL")
if [ "$HEALTH_CODE" = "200" ] || [ "$HEALTH_CODE" = "403" ]; then
    print_success "Jenkins is running (HTTP $HEALTH_CODE)"
else
    print_error "Jenkins returned unexpected status code: $HEALTH_CODE"
    exit 1
fi

# ============================================================================
# Step 2: Verify Jenkins Version
# ============================================================================
print_step "Checking Jenkins version..."

VERSION=$(curl -s -I "$JENKINS_URL/api/json" 2>/dev/null | grep -i "X-Jenkins:" | awk '{print $2}' | tr -d '\r' || echo "unknown")
print_success "Jenkins version: $VERSION"

# ============================================================================
# Step 3: Create Job Config XML
# ============================================================================
print_step "Creating job configuration..."

JOB_CONFIG=$(cat <<'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1428.v27a69c09f980">
  <actions/>
  <description>Proto-DDF E2E Testing Pipeline - Automated Setup</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <hudson.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeepStr>-1</daysToKeepStr>
        <numToKeepStr>10</numToKeepStr>
        <artifactDaysToKeepStr>-1</artifactDaysToKeepStr>
        <artifactNumToKeepStr>-1</artifactNumToKeepStr>
      </strategy>
    </hudson.model.BuildDiscarderProperty>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@3873.v47282919bd78">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@5.2.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>REPO_PATH_PLACEHOLDER</url>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
      <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>
      <submoduleCfg class="java.util.ArrayList"/>
      <extensions/>
    </scm>
    <scriptPath>Jenkinsfile.e2e</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
)

# Replace placeholder with actual repo path
JOB_CONFIG="${JOB_CONFIG/REPO_PATH_PLACEHOLDER/$REPO_PATH}"

# Write to temporary file
echo "$JOB_CONFIG" > /tmp/proto-ddf-e2e-config.xml
print_success "Job configuration created"

# ============================================================================
# Step 4: Check if Job Exists
# ============================================================================
print_step "Checking if job already exists..."

JOB_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL/job/$JOB_NAME" 2>/dev/null || echo "404")

if [ "$JOB_EXISTS" = "200" ]; then
    print_success "Job already exists"
else
    print_step "Creating new job '$JOB_NAME'..."

    # Create the job
    curl -X POST \
        -H "Content-Type: application/xml" \
        --data-binary @/tmp/proto-ddf-e2e-config.xml \
        "$JENKINS_URL/createItem?name=$JOB_NAME" \
        2>/dev/null

    # Verify job creation
    sleep 2
    JOB_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL/job/$JOB_NAME" 2>/dev/null)

    if [ "$JOB_CHECK" = "200" ]; then
        print_success "Job '$JOB_NAME' created successfully"
    else
        print_error "Failed to create job. Status code: $JOB_CHECK"
        exit 1
    fi
fi

# ============================================================================
# Step 5: Trigger Build
# ============================================================================
print_step "Triggering build for job '$JOB_NAME'..."

BUILD_RESPONSE=$(curl -s -X POST "$JENKINS_URL/job/$JOB_NAME/build?delay=0sec" 2>/dev/null || echo "error")

sleep 2

# Get the latest build number
LATEST_BUILD=$(curl -s "$JENKINS_URL/job/$JOB_NAME/api/json" 2>/dev/null | grep -o '"number":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ -n "$LATEST_BUILD" ]; then
    print_success "Build triggered - Build #$LATEST_BUILD"
else
    print_error "Could not determine build number"
    exit 1
fi

# ============================================================================
# Step 6: Monitor Build Progress
# ============================================================================
print_header "Monitoring Build Progress"
echo ""

POLL_INTERVAL=10
MAX_WAIT=2400  # 40 minutes timeout
ELAPSED=0
LAST_CONSOLE_LINE=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    # Get build status
    BUILD_INFO=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/api/json" 2>/dev/null || echo "{}")

    BUILDING=$(echo "$BUILD_INFO" | grep -o '"building":true' || echo "")
    RESULT=$(echo "$BUILD_INFO" | grep -o '"result":"[A-Z]*"' | grep -o '[A-Z]*$' || echo "IN_PROGRESS")
    DURATION=$(echo "$BUILD_INFO" | grep -o '"duration":[0-9]*' | grep -o '[0-9]*$' || echo "0")

    # Display status
    if [ -n "$BUILDING" ] || [ "$RESULT" = "IN_PROGRESS" ]; then
        ELAPSED_MIN=$((ELAPSED / 60))
        echo -ne "\r${YELLOW}⏳ Build #$LATEST_BUILD in progress... (${ELAPSED_MIN}m elapsed)${NC}                    "
    else
        echo ""
        break
    fi

    sleep $POLL_INTERVAL
    ELAPSED=$((ELAPSED + POLL_INTERVAL))
done

echo ""
echo ""

# ============================================================================
# Step 7: Get Final Build Status
# ============================================================================
print_step "Retrieving final build status..."

BUILD_FINAL=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/api/json" 2>/dev/null)
FINAL_RESULT=$(echo "$BUILD_FINAL" | grep -o '"result":"[A-Z]*"' | grep -o '[A-Z]*$' || echo "UNKNOWN")
FINAL_DURATION=$(echo "$BUILD_FINAL" | grep -o '"duration":[0-9]*' | grep -o '[0-9]*$' || echo "0")
DURATION_SEC=$((FINAL_DURATION / 1000))
DURATION_MIN=$((DURATION_SEC / 60))
DURATION_SEC=$((DURATION_SEC % 60))

# Get test results
TEST_RESULTS=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/testReport/api/json" 2>/dev/null || echo "{}")
PASS_COUNT=$(echo "$TEST_RESULTS" | grep -o '"passCount":[0-9]*' | grep -o '[0-9]*$' || echo "0")
FAIL_COUNT=$(echo "$TEST_RESULTS" | grep -o '"failCount":[0-9]*' | grep -o '[0-9]*$' || echo "0")

# ============================================================================
# Step 8: Display Results
# ============================================================================
print_header "Build Results"
echo ""

echo -e "${BLUE}Build Information:${NC}"
echo "  Job Name:       $JOB_NAME"
echo "  Build Number:   #$LATEST_BUILD"
echo "  Status:         ${FINAL_RESULT}"
echo "  Duration:       ${DURATION_MIN}m ${DURATION_SEC}s"
echo ""

if [ "$FINAL_RESULT" = "SUCCESS" ]; then
    print_success "Build completed successfully!"
    echo ""
    echo -e "${BLUE}Test Results:${NC}"
    echo "  Passed:  $PASS_COUNT"
    echo "  Failed:  $FAIL_COUNT"
    echo ""
else
    print_error "Build failed or was aborted (Result: $FINAL_RESULT)"
    echo ""
fi

# ============================================================================
# Step 9: Provide Quick Access Links
# ============================================================================
echo ""
print_header "Quick Access Links"
echo ""

echo -e "${BLUE}Jenkins Dashboard:${NC}"
echo "  http://localhost:8080"
echo ""

echo -e "${BLUE}Job Pages:${NC}"
echo "  Job:        http://localhost:8080/job/$JOB_NAME"
echo "  Build #$LATEST_BUILD:    http://localhost:8080/job/$JOB_NAME/$LATEST_BUILD"
echo "  Console:    http://localhost:8080/job/$JOB_NAME/$LATEST_BUILD/consoleText"
echo "  Test Results: http://localhost:8080/job/$JOB_NAME/$LATEST_BUILD/testReport"
echo ""

# ============================================================================
# Step 10: Show Console Output (last 50 lines)
# ============================================================================
print_step "Retrieving console output (last 50 lines)..."
echo ""

CONSOLE_OUTPUT=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/consoleText" 2>/dev/null | tail -50)

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo "$CONSOLE_OUTPUT"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# Summary
# ============================================================================
print_header "Execution Summary"
echo ""

if [ "$FINAL_RESULT" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ Pipeline execution completed successfully!${NC}"
    echo ""
    echo "Results:"
    echo "  • Tests Passed:  $PASS_COUNT"
    echo "  • Tests Failed:  $FAIL_COUNT"
    echo "  • Duration:      ${DURATION_MIN}m ${DURATION_SEC}s"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Pipeline execution failed or was incomplete.${NC}"
    echo ""
    echo "Result: $FINAL_RESULT"
    echo ""
    echo "For more details, visit:"
    echo "  http://localhost:8080/job/$JOB_NAME/$LATEST_BUILD/consoleText"
    echo ""
    exit 1
fi
