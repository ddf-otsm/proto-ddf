# NetSuite Integration Hub - Setup Checklist ✅

Use this checklist to verify your setup is correct.

## ✅ Prerequisites

- [ ] Python 3.10 or higher installed
  ```bash
  python3 --version
  # Should show: Python 3.10.x or higher
  ```

- [ ] Git installed
  ```bash
  git --version
  ```

- [ ] In the proto-ddf directory
  ```bash
  pwd
  # Should end with: proto-ddf
  ```

## ✅ Submodule Verification

- [ ] Reflex submodule initialized
  ```bash
  ls -la reflex/pyproject.toml
  # Should show the file exists
  ```

- [ ] Submodule status
  ```bash
  git submodule status
  # Should show: commit hash reflex (not empty)
  ```

## ✅ Configuration Files

- [ ] rxconfig.py has network binding
  ```bash
  grep "backend_host" rxconfig.py
  # Should show: backend_host="0.0.0.0"
  ```

- [ ] requirements.txt references submodule
  ```bash
  cat requirements.txt | head -5
  # Should mention: reflex submodule
  ```

- [ ] run.sh is executable
  ```bash
  ls -la run.sh | grep "x"
  # Should show: -rwxr-xr-x or similar
  ```

## ✅ Application Files

- [ ] Main application exists
  ```bash
  wc -l proto_ddf_app/proto_ddf_app.py
  # Should show: ~676 lines
  ```

- [ ] Application imports work
  ```bash
  python3 -c "from proto_ddf_app import proto_ddf_app; print('✅ OK')"
  ```

## ✅ Documentation

- [ ] All documentation files present
  ```bash
  ls *.md
  # Should show: README.md, QUICKSTART.md, EXAMPLES.md, 
  #              VISUAL_GUIDE.md, SUMMARY.md, ARCHITECTURE.md,
  #              DOCUMENTATION_INDEX.md, CHECKLIST.md
  ```

## ✅ Installation Test

- [ ] Create fresh virtual environment
  ```bash
  rm -rf venv
  python3 -m venv venv
  source venv/bin/activate
  ```

- [ ] Upgrade pip
  ```bash
  pip install --upgrade pip setuptools wheel
  ```

- [ ] Install reflex from submodule
  ```bash
  pip install -e ./reflex
  # Should complete without errors
  ```

- [ ] Verify reflex installation
  ```bash
  python3 -c "import reflex; print(f'Reflex {reflex.__version__} from {reflex.__file__}')"
  # Should point to: .../proto-ddf/reflex/reflex/__init__.py
  ```

- [ ] Test application import
  ```bash
  python3 -c "from proto_ddf_app.proto_ddf_app import State; print('✅ Application loads')"
  ```

## ✅ Network Configuration

- [ ] Check IP address detection
  ```bash
  # macOS:
  ipconfig getifaddr en0
  
  # Linux:
  hostname -I | awk '{print $1}'
  ```

- [ ] Verify ports are free
  ```bash
  lsof -i :3000 -i :8000
  # Should show: empty (no processes using these ports)
  ```

## ✅ Run Test

- [ ] Start application
  ```bash
  ./run.sh
  # Should:
  # - Initialize submodule (if needed)
  # - Create venv (if needed)
  # - Install dependencies
  # - Show IP addresses
  # - Start server
  ```

- [ ] Verify URLs displayed
  ```
  Expected output should include:
  📱 Access the application at:
     Local:    http://127.0.0.1:3000
     Network:  http://192.168.x.x:3000
  
  🔌 Backend API running on:
     http://0.0.0.0:8000
  ```

- [ ] Test local access
  ```
  Open browser: http://127.0.0.1:3000
  Should see: NetSuite Integration Hub interface
  ```

- [ ] Test network access (from another device)
  ```
  1. Connect device to same WiFi
  2. Open browser on device
  3. Go to: http://192.168.x.x:3000 (use displayed IP)
  4. Should see: Same interface
  ```

## ✅ Functionality Test

- [ ] Select a data source
  - Click any source card (e.g., CSV File)
  - Should see: Active Integration panel

- [ ] Connect to source
  - Click "1. Connect to Source"
  - Should see: Progress bar animating
  - Should see: Source data table

- [ ] Auto-map fields
  - Click "2. Auto-Map Fields"
  - Should see: Field mapping display

- [ ] Sync to NetSuite
  - Click "3. Sync to NetSuite"
  - Should see: Progress bar
  - Should see: Synced records with status badges

- [ ] Check statistics
  - Should update: Total Records, Successful, Failed

- [ ] Check integration logs
  - Should show: Connection and Sync entries

- [ ] Toggle dark mode
  - Click moon/sun icon (top right)
  - Should switch: Theme colors

## ✅ Cleanup Test

- [ ] Stop server
  ```bash
  Ctrl+C in terminal
  ```

- [ ] Restart server
  ```bash
  ./run.sh
  # Should start faster (using existing venv)
  ```

## 🎯 All Tests Passed?

If all checkboxes are checked, your setup is correct! 🎉

## 🐛 Troubleshooting

### Python Version Error
```bash
# If Python 3.9 or lower:
# Install Python 3.10+ from:
# - https://www.python.org/downloads/
# - brew install python@3.10 (macOS)
# - apt install python3.10 (Ubuntu)
```

### Submodule Not Initialized
```bash
git submodule update --init --recursive
```

### Port Already in Use
```bash
# Kill process on port
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

### Can't Access from Network
```bash
# Check firewall
# macOS:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)

# Linux:
sudo ufw allow 3000
sudo ufw allow 8000
```

### Module Import Error
```bash
# Reinstall from submodule
source venv/bin/activate
pip uninstall reflex
pip install -e ./reflex
```

## 📚 Next Steps

Once all checks pass:

1. ✅ Read [QUICKSTART.md](QUICKSTART.md) for usage guide
2. ✅ Read [ARCHITECTURE.md](ARCHITECTURE.md) for how it works
3. ✅ Run `python3 demo.py` to see features
4. ✅ Try all 6 data sources
5. ✅ Check [EXAMPLES.md](EXAMPLES.md) for real integrations

---

**Happy Integrating! ��**
