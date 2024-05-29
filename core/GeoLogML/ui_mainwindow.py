from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QFileDialog, QListWidget, QListWidgetItem, QLabel, QScrollBar
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QRect, QUrl, Qt
from PySide6.QtWidgets import QProgressBar

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def generate_legend_html(self):
        lithology_colors = {
            0: ('#e6e208', 'Sandstone'),
            1: ('#f2f21d', 'Sandstone/Shale'),
            2: ('#0b8102', 'Shale'),
            3: ('#bb4cd0', 'Marl'),
            4: ('#f75f00', 'Dolomite'),
            5: ('#ff7f0e', 'Limestone'),
            6: ('#1f77b4', 'Chalk'),
            7: ('#ff00ff', 'Halite'),
            8: ('#9467bd', 'Anhydrite'),
            9: ('#d62728', 'Tuff'),
            10: ('#8c564b', 'Coal'),
            11: ('#7f7f7f', 'Basement')
        }
        html = '<h3>Legend:</h3><ul style="list-style: none; padding-left: 0;">'
        for lith_id, (color, name) in lithology_colors.items():
            html += f'<li style="margin-bottom: 2px;"><span style="color: {color}; font-size: 18px;">■</span> {lith_id} - {name}</li>'
        html += '</ul>'
        return html
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("GeoLogML")
        MainWindow.resize(1300, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: white;")

        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setGeometry(QRect(300, 10, 1010, 915))
        self.webEngineView.loadStarted.connect(self.onLoadStarted)
        self.webEngineView.loadProgress.connect(self.onLoadProgress)
        self.webEngineView.loadFinished.connect(self.onLoadFinished)

        self.pushButtonLoad = QPushButton("Выбрать LAS файл", self.centralwidget)
        self.pushButtonLoad.setGeometry(QRect(10, 10, 280, 40))
        self.pushButtonLoad.setStyleSheet(self.button_style())

        self.pushButton = QPushButton("Построить график каротажа", self.centralwidget)
        self.pushButton.setGeometry(QRect(10, 60, 280, 40))
        self.pushButton.setStyleSheet(self.button_style())

        self.pushButtonSimple = QPushButton("Получить предсказание литофаций", self.centralwidget)
        self.pushButtonSimple.setGeometry(QRect(10, 110, 280, 40))
        self.pushButtonSimple.setStyleSheet(self.button_style())

        self.label = QLabel("Выбрать кривые для отрисовки:", self.centralwidget)
        self.label.setGeometry(QRect(10, 160, 280, 30))

        self.columnsListWidget = QListWidget(self.centralwidget)
        self.columnsListWidget.setGeometry(QRect(10, 200, 280, 250))
        self.columnsListWidget.setStyleSheet(self.list_widget_style())
        self.columnsListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.saveButton = QPushButton("Сохранить в Excel", self.centralwidget)
        self.saveButton.setGeometry(QRect(10, 460, 280, 40))
        self.saveButton.setStyleSheet(self.button_style())

        # Создание и стилизация круглого прогресс бара
        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QRect(550, 450, 100, 100))  # Позиционирование на центр WebEngineView
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.progressBar.setStyleSheet(self.circularProgressBarStyle())

        self.legendLabel = QLabel(self.centralwidget)
        self.legendLabel.setGeometry(QRect(300, 920, 1000, 100))  # Регулируйте размер и позицию под ваш интерфейс
        self.legendLabel.setText(self.generate_legend_html())
        self.legendLabel.setStyleSheet("font-size: 14px;")  # При необходимости настройте стиль


        MainWindow.setCentralWidget(self.centralwidget)

    def circularProgressBarStyle(self):
        return """
            QProgressBar {
                border: none;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #05B8CC;
                width: 100px; 
                margin: 0px;
                border-radius: 50px;
            }
        """

    def onLoadStarted(self):
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

    def onLoadProgress(self, progress):
        self.progressBar.setValue(progress)

    def onLoadFinished(self, ok):
        self.progressBar.setVisible(False)

    def button_style(self):
        return """
            QPushButton {
                background-color: #f0f0f0;
                border: 2px solid #dcdcdc;
                border-radius: 5px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
        """

    def list_widget_style(self):
        return """
            QListWidget {
                border: 1px solid #dcdcdc;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background: #e8e8e8;
                color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: white;
                width: 10px;
                margin: 10px 0 10px 0;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #a0a0a0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """

    def onLoadStarted(self):
        self.progressBar.setVisible(True)  # Показать прогресс бар при начале загрузки
        self.progressBar.setValue(0)  # Сбросить значение прогресса

    def onLoadProgress(self, progress):
        self.progressBar.setValue(progress)  # Обновить значение прогресса

    def onLoadFinished(self, ok):
        if ok:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка завершена с ошибкой.")
        self.progressBar.setVisible(False)  # Скрыть прогресс бар после завершения загрузки