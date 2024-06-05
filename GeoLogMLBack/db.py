from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, relationship


# Настройки подключения к PostgreSQL
DB_NAME = "geologml"
DB_USER = "kate"
DB_PASSWORD = "kate"
DB_HOST = "localhost"
DB_PORT = "5432"

# Создание строки подключения
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?client_encoding=utf8"

# Создание объекта Engine
try:
    engine = create_engine(DATABASE_URL)
    print("Подключение к базе данных успешно")
except Exception as e:
    print(f"Ошибка подключения к базе данных: {e}")

# Определение базовой модели
Base = declarative_base()


# Определение моделей
class Wells(Base):
    __tablename__ = 'wells'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    field = Column(String, nullable=False)
    well_loggings = relationship('WellLogging', back_populates='well')



class WellLogging(Base):
    __tablename__ = 'well_logging'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'))
    start_depth = Column(Float)
    stop_depth = Column(Float)
    log_export_date = Column(DateTime)
    file_content = Column(LargeBinary)
    well = relationship('Wells', back_populates='well_loggings')
    logs = relationship('Log', back_populates='well_logging')

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    well_logging_id = Column(Integer, ForeignKey('well_logging.id'))
    depth = Column(Float, nullable=False)
    cali = Column(Float)
    bs = Column(Float)
    dcal = Column(Float)
    rop = Column(Float)
    rdep = Column(Float)
    rsha = Column(Float)
    rmed = Column(Float)
    sp = Column(Float)
    dtc = Column(Float)
    nphi = Column(Float)
    pef = Column(Float)
    gr = Column(Float)
    rhob = Column(Float)
    drho = Column(Float)
    x_loc = Column(Float)
    y_loc = Column(Float)
    z_loc = Column(Float)
    predicted_facies = Column(String)
    well_logging = relationship('WellLogging', back_populates='logs')

#
# # # Пересоздание всех таблиц
# try:
#     Base.metadata.drop_all(engine)  # Удаляем все таблицы
#     Base.metadata.create_all(engine)  # Создаем таблицы заново
#     print("Таблицы успешно пересозданы")
# except Exception as e:
#     print(f"Ошибка при пересоздании таблиц: {e}")
