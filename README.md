# App Closer - Application Manager

A modern, user-friendly desktop application built with PyQt5 that helps you manage and close running applications on Windows systems. Features a dark theme with VS Code-inspired styling and safe process management.

## Features

### 🚀 Core Functionality
- **Smart Process Detection**: Automatically identifies user applications while excluding critical system processes
- **Safe Application Closing**: Terminates applications with proper process handling
- **Memory Usage Display**: Shows memory consumption for each running application
- **Multi-Selection Support**: Select and close multiple applications at once
- **Bulk Operations**: Close all non-essential applications with one click

### 🎨 User Interface
- **Modern Dark Theme**: VS Code-inspired color scheme
- **Responsive Design**: Clean and intuitive layout
- **Real-time Updates**: Live application list with current memory usage
- **Progress Indicators**: Visual feedback for long operations
- **Professional Styling**: Custom scrollbars, buttons, and animations

### 🔧 Technical Features
- **Automatic PyCache Cleanup**: Cleans Python cache directories on application close
- **Safe Process Filtering**: Protects critical system processes from accidental closure
- **Error Handling**: Robust error management with user-friendly messages
- **Performance Optimized**: Efficient process enumeration and memory management

## Installation

### Prerequisites

- **Python 3.6 or higher**
- **Windows Operating System** (tested on Windows 10/11)

### Required Packages

Install the required dependencies using pip:

```bash
pip install pyqt5 psutil pywin32
```

### Manual Installation

1. **Clone or download** the project files:
   - `main.py` - Main application logic
   - `style.py` - Application styling and themes

2. **Ensure all dependencies** are installed:
   ```bash
   pip install pyqt5 psutil pywin32
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Starting the Application

```bash
python main.py
```

The application will automatically scan for running user applications and display them in a sorted list by memory usage.

### Basic Operations

1. **Refresh List**: Click the "Refresh" button to update the application list
2. **Select Applications**: Click on individual applications or use Ctrl+Click for multiple selection
3. **Close Selected**: Click "Close Selected" to terminate chosen applications
4. **Close All**: Click "Close All" to close all non-system applications

### Safety Features

- **Protected System Processes**: Critical Windows processes are automatically excluded
- **Confirmation Dialogs**: All close operations require user confirmation
- **Memory Protection**: System processes and services are never shown or closed

## Protected System Processes

The application automatically protects these critical system processes:

- `explorer.exe` - Windows Explorer
- `csrss.exe` - Client Server Runtime Process
- `winlogon.exe` - Windows Logon Application
- `services.exe` - Service Control Manager
- `lsass.exe` - Local Security Authority Process
- `svchost.exe` - Service Host Process
- `system` - System Process
- `system idle process` - System Idle Process
- `wininit.exe` - Windows Initialization Process
- `dwm.exe` - Desktop Window Manager
- `taskhostw.exe` - Host Process for Windows Tasks
- `ctfmon.exe` - Alternative Input Services

## Technical Details

### Architecture

- **Frontend**: PyQt5 with custom QSS styling
- **Process Management**: psutil for process enumeration and management
- **Windows Integration**: pywin32 for window management and process details
- **Memory Management**: Efficient garbage collection and resource cleanup

### Process Detection Logic

1. **Enumeration**: Iterates through all running processes
2. **System Filtering**: Excludes processes from Windows system directories
3. **GUI Detection**: Filters processes without visible windows
4. **User Filtering**: Excludes system user processes (SYSTEM, LOCAL SERVICE, etc.)
5. **Memory Calculation**: Calculates and displays memory usage in MB

### Safety Mechanisms

- Multiple validation layers for process identification
- Graceful termination attempts before force killing
- Comprehensive error handling and user feedback
- Protected process whitelist

## PyCache Cleanup

The application includes an automatic cleanup feature that:

- **Removes** all `__pycache__` directories in the project folder
- **Deletes** individual `.pyc` cache files
- **Runs automatically** when the application closes
- **Provides console feedback** about cleanup operations

## Troubleshooting

### Common Issues

1. **"Access Denied" errors**
   - Run the application as Administrator
   - Some system processes require elevated privileges

2. **Missing applications in list**
   - Applications without visible windows are filtered out
   - System processes are intentionally excluded for safety

3. **Application fails to close**
   - Some applications may resist termination
   - The app attempts both graceful and forced termination
   - Administrative privileges may be required for some apps

### Performance Tips

- The initial scan may take a few seconds on systems with many processes
- Use the refresh button sparingly to avoid unnecessary system scans
- Closing many applications simultaneously may temporarily impact system performance

## Development

### File Structure

```
app-closer/
├── main.py          # Main application logic
├── style.py         # UI styles and themes
└── README.md        # This file
```

### Code Style

- PEP 8 compliance
- Type hints where applicable
- Comprehensive error handling
- Modular design for easy maintenance

### Building from Source

No special build process required. The application runs directly from Python source.

## License

This project is provided for educational and personal use. Please ensure you have the right to manage processes on systems where this application is deployed.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## Security Notes

- This application terminates processes - use with caution
- Always save your work before closing applications
- The application is designed to be safe but cannot prevent data loss in unsaved applications
- Run with appropriate permissions for your use case

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify Python version compatibility
4. Check Windows system requirements

---

**Note**: This tool is designed for technical users who understand the implications of process termination. Use responsibly and always ensure important work is saved before closing applications.