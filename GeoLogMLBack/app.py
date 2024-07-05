import logging
import time
from datetime import datetime
import lasio
import pandas as pd
from flask import Flask, jsonify, request, send_file
from sqlalchemy import create_engine, DateTime, Column, LargeBinary
from waitress import serve
from LithologyModel import LithologyModel
from constants import Constants
import os
from sqlalchemy.orm import declarative_base, sessionmaker
from db import DATABASE_URL, Log, Wells, WellLogging
import io

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
model_path = 'ovr_classifier.pkl'
scaler_path = 'scaler.pkl'
lithology_model = LithologyModel(model_path, scaler_path)
Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/save_to_db', methods=['POST'])
def save_to_db_endpoint():
    try:
        input_las_file = request.files['file']
        file_content = input_las_file.read()

        # Чтение файла с правильным декодированием
        file_str = io.StringIO(file_content.decode('utf-8'))
        las = lasio.read(file_str)

        save_to_db_chat(file_content, las)
        return jsonify({'message': 'File saved to database successfully'}), 200

    except Exception as e:
        logging.exception("Failed to save the LAS file to the database")
        return jsonify({'error': str(e)}), 500


@app.route('/predict', methods=['POST'])
def predict():
    start_time = time.time()  # Записываем время начала обработки запроса
    try:
        input_las_file = request.files['file']
        file_content = input_las_file.read()

        # Чтение файла с правильным декодированием
        file_str = io.StringIO(file_content.decode('utf-8'))
        las = lasio.read(file_str)

        df = las.df()
        predictions = lithology_model.predict(df[Constants.FEATURES])
        df['Predictions'] = predictions
        las.set_data(df)

        string_io = io.StringIO()
        las.write(string_io)
        file_bytes = io.BytesIO(string_io.getvalue().encode('utf-8'))
        file_bytes.seek(0)
        end_time = time.time()
        logging.info(f"Request processed in {end_time - start_time} seconds")

        return send_file(file_bytes, as_attachment=True, download_name=input_las_file.filename,
                         mimetype='application/octet-stream')
    except Exception as e:
        logging.exception("Failed to process the LAS file")
        return jsonify({'error': str(e)}), 500

@app.route('/download_well_data', methods=['GET'])
def download_well_data():
    well_name = request.args.get('well_name')
    try:
        well_logging = session.query(WellLogging).join(Wells).filter(Wells.name == well_name).first()
        if well_logging is None:
            logging.error(f"Well not found: {well_name}")
            return jsonify({'error': 'Well not found'}), 404

        file_content = well_logging.file_content

        return send_file(io.BytesIO(file_content), download_name=f"{well_name}.las", as_attachment=True,
                         mimetype='application/octet-stream')
    except Exception as e:
        logging.exception(f"Failed to download well data for {well_name}")
        return jsonify({'error': str(e)}), 500


@app.route('/wells_names', methods=['GET'])
def get_wells():
    try:
        wells_query = session.query(Wells.name).all()
        wells = [well.name for well in wells_query]
        return jsonify(wells)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/well_loc', methods=['GET'])
def get_well_data():
    try:
        # Получение данных из базы данных с использованием ORM
        logs_query = session.query(
            Wells.name.label('WELL'),
            Log.x_loc.label('X_LOC'),
            Log.y_loc.label('Y_LOC')
        ).join(WellLogging, Wells.id == WellLogging.well_id).join(Log, WellLogging.id == Log.well_logging_id)

        df = pd.read_sql(logs_query.statement, logs_query.session.bind)

        # Группировка данных и вычисление характеристик
        well_names_uniq = df['WELL'].unique()
        X_cor = df.groupby(['WELL'])['X_LOC'].mean()  # location coordinate
        Y_cor = df.groupby(['WELL'])['Y_LOC'].mean()
        data_count = df.groupby(['WELL']).count().sum(axis='columns')

        loc_wells_df = pd.DataFrame({'WELL': well_names_uniq, 'X_LOC': X_cor, 'Y_LOC': Y_cor, 'data_points': data_count})

        # Преобразование данных в формат JSON
        result = loc_wells_df.to_dict(orient='records')

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def save_to_db_chat(file_content, las):
    well_name = las.well['UWI'].value.strip()
    field_name = las.well['FLD'].value.strip() if 'FLD' in las.well else 'Unknown'

    # Проверка существования скважины
    existing_well = session.query(Wells).filter_by(name=well_name).first()
    if not existing_well:
        new_well = Wells(
            name=well_name,
            field=field_name
        )
        session.add(new_well)
        session.commit()
        existing_well = new_well

    # Форматирование даты
    datetime_str = las.well['DATE'].value.strip()
    datetime_str = datetime_str.split(' :')[0].strip()
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_obj = datetime.strptime(datetime_str, datetime_format)

    # Проверка существования отчета
    existing_well_logging = session.query(WellLogging).filter_by(
        well_id=existing_well.id,
        log_export_date=datetime_obj
    ).first()

    if existing_well_logging:
        # Если отчет существует, выходим без сохранения логов
        logging.info("Report already exists in the database. Skipping log saving.")
        return

    # Создание нового отчета, если он не существует
    new_well_logging = WellLogging(
        well_id=existing_well.id,
        start_depth=float(las.well['STRT'].value),
        stop_depth=float(las.well['STOP'].value),
        log_export_date=datetime_obj,
        file_content=file_content
    )
    session.add(new_well_logging)
    session.commit()

    # Получение данных из LAS файла и сохранение логов
    df = las.df()
    logs = []
    for depth, row in df.iterrows():
        # Проверка на существование логов
        existing_log = session.query(Log).filter_by(
            well_logging_id=new_well_logging.id,
            depth=depth
        ).first()

        if existing_log:
            logging.info(f"Log at depth {depth} already exists. Skipping.")
            continue

        logs.append(Log(
            well_logging_id=new_well_logging.id,
            depth=depth,
            cali=row.get('CALI', None),
            bs=row.get('BS', None),
            dcal=row.get('DCAL', None),
            rop=row.get('ROP', None),
            rdep=row.get('RDEP', None),
            rsha=row.get('RSHA', None),
            rmed=row.get('RMED', None),
            sp=row.get('SP', None),
            dtc=row.get('DTC', None),
            nphi=row.get('NPHI', None),
            pef=row.get('PEF', None),
            gr=row.get('GR', None),
            rhob=row.get('RHOB', None),
            drho=row.get('DRHO', None),
            x_loc=row.get('X_LOC', None),
            y_loc=row.get('Y_LOC', None),
            z_loc=row.get('Z_LOC', None),
            predicted_facies=row.get('Predictions', None)
        ))

    if logs:
        session.bulk_save_objects(logs)
        session.commit()
        logging.info("Logs saved successfully.")
    else:
        logging.info("No new logs to save.")


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)
