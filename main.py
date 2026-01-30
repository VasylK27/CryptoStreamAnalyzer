import sys
from PySide6.QtWidgets import QApplication
from utils.helpers import load_config
from gui.main_window import MainWindow

def main():
    # 1. Creating an instance of the Qt application
    app = QApplication(sys.argv)

    # 2. Load settings from our config.json
    config = load_config()

    if not config:
        print("Failed to load configuration. Please check the config.json file.")
        sys.exit(1)

    # 3. Creating and displaying the main window
    window = MainWindow(config)
    window.show()

    # 4. Starting the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
