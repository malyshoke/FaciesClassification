import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class LithologyModel:
    def __init__(self, model_path, scaler_path):
        self.model = self.load_model(model_path)
        self.scaler = self.load_scaler(scaler_path)

    def load_model(self, model_path):
        try:
            model = joblib.load(model_path)
            print("Модель загружена успешно.")
            return model
        except Exception as e:
            print("Ошибка при загрузке модели:", str(e))
            return None

    def load_scaler(self, scaler_path):
        try:
            scaler = joblib.load(scaler_path)
            print("Scaler загружен успешно.")
            return scaler
        except Exception as e:
            print("Ошибка при загрузке scaler:", str(e))
            return None

    def preprocess_data(self, data):
        if self.scaler is not None:
            data = self.scaler.transform(data)
        return data

    def predict(self, data):
        if self.model is not None:
            preprocessed_data = self.preprocess_data(data)
            predictions = self.model.predict(preprocessed_data)
            if isinstance(predictions, np.ndarray) and predictions.ndim > 1:
                predictions = predictions.ravel()
            return predictions
        else:
            print("Модель не загружена.")
            return None

    def save_scaler(self, scaler_path):
        if self.scaler is not None:
            try:
                joblib.dump(self.scaler, scaler_path, compress=True)
                print("Scaler сохранен успешно.")
            except Exception as e:
                print("Ошибка при сохранении scaler:", str(e))
        else:
            print("Scaler не загружен, нечего сохранять.")
