import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

from browser.main_window import MainWindow

def main():
    """
    Entry point for the Searcher Browser.
    Initializes the PyQt application and shows the main window.
    """
    # High DPI scaling is enabled by default in PyQt6, but we can ensure attributes if needed
    
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Application configuration
    app.setApplicationName("Searcher")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SearcherTeam")
    
    # Optional: Set a placeholder style if we weren't doing it manually in MainWindow
    # app.setStyle("Fusion") 
    
    # Create and show the main window
    window = MainWindow()
    
    # In Phase 1 we don't have a logo yet, but this is where it would be loaded:
    # window.setWindowIcon(QIcon("assets/logo/logo.png"))
    
    window.showMaximized()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
