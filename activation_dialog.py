from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox,
)
from PyQt6.QtCore import Qt
from license_manager import activate_license, get_stored_key


class ActivationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activate License")
        self.setFixedSize(420, 240)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = QVBoxLayout()
        layout.setSpacing(12)

        title = QLabel("Enter your license key to unlock the app")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("KM-XXXX-XXXX-XXXX")
        self.key_input.setMaxLength(64)
        layout.addWidget(self.key_input)

        stored = get_stored_key()
        if stored:
            self.key_input.setText(stored)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.clicked.connect(self._on_activate)
        layout.addWidget(self.activate_btn)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def _on_activate(self):
        key = self.key_input.text().strip()
        if not key:
            self.status_label.setText("Please enter a license key")
            return

        self.activate_btn.setEnabled(False)
        self.status_label.setText("Activating...")

        result = activate_license(key)
        if result["success"]:
            QMessageBox.information(self, "Success", "License activated!")
            self.accept()
        else:
            self.status_label.setText(f"Failed: {result['message']}")
            self.activate_btn.setEnabled(True)
