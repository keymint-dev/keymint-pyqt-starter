import sys
import os
from dotenv import load_dotenv
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QDialog, QMainWindow, QLabel
from license_manager import is_activated, get_stored_key, activate_license, check_stored_offline_license
from activation_dialog import ActivationDialog

load_dotenv()


class MainWindow(QMainWindow):
    def __init__(self, offline_expires_at=None):
        super().__init__()
        self.setWindowTitle("PyQt License Starter")
        self.setMinimumSize(800, 600)
        text = "License validated. Replace this with your app."
        if offline_expires_at:
            text += f"\nOffline license, valid until {offline_expires_at.astimezone():%Y-%m-%d}"
        label = QLabel(text, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
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

    offline = check_stored_offline_license()
    if offline and offline["success"]:
        window = MainWindow(offline["license"].expires_at)
        window.show()
        sys.exit(app.exec())
        return

    dialog = ActivationDialog(message=offline["message"] if offline else "")
    if dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow(dialog.offline_expires_at)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
