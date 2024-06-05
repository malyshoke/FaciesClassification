from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QFileDialog, QListWidget, QListWidgetItem, QLabel, \
    QScrollBar, QComboBox, QTabWidget
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

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QRect(10, 10, 280, 750))
        self.tabWidget.setStyleSheet("background-color: white;")

        self.tabFile = QWidget()
        self.tabDB = QWidget()

        self.tabWidget.addTab(self.tabFile, "Загрузка из файла")
        self.tabWidget.addTab(self.tabDB, "Загрузка из БД")

        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setGeometry(QRect(300, 10, 1050, 950))
        self.webEngineView.loadStarted.connect(self.onLoadStarted)
        self.webEngineView.loadProgress.connect(self.onLoadProgress)
        self.webEngineView.loadFinished.connect(self.onLoadFinished)

        # Вкладка для загрузки из файла
        self.pushButtonLoad = QPushButton("Выбрать LAS файл", self.tabFile)
        self.pushButtonLoad.setGeometry(QRect(10, 10, 260, 40))
        self.pushButtonLoad.setStyleSheet(self.button_style())

        self.pushButtonFilePlot = QPushButton("Построить график каротажа", self.tabFile)
        self.pushButtonFilePlot.setGeometry(QRect(10, 60, 260, 40))
        self.pushButtonFilePlot.setStyleSheet(self.button_style())

        self.pushButtonFilePredict = QPushButton("Получить предсказание литофаций", self.tabFile)
        self.pushButtonFilePredict.setGeometry(QRect(10, 110, 260, 40))
        self.pushButtonFilePredict.setStyleSheet(self.button_style())

        self.labelFile = QLabel("Выбрать кривые для отрисовки:", self.tabFile)
        self.labelFile.setGeometry(QRect(10, 160, 260, 30))

        self.columnsListWidgetFile = QListWidget(self.tabFile)
        self.columnsListWidgetFile.setGeometry(QRect(10, 200, 260, 250))
        self.columnsListWidgetFile.setStyleSheet(self.list_widget_style())
        self.columnsListWidgetFile.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.saveToDbButtonFile = QPushButton("Сохранить в базу данных", self.tabFile)
        self.saveToDbButtonFile.setGeometry(QRect(10, 460, 260, 40))
        self.saveToDbButtonFile.setStyleSheet(self.button_style())

        self.saveButtonFile = QPushButton("Сохранить в Excel", self.tabFile)
        self.saveButtonFile.setGeometry(QRect(10, 510, 260, 40))
        self.saveButtonFile.setStyleSheet(self.button_style())

        self.labelDbWell = QLabel("Выберите название скважины:", self.tabDB)
        self.labelDbWell.setGeometry(QRect(10, 10, 260, 30))

        self.wellComboBox = QComboBox(self.tabDB)
        self.wellComboBox.setGeometry(QRect(10, 50, 260, 40))
        self.wellComboBox.setStyleSheet(self.combo_box_style())

        self.pushButtonDbPlot = QPushButton("Построить график каротажа", self.tabDB)
        self.pushButtonDbPlot.setGeometry(QRect(10, 100, 260, 40))
        self.pushButtonDbPlot.setStyleSheet(self.button_style())

        self.pushButtonDbPredict = QPushButton("Получить предсказание литофаций", self.tabDB)
        self.pushButtonDbPredict.setGeometry(QRect(10, 150, 260, 40))
        self.pushButtonDbPredict.setStyleSheet(self.button_style())

        self.labelDb = QLabel("Выбрать кривые для отрисовки:", self.tabDB)
        self.labelDb.setGeometry(QRect(10, 200, 260, 30))

        self.columnsListWidgetDb = QListWidget(self.tabDB)
        self.columnsListWidgetDb.setGeometry(QRect(10, 240, 260, 250))
        self.columnsListWidgetDb.setStyleSheet(self.list_widget_style())
        self.columnsListWidgetDb.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.saveButtonDb = QPushButton("Сохранить в Excel", self.tabDB)
        self.saveButtonDb.setGeometry(QRect(10, 500, 260, 40))
        self.saveButtonDb.setStyleSheet(self.button_style())

        self.plotWellButton = QPushButton("Изучить расположение скважин", self.tabDB)
        self.plotWellButton.setGeometry(QRect(10, 550, 260, 40))
        self.plotWellButton.setStyleSheet(self.button_style())

        # Прогресс бар
        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QRect(550, 450, 100, 100))
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        self.progressBar.setStyleSheet(self.circularProgressBarStyle())

        self.legendLabel = QLabel(self.centralwidget)
        self.legendLabel.setGeometry(QRect(300, 920, 1000, 100))
        self.legendLabel.setText(self.generate_legend_html())
        self.legendLabel.setStyleSheet("font-size: 14px;")

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

    def combo_box_style(self):
        return """
            QComboBox {
                border: 2px solid #dcdcdc;
                border-radius: 5px;
                padding: 2px;
                background-color: #f0f0f0;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #dcdcdc;
                selection-background-color: #e8e8e8;
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