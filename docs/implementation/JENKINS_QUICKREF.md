# Jenkins Quick Reference - proto-ddf

## 🚀 Essential Commands

```bash
# Load Jenkins helper
source jenkins_helper.sh

# Check status
jenkins_status

# Start/Stop/Restart
jenkins_start
jenkins_stop
jenkins_restart

# View logs (live)
jenkins_logs

# Open UI in browser
jenkins_open

# Get admin password
jenkins_password

# Trigger build
jenkins_build
```

## 📋 Configuration

| Item | Value |
|------|-------|
| **Jenkins URL** | http://localhost:17843 |
| **Pipeline Name** | `proto-ddf-local` |
| **Jenkinsfile** | `Jenkinsfile.local` |
| **Port** | 17843 |
| **Password File** | `~/vars/jenkins_admin_password_port17843.txt` |
| **Config File** | `~/vars/jenkins_config.sh` |
| **Log File** | `~/vars/jenkins.log` |
| **PID File** | `~/vars/jenkins.pid` |

## 🔄 Pipeline Stages

1. **Checkout** - Clone repo + init submodules
2. **Environment Setup** - Create venv
3. **Install Dependencies** - Install Reflex + requirements
4. **Verify Installation** - Check versions
5. **Lint & Quality** - Black, isort, Flake8
6. **Build Check** - Compile Reflex app
7. **Security Scan** - Check vulnerabilities

## 📝 Daily Workflow

```bash
# 1. Load helper
source jenkins_helper.sh

# 2. Check Jenkins is running
jenkins_status

# 3. Make your code changes
# ... edit files ...

# 4. Commit
git add .
git commit -m "Your message"

# 5. Test build
jenkins_build

# 6. Monitor
jenkins_open  # or jenkins_logs
```

## 🐛 Troubleshooting

### Jenkins Won't Start
```bash
lsof -i :17843                 # Check port
tail -50 ~/vars/jenkins.log    # Check logs
jenkins_start                  # Try starting
```

### Build Fails
```bash
# Check console in Jenkins UI
jenkins_open

# Or view logs
jenkins_logs

# Check submodules
git submodule update --init --recursive
```

### Can't Access UI
```bash
curl -I http://localhost:17843  # Test connection
jenkins_restart                 # Restart Jenkins
```

## 📚 Documentation

- **Full Guide**: [JENKINS_SETUP.md](JENKINS_SETUP.md)
- **Shared Setup**: [~/vars/JENKINS_LOCAL_HANDOFF.md](/Users/luismartins/vars/JENKINS_LOCAL_HANDOFF.md)
- **Project README**: [README.md](README.md)

## 🔗 Quick Links

- Jenkins UI: http://localhost:17843
- Pipeline: http://localhost:17843/job/proto-ddf-local/

## 💡 Tips

```bash
# Alias for quick access (add to ~/.bashrc or ~/.zshrc)
alias j='source /Users/luismartins/local_repos/proto-ddf/jenkins_helper.sh'

# One-liner: status + open
source jenkins_helper.sh && jenkins_status && jenkins_open

# Watch logs in real-time
jenkins_logs

# Get password quickly
cat ~/vars/jenkins_admin_password_port17843.txt
```

---

**Keep this card handy!** 🚀

