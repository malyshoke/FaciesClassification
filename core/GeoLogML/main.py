import sys
import os
import re
import numpy as np
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QListWidgetItem
from PySide6.QtCore import QUrl, Qt
from ui_mainwindow import Ui_MainWindow
from cegal.welltools.wells import Well
from cegal.welltools.plotting import CegalWellPlotter as cwp
from plotly.offline import plot
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import joblib
from constants import Constants
from LithologyModel import LithologyModel
from PySide6.QtWidgets import QMessageBox

class LithologyDescription:
    def __init__(self, lithology_dict):
        self.dictionary = lithology_dict

def add_legend_to_figure(fig, lithology_description, well_name):
    # Получаем количество колонок из меток осей x
    x_axes = [ax for ax in fig.layout if re.match(r'xaxis\d*', ax)]
    num_cols = len(x_axes)

    # Создаем новую фигуру с дополнительной колонкой для легенды
    fig_with_legend = make_subplots(
        rows=1,
        cols=num_cols + 1,  # Увеличиваем количество колонок на 1
        shared_yaxes=True,
        subplot_titles=[*[fig.layout.annotations[i].text for i in range(len(fig.layout.annotations))], "Facies Colors"]
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
    current_width = fig.layout.width if fig.layout.width is not None else 700  # Задаем значение по умолчанию, если None

    # Обновляем макет
    fig_with_legend.update_layout(
        height=fig.layout.height,
        width=current_width + 200,  # Увеличиваем ширину для новой колонки
        title='',  # Убираем заголовок
        yaxis=dict(autorange='reversed')  # Инвертируем ось Y
    )

    fig_with_legend.update_layout(
        width=current_width + 150,
        height=720,
        title_text=f"Скважина {well_name}",
        title_x=0.5
    )
    # Поворачиваем названия колонок на 45 градусов
    for annotation in fig_with_legend.layout.annotations:
        annotation['textangle'] = 45

    return fig_with_legend

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.file_path = None
        self.columns = []
        self.test_well = None

        # Инициализация LithologyModel
        self.lithology_model = LithologyModel('catboost_model.pkl', 'new_scaler.pkl')

        lithology_description_dict = {
            Constants.LITHOLOGY_NUMBERS[v]: (k, Constants.LITHOLOGY_COLORS[Constants.LITHOLOGY_NUMBERS[v]])
            for k, v in Constants.LITHOLOGY_KEYS.items()
        }
        self.lithology_description = LithologyDescription(lithology_description_dict)

        # Подключение обработчиков событий
        self.ui.pushButtonLoad.clicked.connect(self.load_las_file)
        self.ui.pushButton.clicked.connect(self.plot_full_graph)
        self.ui.pushButtonSimple.clicked.connect(self.get_lithology_predictions)
        self.ui.saveButton.clicked.connect(self.save_to_csv)

    def load_las_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать LAS файл", "", "LAS Files (*.las)")
        if file_path:
            self.file_path = file_path
            print(f"Файл выбран: {file_path}")

            force_well = Well(filename=self.file_path, path=None)
            self.test_well = pd.DataFrame(force_well.df())

            # Выбираем только те колонки, которые не входят в exclude_columns
            self.columns = [col for col in self.test_well.columns if col not in Constants.exclude_columns]
            self.ui.columnsListWidget.clear()
            for column in self.columns:
                item = QListWidgetItem(column)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.ui.columnsListWidget.addItem(item)

    def save_to_csv(self):
        if self.test_well is not None:
            file_name, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "CSV Files (*.csv)")
            if file_name:
                self.test_well.to_csv(file_name, index=False)
                print(f"Данные сохранены в {file_name}")
        else:
            QMessageBox.warning(self, "Нет данных", "Загрузите данные перед сохранением в CSV.")

    def get_selected_columns(self):
        selected_columns = []
        for index in range(self.ui.columnsListWidget.count()):
            item = self.ui.columnsListWidget.item(index)
            if item.checkState() == Qt.Checked:
                selected_columns.append(item.text())
        return selected_columns

    def plot_full_graph(self):
        if not self.file_path:
            QMessageBox.warning(self, "Файл не выбран", "Пожалуйста, выберите файл LAS перед построением графика.")
            return

        try:
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

            selected_columns = self.get_selected_columns()
            if not selected_columns:
                QMessageBox.information(self, "Колонки не выбраны", "Пожалуйста, выберите хотя бы одну колонку для построения графика.")
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
                title_text=f"Скважина {well_name}",
                title_x=0.5,
            )
            print("График сгенерирован.")

            print("Преобразование графика в HTML...")
            config = {
                'displayModeBar': False
            }
            raw_html = plot(fig, include_plotlyjs='cdn', output_type='div', config=config)
            print("HTML сгенерирован.")

            print("Загрузка HTML в QWebEngineView...")
            self.ui.webEngineView.setHtml(raw_html, baseUrl=QUrl("https://cdn.plot.ly/plotly-latest.min.js"))
            print("HTML загружен в QWebEngineView.")

        except Exception as e:
            print("Ошибка при построении графика:", str(e))

    def get_lithology_predictions(self):
        if not self.file_path:
            QMessageBox.warning(self, "Файл не выбран", "Пожалуйста, выберите файл LAS перед построением графика.")
            return

        try:
            print("Загрузка данных скважины...")
            force_well = Well(filename=self.file_path, path=None)
            test_well = pd.DataFrame(force_well.df())
            print("Данные загружены успешно.")

            test_well = test_well.iloc[10:]
            test_well = test_well.iloc[np.arange(len(test_well)) % 5 != 0]
            max_rows = 10000
            if len(test_well) > max_rows:
                print(f"Сокращение данных с {len(test_well)} строк до {max_rows} строк...")
                test_well = test_well.head(max_rows)
                print(f"Сокращенные данные до {len(test_well)} строк.")

            print("Получение предсказаний...")
            selected_columns = self.get_selected_columns()
            if not set(Constants.FEATURES).issubset(test_well.columns):
                missing = list(set(Constants.FEATURES) - set(test_well.columns))
                QMessageBox.critical(self, "Недостающие колонки",
                                     f"Отсутствуют следующие необходимые столбцы: {', '.join(missing)}")

            # Предобработка данных и получение предсказаний
            predictions = self.lithology_model.predict(test_well[Constants.FEATURES])

            if predictions is not None:
                test_well['Predicted_Class'] = predictions
                test_well['Facies'] = test_well['Predicted_Class'].map(Constants.LITHOLOGY_KEYS).map(Constants.LITHOLOGY_NUMBERS)
                test_well['Predicted Facies'] = test_well['FORCE_2020_LITHOFACIES_LITHOLOGY'].map(Constants.LITHOLOGY_NUMBERS)
                print("Предсказания обработаны")
                unique_facies = test_well['Predicted Facies'].unique()
                unique_lithology_description = {key: self.lithology_description.dictionary[key] for key in unique_facies if
                                                key in self.lithology_description.dictionary}
                print("Генерация графика...")
                print(unique_lithology_description)
                fig = cwp.plot_logs(
                    df=test_well,
                    logs=selected_columns,
                    lithology_logs=['Predicted Facies'],
                    lithology_description=LithologyDescription(unique_lithology_description),
                    show_fig=False
                )
                well_name = os.path.basename(self.file_path).replace(".las", "")
                fig_with_legend = add_legend_to_figure(fig, self.lithology_description, well_name)
                config = {
                    'displayModeBar': False
                }
                print("Преобразование графика в HTML...")
                raw_html = plot(fig_with_legend, include_plotlyjs='cdn', output_type='div', config=config)
                print("HTML сгенерирован.")

                print("Загрузка HTML в QWebEngineView...")
                self.ui.webEngineView.setHtml(raw_html, baseUrl=QUrl("https://cdn.plot.ly/plotly-latest.min.js"))
                print("HTML загружен в QWebEngineView.")

        except Exception as e:
            print("Ошибка при выполнении предсказания:", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
