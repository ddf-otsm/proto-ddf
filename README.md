# Proto-DDF 🎨

**Proto-DDF** (Prototype Data-Driven Forms) is an AI-powered Reflex application generator that helps you create full-stack Python web applications with a beautiful UI.

## 🌟 Features

- **🎨 Generator Interface**: Visual interface to create and manage Reflex applications
- **📦 Template Library**: Pre-built templates for common use cases
- **🔧 Centralized Config**: Non-sensitive constants managed in `config/`
- **🎲 Smart Port Assignment**: Random ports (3000-5000) with persistence
- **📁 Organized Structure**: Clear separation between generator and generated apps

## 📂 Project Structure

```
proto-ddf/
├── proto_ddf_app/          # Main generator application
│   ├── generator.py         # Generator interface
│   └── proto_ddf_app.py    # Original NetSuite Integration Hub (legacy)
├── generated/               # Generated applications directory
│   ├── netsuite_integration_hub/  # Example generated app
│   │   ├── proto_ddf_app/
│   │   ├── rxconfig.py
│   │   └── requirements.txt
│   └── README.md
├── config/                  # Centralized configuration
│   ├── __init__.py
│   ├── constants.py         # Non-sensitive constants
│   ├── .port_config.json    # Auto-generated port assignments (gitignored)
│   └── README.md
├── reflex/                  # Reflex framework (submodule)
├── rxconfig.py              # Main Reflex configuration
├── run.sh                   # Main runner script
└── venv/                    # Python virtual environment
```

## 🚀 Quick Start

### 1. Run the Generator Interface

```bash
./run.sh
```

This will start the Proto-DDF generator interface where you can:
- View generated applications
- Create new applications from templates
- Manage existing apps
- Access app documentation

### 2. Run a Generated App

```bash
cd generated/netsuite_integration_hub
./run.sh
```

*Note: Generated apps include their own run scripts that handle virtual environment activation and port configuration automatically.*

## 🛠️ Requirements

- **Python 3.10+** (Python 3.11 or 3.13 recommended)
- **Reflex** (installed from submodule)
- **Bun** (auto-installed by Reflex for frontend)
- **Node.js 20.19.0+** (recommended)

## 📱 Generated Applications

### NetSuite Integration Hub
A comprehensive showcase of data integration capabilities:
- 📊 Multi-source integration (CSV, JSON, Database, REST API, Salesforce, Webhook)
- 🔄 Real-time sync with progress tracking
- 🔀 Intelligent field mapping
- 📈 Statistics dashboard
- 📝 Integration logs

**Access**: The generated app will display its access URLs when started, including both local and network addresses.

## ⚙️ Configuration

### Port Management

Ports are randomly assigned (3000-5000) and saved in `config/.port_config.json`:

```json
{
  "backend": 4666,
  "frontend": 4138
}
```

To reset ports:
```bash
rm config/.port_config.json
```

### Adding Custom Constants

Edit `config/constants.py` to add new non-sensitive configuration:

```python
# Your custom constants
MY_CUSTOM_SETTING = "value"
```

Then import in your code:
```python
from config.constants import MY_CUSTOM_SETTING
```

## 📚 Documentation

- [Architecture Guide](ARCHITECTURE.md) - System design and structure
- [Quick Start Guide](QUICKSTART.md) - Getting started quickly
- [Examples](EXAMPLES.md) - Code examples and patterns
- [Visual Guide](VISUAL_GUIDE.md) - UI components and layouts
- [Config Documentation](config/README.md) - Configuration management

## 🔧 Development

### Running in Development Mode

The default configuration runs in development mode with:
- Hot reload enabled
- Debug logging
- Detailed error messages

### Project Structure Best Practices

1. **Generator App** (`proto_ddf_app/`): Main interface for creating apps
2. **Generated Apps** (`generated/`): Each generated app is self-contained
3. **Shared Config** (`config/`): Centralized non-sensitive constants
4. **Documentation**: Keep docs up-to-date as you add features

## 🤝 Contributing

1. Keep generated apps in `generated/` directory
2. Add new templates to the generator interface
3. Update documentation when adding features
4. Test on multiple Python versions (3.10, 3.11, 3.13)

## 📄 License

See LICENSE file for details.

## 🐛 Troubleshooting

### Port Already in Use

Ports are randomly assigned (3000-5000) and saved in `config/.port_config.json`. If ports are in use:

```bash
# Reset to get new random ports
rm config/.port_config.json
./run.sh
```

This will generate new random ports for both the generator interface and any generated apps.

### Python Version Error

Make sure you have Python 3.10+:
```bash
python3 --version
```

If needed, install a newer Python version and recreate the venv:
```bash
rm -rf venv
python3.11 -m venv venv
./run.sh
```

### Reflex Not Found

Reinstall Reflex from the submodule:
```bash
source venv/bin/activate
pip install -e ./reflex
```

## 🎯 Roadmap

- [ ] AI-powered code generation
- [ ] More templates (Dashboard, Chat, E-commerce, CMS)
- [ ] Component library
- [ ] Deployment helpers
- [ ] Database schema generation
- [ ] API endpoint generation
- [ ] Authentication templates

---

Built with ❤️ using [Reflex](https://reflex.dev) - Pure Python Web Apps
