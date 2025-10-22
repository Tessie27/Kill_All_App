import sys
import os
import psutil
import win32gui
import win32process
import win32con
import shutil
import time
import threading
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QMessageBox, QListWidgetItem, QHBoxLayout, QLabel, QProgressBar,
    QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QStyle

# Import styles
from style import APP_STYLES


class AppCloser(QWidget):
    update_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        # System processes that should NEVER be closed
        self.critical_system_processes = {
            "explorer.exe", "csrss.exe", "winlogon.exe", "services.exe",
            "lsass.exe", "svchost.exe", "system", "system idle process",
            "wininit.exe", "dwm.exe", "taskhostw.exe", "ctfmon.exe"
        }
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_user_apps()
        
    def setup_ui(self):
        self.setWindowTitle("App Closer")
        self.setGeometry(300, 300, 480, 420)
        self.setMinimumSize(440, 380)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Header
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_layout = QVBoxLayout(header_frame)
        
        app_title_label = QLabel("Application Manager")
        app_title_label.setObjectName("title")
        app_title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont('Cascadia Code', 11, QFont.Bold)
        app_title_label.setFont(title_font)
        
        self.status_label = QLabel("Scanning for applications...")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont('Cascadia Code', 9, QFont.Bold)
        self.status_label.setFont(status_font)
        
        header_layout.addWidget(app_title_label)
        header_layout.addWidget(self.status_label)
        
        # Apps list section
        list_frame = QFrame()
        list_frame.setObjectName("content")
        list_layout = QVBoxLayout(list_frame)
        
        list_info_layout = QHBoxLayout()
        list_label = QLabel("Running Applications:")
        list_label.setStyleSheet("color: #569CD6; font-weight: bold; font-size: 9pt;")
        
        self.app_count_label = QLabel("0 apps")
        self.app_count_label.setStyleSheet("color: #969696; font-size: 9pt;")
        
        list_info_layout.addWidget(list_label)
        list_info_layout.addStretch()
        list_info_layout.addWidget(self.app_count_label)
        
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        
        list_layout.addLayout(list_info_layout)
        list_layout.addWidget(self.list_widget)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)
        
        # Buttons section
        buttons_frame = QFrame()
        buttons_frame.setObjectName("content")
        button_layout = QHBoxLayout(buttons_frame)
        
        self.refresh_btn = QPushButton("Refresh")
        self.close_selected_btn = QPushButton("Close Selected")
        self.close_all_btn = QPushButton("Close All")
        
        # Set button icons with smaller size
        self.refresh_btn.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.close_selected_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.close_all_btn.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))
        
        # Set button fonts
        button_font = QFont('Cascadia Code', 9, QFont.Bold)
        self.refresh_btn.setFont(button_font)
        self.close_selected_btn.setFont(button_font)
        self.close_all_btn.setFont(button_font)
        
        # Style buttons
        self.close_selected_btn.setObjectName("danger")
        self.close_all_btn.setObjectName("danger")
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_selected_btn)
        button_layout.addWidget(self.close_all_btn)
        
        # Assemble main layout
        main_layout.addWidget(header_frame)
        main_layout.addWidget(list_frame)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(buttons_frame)
        
        self.setLayout(main_layout)
        
    def setup_styles(self):
        """Apply styles and set title bar color"""
        self.setStyleSheet(APP_STYLES)
        
        # Set application-wide font
        app_font = QFont('Cascadia Code', 9, QFont.Bold)
        QApplication.setFont(app_font)
        
    def setup_connections(self):
        self.refresh_btn.clicked.connect(self.load_user_apps)
        self.close_selected_btn.clicked.connect(self.close_selected_apps)
        self.close_all_btn.clicked.connect(self.close_all_apps)
        self.update_signal.connect(self.on_update_complete)
        self.list_widget.itemSelectionChanged.connect(self.update_button_states)
    
    def get_user_apps(self):
        """Get all user applications that can be safely closed"""
        user_apps = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username']):
            try:
                # Skip system processes
                if proc.info['name'].lower() in self.critical_system_processes:
                    continue
                
                # Skip processes without GUI (no windows)
                if not self.has_visible_windows(proc.info['pid']):
                    continue
                
                # Skip Windows system processes
                if self.is_windows_system_process(proc):
                    continue
                
                # Get memory usage
                memory_mb = proc.memory_info().rss / 1024 / 1024
                
                user_apps.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory': memory_mb,
                    'process': proc
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return user_apps
    
    def has_visible_windows(self, pid):
        """Check if process has visible windows"""
        has_visible = False
        
        def enum_window_callback(hwnd, _):
            nonlocal has_visible
            if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                try:
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:
                        has_visible = True
                except:
                    pass
        
        win32gui.EnumWindows(enum_window_callback, None)
        return has_visible
    
    def is_windows_system_process(self, proc):
        """Check if process is a Windows system process"""
        try:
            exe_path = proc.info['exe'] or ""
            username = proc.info['username'] or ""
            
            # Check if it's in Windows system directories
            system_dirs = [
                os.environ.get('SystemRoot', 'C:\\Windows'),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32'),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SysWOW64'),
            ]
            
            if any(exe_path.lower().startswith(dir.lower()) for dir in system_dirs):
                return True
                
            # Check if it's a system user
            if 'SYSTEM' in username or 'LOCAL SERVICE' in username or 'NETWORK SERVICE' in username:
                return True
                
        except:
            pass
            
        return False

    def load_user_apps(self):
        """Load user applications"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Scanning for applications...")
        self.refresh_btn.setEnabled(False)
        
        QTimer.singleShot(100, self._load_apps_async)
        
    def _load_apps_async(self):
        """Async apps loading"""
        try:
            self.user_apps = self.get_user_apps()
            self.update_signal.emit()
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.progress_bar.setVisible(False)
            self.refresh_btn.setEnabled(True)
            
    def on_update_complete(self):
        """Update UI after apps loading"""
        self.populate_list()
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        
        app_count = len(self.user_apps)
        self.status_label.setText(f"Ready - {app_count} applications found")
        self.app_count_label.setText(f"{app_count} app(s)")
        self.update_button_states()
        
    def populate_list(self):
        self.list_widget.clear()
        
        # Sort by memory usage
        sorted_apps = sorted(self.user_apps, key=lambda x: x['memory'], reverse=True)
        
        for app in sorted_apps:
            # Format the display text nicely
            display_name = app['name'].replace('.exe', '')
            item_text = f"{display_name} - {app['memory']:.1f} MB"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, app)
            self.list_widget.addItem(item)
            
    def update_button_states(self):
        """Update button states based on selection"""
        selected_count = len(self.list_widget.selectedItems())
        total_count = self.list_widget.count()
        
        self.close_selected_btn.setEnabled(selected_count > 0)
        self.close_all_btn.setEnabled(total_count > 0)
        
        # Update button text to show count
        if selected_count > 0:
            self.close_selected_btn.setText(f"Close Selected ({selected_count})")
        else:
            self.close_selected_btn.setText("Close Selected")
            
    def get_selected_apps(self):
        """Get list of selected applications"""
        selected_apps = []
        for item in self.list_widget.selectedItems():
            app_data = item.data(Qt.UserRole)
            selected_apps.append(app_data)
        return selected_apps

    def close_selected_apps(self):
        """Close selected applications"""
        selected_apps = self.get_selected_apps()
        if not selected_apps:
            QMessageBox.information(self, "No Selection", "No applications selected.")
            return

        confirm = QMessageBox.question(
            self, "Close Selected", 
            f"Close {len(selected_apps)} selected application(s)?\n\n"
            "Unsaved work may be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.close_applications(selected_apps)

    def close_all_apps(self):
        """Close all user applications"""
        if not self.user_apps:
            QMessageBox.information(self, "No Apps", "No applications found to close.")
            return

        confirm = QMessageBox.question(
            self, "Close All Apps", 
            f"Close ALL {len(self.user_apps)} applications?\n\n"
            "This will close all your open programs!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.close_applications(self.user_apps)

    def close_applications(self, apps_to_close):
        """Close applications with progress"""
        success_count = 0
        fail_count = 0
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(apps_to_close))
        
        for i, app in enumerate(apps_to_close):
            self.progress_bar.setValue(i)
            self.status_label.setText(f"Closing {app['name']}...")
            QApplication.processEvents()  # Keep UI responsive
            
            try:
                # Try to terminate the process
                app['process'].terminate()
                success_count += 1
            except:
                try:
                    # Force kill if terminate fails
                    app['process'].kill()
                    success_count += 1
                except:
                    fail_count += 1
        
        self.progress_bar.setVisible(False)
        
        # Show results
        if fail_count == 0:
            message = f"Successfully closed {success_count} application(s)!"
        else:
            message = f"Closed {success_count} app(s), {fail_count} failed to close."
            
        QMessageBox.information(self, "Done", message)
        
        # Refresh list
        QTimer.singleShot(1000, self.load_user_apps)

    def clear_pycache(self):
        """Clear all __pycache__ directories in the current directory and subdirectories"""
        try:
            current_dir = Path.cwd()
            pycache_dirs = list(current_dir.rglob("__pycache__"))
            
            if not pycache_dirs:
                print("No __pycache__ directories found to clean.")
                return
                
            cleared_count = 0
            for pycache_dir in pycache_dirs:
                try:
                    # Check if directory exists and is a pycache directory
                    if pycache_dir.is_dir() and pycache_dir.name == "__pycache__":
                        shutil.rmtree(pycache_dir, ignore_errors=True)
                        print(f"Cleared: {pycache_dir}")
                        cleared_count += 1
                except Exception as e:
                    print(f"Error clearing {pycache_dir}: {e}")
                    
            print(f"Successfully cleared {cleared_count} __pycache__ directories")
            
            # Also clean individual .pyc files that might be outside pycache
            pyc_files = list(current_dir.rglob("*.pyc"))
            for pyc_file in pyc_files:
                try:
                    pyc_file.unlink()
                    print(f"Cleared: {pyc_file}")
                    cleared_count += 1
                except Exception as e:
                    print(f"Error clearing {pyc_file}: {e}")
                    
        except Exception as e:
            print(f"Error during pycache cleanup: {e}")

    def closeEvent(self, event):
        """Handle application close - clear pycache before closing"""
        print("Application closing - starting pycache cleanup...")
        
        # Run cleanup in a separate thread to avoid blocking the UI
        cleanup_thread = threading.Thread(target=self.clear_pycache)
        cleanup_thread.daemon = True
        cleanup_thread.start()
        
        # Wait a moment for the cleanup to start
        cleanup_thread.join(timeout=2.0)
        
        event.accept()


def main():
    """Main function to handle application startup and cleanup"""
    app = QApplication(sys.argv)
    app.setApplicationName("App Closer")
    app.setApplicationVersion("1.0")
    
    # Use default system icon
    app_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    app.setWindowIcon(app_icon)
    
    window = AppCloser()
    window.show()
    
    try:
        result = app.exec_()
    finally:
        # Ensure cleanup runs after app closes
        print("Performing final pycache cleanup...")
        window.clear_pycache()
    
    return result


if __name__ == "__main__":
    sys.exit(main())