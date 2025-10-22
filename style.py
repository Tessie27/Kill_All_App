"""
Styles for the App Closer - Modern Theme
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
    
    /* Title Bar - Keep default style but change color */
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
        padding: 5px;
    }
    
    /* Content Sections */
    QFrame#content {
        background-color: #252526;
        border-radius: 6px;
        border: 1px solid #3E3E42;
        margin: 8px;
        padding: 8px;
    }
    
    /* Labels */
    QLabel {
        color: #CCCCCC;
        padding: 4px;
        background-color: transparent;
    }
    
    QLabel#title {
        font-size: 13pt;
        font-weight: bold;
        color: #569CD6;
        padding: 6px;
        background-color: transparent;
    }
    
    QLabel#status {
        font-size: 9pt;
        color: #969696;
        padding: 3px;
        background-color: transparent;
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
        padding: 6px;
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
    
    /* Modern Scrollbar Design */
    QListWidget::vertical-scrollbar:vertical {
        border: none;
        background: transparent;
        width: 14px;
        margin: 0px;
        border-radius: 0px;
    }
    
    QListWidget::vertical-scrollbar::handle:vertical {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #565656, stop:0.5 #646464, stop:1 #565656
        );
        border: 1px solid #404040;
        border-radius: 7px;
        min-height: 30px;
        margin: 3px 2px 3px 2px;
    }
    
    QListWidget::vertical-scrollbar::handle:vertical:hover {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #707070, stop:0.5 #7E7E7E, stop:1 #707070
        );
        border: 1px solid #505050;
    }
    
    QListWidget::vertical-scrollbar::handle:vertical:pressed {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 #569CD6, stop:0.5 #4E94D1, stop:1 #569CD6
        );
        border: 1px solid #3E7CB3;
    }
    
    QListWidget::vertical-scrollbar::add-line:vertical, 
    QListWidget::vertical-scrollbar::sub-line:vertical {
        border: none;
        background: none;
        height: 0px;
        subcontrol-origin: margin;
        subcontrol-position: top;
    }
    
    QListWidget::vertical-scrollbar::add-page:vertical, 
    QListWidget::vertical-scrollbar::sub-page:vertical {
        background: rgba(30, 30, 30, 150);
        border-radius: 0px;
    }
    
    /* Horizontal Scrollbar - Modern Style */
    QListWidget::horizontal-scrollbar:horizontal {
        border: none;
        background: transparent;
        height: 14px;
        margin: 0px;
        border-radius: 0px;
    }
    
    QListWidget::horizontal-scrollbar::handle:horizontal {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #565656, stop:0.5 #646464, stop:1 #565656
        );
        border: 1px solid #404040;
        border-radius: 7px;
        min-width: 30px;
        margin: 2px 3px 2px 3px;
    }
    
    QListWidget::horizontal-scrollbar::handle:horizontal:hover {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #707070, stop:0.5 #7E7E7E, stop:1 #707070
        );
        border: 1px solid #505050;
    }
    
    QListWidget::horizontal-scrollbar::handle:horizontal:pressed {
        background: qlineargradient(
            spread:pad, x1:0, y1:0, x2:0, y2:1,
            stop:0 #569CD6, stop:0.5 #4E94D1, stop:1 #569CD6
        );
        border: 1px solid #3E7CB3;
    }
    
    QListWidget::horizontal-scrollbar::add-line:horizontal, 
    QListWidget::horizontal-scrollbar::sub-line:horizontal {
        border: none;
        background: none;
        width: 0px;
    }
    
    QListWidget::horizontal-scrollbar::add-page:horizontal, 
    QListWidget::horizontal-scrollbar::sub-page:horizontal {
        background: rgba(30, 30, 30, 150);
        border-radius: 0px;
    }
    
    /* Scrollbar Corner */
    QListWidget::corner {
        background: #252526;
        border: none;
    }
    
    /* Buttons */
    QPushButton {
        background-color: #0E639C;
        color: #FFFFFF;
        border: 1px solid #0E639C;
        padding: 6px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 9pt;
        min-width: 70px;
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
        padding: 7px 14px;
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