# ui_train_model.py

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                               QPlainTextEdit, QFileDialog, QMessageBox, QListWidget, QListWidgetItem, QComboBox)
import pandas as pd
from PySide6.QtCore import QUrl, Qt

class Ui_TrainModelScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Train Model")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        self.file_label = QLabel("No file selected")
        self.layout.addWidget(self.file_label)

        self.file_button = QPushButton("Load CSV File")
        self.file_button.clicked.connect(self.load_file)
        self.layout.addWidget(self.file_button)

        self.columns_list_widget = QListWidget()
        self.layout.addWidget(self.columns_list_widget)

        self.task_label = QLabel("Prediction Task")
        self.layout.addWidget(self.task_label)

        self.task_combo_box = QComboBox()
        self.task_combo_box.addItems(["Classification", "Regression", "Forecasting"])
        self.layout.addWidget(self.task_combo_box)

        self.target_label = QLabel("Target Column")
        self.layout.addWidget(self.target_label)

        self.target_combo_box = QComboBox()
        self.layout.addWidget(self.target_combo_box)

        self.time_label = QLabel("Time Column")
        self.layout.addWidget(self.time_label)

        self.time_combo_box = QComboBox()
        self.layout.addWidget(self.time_combo_box)

        self.train_button = QPushButton("Train Model")
        self.train_button.clicked.connect(self.train_model)
        self.layout.addWidget(self.train_button)

        self.results_text_box = QPlainTextEdit()
        self.layout.addWidget(self.results_text_box)

        self.setLayout(self.layout)

        self.df = None

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            self.file_label.setText(file_path)
            self.df = pd.read_csv(file_path)
            self.update_widgets()
            QMessageBox.information(self, "Data Loaded", f"File {file_path} loaded successfully.")
        else:
            QMessageBox.warning(self, "Load Error", "Failed to load file.")

    def update_widgets(self):
        self.columns_list_widget.clear()
        self.target_combo_box.clear()
        self.time_combo_box.clear()
        if self.df is not None:
            for column in self.df.columns:
                item = QListWidgetItem(column)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                self.columns_list_widget.addItem(item)
                self.target_combo_box.addItem(column)
                self.time_combo_box.addItem(column)

    def train_model(self):
        if self.df is None:
            QMessageBox.warning(self, "No Data", "No data loaded to train the model.")
            return

        selected_columns = [item.text() for item in self.columns_list_widget.findItems("", Qt.MatchContains) if
                            item.checkState() == Qt.Checked]
        target_column = self.target_combo_box.currentText()
        task = self.task_combo_box.currentText()
        time_column = self.time_combo_box.currentText()

        if not selected_columns:
            QMessageBox.warning(self, "No Columns Selected", "No columns selected for training.")
            return

        if not target_column:
            QMessageBox.warning(self, "No Target Column", "No target column selected.")
            return

        # Here you can add logic to train the model based on the selected columns, target column, and task type.
        # For demonstration, we will just print the selected options to the results text box.

        self.results_text_box.setPlainText(f"Selected Columns: {selected_columns}\n"
                                           f"Target Column: {target_column}\n"
                                           f"Prediction Task: {task}\n"
                                           f"Time Column: {time_column}")
