#!/bin/bash
# Verify Jenkins Build Results for proto-ddf

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔍 Verifying proto-ddf Jenkins Build${NC}"
echo "===================================="

# Load Jenkins helper
source jenkins_helper.sh >/dev/null 2>&1

# Check if pipeline exists
echo -e "${BLUE}📋 Checking pipeline existence...${NC}"
PIPELINE_EXISTS=$(curl -s "http://localhost:17843/job/proto-ddf-local/api/json" | grep -o '"name":"proto-ddf-local"' || echo "false")

if [ "$PIPELINE_EXISTS" = "false" ]; then
    echo -e "${RED}❌ Pipeline 'proto-ddf-local' not found${NC}"
    echo -e "${YELLOW}   Please create it first in Jenkins UI${NC}"
    echo ""
    echo "   Go to: http://localhost:17843"
    echo "   Click: New Item → proto-ddf-local → Pipeline → OK"
    echo "   Configure: Pipeline script from SCM → Git"
    echo "   Repository: file:///Users/luismartins/local_repos/proto-ddf"
    echo "   Script Path: Jenkinsfile.local"
    echo "   Save"
    exit 1
fi

echo -e "${GREEN}✅ Pipeline 'proto-ddf-local' found${NC}"

# Get build information
echo -e "${BLUE}📊 Getting build information...${NC}"
BUILD_INFO=$(curl -s "http://localhost:17843/job/proto-ddf-local/api/json")

# Check if there are any builds
BUILD_COUNT=$(echo "$BUILD_INFO" | grep -o '"number":[0-9]*' | wc -l)

if [ "$BUILD_COUNT" -eq "0" ]; then
    echo -e "${YELLOW}⚠️  No builds found${NC}"
    echo -e "${YELLOW}   Please trigger your first build${NC}"
    echo ""
    echo "   Run: source jenkins_helper.sh && jenkins_build"
    echo "   Or: open http://localhost:17843/job/proto-ddf-local/build"
    exit 0
fi

echo -e "${GREEN}✅ Found ${BUILD_COUNT} build(s)${NC}"

# Get latest build info
LATEST_BUILD=$(echo "$BUILD_INFO" | grep -o '"number":[0-9]*' | head -1 | cut -d':' -f2)
BUILD_URL="http://localhost:17843/job/proto-ddf-local/${LATEST_BUILD}/"

echo -e "${BLUE}🔍 Analyzing latest build #${LATEST_BUILD}...${NC}"

# Get build details
BUILD_DETAILS=$(curl -s "${BUILD_URL}api/json")

# Extract build result
BUILD_RESULT=$(echo "$BUILD_DETAILS" | grep -o '"result":"[^"]*"' | cut -d'"' -f4)

if [ "$BUILD_RESULT" = "SUCCESS" ]; then
    echo -e "${GREEN}✅ Build #${LATEST_BUILD} PASSED${NC}"
elif [ "$BUILD_RESULT" = "FAILURE" ]; then
    echo -e "${RED}❌ Build #${LATEST_BUILD} FAILED${NC}"
elif [ "$BUILD_RESULT" = "null" ] || [ -z "$BUILD_RESULT" ]; then
    echo -e "${YELLOW}🔄 Build #${LATEST_BUILD} IN PROGRESS${NC}"
else
    echo -e "${YELLOW}⚠️  Build #${LATEST_BUILD} status: ${BUILD_RESULT}${NC}"
fi

# Get build duration
BUILD_DURATION=$(echo "$BUILD_DETAILS" | grep -o '"duration":[0-9]*' | cut -d':' -f2)
if [ ! -z "$BUILD_DURATION" ] && [ "$BUILD_DURATION" != "0" ]; then
    DURATION_SEC=$((BUILD_DURATION / 1000))
    echo -e "${BLUE}⏱️  Build duration: ${DURATION_SEC} seconds${NC}"
fi

# Check if stages completed
echo ""
echo -e "${BLUE}📝 Build Stages Analysis:${NC}"
echo "=========================="

# Get console output to check stages
CONSOLE_OUTPUT=$(curl -s "${BUILD_URL}consoleText")

# Check each stage
STAGES=("Checkout" "Environment Setup" "Install Dependencies" "Verify Installation" "Lint & Quality" "Build Check" "Security Scan")
STAGE_COUNT=0

for STAGE in "${STAGES[@]}"; do
    if echo "$CONSOLE_OUTPUT" | grep -q "$STAGE"; then
        echo -e "${GREEN}✅ $STAGE${NC}"
        ((STAGE_COUNT++))
    else
        echo -e "${RED}❌ $STAGE${NC}"
    fi
done

echo ""
if [ "$STAGE_COUNT" -eq "${#STAGES[@]}" ]; then
    echo -e "${GREEN}🎉 ALL ${#STAGES[@]} STAGES COMPLETED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}⚠️  ${STAGE_COUNT}/${#STAGES[@]} stages completed${NC}"
fi

echo ""
echo -e "${BLUE}🔗 Build Links:${NC}"
echo "==============="
echo "Jenkins UI: http://localhost:17843"
echo "Build Page: ${BUILD_URL}"
echo "Console Log: ${BUILD_URL}console"

echo ""
echo -e "${BLUE}💡 Next Steps:${NC}"
echo "==============="
if [ "$BUILD_RESULT" = "SUCCESS" ]; then
    echo "✅ Build passed! Your CI/CD pipeline is working."
    echo "   • Commit more changes and watch automated builds"
    echo "   • Check JENKINS_QUICKREF.md for daily usage"
elif [ "$BUILD_RESULT" = "FAILURE" ]; then
    echo "❌ Build failed. Check the console output for errors:"
    echo "   • Go to: ${BUILD_URL}console"
    echo "   • Fix any issues and commit changes"
    echo "   • Jenkins will automatically build on next commit"
else
    echo "🔄 Build in progress. Wait for completion or check:"
    echo "   • Console: ${BUILD_URL}console"
    echo "   • Status: ${BUILD_URL}"
fi
