# Proto DDF - Data Dashboard Prototype

A prototype data visualization dashboard built with [Reflex](https://reflex.dev/), a Python framework for building full-stack web applications.

## 🚀 Features

- **Interactive Dashboard**: Real-time data visualization
- **Data Generation**: Simulate data processing with loading states
- **Interactive Components**: Counter with increment/reset functionality
- **Responsive Design**: Modern UI with cards and grids
- **Dark/Light Mode**: Toggle between color modes

## 🏗️ Project Structure

```
proto-ddf/
├── proto_ddf_app/           # Main application code
│   └── proto_ddf_app.py     # Dashboard application
├── reflex/                  # Reflex framework (submodule)
├── venv/                    # Python virtual environment
├── .web/                    # Generated web assets
└── requirements.txt         # Python dependencies
```

## 🛠️ Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ddf-otsm/proto-ddf.git
   cd proto-ddf
   ```

2. **Initialize submodules**:
   ```bash
   git submodule update --init --recursive
   ```

3. **Set up virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Running the Application

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the development server**:
   ```bash
   reflex run
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

## 📊 Dashboard Features

### Interactive Counter
- Click "Increment" to increase the counter
- Click "Reset" to reset to zero
- Real-time state updates

### Data Generation
- Click "Generate Sample Data" to create random data points
- Loading state with progress indication
- Generates 10 data points with random values and categories

### Data Visualization
- **Data Cards**: Display generated data points in a grid layout
- **Color Coding**: Green for values > 50, orange for lower values
- **Quarterly Chart**: Progress bars showing quarterly data

## 🎨 UI Components

- **Responsive Grid**: 5-column layout for data cards
- **Modern Cards**: Clean card-based design
- **Progress Bars**: Visual representation of data
- **Color Modes**: Dark/light theme toggle
- **Loading States**: User feedback during data generation

## 🔧 Development

The application is built using:
- **Reflex**: Python web framework
- **Python 3.10+**: Required for Reflex
- **Type Hints**: Full type annotation support
- **State Management**: Reactive state with Reflex

## 📝 Key Files

- `proto_ddf_app/proto_ddf_app.py`: Main application logic
- `rxconfig.py`: Reflex configuration
- `requirements.txt`: Python dependencies
- `.gitmodules`: Submodule configuration

## 🌐 Deployment

The application can be deployed using:
- **Reflex Hosting**: `reflex deploy`
- **Docker**: Container deployment
- **Traditional hosting**: Static file serving

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is part of the DDF (Data-Driven Framework) ecosystem and follows the same licensing terms as the parent project.

## 🔗 Links

- [Reflex Documentation](https://reflex.dev/docs/)
- [GitHub Repository](https://github.com/ddf-otsm/proto-ddf)
- [Reflex Framework](https://github.com/reflex-dev/reflex)
