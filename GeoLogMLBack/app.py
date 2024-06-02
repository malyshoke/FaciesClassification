import logging
import time
from datetime import datetime
import lasio
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

        # Сохранение обновленного файла в базу данных
        string_io = io.StringIO()
        las.write(string_io)
        file_bytes = io.BytesIO(string_io.getvalue().encode('utf-8'))
        save_to_db_chat(file_bytes.getvalue(), las)

        file_bytes.seek(0)
        end_time = time.time()  # Записываем время окончания обработки запроса
        logging.info(f"Request processed in {end_time - start_time} seconds")

        return send_file(file_bytes, as_attachment=True, download_name=input_las_file.filename,
                         mimetype='application/octet-stream')
    except Exception as e:
        logging.exception("Failed to process the LAS file")
        return jsonify({'error': str(e)}), 500


def save_to_db_chat(file_content, las):
    well_name = las.well['WELL'].value.strip()
    field_name = las.well['FLD'].value.strip() if 'FLD' in las.well else 'Unknown'
    existing_well = session.query(Wells).filter_by(name=well_name).first()
    if not existing_well:
        new_well = Wells(
            name=well_name,
            field=field_name
        )
        session.add(new_well)
        session.commit()
        existing_well = new_well
    datetime_str = las.well['DATE'].value.strip()
    datetime_str = datetime_str.split(' :')[0].strip()
    datetime_format = "%Y-%m-%d %H:%M:%S"
    datetime_obj = datetime.strptime(datetime_str, datetime_format)

    new_well_logging = WellLogging(
        well_id=existing_well.id,
        start_depth=float(las.well['STRT'].value),
        stop_depth=float(las.well['STOP'].value),
        log_export_date=datetime_obj,
        file_content=file_content
    )
    session.add(new_well_logging)
    session.commit()

    df = las.df()
    logs = []
    for depth, row in df.iterrows():
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
            predicted_facies=row.get('Predictions', None)
        ))
    session.bulk_save_objects(logs)
    session.commit()


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8081)
