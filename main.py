import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QLabel
from license_manager import is_activated, get_stored_key, activate_license
from activation_dialog import ActivationDialog

load_dotenv()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt License Starter")
        self.setMinimumSize(800, 600)
        label = QLabel("License validated. Replace this with your app.", self)
        label.setAlignment(4)  # Qt.AlignCenter
        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)

    if is_activated():
        stored_key = get_stored_key()
        if stored_key:
            result = activate_license(stored_key)
            if result["success"]:
                window = MainWindow()
                window.show()
                sys.exit(app.exec())
                return

    dialog = ActivationDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
