# NetSuite Integration Hub - Quick Start Guide 🚀

## Overview

This application showcases NetSuite integration patterns with multiple data sources. It demonstrates how to connect, map, and sync data from various sources (CSV, JSON, Database, Salesforce, etc.) to NetSuite.

## Prerequisites

- **Python 3.10 or higher** (REQUIRED - Reflex needs Python 3.10+)
- pip (Python package manager)
- Git (for cloning and managing submodules)

Check your Python version:
```bash
python3 --version
# Should output: Python 3.10.x or higher
```

If you have Python 3.9 or lower, you'll need to upgrade or install Python 3.10+

## Installation

### Option 1: Using the Run Script (Recommended)

```bash
# Make the script executable
chmod +x run.sh

# Run the application
./run.sh
```

The script will automatically:
- Create a virtual environment if it doesn't exist
- Install all dependencies
- Initialize submodules
- Start the development server

### Option 2: Manual Setup

```bash
# Check Python version (must be 3.10+)
python3 --version

# Initialize the reflex submodule
git submodule update --init --recursive

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install Reflex from submodule (NOT from PyPI!)
pip install -e ./reflex

# Install other dependencies
pip install -r requirements.txt

# Initialize Reflex app
reflex init

# Run the application
reflex run
```

## Usage Guide

### 1. Access the Application

Once the server is running, the script will display access URLs:
```
Local:    http://127.0.0.1:3000
Network:  http://<your-ip>:3000
```

You can access from:
- **Same machine**: Use the Local URL
- **Other devices on network**: Use the Network URL (e.g., http://192.168.1.100:3000)

### 2. Integration Workflow

#### Step 1: View Statistics Dashboard
- The top section shows real-time statistics:
  - Total Records synced
  - Successful syncs
  - Failed syncs
  - Active data sources

#### Step 2: Select a Data Source
Choose from 6 available sources:
- **📄 CSV File**: Import from CSV files
- **🔗 JSON API**: Connect to JSON endpoints
- **💾 Database**: Direct database connections
- **🌐 REST API**: Generic REST API integration
- **☁️ Salesforce**: Salesforce CRM connector
- **🔔 Webhook**: Real-time webhook receiver

#### Step 3: Connect to Source
1. Click "1. Connect to Source"
2. Watch the real-time progress bar
3. View connection status and record count
4. Preview source data in the table below

#### Step 4: Auto-Map Fields
1. Click "2. Auto-Map Fields"
2. Review the intelligent field mappings
3. See how source fields map to NetSuite fields:
   - Customer Name
   - Email
   - Phone
   - Address
   - Account ID

#### Step 5: Sync to NetSuite
1. Click "3. Sync to NetSuite"
2. Monitor real-time sync progress
3. View individual record status (success/error)
4. Check the Integration Logs for activity history

#### Step 6: Monitor Results
- **Synced Records**: View all records with status badges
- **Integration Logs**: Timestamped activity log
- **Statistics**: Updated totals and metrics

### 3. Reset and Try Another Source
- Click the "Reset" button to clear the current integration
- Select a different data source to see how field mapping adapts
- Each source has unique field names demonstrating intelligent mapping

## Features Demonstrated

### 🔄 Multi-Source Integration
- Different data structures for each source type
- Unique field naming conventions
- Realistic sample data

### 🧠 Intelligent Field Mapping
- Pattern-based field detection
- Automatic mapping to NetSuite standards
- Visual representation of mappings

### 📊 Real-Time Progress
- Connection progress tracking
- Sync progress with percentage
- Live status updates

### ❌ Error Handling
- Simulated 90% success rate
- Detailed error messages
- Visual error indicators

### 📈 Analytics & Monitoring
- Integration statistics dashboard
- Timestamped activity logs
- Success/failure tracking

## Sample Data Sources

### CSV File
```
id, name, email, phone, location
1, "Acme Corp", "contact@acme.com", "+1-555-0101", "New York"
```

### JSON API
```json
{
  "customer_id": "JSON001",
  "company": "DataFlow Systems",
  "contact_email": "admin@dataflow.io",
  "tel": "+1-555-0201",
  "city": "Boston"
}
```

### Database
```sql
cust_id, cust_name, email_address, phone_number, region
DB100, "Enterprise Analytics", "sales@enterprise.com", "+1-555-0301", "Chicago"
```

## Architecture

### Technology Stack
- **Framework**: Reflex (Python full-stack framework)
- **Language**: Python 3.10+
- **UI**: Radix UI components via Reflex
- **State Management**: Reflex reactive state
- **Styling**: TailwindCSS v4

### Project Structure
```
proto-ddf/
├── proto_ddf_app/
│   ├── __init__.py
│   └── proto_ddf_app.py    # Main application
├── assets/
│   └── favicon.ico
├── rxconfig.py              # Reflex configuration
├── requirements.txt         # Dependencies
├── run.sh                   # Run script
├── demo.py                  # Feature demo
├── README.md                # Full documentation
└── QUICKSTART.md           # This file
```

## Customization

### Adding New Data Sources

To add a new data source, update `proto_ddf_app.py`:

```python
# 1. Add to SourceType enum
class SourceType(str, Enum):
    # ... existing sources ...
    NEW_SOURCE = "New Source"

# 2. Add sample data
sample_data: Dict[str, List[Dict]] = {
    # ... existing data ...
    SourceType.NEW_SOURCE: [
        {"field1": "value1", "field2": "value2"}
    ]
}

# 3. Add source card to UI
source_card(SourceType.NEW_SOURCE, "Description", "🎯")
```

### Customizing Field Mapping

Modify the `auto_map_fields()` method in the `State` class:

```python
mapping_patterns = {
    "new_pattern": ["NetSuite Field", "source_field_variant1", "source_field_variant2"],
    # ... existing patterns ...
}
```

## Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or edit rxconfig.py to change ports:
# Change frontend_port=3000 to another port
# Change backend_port=8000 to another port
```

### Cannot Access from Network
```bash
# Check firewall settings - ports 3000 and 8000 must be open

# On macOS:
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)

# On Linux with ufw:
sudo ufw allow 3000
sudo ufw allow 8000
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Submodule Issues
```bash
# Update submodules
git submodule update --init --recursive
```

## Development

### Running in Development Mode
```bash
reflex run --loglevel debug
```

### Exporting for Production
```bash
reflex export
```

### Running Tests
```bash
python3 demo.py  # Feature demo
python3 -m pytest  # If tests are added
```

## Deployment Options

### Reflex Hosting
```bash
reflex deploy
```

### Docker
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["reflex", "run", "--env", "prod"]
```

### Traditional Hosting
```bash
reflex export
# Deploy the .web/_static folder
```

## Support & Resources

- **Reflex Documentation**: https://reflex.dev/docs/
- **GitHub**: https://github.com/ddf-otsm/proto-ddf
- **Demo Script**: Run `python3 demo.py` for feature overview

## Next Steps

1. ✅ Run the application: `./run.sh`
2. ✅ Try all 6 data sources
3. ✅ Explore field mapping for each source
4. ✅ Monitor sync statistics and logs
5. ✅ Toggle dark/light mode
6. 🚀 Customize for your needs

---

**Happy Integrating! 🔄**

For more detailed information, see [README.md](README.md)
