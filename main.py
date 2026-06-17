import sys
from PyQt6.QtWidgets import QApplication
from src.presentation.main_window import MainWindow
from src.presentation.theme import STYLESHEET


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
