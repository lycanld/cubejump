import sys, os, json, zipfile, requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


UPDATE_INFO_URL = "lycanld.github.io/cubejump/latest.txt"  # URL to version + zip link
CURRENT_VERSION_FILE = "currentver.json"


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        with requests.get(self.url, stream=True) as r:
            total = int(r.headers.get('content-length', 0))
            with open(self.save_path, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int((downloaded / total) * 100)
                        self.progress.emit(percent)
        self.finished.emit()


class UpdaterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CubeJump Updater")
        self.setFixedSize(300, 150)

        self.layout = QVBoxLayout()
        self.label = QLabel("Checking for updates...")
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setValue(0)
        self.progress.hide()
        self.button = QPushButton("Update Now")
        self.button.clicked.connect(self.start_update)
        self.button.setEnabled(False)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        self.latest_version = None
        self.download_url = None
        self.download_path = "update_package.zip"
        self.load_version_info()

    def load_version_info(self):
        try:
            r = requests.get(UPDATE_INFO_URL)
            lines = r.text.strip().split("\n")
            self.latest_version = lines[0].strip()
            self.download_url = lines[1].strip()

            with open(CURRENT_VERSION_FILE, 'r') as f:
                current = json.load(f)["version"]

            if self.latest_version != current:
                self.label.setText(f"Update available: {self.latest_version}")
                self.button.setEnabled(True)
            else:
                self.label.setText("You're already up to date.")
        except Exception as e:
            self.label.setText("Error checking update.")
            print(e)

    def start_update(self):
        self.progress.show()
        self.button.setEnabled(False)
        self.label.setText("Downloading...")
        self.thread = DownloadThread(self.download_url, self.download_path)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.extract_update)
        self.thread.start()

    def extract_update(self):
        try:
            with zipfile.ZipFile(self.download_path, 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())
            os.remove(self.download_path)

            with open(CURRENT_VERSION_FILE, 'w') as f:
                json.dump({"version": self.latest_version}, f)

            QMessageBox.information(self, "Update Complete", "Update installed successfully!")
            self.label.setText("Update complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to extract update:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = UpdaterWindow()
    win.show()
    sys.exit(app.exec_())
