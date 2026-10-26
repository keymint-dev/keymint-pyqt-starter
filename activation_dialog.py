from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFileDialog,
)
from PyQt6.QtCore import Qt
from license_manager import activate_license, get_stored_key, import_offline_license


class ActivationDialog(QDialog):
    def __init__(self, parent=None, message=""):
        super().__init__(parent)
        self.offline_expires_at = None  # set when an offline license is imported
        self.setWindowTitle("Activate License")
        self.setFixedSize(420, 290)
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

        self.import_btn = QPushButton("Import offline license (.lic)…")
        self.import_btn.clicked.connect(self._on_import)
        layout.addWidget(self.import_btn)

        self.status_label = QLabel(message)
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

    def _on_import(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import offline license", "", "Keymint license (*.lic);;All files (*)"
        )
        if not path:
            return
        self.status_label.setText("")
        result = import_offline_license(path)
        if result["success"]:
            self.offline_expires_at = result["license"].expires_at
            QMessageBox.information(
                self, "Success",
                f"Offline license valid until {self.offline_expires_at.astimezone():%Y-%m-%d}",
            )
            self.accept()
        else:
            self.status_label.setText(result["message"])
