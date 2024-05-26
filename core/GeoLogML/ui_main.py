from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QFileDialog, QListWidget, QListWidgetItem
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QRect, QUrl, Qt

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 1100)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setGeometry(QRect(300, 10, 1000, 900))
        # Подключение обработчиков событий
        self.webEngineView.loadStarted.connect(self.onLoadStarted)
        self.webEngineView.loadProgress.connect(self.onLoadProgress)
        self.webEngineView.loadFinished.connect(self.onLoadFinished)

        self.pushButtonLoad = QPushButton("Выбрать LAS файл", self.centralwidget)
        self.pushButtonLoad.setGeometry(QRect(10, 10, 280, 50))

        self.pushButton = QPushButton("Построить график каротажа", self.centralwidget)
        self.pushButton.setGeometry(QRect(10, 70, 280, 50))

        self.pushButtonSimple = QPushButton("Получить предсказание литологии", self.centralwidget)
        self.pushButtonSimple.setGeometry(QRect(10, 130, 280, 50))

        self.columnsListWidget = QListWidget(self.centralwidget)
        self.columnsListWidget.setGeometry(QRect(10, 190, 280, 200))

        MainWindow.setCentralWidget(self.centralwidget)

    def onLoadStarted(self):
        print("Загрузка начата.")

    def onLoadProgress(self, progress):
        print(f"Загрузка прогресс: {progress}%")

    def onLoadFinished(self, ok):
        if ok:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка завершена с ошибкой.")
