import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QProgressBar, QComboBox, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pytube import YouTube
import threading

class Downloader(QThread):
    update_signal = pyqtSignal(int)

    def __init__(self, video_url, download_path, resolution, app):
        super().__init__()
        self.video_url = video_url
        self.download_path = download_path
        self.resolution = resolution
        self.app = app

    def run(self):
        yt = YouTube(self.video_url)
        stream = yt.streams.filter(res=self.resolution).first()

        def download():
            stream.download(output_path=self.download_path)
            self.update_signal.emit(100)

        download_thread = threading.Thread(target=download)
        download_thread.start()

        for i in range(100):
            self.update_signal.emit(i)
            self.msleep(50)
        
        self.update_signal.emit(100)

class YouTubeDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 400, 250)
        self.setWindowTitle('YouTube Downloader')

        layout = QVBoxLayout()

        self.url_label = QLabel('URL Video YouTube:')
        self.url_entry = QLineEdit()
        self.path_label = QLabel('Lokasi Penyimpanan:')
        self.path_button = QPushButton('Pilih Folder')
        self.resolution_label = QLabel('Resolusi:')
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem('360p')
        self.resolution_combo.addItem('720p')
        self.download_button = QPushButton('Unduh Video')
        self.progress_label = QLabel('')
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        layout.addWidget(self.url_label)
        layout.addWidget(self.url_entry)
        layout.addWidget(self.path_label)
        layout.addWidget(self.path_button)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combo)
        layout.addWidget(self.download_button)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.download_button.clicked.connect(self.start_download)
        self.path_button.clicked.connect(self.select_folder)
        
        self.downloader = None

    def start_download(self):
        if self.downloader is None:
            video_url = self.url_entry.text()
            download_path = self.download_path
            resolution = self.resolution_combo.currentText()
            if video_url and download_path:
                self.downloader = Downloader(video_url, download_path, resolution, self)
                self.downloader.update_signal.connect(self.update_progress)
                self.downloader.start()
                self.progress_bar.setVisible(True)
                self.progress_label.setText('')  # Mengosongkan label setelah tombol "Unduh Video" diklik

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_label.setText('Video berhasil diunduh!')
            self.downloader = None

    def select_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        download_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Penyimpanan", options=options)
        if download_path:
            self.download_path = download_path
            self.path_label.setText(f'Lokasi Penyimpanan: {download_path}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = YouTubeDownloaderApp()
    ex.show()
    sys.exit(app.exec_())
