import sys
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
import asyncio
import aiohttp


class KittyShowcase(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kitty Showcase")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: blue;")

        self.label = QLabel(self)
        self.label.setFixedSize(300, 300)
        self.label.move(50, 50)

        self.button = QPushButton("Click Me!", self)
        self.button.setFixedSize(100, 30)
        self.button.move(150, 350)
        self.button.setStyleSheet("background-color: grey; color: white; font-size: 16px;")
        self.button.clicked.connect(self.show_cat)

        self.thread = QThread()
        self.worker = ImageDownloader()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.download_image)
        self.worker.image_downloaded.connect(self.set_image)

        self.thread.start()

    def show_cat(self):
        self.worker.download_image()

    def set_image(self, image_data):
        image = QImage.fromData(image_data)
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)


class ImageDownloader(QObject):
    image_downloaded = pyqtSignal(bytes)

    async def get_image_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://cataas.com/cat?type=sm") as response:
                return await response.read()

    def download_image(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_data = loop.run_until_complete(self.get_image_data())
        loop.close()
        self.image_downloaded.emit(image_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KittyShowcase()
    window.show()
    sys.exit(app.exec())
