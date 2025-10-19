#!/bin/bash

JENKINS_URL="http://localhost:8080"
JOB_NAME="proto-ddf-e2e"
REPO_PATH="/Users/luismartins/local_repos/proto-ddf"

echo "🚀 Starting Jenkins Pipeline Execution..."
echo ""

# Get CSRF Crumb
echo "[1/5] Getting CSRF crumb..."
CRUMB=$(curl -s "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)" 2>/dev/null)
if [ -z "$CRUMB" ]; then
    echo "⚠️  No CSRF required (development mode)"
    CRUMB_HEADER=""
else
    CRUMB_HEADER="-H \"$CRUMB\""
    echo "✅ CSRF Crumb obtained"
fi

# Check if job exists
echo "[2/5] Checking for existing job..."
JOB_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" "$JENKINS_URL/job/$JOB_NAME" 2>/dev/null)

if [ "$JOB_EXISTS" != "200" ]; then
    echo "Creating job $JOB_NAME..."
    JOB_CONFIG=$(cat <<'EOF'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1428.v27a69c09f980">
  <actions/>
  <description>Proto-DDF E2E Testing Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsFlowDefinition" plugin="workflow-cps@3873.v47282919bd78">
    <script>node { echo "Proto-DDF E2E Test Pipeline" }</script>
    <sandbox>true</sandbox>
  </definition>
  <triggers/>
  <disabled>false</disabled>
</flow-definition>
EOF
)
    echo "$JOB_CONFIG" > /tmp/job.xml
    curl -X POST $CRUMB_HEADER -H "Content-Type: application/xml" --data-binary @/tmp/job.xml "$JENKINS_URL/createItem?name=$JOB_NAME" 2>/dev/null
    sleep 1
fi

# Trigger build
echo "[3/5] Triggering build..."
BUILD_RESPONSE=$(curl -X POST $CRUMB_HEADER "$JENKINS_URL/job/$JOB_NAME/build?delay=0sec" 2>/dev/null)
sleep 2

# Get latest build
LATEST_BUILD=$(curl -s "$JENKINS_URL/job/$JOB_NAME/api/json" 2>/dev/null | grep -o '"number":[0-9]*' | head -1 | grep -o '[0-9]*')
echo "✅ Build #$LATEST_BUILD triggered"

# Monitor build
echo "[4/5] Monitoring build progress..."
for i in {1..10}; do
    BUILD_STATUS=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/api/json" 2>/dev/null)
    RESULT=$(echo "$BUILD_STATUS" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
    BUILDING=$(echo "$BUILD_STATUS" | grep '"building":true' || echo "")

    if [ -z "$BUILDING" ] || [ "$RESULT" != "null" ]; then
        echo "✅ Build completed with result: $RESULT"
        break
    fi

    echo "⏳ Waiting... (attempt $i/10)"
    sleep 3
done

# Final status
echo "[5/5] Getting final status..."
BUILD_FINAL=$(curl -s "$JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/api/json" 2>/dev/null)
FINAL_RESULT=$(echo "$BUILD_FINAL" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)
DURATION=$(echo "$BUILD_FINAL" | grep -o '"duration":[0-9]*' | grep -o '[0-9]*')
DURATION_SEC=$((DURATION / 1000))

echo ""
echo "╔════════════════════════════════════════╗"
echo "║ Build Results"
echo "╚════════════════════════════════════════╝"
echo "Job:      $JOB_NAME"
echo "Build:    #$LATEST_BUILD"
echo "Result:   $FINAL_RESULT"
echo "Duration: ${DURATION_SEC}s"
echo ""

# Jenkins URLs
echo "📊 Jenkins Dashboard URLs:"
echo "  Dashboard:  $JENKINS_URL"
echo "  Job:        $JENKINS_URL/job/$JOB_NAME"
echo "  Build:      $JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD"
echo "  Console:    $JENKINS_URL/job/$JOB_NAME/$LATEST_BUILD/consoleText"
echo ""
