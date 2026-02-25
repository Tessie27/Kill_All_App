import sys
import os
import logging
import traceback
import psutil
import win32gui
import win32process
import win32con
import shutil
import time
import threading
import json
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton,
    QMessageBox, QListWidgetItem, QHBoxLayout, QLabel, QProgressBar,
    QFrame, QSystemTrayIcon, QMenu, QAction, QCheckBox, QGroupBox,
    QSplitter, QTabWidget, QTextEdit, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor
from PyQt5.QtWidgets import QStyle

# Import styles
from style import APP_STYLES

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logger = logging.getLogger("AppCloser")
logger.setLevel(logging.DEBUG)

# Console handler (always active – useful when running from terminal)
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setLevel(logging.DEBUG)
_console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(_console_handler)


class QtLogHandler(logging.Handler):
    """A logging.Handler that appends colour-coded HTML lines to a QTextEdit."""

    LEVEL_COLORS = {
        logging.DEBUG:    "#888888",
        logging.INFO:     "#CCCCCC",
        logging.WARNING:  "#FFD166",
        logging.ERROR:    "#FF6B6B",
        logging.CRITICAL: "#FF3333",
    }

    def __init__(self, text_edit: QTextEdit):
        super().__init__()
        self._widget = text_edit
        self.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s",
                                            datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            color = self.LEVEL_COLORS.get(record.levelno, "#CCCCCC")
            # Escape HTML special chars
            msg = (msg.replace("&", "&amp;")
                      .replace("<", "&lt;")
                      .replace(">", "&gt;"))
            html = f'<span style="color:{color}; font-family:\'Cascadia Code\',monospace; font-size:9pt;">{msg}</span>'
            self._widget.append(html)
            # Auto-scroll to bottom
            cursor = self._widget.textCursor()
            cursor.movePosition(QTextCursor.End)
            self._widget.setTextCursor(cursor)
        except Exception:
            self.handleError(record)


# ---------------------------------------------------------------------------
# Main Application Widget
# ---------------------------------------------------------------------------

class AppCloser(QWidget):
    update_signal = pyqtSignal()
    memory_updated = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        # System processes that should NEVER be closed
        self.critical_system_processes = {
            "explorer.exe", "csrss.exe", "winlogon.exe", "services.exe",
            "lsass.exe", "svchost.exe", "system", "system idle process",
            "wininit.exe", "dwm.exe", "taskhostw.exe", "ctfmon.exe",
            "fontdrvhost.exe", "sihost.exe", "runtimebroker.exe"
        }

        self.settings_file = Path("app_closer_settings.json")
        self.whitelist = set()
        self.auto_refresh = True
        self.refresh_interval = 5000  # 5 seconds
        self.total_memory_saved = 0.0
        self._refreshing = False  # Refresh-lock to prevent concurrent scans

        self.load_settings()
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_tray_icon()
        self.load_user_apps()
        self.start_auto_refresh()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def setup_ui(self):
        self.setWindowTitle("App Closer - Advanced Application Manager")
        self.setGeometry(300, 300, 900, 650)
        self.setMinimumSize(700, 500)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        # Header with stats
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_layout = QVBoxLayout(header_frame)

        app_title_label = QLabel("Advanced Application Manager")
        app_title_label.setObjectName("title")
        app_title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont('Cascadia Code', 12, QFont.Bold)
        app_title_label.setFont(title_font)

        stats_layout = QHBoxLayout()

        self.status_label = QLabel("Scanning for applications...")
        self.status_label.setObjectName("status")
        status_font = QFont('Cascadia Code', 9, QFont.Bold)
        self.status_label.setFont(status_font)

        self.memory_label = QLabel("Total Memory: 0 MB")
        self.memory_label.setObjectName("memory")
        self.memory_label.setFont(status_font)

        self.saved_label = QLabel("Memory Saved: 0 MB")
        self.saved_label.setObjectName("saved")
        self.saved_label.setFont(status_font)

        stats_layout.addWidget(self.status_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.memory_label)
        stats_layout.addWidget(self.saved_label)

        header_layout.addWidget(app_title_label)
        header_layout.addLayout(stats_layout)

        # Tab widget
        self.tab_widget = QTabWidget()

        # ---- Apps tab ----
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)

        list_frame = QFrame()
        list_frame.setObjectName("content")
        list_layout = QVBoxLayout(list_frame)

        list_info_layout = QHBoxLayout()
        list_label = QLabel("Running Applications:")
        list_label.setStyleSheet("color: #569CD6; font-weight: bold; font-size: 10pt;")

        self.app_count_label = QLabel("0 apps")
        self.app_count_label.setStyleSheet("color: #969696; font-size: 9pt;")

        self.auto_refresh_cb = QCheckBox("Auto-refresh (5s)")
        self.auto_refresh_cb.setChecked(self.auto_refresh)
        self.auto_refresh_cb.setStyleSheet("color: #CCCCCC;")

        list_info_layout.addWidget(list_label)
        list_info_layout.addStretch()
        list_info_layout.addWidget(self.auto_refresh_cb)
        list_info_layout.addWidget(self.app_count_label)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)

        list_layout.addLayout(list_info_layout)
        list_layout.addWidget(self.list_widget)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedHeight(16)

        buttons_frame = QFrame()
        buttons_frame.setObjectName("content")
        button_layout = QHBoxLayout(buttons_frame)

        self.refresh_btn = QPushButton("Refresh")
        self.close_selected_btn = QPushButton("Close Selected")
        self.close_all_btn = QPushButton("Close All")
        self.whitelist_btn = QPushButton("Whitelist Selected")

        button_font = QFont('Cascadia Code', 9, QFont.Bold)
        self.refresh_btn.setFont(button_font)
        self.close_selected_btn.setFont(button_font)
        self.close_all_btn.setFont(button_font)
        self.whitelist_btn.setFont(button_font)

        self.close_selected_btn.setObjectName("danger")
        self.close_all_btn.setObjectName("danger")
        self.whitelist_btn.setObjectName("success")

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.whitelist_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_selected_btn)
        button_layout.addWidget(self.close_all_btn)

        apps_layout.addWidget(list_frame)
        apps_layout.addWidget(self.progress_bar)
        apps_layout.addWidget(buttons_frame)

        # ---- Settings tab ----
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        whitelist_group = QGroupBox("Whitelisted Applications")
        whitelist_layout = QVBoxLayout(whitelist_group)

        self.whitelist_list = QListWidget()
        self.whitelist_list.setAlternatingRowColors(True)

        whitelist_buttons_layout = QHBoxLayout()
        self.remove_whitelist_btn = QPushButton("Remove Selected")
        self.clear_whitelist_btn = QPushButton("Clear All")

        whitelist_buttons_layout.addWidget(self.remove_whitelist_btn)
        whitelist_buttons_layout.addStretch()
        whitelist_buttons_layout.addWidget(self.clear_whitelist_btn)

        whitelist_layout.addWidget(self.whitelist_list)
        whitelist_layout.addLayout(whitelist_buttons_layout)

        info_group = QGroupBox("System Information")
        info_layout = QVBoxLayout(info_group)

        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setMaximumHeight(150)

        info_layout.addWidget(self.system_info_text)

        settings_layout.addWidget(whitelist_group)
        settings_layout.addWidget(info_group)
        settings_layout.addStretch()

        # ---- Debug Log tab ----
        debug_tab = QWidget()
        debug_layout = QVBoxLayout(debug_tab)

        debug_label = QLabel("Live Debug Log")
        debug_label.setStyleSheet("color: #569CD6; font-weight: bold; font-size: 10pt;")

        self.debug_log_widget = QTextEdit()
        self.debug_log_widget.setReadOnly(True)
        self.debug_log_widget.setFont(QFont('Cascadia Code', 9))
        self.debug_log_widget.setStyleSheet(
            "background-color: #111111; color: #CCCCCC; border: 1px solid #3E3E42;"
        )

        debug_btn_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("Clear Log")
        self.copy_log_btn = QPushButton("Copy to Clipboard")
        debug_btn_layout.addWidget(self.clear_log_btn)
        debug_btn_layout.addWidget(self.copy_log_btn)
        debug_btn_layout.addStretch()

        debug_layout.addWidget(debug_label)
        debug_layout.addWidget(self.debug_log_widget)
        debug_layout.addLayout(debug_btn_layout)

        # Attach the Qt log handler now that the widget exists
        self._qt_log_handler = QtLogHandler(self.debug_log_widget)
        self._qt_log_handler.setLevel(logging.DEBUG)
        logger.addHandler(self._qt_log_handler)

        # Add all tabs
        self.tab_widget.addTab(apps_tab, "Applications")
        self.tab_widget.addTab(settings_tab, "Settings")
        self.tab_widget.addTab(debug_tab, "Debug Log")

        main_layout.addWidget(header_frame)
        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)

        self.update_system_info()

    def setup_styles(self):
        self.setStyleSheet(APP_STYLES)
        app_font = QFont('Cascadia Code', 9, QFont.Bold)
        QApplication.setFont(app_font)

    def setup_connections(self):
        self.refresh_btn.clicked.connect(self.load_user_apps)
        self.close_selected_btn.clicked.connect(self.close_selected_apps)
        self.close_all_btn.clicked.connect(self.close_all_apps)
        self.whitelist_btn.clicked.connect(self.whitelist_selected)
        self.remove_whitelist_btn.clicked.connect(self.remove_whitelisted)
        self.clear_whitelist_btn.clicked.connect(self.clear_whitelist)
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        self.update_signal.connect(self.on_update_complete)
        self.memory_updated.connect(self.on_memory_updated)
        self.list_widget.itemSelectionChanged.connect(self.update_button_states)
        self.clear_log_btn.clicked.connect(self.debug_log_widget.clear)
        self.copy_log_btn.clicked.connect(self._copy_log_to_clipboard)

    # ------------------------------------------------------------------
    # Debug helpers
    # ------------------------------------------------------------------

    def _copy_log_to_clipboard(self):
        QApplication.clipboard().setText(self.debug_log_widget.toPlainText())

    # ------------------------------------------------------------------
    # Tray icon
    # ------------------------------------------------------------------

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))

        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)

        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def quit_application(self):
        self.save_settings()
        QApplication.quit()

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------

    def load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.whitelist = set(settings.get('whitelist', []))
                    self.auto_refresh = settings.get('auto_refresh', True)
                    self.total_memory_saved = settings.get('total_memory_saved', 0.0)
        except Exception as e:
            logger.error("Error loading settings: %s", e)

    def save_settings(self):
        try:
            settings = {
                'whitelist': list(self.whitelist),
                'auto_refresh': self.auto_refresh,
                'total_memory_saved': self.total_memory_saved,
                'last_saved': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            logger.error("Error saving settings: %s", e)

    # ------------------------------------------------------------------
    # System info
    # ------------------------------------------------------------------

    def update_system_info(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024 ** 3)
            memory_used = memory.used / (1024 ** 3)
            memory_percent = memory.percent
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024 ** 3)
            disk_used = disk.used / (1024 ** 3)
            disk_percent = disk.percent

            info_text = (
                f"CPU Usage: {cpu_percent:.1f}%\n"
                f"Memory: {memory_used:.1f} GB / {memory_total:.1f} GB ({memory_percent:.1f}%)\n"
                f"Disk: {disk_used:.1f} GB / {disk_total:.1f} GB ({disk_percent:.1f}%)\n"
                f"Running Processes: {len(psutil.pids())}"
            )
            self.system_info_text.setText(info_text)
        except Exception as e:
            logger.error("Error getting system info: %s", e)
            self.system_info_text.setText(f"Error getting system info: {e}")

    # ------------------------------------------------------------------
    # App scanning
    # ------------------------------------------------------------------

    def get_user_apps(self):
        """Get all user applications that can be safely closed."""
        user_apps = []
        total_memory = 0.0

        for proc in psutil.process_iter(['pid', 'name', 'exe', 'username', 'memory_info']):
            try:
                proc_name = proc.info['name'].lower()

                if proc_name in self.critical_system_processes:
                    continue
                if proc_name in self.whitelist:
                    continue
                if not self.has_visible_windows(proc.info['pid']):
                    continue
                if self.is_windows_system_process(proc):
                    continue

                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                total_memory += memory_mb
                cpu_percent = proc.cpu_percent()

                user_apps.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'memory': memory_mb,
                    'cpu': cpu_percent,
                    'process': proc
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logger.warning("Unexpected error enumerating process: %s", e)

        self.memory_updated.emit(total_memory)
        return user_apps

    def has_visible_windows(self, pid):
        """Check if process has visible windows."""
        has_visible = False

        def enum_window_callback(hwnd, _):
            nonlocal has_visible
            try:
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:
                        has_visible = True
            except Exception as e:
                logger.debug("Win32 error in window enumeration: %s", e)

        try:
            win32gui.EnumWindows(enum_window_callback, None)
        except Exception as e:
            logger.warning("EnumWindows failed for pid %s: %s", pid, e)

        return has_visible

    def is_windows_system_process(self, proc):
        """Check if process is a Windows system process."""
        try:
            exe_path = proc.info['exe'] or ""
            username = proc.info['username'] or ""

            system_dirs = [
                os.environ.get('SystemRoot', 'C:\\Windows'),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32'),
                os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'SysWOW64'),
            ]

            if any(exe_path.lower().startswith(d.lower()) for d in system_dirs):
                return True

            if any(role in username for role in ('SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE')):
                return True

        except Exception as e:
            logger.debug("Error checking system process: %s", e)

        return False

    # ------------------------------------------------------------------
    # Load / refresh
    # ------------------------------------------------------------------

    def load_user_apps(self):
        """Load user applications (guarded by refresh-lock)."""
        if self._refreshing:
            logger.debug("Refresh already in progress, skipping.")
            return

        self._refreshing = True
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label.setText("Scanning for applications...")
        self.refresh_btn.setEnabled(False)
        logger.info("Scanning for applications...")

        QTimer.singleShot(100, self._load_apps_async)

    def _load_apps_async(self):
        """Run app scan on the event loop (100 ms delay keeps UI snappy)."""
        try:
            self.user_apps = self.get_user_apps()
            self.update_system_info()
            self.update_signal.emit()
        except Exception as e:
            logger.error("Error during app scan: %s\n%s", e, traceback.format_exc())
            self.status_label.setText(f"Scan error: {e}")
            self.progress_bar.setVisible(False)
            self.refresh_btn.setEnabled(True)
            self._refreshing = False

    def on_update_complete(self):
        """Update UI after apps loading."""
        try:
            self.populate_list()
            self.populate_whitelist()
        except Exception as e:
            logger.error("Error populating UI: %s", e)
        finally:
            self.progress_bar.setVisible(False)
            self.refresh_btn.setEnabled(True)
            self._refreshing = False

        app_count = len(getattr(self, 'user_apps', []))
        self.status_label.setText(f"Ready - {app_count} applications found")
        self.app_count_label.setText(f"{app_count} app(s)")
        self.update_button_states()
        logger.info("Scan complete: %d application(s) found.", app_count)

    def on_memory_updated(self, total_memory):
        self.memory_label.setText(f"Total Memory: {total_memory:.0f} MB")
        self.saved_label.setText(f"Memory Saved: {self.total_memory_saved:.0f} MB")

    # ------------------------------------------------------------------
    # List population
    # ------------------------------------------------------------------

    def populate_list(self):
        try:
            self.list_widget.clear()
            sorted_apps = sorted(self.user_apps, key=lambda x: x['memory'], reverse=True)
            for app in sorted_apps:
                display_name = app['name'].replace('.exe', '')
                item_text = f"{display_name} - {app['memory']:.1f} MB - CPU: {app['cpu']:.1f}%"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, app)
                if app['memory'] > 500:
                    item.setForeground(QColor('#FF6B6B'))
                elif app['memory'] > 100:
                    item.setForeground(QColor('#FFD166'))
                self.list_widget.addItem(item)
        except Exception as e:
            logger.error("Error in populate_list: %s", e)

    def populate_whitelist(self):
        try:
            self.whitelist_list.clear()
            for app_name in sorted(self.whitelist):
                item = QListWidgetItem(app_name)
                item.setForeground(QColor('#90EE90'))
                self.whitelist_list.addItem(item)
        except Exception as e:
            logger.error("Error in populate_whitelist: %s", e)

    def update_button_states(self):
        selected_count = len(self.list_widget.selectedItems())
        total_count = self.list_widget.count()

        self.close_selected_btn.setEnabled(selected_count > 0)
        self.close_all_btn.setEnabled(total_count > 0)
        self.whitelist_btn.setEnabled(selected_count > 0)

        if selected_count > 0:
            self.close_selected_btn.setText(f"Close Selected ({selected_count})")
            self.whitelist_btn.setText(f"Whitelist ({selected_count})")
        else:
            self.close_selected_btn.setText("Close Selected")
            self.whitelist_btn.setText("Whitelist Selected")

    def get_selected_apps(self):
        return [item.data(Qt.UserRole) for item in self.list_widget.selectedItems()]

    # ------------------------------------------------------------------
    # Close actions
    # ------------------------------------------------------------------

    def close_selected_apps(self):
        selected_apps = self.get_selected_apps()
        if not selected_apps:
            QMessageBox.information(self, "No Selection", "No applications selected.")
            return

        total_memory = sum(app['memory'] for app in selected_apps)
        confirm = QMessageBox.question(
            self, "Close Selected",
            f"Close {len(selected_apps)} selected application(s)?\n\n"
            f"This will free approximately {total_memory:.1f} MB of memory.\n"
            "Unsaved work may be lost.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.close_applications(selected_apps)

    def close_all_apps(self):
        if not getattr(self, 'user_apps', []):
            QMessageBox.information(self, "No Apps", "No applications found to close.")
            return

        total_memory = sum(app['memory'] for app in self.user_apps)
        confirm = QMessageBox.question(
            self, "Close All Apps",
            f"Close ALL {len(self.user_apps)} applications?\n\n"
            f"This will free approximately {total_memory:.1f} MB of memory.\n"
            "This will close all your open programs!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.close_applications(self.user_apps)

    def close_applications(self, apps_to_close):
        """Close applications with progress tracking and per-process error logging."""
        success_count = 0
        fail_count = 0
        memory_freed = 0.0

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(apps_to_close))

        for i, app in enumerate(apps_to_close):
            self.progress_bar.setValue(i)
            self.status_label.setText(f"Closing {app['name']}...")
            QApplication.processEvents()
            try:
                app['process'].terminate()
                gone, alive = psutil.wait_procs([app['process']], timeout=3)
                if alive:
                    for p in alive:
                        p.kill()
                memory_freed += app['memory']
                success_count += 1
                logger.info("Closed: %s (%.1f MB freed)", app['name'], app['memory'])
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                fail_count += 1
                logger.warning("Could not close %s: %s", app['name'], e)
            except Exception as e:
                fail_count += 1
                logger.error("Unexpected error closing %s: %s\n%s",
                             app['name'], e, traceback.format_exc())

        self.progress_bar.setVisible(False)

        if success_count > 0:
            self.total_memory_saved += memory_freed
            current_total = sum(a['memory'] for a in getattr(self, 'user_apps', []))
            self.memory_updated.emit(current_total)

        if fail_count == 0:
            message = f"Successfully closed {success_count} application(s)! Freed {memory_freed:.1f} MB"
            QMessageBox.information(self, "Done", message)
        else:
            message = (f"Closed {success_count} app(s), {fail_count} failed to close. "
                       f"Freed {memory_freed:.1f} MB\n\nSee the Debug Log tab for details.")
            QMessageBox.warning(self, "Done", message)

        QTimer.singleShot(1000, self.load_user_apps)

    # ------------------------------------------------------------------
    # Whitelist management
    # ------------------------------------------------------------------

    def whitelist_selected(self):
        selected_apps = self.get_selected_apps()
        if not selected_apps:
            return
        for app in selected_apps:
            self.whitelist.add(app['name'].lower())
        self.save_settings()
        self.populate_whitelist()
        logger.info("Added %d app(s) to whitelist.", len(selected_apps))
        QMessageBox.information(self, "Whitelist Updated",
                                f"Added {len(selected_apps)} application(s) to whitelist")

    def remove_whitelisted(self):
        selected_items = self.whitelist_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.whitelist.discard(item.text())
        self.save_settings()
        self.populate_whitelist()
        self.load_user_apps()
        logger.info("Removed %d app(s) from whitelist.", len(selected_items))

    def clear_whitelist(self):
        if not self.whitelist:
            return
        confirm = QMessageBox.question(
            self, "Clear Whitelist",
            "Clear all whitelisted applications?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.whitelist.clear()
            self.save_settings()
            self.populate_whitelist()
            self.load_user_apps()
            logger.info("Whitelist cleared.")

    # ------------------------------------------------------------------
    # Auto-refresh
    # ------------------------------------------------------------------

    def toggle_auto_refresh(self, checked):
        self.auto_refresh = checked
        self.save_settings()
        if checked:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()
        logger.info("Auto-refresh %s.", "enabled" if checked else "disabled")

    def start_auto_refresh(self):
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_user_apps)
        self.refresh_timer.start(self.refresh_interval)

    def stop_auto_refresh(self):
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()

    # ------------------------------------------------------------------
    # Pycache cleanup
    # ------------------------------------------------------------------

    def clear_pycache(self):
        try:
            current_dir = Path.cwd()
            pycache_dirs = list(current_dir.rglob("__pycache__"))
            cleared_count = 0
            for pycache_dir in pycache_dirs:
                try:
                    if pycache_dir.is_dir() and pycache_dir.name == "__pycache__":
                        shutil.rmtree(pycache_dir, ignore_errors=True)
                        cleared_count += 1
                except Exception as e:
                    logger.warning("Error clearing %s: %s", pycache_dir, e)

            pyc_files = list(current_dir.rglob("*.pyc"))
            for pyc_file in pyc_files:
                try:
                    pyc_file.unlink()
                    cleared_count += 1
                except Exception as e:
                    logger.warning("Error removing %s: %s", pyc_file, e)

            logger.info("Cleared %d cache item(s).", cleared_count)
        except Exception as e:
            logger.error("Error during pycache cleanup: %s", e)

    # ------------------------------------------------------------------
    # Window close
    # ------------------------------------------------------------------

    def closeEvent(self, event):
        self.save_settings()
        logger.info("Application closing - starting pycache cleanup...")

        cleanup_thread = threading.Thread(target=self.clear_pycache, daemon=True)
        cleanup_thread.start()

        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def global_exception_hook(exc_type, exc_value, exc_tb):
    """Catch any unhandled exception and route it to the logger."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.critical("Unhandled exception:\n%s", msg)


def main():
    sys.excepthook = global_exception_hook

    app = QApplication(sys.argv)
    app.setApplicationName("App Closer")
    app.setApplicationVersion("2.1")
    app.setQuitOnLastWindowClosed(False)

    app_icon = app.style().standardIcon(QStyle.SP_ComputerIcon)
    app.setWindowIcon(app_icon)

    window = AppCloser()
    window.show()

    try:
        result = app.exec_()
    finally:
        logger.info("Performing final pycache cleanup...")
        window.clear_pycache()
        window.save_settings()

    return result


if __name__ == "__main__":
    sys.exit(main())
