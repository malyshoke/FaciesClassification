import sys
import os
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QFileDialog
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtCore import QRect, QUrl
from cegal.welltools.wells import Well
from cegal.welltools.plotting import CegalWellPlotter as cwp
from plotly.offline import plot
import plotly.graph_objects as go

class Ui_MainWindow(QMainWindow):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("background-color: white;")  # Установка белого фона

        self.webEngineView = QWebEngineView(self.centralwidget)
        self.webEngineView.setGeometry(QRect(300, 10, 880, 780))

        # Установка политик безопасности и JavaScript для QWebEngineView
        settings = self.webEngineView.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)

        # Подключение обработчиков событий
        self.webEngineView.loadStarted.connect(self.onLoadStarted)
        self.webEngineView.loadProgress.connect(self.onLoadProgress)
        self.webEngineView.loadFinished.connect(self.onLoadFinished)

        self.pushButtonLoad = QPushButton("Выбрать LAS файл", self.centralwidget)
        self.pushButtonLoad.setGeometry(QRect(10, 10, 280, 50))
        self.pushButtonLoad.clicked.connect(self.load_las_file)

        self.pushButton = QPushButton("Построить график каротажа", self.centralwidget)
        self.pushButton.setGeometry(QRect(10, 70, 280, 50))
        self.pushButton.clicked.connect(self.plot_full_graph)

        self.pushButtonSimple = QPushButton("Построить простой график", self.centralwidget)
        self.pushButtonSimple.setGeometry(QRect(10, 130, 280, 50))
        self.pushButtonSimple.clicked.connect(self.plot_simple_graph)

        MainWindow.setCentralWidget(self.centralwidget)

        self.file_path = None  # Переменная для хранения пути к выбранному файлу

    def load_las_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать LAS файл", "", "LAS Files (*.las)")
        if file_path:
            self.file_path = file_path
            print(f"Файл выбран: {file_path}")

    def plot_simple_graph(self):
        try:
            print("Генерация простого графика...")
            fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
            fig.update_layout(title_text="Простой график", title_x=0.5)  # Располагаем заголовок посередине
            print("График сгенерирован.")

            print("Преобразование графика в HTML...")
            raw_html = plot(fig, include_plotlyjs='cdn', output_type='div')
            print("HTML сгенерирован.")

            print("Загрузка HTML в QWebEngineView...")
            self.webEngineView.setHtml(raw_html, baseUrl=QUrl("https://cdn.plot.ly/plotly-latest.min.js"))
            print("HTML загружен в QWebEngineView.")

        except Exception as e:
            print("Ошибка при генерации или загрузке графика:", str(e))

    def plot_full_graph(self):
        if not self.file_path:
            print("Пожалуйста, выберите файл LAS перед построением графика.")
            return

        try:
            # Извлекаем название скважины из имени файла
            well_name = os.path.basename(self.file_path).replace(".las", "")

            print("Загрузка данных скважины...")
            force_well = Well(filename=self.file_path, path=None)
            test_well = pd.DataFrame(force_well.df())
            print("Данные загружены успешно.")
            test_well = test_well.dropna()
            max_rows = 10000  # Увеличиваем количество данных для диагностики
            if len(test_well) > max_rows:
                print(f"Сокращение данных с {len(test_well)} строк до {max_rows} строк...")
                test_well = test_well.head(max_rows)
                print(f"Сокращенные данные до {len(test_well)} строк.")

            print("Генерация полного графика...")
            fig = cwp.plot_logs(
                df=test_well,
                logs=['CALI', 'RSHA', 'RMED', 'RDEP', 'RHOB'],
                log_scale_logs=['RMED', 'RDEP'],
                show_fig=False
            )
            fig.update_layout(
                width=800,
                height=700,
                title_text=f"Скважина {well_name}",  # Устанавливаем заголовок
                title_x=0.5  # Располагаем заголовок посередине
            )
            print("График сгенерирован.")

            print("Преобразование графика в HTML...")
            raw_html = plot(fig, include_plotlyjs='cdn', output_type='div')
            print("HTML сгенерирован.")

            print("Загрузка HTML в QWebEngineView...")
            self.webEngineView.setHtml(raw_html, baseUrl=QUrl("https://cdn.plot.ly/plotly-latest.min.js"))
            print("HTML загружен в QWebEngineView.")

        except Exception as e:
            print("Ошибка при генерации или загрузке графика:", str(e))

    def onLoadStarted(self):
        print("Загрузка начата.")

    def onLoadProgress(self, progress):
        print(f"Загрузка прогресс: {progress}%")

    def onLoadFinished(self, ok):
        if ok:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка завершена с ошибкой.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
