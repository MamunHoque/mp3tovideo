"""
Main entry point for Video Story Generator application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()




