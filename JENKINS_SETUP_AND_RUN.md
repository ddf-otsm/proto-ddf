# Jenkins Pipeline Setup & Execution Guide

**Status**: ✅ Ready for Production  
**Date**: October 17, 2025

---

## 📋 Quick Start

### Prerequisites
```bash
# 1. Jenkins is running
lsof -i :8080 | grep LISTEN

# 2. Proto-DDF repo is ready
cd /Users/luismartins/local_repos/proto-ddf
git status

# 3. Python venv with dependencies
./venv/bin/python -m pytest --version
```

---

## 🚀 Setup Pipeline Job in Jenkins

### Option 1: Automated Setup (Recommended)

```bash
# Create a setup script that will configure the job
cat > setup_jenkins_job.sh << 'EOF'
#!/bin/bash

JENKINS_URL="http://localhost:8080"
JOB_NAME="proto-ddf-e2e"
REPO_PATH="/Users/luismartins/local_repos/proto-ddf"

# 1. Get CSRF token
CRUMB=$(curl -s "$JENKINS_URL/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)" 2>/dev/null)

echo "Creating job: $JOB_NAME"

# 2. Create job config XML
cat > /tmp/job-config.xml << 'JOBXML'
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@1428.v27a69c09f980">
  <actions/>
  <description>Proto-DDF E2E Testing Pipeline</description>
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
    <com.cloudbees.plugins.credentials.CredentialsProvider_-StoreCredentialsAction/>
  </properties>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@3873.v47282919bd78">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@5.2.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>file:///Users/luismartins/local_repos/proto-ddf</url>
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
JOBXML

# 3. Create the job
curl -X POST \
  -H "$CRUMB" \
  -H "Content-Type: application/xml" \
  --data-binary @/tmp/job-config.xml \
  "$JENKINS_URL/createItem?name=$JOB_NAME" \
  2>/dev/null

echo "Job created: $JOB_NAME"
echo "Ready to build at: $JENKINS_URL/job/$JOB_NAME"
EOF

chmod +x setup_jenkins_job.sh
./setup_jenkins_job.sh
```

### Option 2: Manual Setup in Jenkins UI

1. **Create New Job**
   - Jenkins Dashboard → "New Item"
   - Name: `proto-ddf-e2e`
   - Type: "Pipeline"
   - Click "OK"

2. **Configure Pipeline**
   - **Description**: `Proto-DDF E2E Testing Pipeline`
   
   - **Build Triggers**: (none for manual)
   
   - **Pipeline** section:
     - Definition: `Pipeline script from SCM`
     - SCM: `Git`
     - Repository URL: `/Users/luismartins/local_repos/proto-ddf`
     - Credentials: (none for local path)
     - Branches to build: `*/main`
     - Script Path: `Jenkinsfile.e2e`
   
   - **Advanced Project Options**:
     - Lightweight checkout: ✅ checked

3. **Save and Build**
   - Click "Save"
   - Click "Build Now"

---

## 🔨 Running the Pipeline

### Method 1: Jenkins Web UI

```
1. Navigate to: http://localhost:8080/job/proto-ddf-e2e
2. Click "Build Now" button
3. Watch build in real-time:
   - Click on build number (e.g., #1)
   - Select "Console Output"
   - Monitor progress
```

### Method 2: Jenkins CLI

```bash
# Build and wait for completion
java -jar jenkins-cli.jar -s http://localhost:8080 build proto-ddf-e2e -s -v

# Build without waiting
java -jar jenkins-cli.jar -s http://localhost:8080 build proto-ddf-e2e

# Get build status
java -jar jenkins-cli.jar -s http://localhost:8080 get-job proto-ddf-e2e
```

### Method 3: cURL API

```bash
# Get Jenkins crumb (CSRF token)
CRUMB=$(curl -s "http://localhost:8080/crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)")

# Trigger build
curl -X POST \
  -H "$CRUMB" \
  "http://localhost:8080/job/proto-ddf-e2e/build?delay=0sec"

# Check job status
curl -s "http://localhost:8080/job/proto-ddf-e2e/api/json" | jq '.lastBuild'

# Get console output
curl -s "http://localhost:8080/job/proto-ddf-e2e/lastBuild/consoleText"
```

---

## 📊 Expected Pipeline Output

### Stage 1: Setup (5-10 minutes)

```
[Pipeline] Start of Pipeline
[Pipeline] stage
[Pipeline] { (Setup)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
📦 Setting up E2E test environment...
+ [ -d venv ]
+ python3 -m venv venv
+ source venv/bin/activate
+ pip install -q --upgrade pip setuptools wheel
Successfully installed pip-24.0 setuptools-68.0.0 wheel-0.41.0
+ pip install -q -e ./reflex
Successfully installed reflex-0.8.15.dev1
+ pip install -q -r requirements.txt
Successfully installed psutil-6.0.0 pytest-8.4.2 playwright-1.40.0
+ python -m playwright install --with-deps chromium
✅ Playwright chromium installed successfully
[Pipeline] }
[Pipeline] }
[Pipeline] }
```

### Stage 2: Start Generator (2-3 minutes)

```
[Pipeline] stage
[Pipeline] { (Start Generator)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
🚀 Starting Proto-DDF generator...
+ pkill -f reflex run
+ sleep 2
+ timeout 60 reflex run &
Compiled successfully
✅ Generator is ready on http://localhost:3903
Generator PID: 45678 saved to /tmp/generator.pid
[Pipeline] }
[Pipeline] }
[Pipeline] }
```

### Stage 3: Run E2E Tests (10-15 minutes)

```
[Pipeline] stage
[Pipeline] { (Run E2E Tests)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
🧪 Running E2E tests...
collected 13 items

tests/e2e/test_process_management.py::TestAutoStart::test_open_app_when_down_auto_starts PASSED [ 7%]
tests/e2e/test_process_management.py::TestAutoStart::test_open_app_when_running_redirects_immediately PASSED [ 15%]
tests/e2e/test_process_management.py::TestAutoStart::test_open_app_preview_button_auto_starts PASSED [ 23%]
tests/e2e/test_process_management.py::TestProcessControl::test_stop_button_stops_running_app PASSED [ 31%]
tests/e2e/test_process_management.py::TestProcessControl::test_restart_button_restarts_app PASSED [ 38%]
tests/e2e/test_process_management.py::TestHealthDashboard::test_health_dashboard_shows_generator_ports PASSED [ 46%]
tests/e2e/test_process_management.py::TestHealthDashboard::test_health_dashboard_shows_app_count PASSED [ 54%]
tests/e2e/test_process_management.py::TestHealthDashboard::test_health_dashboard_shows_running_count PASSED [ 62%]
tests/e2e/test_process_management.py::TestHealthDashboard::test_health_badges_show_app_status PASSED [ 69%]
tests/e2e/test_process_management.py::TestHealthDashboard::test_refresh_health_button_updates_status PASSED [ 77%]
tests/e2e/test_process_management.py::TestPortStability::test_ports_remain_stable_after_restart PASSED [ 85%]
tests/e2e/test_process_management.py::TestPortStability::test_ports_remain_stable_after_generator_restart PASSED [ 92%]
tests/e2e/test_process_management.py::TestErrorHandling::test_shows_error_when_app_fails_to_start PASSED [100%]

======================== 13 passed in 452s ========================
[Pipeline] }
[Pipeline] }
[Pipeline] }
```

### Stage 4: Unit Tests (1-2 minutes)

```
[Pipeline] stage
[Pipeline] { (Unit Tests)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
✅ Running unit tests...
collected 18 items

tests/unit/test_config.py::TestPortConfiguration::test_backend_host_configuration PASSED
tests/unit/test_config.py::TestPortConfiguration::test_port_persistence PASSED
tests/unit/test_config.py::TestPortConfiguration::test_port_range_validation PASSED
tests/unit/test_config.py::TestPortConfiguration::test_port_uniqueness PASSED
tests/unit/test_config.py::TestApplicationConfiguration::test_app_name PASSED
tests/unit/test_config.py::TestApplicationConfiguration::test_field_mapping_patterns PASSED
tests/unit/test_config.py::TestApplicationConfiguration::test_integration_settings PASSED
tests/unit/test_config.py::TestApplicationConfiguration::test_netsuite_fields PASSED
tests/unit/test_config.py::TestApplicationConfiguration::test_supported_sources PASSED
tests/unit/test_generator.py::TestGeneratorState::test_generator_methods_exist PASSED
tests/unit/test_generator.py::TestGeneratorState::test_generator_state_class_exists PASSED
tests/unit/test_generator.py::TestGeneratorState::test_load_generated_apps_function PASSED
tests/unit/test_generator.py::TestGeneratorComponents::test_app_card_import PASSED
tests/unit/test_generator.py::TestGeneratorComponents::test_generator_app_import PASSED
tests/unit/test_generator.py::TestGeneratorComponents::test_index_import PASSED
tests/unit/test_generator.py::TestGeneratedAppStructure::test_generated_directory_exists PASSED
tests/unit/test_generator.py::TestGeneratedAppStructure::test_netsuite_hub_exists PASSED
tests/unit/test_generator.py::TestGeneratedAppStructure::test_netsuite_hub_structure PASSED

======================== 18 passed in 0.47s ========================
[Pipeline] }
[Pipeline] }
[Pipeline] }
```

### Stage 5: Cleanup (30 seconds)

```
[Pipeline] stage
[Pipeline] { (Cleanup)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
🧹 Cleaning up...
+ [ -f /tmp/generator.pid ]
+ kill 45678
+ rm /tmp/generator.pid
+ pkill -f reflex run
+ pkill -f node
[Pipeline] }
[Pipeline] }
[Pipeline] }
```

### Post-Build (Success)

```
[Pipeline] stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] script
[Pipeline] {
[Pipeline] sh
📝 Generating reports...
[Pipeline] junit
Recording test results
Archiving artifacts
[Pipeline] }
[Pipeline] }
[Pipeline] }
[Pipeline] End of Pipeline
✅ E2E tests passed!

Build time: 32 minutes 45 seconds
Status: SUCCESS ✅
```

---

## 📈 Monitoring & Verification

### Real-Time Dashboard
```
Jenkins URL: http://localhost:8080/
Job URL: http://localhost:8080/job/proto-ddf-e2e
Last Build: http://localhost:8080/job/proto-ddf-e2e/lastBuild
Console: http://localhost:8080/job/proto-ddf-e2e/lastBuild/consoleText
```

### API Queries

```bash
# Job info
curl -s http://localhost:8080/job/proto-ddf-e2e/api/json | jq '.{name, description, lastBuild}'

# Last build status
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/api/json | jq '.{number, result, duration, timestamp}'

# Build stages (pipeline)
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/wfapi/describe | jq '.stages'

# Get console output (last 50 lines)
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/consoleText | tail -50

# Test results
curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/testReport/api/json | jq '.{duration, passCount, failCount}'
```

---

## 🔍 Troubleshooting

### Build Fails at Setup Stage

**Error**: `Cannot find or open Jenkinsfile.e2e`

**Solution**:
```bash
# Verify Jenkinsfile exists
ls -la Jenkinsfile.e2e

# Verify Git repository is initialized
git remote -v
```

### Build Fails at Start Generator Stage

**Error**: `reflex run` times out

**Solution**:
```bash
# Check if port is already in use
lsof -i :3903

# Kill existing process
pkill -f "reflex run"

# Start generator manually
make run
```

### Build Fails at E2E Tests Stage

**Error**: `Playwright tests timeout`

**Solution**:
```bash
# Increase timeout in Jenkinsfile
timeout(time: 30, unit: 'MINUTES') {
    sh 'pytest tests/e2e/ -v'
}

# Or run manually to debug
pytest tests/e2e/test_process_management.py -v -s
```

### Jenkins Cannot Access Repository

**Error**: `fatal: repository not found`

**Solution**:
```bash
# Use absolute path instead of Git URL
Repository URL: /Users/luismartins/local_repos/proto-ddf
Credentials: (none)

# Or configure Git
git config --global user.email "jenkins@local.dev"
git config --global user.name "Jenkins"
```

---

## ✅ Verification Checklist

Before running the pipeline, verify:

- [ ] Jenkins is running (`lsof -i :8080`)
- [ ] Proto-DDF repo is clean (`git status`)
- [ ] Python venv exists (`./venv/bin/python --version`)
- [ ] Dependencies installed (`pip list | grep pytest`)
- [ ] Jenkinsfile.e2e exists (`ls Jenkinsfile.e2e`)
- [ ] Port 3903 is available (`lsof -i :3903`)
- [ ] Generated apps directory exists (`ls -la generated/`)

---

## 🎯 Success Criteria

### ✅ All Tests Pass
- 18/18 Unit tests: ✅ PASS
- 13/13 E2E tests: ✅ PASS
- Total: 31/31 tests passing

### ✅ All Stages Complete
1. Setup: ✅ PASS
2. Start Generator: ✅ PASS
3. Run E2E Tests: ✅ PASS
4. Unit Tests: ✅ PASS
5. Cleanup: ✅ PASS

### ✅ Artifacts Generated
- Console output logged
- Test results archived
- Build duration: ~30-40 minutes
- Status: SUCCESS

---

## 🚀 Next Steps

1. **Verify Pipeline is Running**
   ```bash
   curl -s http://localhost:8080/job/proto-ddf-e2e/api/json | jq '.lastBuild'
   ```

2. **Monitor Build Progress**
   ```bash
   watch -n 5 'curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/api/json | jq ".{result, executor, duration}"'
   ```

3. **View Test Results**
   ```bash
   curl -s http://localhost:8080/job/proto-ddf-e2e/lastBuild/testReport/api/json | jq '.'
   ```

4. **Integrate into CI/CD**
   - Add webhooks for auto-trigger
   - Configure notifications
   - Set up performance tracking

---

## 📚 References

- [Jenkinsfile Syntax](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/)
- [Jenkins CLI Documentation](https://www.jenkins.io/doc/book/managing/cli/)
- [Jenkins REST API](https://www.jenkins.io/doc/book/using-jenkins/remote-access-api/)
- [Reflex Framework Documentation](https://reflex.dev/docs/)
- [Playwright Documentation](https://playwright.dev/python/)

---

**Prepared by**: AI Assistant  
**Status**: ✅ READY FOR JENKINS EXECUTION  
**Last Updated**: October 17, 2025
