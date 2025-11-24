"""
Enhanced Styles for the App Closer - Modern Theme
"""

APP_STYLES = """
    /* Main Application Styles */
    QMainWindow {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'Courier New', monospace;
        font-weight: bold;
        font-size: 10pt;
    }
    
    QWidget {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Cascadia Code', 'Cascadia Mono', 'Consolas', 'Courier New', monospace;
        font-weight: bold;
        font-size: 10pt;
    }
    
    /* Title Bar */
    QWidget::title {
        background-color: #252526;
        color: #CCCCCC;
        font-size: 9pt;
    }
    
    /* Header Section */
    QFrame#header {
        background-color: #252526;
        border-radius: 8px;
        border: 1px solid #3E3E42;
        margin: 8px;
        padding: 8px;
    }
    
    /* Content Sections */
    QFrame#content {
        background-color: #252526;
        border-radius: 6px;
        border: 1px solid #3E3E42;
        margin: 4px;
        padding: 8px;
    }
    
    /* Labels */
    QLabel {
        color: #CCCCCC;
        padding: 4px;
        background-color: transparent;
    }
    
    QLabel#title {
        font-size: 14pt;
        font-weight: bold;
        color: #569CD6;
        padding: 6px;
        background-color: transparent;
    }
    
    QLabel#status {
        font-size: 9pt;
        color: #90EE90;
        padding: 3px;
        background-color: transparent;
    }
    
    QLabel#memory {
        font-size: 9pt;
        color: #FFD166;
        padding: 3px;
        background-color: transparent;
    }
    
    QLabel#saved {
        font-size: 9pt;
        color: #90EE90;
        padding: 3px;
        background-color: transparent;
    }
    
    /* Tab Widget */
    QTabWidget::pane {
        border: 1px solid #3E3E42;
        border-radius: 4px;
        background-color: #252526;
    }
    
    QTabWidget::tab-bar {
        alignment: center;
    }
    
    QTabBar::tab {
        background-color: #2D2D30;
        color: #CCCCCC;
        padding: 8px 16px;
        margin: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
        font-weight: bold;
    }
    
    QTabBar::tab:selected {
        background-color: #0E639C;
        color: #FFFFFF;
    }
    
    QTabBar::tab:hover:!selected {
        background-color: #37373D;
    }
    
    /* List Widget */
    QListWidget {
        border: 1px solid #3E3E42;
        border-radius: 4px;
        background-color: #1E1E1E;
        color: #CCCCCC;
        font-size: 9pt;
        outline: none;
        padding: 4px;
    }
    
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #2D2D30;
        background-color: #1E1E1E;
        margin: 1px;
        border-radius: 3px;
    }
    
    QListWidget::item:hover {
        background-color: #2A2D2E;
        border: none;
    }
    
    QListWidget::item:selected {
        background-color: #37373D;
        color: #FFFFFF;
        border: none;
        border-radius: 3px;
    }
    
    /* Group Box */
    QGroupBox {
        color: #569CD6;
        font-weight: bold;
        border: 1px solid #3E3E42;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 8px;
        background-color: #252526;
    }
    
    /* Text Edit */
    QTextEdit {
        background-color: #1E1E1E;
        color: #CCCCCC;
        border: 1px solid #3E3E42;
        border-radius: 4px;
        padding: 4px;
        font-size: 9pt;
    }
    
    /* Checkbox */
    QCheckBox {
        color: #CCCCCC;
        spacing: 8px;
    }
    
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
    
    QCheckBox::indicator:unchecked {
        border: 2px solid #3E3E42;
        background-color: #1E1E1E;
        border-radius: 3px;
    }
    
    QCheckBox::indicator:checked {
        border: 2px solid #0E639C;
        background-color: #0E639C;
        border-radius: 3px;
    }
    
    /* Modern Scrollbar Design */
    QScrollBar:vertical {
        border: none;
        background: #252526;
        width: 14px;
        margin: 0px;
        border-radius: 0px;
    }
    
    QScrollBar::handle:vertical {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #565656, stop:0.5 #646464, stop:1 #565656
        );
        border: 1px solid #404040;
        border-radius: 7px;
        min-height: 30px;
        margin: 3px 2px 3px 2px;
    }
    
    QScrollBar::handle:vertical:hover {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #707070, stop:0.5 #7E7E7E, stop:1 #707070
        );
        border: 1px solid #505050;
    }
    
    QScrollBar::handle:vertical:pressed {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #569CD6, stop:0.5 #4E94D1, stop:1 #569CD6
        );
        border: 1px solid #3E7CB3;
    }
    
    QScrollBar::add-line:vertical, 
    QScrollBar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
    }
    
    QScrollBar::add-page:vertical, 
    QScrollBar::sub-page:vertical {
        background: rgba(30, 30, 30, 150);
    }
    
    /* Horizontal Scrollbar */
    QScrollBar:horizontal {
        border: none;
        background: #252526;
        height: 14px;
        margin: 0px;
        border-radius: 0px;
    }
    
    QScrollBar::handle:horizontal {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #565656, stop:0.5 #646464, stop:1 #565656
        );
        border: 1px solid #404040;
        border-radius: 7px;
        min-width: 30px;
        margin: 2px 3px 2px 3px;
    }
    
    QScrollBar::handle:horizontal:hover {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #707070, stop:0.5 #7E7E7E, stop:1 #707070
        );
        border: 1px solid #505050;
    }
    
    QScrollBar::handle:horizontal:pressed {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #569CD6, stop:0.5 #4E94D1, stop:1 #569CD6
        );
        border: 1px solid #3E7CB3;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0E639C;
        color: #FFFFFF;
        border: 1px solid #0E639C;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 9pt;
        min-width: 80px;
    }
    
    QPushButton:hover {
        background-color: #1177BB;
        color: #FFFFFF;
        border: 1px solid #1177BB;
    }
    
    QPushButton:pressed {
        background-color: #0C547D;
        color: #FFFFFF;
        border: 1px solid #0C547D;
    }
    
    QPushButton:disabled {
        background-color: #424242;
        color: #666666;
        border: 1px solid #424242;
    }
    
    QPushButton#danger {
        background-color: #F44747;
        color: #FFFFFF;
        font-size: 9pt;
        padding: 8px 16px;
        border: 1px solid #F44747;
    }
    
    QPushButton#danger:hover {
        background-color: #FF5C5C;
        color: #FFFFFF;
        border: 1px solid #FF5C5C;
    }
    
    QPushButton#danger:pressed {
        background-color: #D13434;
        color: #FFFFFF;
        border: 1px solid #D13434;
    }
    
    QPushButton#success {
        background-color: #4EC9B0;
        color: #FFFFFF;
        font-size: 9pt;
        padding: 8px 16px;
        border: 1px solid #4EC9B0;
    }
    
    QPushButton#success:hover {
        background-color: #5ED9C0;
        color: #FFFFFF;
        border: 1px solid #5ED9C0;
    }
    
    QPushButton#success:pressed {
        background-color: #3EB9A0;
        color: #FFFFFF;
        border: 1px solid #3EB9A0;
    }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #3E3E42;
        border-radius: 4px;
        text-align: center;
        background-color: #1E1E1E;
        color: #CCCCCC;
        height: 18px;
        font-size: 9pt;
    }
    
    QProgressBar::chunk {
        background-color: #0E639C;
        border-radius: 3px;
        border: none;
    }
    
    /* Message Box Styling */
    QMessageBox {
        background-color: #1E1E1E;
        color: #CCCCCC;
    }
    
    QMessageBox QLabel {
        color: #CCCCCC;
        background-color: transparent;
    }
    
    QMessageBox QPushButton {
        background-color: #0E639C;
        color: #FFFFFF;
        border: 1px solid #0E639C;
        padding: 6px 12px;
        border-radius: 4px;
        min-width: 70px;
    }
    
    QMessageBox QPushButton:hover {
        background-color: #1177BB;
        color: #FFFFFF;
    }
"""
