import sys
import os
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QFileDialog, QListWidget, QListWidgetItem
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QRect, QUrl, Qt
from cegal.welltools.wells import Well
from cegal.welltools.plotting import CegalWellPlotter as cwp
from plotly.offline import plot
import joblib
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import re
# Создание класса-обертки для литологий
class LithologyDescription:
    def __init__(self, lithology_dict):
        self.dictionary = lithology_dict

# Примерные цвета для каждой литологии
lithology_colors = {
    0: '#e6e208',  # Sandstone
    1: '#f2f21d',  # Sandstone/Shale
    2: '#ff7f0e',  # Shale
    3: '#bb4cd0',  # Marl
    4: '#f75f00',  # Dolomite
    5: '#0b8102',  # Limestone
    6: '#1f77b4',  # Chalk
    7: '#ff00ff',  # Halite
    8: '#9467bd',  # Anhydrite
    9: '#d62728',  # Tuff
    10: '#8c564b',  # Coal
    11: '#7f7f7f'  # Basement
}

# Создание словарей литологий и цветов
lithology_numbers = {
    30000: 0,
    65030: 1,
    65000: 2,
    80000: 3,
    74000: 4,
    70000: 5,
    70032: 6,
    88000: 7,
    86000: 8,
    99000: 9,
    90000: 10,
    93000: 11
}

lithology_keys = {
    'Sandstone': 30000,
    'Sandstone/Shale': 65030,
    'Shale': 65000,
    'Marl': 80000,
    'Dolomite': 74000,
    'Limestone': 70000,
    'Chalk': 70032,
    'Halite': 88000,
    'Anhydrite': 86000,
    'Tuff': 99000,
    'Coal': 90000,
    'Basement': 93000
}

# Создание словаря литологий с названиями и цветами
lithology_description_dict = {lithology_numbers[v]: (k, lithology_colors[lithology_numbers[v]]) for k, v in lithology_keys.items()}
lithology_description = LithologyDescription(lithology_description_dict)
class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.catboost_model = None  # Инициализируем модель как None
        self.setupUi(self)
        self.load_model()  # Автоматически загружаем модель
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
        self.pushButtonLoad.clicked.connect(self.load_las_file)

        self.pushButton = QPushButton("Построить график каротажа", self.centralwidget)
        self.pushButton.setGeometry(QRect(10, 70, 280, 50))
        self.pushButton.clicked.connect(self.plot_full_graph)

        self.pushButtonSimple = QPushButton("Получить предсказание литологии", self.centralwidget)
        self.pushButtonSimple.setGeometry(QRect(10, 130, 280, 50))
        self.pushButtonSimple.clicked.connect(self.get_lithology_predictions)

        self.columnsListWidget = QListWidget(self.centralwidget)
        self.columnsListWidget.setGeometry(QRect(10, 190, 280, 200))

        MainWindow.setCentralWidget(self.centralwidget)

        self.file_path = None  # Переменная для хранения пути к выбранному файлу
        self.columns = []  # Переменная для хранения колонок датафрейма

    def load_las_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать LAS файл", "", "LAS Files (*.las)")
        if file_path:
            self.file_path = file_path
            print(f"Файл выбран: {file_path}")

            # Загрузка колонок из LAS файла
            force_well = Well(filename=self.file_path, path=None)
            test_well = pd.DataFrame(force_well.df())
            self.columns = test_well.columns.tolist()

            # Заполнение выпадающего списка колонками
            self.columnsListWidget.clear()
            for column in self.columns:
                item = QListWidgetItem(column)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.columnsListWidget.addItem(item)

    def get_selected_columns(self):
        selected_columns = []
        for index in range(self.columnsListWidget.count()):
            item = self.columnsListWidget.item(index)
            if item.checkState() == Qt.Checked:
                selected_columns.append(item.text())
        return selected_columns


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
            max_rows = 10000
            if len(test_well) > max_rows:
                print(f"Сокращение данных с {len(test_well)} строк до {max_rows} строк...")
                test_well = test_well.head(max_rows)
                print(f"Сокращенные данные до {len(test_well)} строк.")

            # Получаем выбранные пользователем колонки
            selected_columns = self.get_selected_columns()
            if not selected_columns:
                print("Пожалуйста, выберите хотя бы одну колонку для построения графика.")
                return

            print("Генерация полного графика...")
            fig = cwp.plot_logs(
                df=test_well,
                logs=selected_columns,
                show_fig=False
            )
            fig.update_layout(
                width=820,
                height=720,
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

    def load_model(self):
        model_path = './catboost_model.pkl'  # Задаём путь к файлу модели
        try:
            self.catboost_model = joblib.load(model_path)
            print(f"Модель загружена из: {model_path}")
        except FileNotFoundError:
            print(f"Файл модели не найден в пути: {model_path}")
        except Exception as e:
            print(f"Ошибка при загрузке модели: {str(e)}")

    def get_lithology_predictions(self):
        print(lithology_description)
        features = ['DEPTH_MD',
                    'CALI',
                    'RSHA',
                    'RMED',
                    'RDEP',
                    'RHOB',
                    'GR',
                    'PEF',
                    'DTC',
                    'BS',
                    'NPHI',
                    'SP']

        if not self.file_path:
            print("Пожалуйста, выберите файл LAS перед выполнением предсказания.")
            return

        try:
            print("Загрузка данных скважины...")
            force_well = Well(filename=self.file_path, path=None)
            test_well = pd.DataFrame(force_well.df())
            print("Данные загружены успешно.")

            test_well = test_well.iloc[10:]  # Удаление первых 1000 строк
            test_well = test_well.iloc[np.arange(len(test_well)) % 5 != 0]
            max_rows = 10000
            if len(test_well) > max_rows:
                print(f"Сокращение данных с {len(test_well)} строк до {max_rows} строк...")
                test_well = test_well.head(max_rows)
                print(f"Сокращенные данные до {len(test_well)} строк.")

            print("Получение предсказаний...")
            selected_columns = self.get_selected_columns()
            if not set(features).issubset(test_well.columns):
                missing = list(set(features) - set(test_well.columns))
                raise ValueError(f"Отсутствуют следующие необходимые столбцы: {missing}")

            predicted_classes = self.catboost_model.predict(test_well[features])
            if isinstance(predicted_classes, np.ndarray) and predicted_classes.ndim > 1:
                # Преобразуем предсказания в одномерный массив, если они в формате массива массивов
                predicted_classes = predicted_classes.ravel()

            # Добавление предсказанных классов в DataFrame
            test_well['Predicted_Class'] = predicted_classes
            print(test_well['Predicted_Class'])

            test_well['Facies'] = test_well['Predicted_Class'].map(lithology_keys).map(lithology_numbers)
            test_well['Predicted Facies'] = test_well['FORCE_2020_LITHOFACIES_LITHOLOGY'].map(lithology_numbers)
            print("Предсказания обработаны")
            unique_facies = test_well['Predicted Facies'].unique()
            # Создаем новый словарь с уникальными значениями
            unique_lithology_description = {key: lithology_description_dict[key] for key in unique_facies if
                                            key in lithology_description_dict}
            print("Генерация графика...")
            print(unique_lithology_description)
            fig = cwp.plot_logs(
                df=test_well,
                logs=selected_columns,
                lithology_logs=['Facies'],
                lithology_description=LithologyDescription(unique_lithology_description),
                show_fig=False
            )
            # Убираем легенду каротажных кривых
            fig.update_layout(showlegend=False)

            # Получаем количество колонок из меток осей x
            x_axes = [ax for ax in fig.layout if re.match(r'xaxis\d*', ax)]
            num_cols = len(x_axes)

            # Создаем новую фигуру с дополнительной колонкой для легенды
            fig_with_legend = make_subplots(
                rows=1,
                cols=num_cols + 1,  # Увеличиваем количество колонок на 1
                shared_yaxes=True,
                subplot_titles=[*[fig.layout.annotations[i].text for i in range(len(fig.layout.annotations))],
                                "Facies Colors"]
            )

            # Копируем существующие трейсы в новую фигуру
            for trace in fig.data:
                col = int(re.search(r'\d+', trace.xaxis).group()) if re.search(r'\d+', trace.xaxis) else 1
                fig_with_legend.add_trace(trace, row=1, col=col)

            # Генерация данных для легенды литологии
            lithology_values = list(lithology_description.dictionary.keys())
            lithology_names = [lithology_description.dictionary[val][0] for val in lithology_values]
            lithology_colors = [lithology_description.dictionary[val][1] for val in lithology_values]

            # Создаем Heatmap для легенды литологии
            fig_with_legend.add_trace(
                go.Heatmap(
                    z=np.array(lithology_values).reshape(len(lithology_values), 1),
                    # Преобразуем значения литологии в 2D массив
                    x=['Facies Colors'],  # Используем подпись для нового столбца
                    y=lithology_names,
                    colorscale=list(zip(np.linspace(0, 1, len(lithology_colors)), lithology_colors)),
                    showscale=False,  # Отключаем цветовую шкалу
                    hoverinfo='y',
                    hovertemplate="<b>Lithology</b>: %{y}<extra></extra>"
                ),
                row=1,
                col=num_cols + 1  # Добавляем в новую последнюю колонку
            )

            # Проверка и обновление ширины
            current_width = fig.layout.width if fig.layout.width is not None else 800  # Задаем значение по умолчанию, если None
            well_name = os.path.basename(self.file_path).replace(".las", "")
            # Обновляем макет
            fig_with_legend.update_layout(
                height=fig.layout.height,
                width=current_width + 200,  # Увеличиваем ширину для новой колонки
                title_text=f"Скважина {well_name}",  # Устанавливаем заголовок
                title_x=0.5,  # Располагаем заголовок посередине
                yaxis=dict(autorange='reversed')  # Инвертируем ось Y
            )
            # Поворачиваем названия колонок на 45 градусов
            for annotation in fig_with_legend.layout.annotations:
                annotation['textangle'] = 45

            print("Преобразование графика в HTML...")
            raw_html = plot(fig_with_legend, include_plotlyjs='cdn', output_type='div')
            print("HTML сгенерирован.")
            print("Загрузка HTML в QWebEngineView...")
            self.webEngineView.setHtml(raw_html, baseUrl=QUrl("https://cdn.plot.ly/plotly-latest.min.js"))
            print("HTML загружен в QWebEngineView.")

        except Exception as e:
            print(f"Ошибка при выполнении предсказания или построении графика: {type(e).__name__}: {e}")

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
