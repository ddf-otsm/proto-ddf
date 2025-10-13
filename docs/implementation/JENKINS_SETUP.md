# Jenkins CI/CD Setup - proto-ddf

**Project**: NetSuite Integration Hub (proto-ddf)
**Type**: Python/Reflex Web Application
**Jenkins Instance**: Shared local instance (http://localhost:17843)

---

## 📋 Overview

This project uses a **shared Jenkins local instance** for CI/CD. The Jenkins server runs on port `17843` and is shared across all local repositories.

### Quick Links

| Resource | Location |
|----------|----------|
| **Jenkins UI** | http://localhost:17843 |
| **Pipeline Name** | `proto-ddf-local` |
| **Jenkinsfile** | `Jenkinsfile.local` |
| **Helper Script** | `jenkins_helper.sh` |
| **Shared Config** | `~/vars/jenkins_config.sh` |
| **Admin Password** | `~/vars/jenkins_admin_password_port17843.txt` |

---

## 🚀 Quick Start

### 1. Load Jenkins Helper

```bash
# Source the helper script to get all Jenkins functions
source jenkins_helper.sh

# Check if Jenkins is running
jenkins_status
```

### 2. Start Jenkins (if not running)

```bash
jenkins_start
```

### 3. Access Jenkins UI

```bash
# Open Jenkins in browser
jenkins_open

# Get admin password (for first login)
jenkins_password
```

### 4. Create Pipeline (First Time Only)

1. Click **New Item**
2. Enter name: `proto-ddf-local`
3. Select **Pipeline**
4. Click **OK**
5. Configure:
   - **Definition**: Pipeline script from SCM
   - **SCM**: Git
   - **Repository URL**: `file:///Users/luismartins/local_repos/proto-ddf`
   - **Branch Specifier**: `*/master` (or your default branch)
   - **Script Path**: `Jenkinsfile.local`
6. Click **Save**

### 5. Run Your First Build

```bash
# Trigger a build
jenkins_build

# Or manually in Jenkins UI:
# Click "Build Now" on the pipeline page
```

---

## 🔧 Jenkins Helper Commands

The `jenkins_helper.sh` script provides convenient commands for managing Jenkins:

```bash
# Source the helper
source jenkins_helper.sh

# Check status
jenkins_status

# Start/stop/restart
jenkins_start
jenkins_stop
jenkins_restart

# View logs (live)
jenkins_logs

# Open in browser
jenkins_open

# Get admin password
jenkins_password

# Trigger build
jenkins_build

# Show help
jenkins_help
```

---

## 📝 Pipeline Stages

The `Jenkinsfile.local` defines the following stages:

### 1. Checkout
- Clones the repository
- Initializes git submodules (reflex)

### 2. Environment Setup
- Creates Python virtual environment
- Installs/upgrades pip, setuptools, wheel

### 3. Install Dependencies
- Installs Reflex from submodule (editable mode)
- Installs other requirements from `requirements.txt`

### 4. Verify Installation
- Checks Python version
- Verifies Reflex installation
- Lists installed packages

### 5. Lint & Quality
- **Black**: Code formatting check
- **isort**: Import sorting check
- **Flake8**: Linting and style check

### 6. Build Check
- Initializes Reflex (generates `.web` directory)
- Validates configuration (`rxconfig.py`)
- Compiles the application (export check)

### 7. Security Scan
- Uses `safety` to check for known vulnerabilities in dependencies

### Post Actions
- **Always**: Clean up build artifacts and `__pycache__` directories
- **Success**: Logs success message
- **Failure**: Logs failure message

---

## 🔄 Development Workflow

### Daily Workflow

```bash
# 1. Start your day - check Jenkins status
source jenkins_helper.sh
jenkins_status

# 2. Make code changes
# ... edit files ...

# 3. Commit changes
git add .
git commit -m "Your changes"

# 4. Test locally (optional)
./run.sh

# 5. Trigger Jenkins build
jenkins_build

# 6. Monitor build
jenkins_open  # View in browser
# Or
jenkins_logs  # Watch logs in terminal
```

### Before Pushing to Remote

```bash
# Run a local Jenkins build to verify everything passes
jenkins_build

# Wait for build to complete and verify it's green
jenkins_open
```

---

## 🛠️ Customizing the Pipeline

### Adding Test Stage

Edit `Jenkinsfile.local` and add after the "Verify Installation" stage:

```groovy
stage('Run Tests') {
    steps {
        echo '🧪 Running tests...'
        sh '''
            cd ${APP_DIR}
            source ${VENV_DIR}/bin/activate

            # Install pytest
            pip install pytest pytest-cov

            # Run tests (if you create a tests/ directory)
            pytest tests/ -v --cov=proto_ddf_app
        '''
    }
}
```

### Adding Build Artifacts

Add to the `post` section:

```groovy
post {
    success {
        archiveArtifacts artifacts: '.web/**/*', allowEmptyArchive: true
        echo '✅ Build artifacts archived!'
    }
}
```

### Adding Notifications

Install the Email Extension Plugin or Slack Plugin in Jenkins, then add:

```groovy
post {
    failure {
        emailext (
            subject: "Build Failed: ${PROJECT_NAME}",
            body: "The build failed. Check console output.",
            to: "your-email@example.com"
        )
    }
}
```

---

## 🐛 Troubleshooting

### Jenkins Won't Start

```bash
# Check if port is in use
lsof -i :17843

# Check logs for errors
tail -50 ~/vars/jenkins.log

# Kill any zombie processes
ps aux | grep jenkins | grep -v grep | awk '{print $2}' | xargs kill

# Try starting again
jenkins_start
```

### Build Fails on Submodule

```bash
# Manually initialize submodules
cd /Users/luismartins/local_repos/proto-ddf
git submodule update --init --recursive

# Then trigger build again
jenkins_build
```

### Build Fails on Dependencies

```bash
# Manually test dependency installation
cd /Users/luismartins/local_repos/proto-ddf
python3 -m venv test_venv
source test_venv/bin/activate
pip install -e ./reflex
pip install -r requirements.txt

# If successful, trigger build again
jenkins_build
```

### Build Hangs on Export

The `reflex export` command has a 60-second timeout. If it hangs:

1. Edit `Jenkinsfile.local`
2. Find the `timeout 60` line
3. Increase to `timeout 120` or remove the timeout
4. Commit and trigger build

### Can't Access Jenkins UI

```bash
# Verify Jenkins is running
curl -I http://localhost:17843

# Try restarting
jenkins_restart

# Open in different browser
jenkins_open
```

---

## 📊 Monitoring Builds

### Console Output

1. Open Jenkins UI: `jenkins_open`
2. Click on your pipeline: `proto-ddf-local`
3. Click on a build number (e.g., `#5`)
4. Click **Console Output**

### Build History

- **Blue**: Build in progress
- **Green**: Build successful
- **Yellow**: Build unstable (passed with warnings)
- **Red**: Build failed

### Build Trends

Jenkins tracks:
- Build duration over time
- Success/failure rates
- Test results (if configured)

---

## 🔐 Security Best Practices

### Password Management

```bash
# Never commit the password file
echo "jenkins_admin_password_port17843.txt" >> .gitignore

# Store password securely
chmod 600 ~/vars/jenkins_admin_password_port17843.txt
```

### Network Security

The Jenkins instance is bound to `127.0.0.1` (localhost only) and uses a non-standard port `17843` for security.

### Credential Storage

For API tokens or sensitive data in pipelines:

1. Go to Jenkins → Manage Jenkins → Credentials
2. Add credentials (username/password, secret text, etc.)
3. Reference in Jenkinsfile using `credentials()` function

---

## 📚 Resources

### Jenkins Documentation
- [Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Pipeline Steps Reference](https://www.jenkins.io/doc/pipeline/steps/)
- [Best Practices](https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/)

### Project Documentation
- [Main README](README.md) - Project overview
- [Quickstart Guide](QUICKSTART.md) - Getting started
- [Architecture](ARCHITECTURE.md) - System design

### Shared Jenkins Setup
- [Jenkins Local Handoff](/Users/luismartins/vars/JENKINS_LOCAL_HANDOFF.md) - Complete setup guide
- Shared Config: `~/vars/jenkins_config.sh`

---

## 🎯 Next Steps

### Immediate

- [x] Jenkinsfile created
- [ ] Pipeline created in Jenkins UI
- [ ] First successful build
- [ ] Team members can access Jenkins

### Future Enhancements

- [ ] Add unit tests (pytest)
- [ ] Add integration tests
- [ ] Configure build triggers (webhooks or polling)
- [ ] Add code coverage reporting
- [ ] Add deployment stage (if applicable)
- [ ] Configure email/Slack notifications
- [ ] Add security scanning (bandit)
- [ ] Add performance testing

---

## 📝 Maintenance

### Regular Tasks

**Weekly**:
- Check build logs for warnings
- Review security scan results
- Update dependencies (if needed)

**Monthly**:
- Update Jenkins plugins
- Review and clean old builds
- Update Jenkinsfile best practices

### Backup

Jenkins configuration is stored in `~/.jenkins/`. Back it up regularly:

```bash
# Create backup
tar -czf jenkins_backup_$(date +%Y%m%d).tar.gz ~/.jenkins/

# Restore backup
tar -xzf jenkins_backup_YYYYMMDD.tar.gz -C ~/
```

---

## 🤝 Contributing

### Modifying the Pipeline

1. Edit `Jenkinsfile.local`
2. Test changes locally:
   ```bash
   jenkins_build
   ```
3. Commit changes:
   ```bash
   git add Jenkinsfile.local
   git commit -m "Update Jenkins pipeline: [description]"
   ```
4. Push to remote (after verification)

### Sharing Updates

If you make improvements to the Jenkins setup:
1. Update this documentation
2. Share with the team
3. Update the shared handoff document if applicable

---

**Status**: ✅ Ready for use
**Last Updated**: October 10, 2025
**Maintained by**: Development Team

---

## 💡 Tips & Tricks

### Quick Commands

```bash
# One-liner to check status and open Jenkins
source jenkins_helper.sh && jenkins_status && jenkins_open

# Watch logs in real-time
jenkins_logs

# Restart Jenkins and open in browser
jenkins_restart && jenkins_open
```

### IDE Integration

Add to your `.bashrc` or `.zshrc`:

```bash
# Quick alias for Jenkins helper
alias j='source /Users/luismartins/local_repos/proto-ddf/jenkins_helper.sh'

# Now you can just type: j && jenkins_status
```

### Build Status Badge

Add to your `README.md`:

```markdown
![Jenkins Build Status](http://localhost:17843/buildStatus/icon?job=proto-ddf-local)
```

---

**Happy CI/CD!** 🚀
