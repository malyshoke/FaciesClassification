from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import psycopg2

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
    logs = relationship('Log', back_populates='well')

class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'))
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
    predicted_facies = Column(String)
    well = relationship('Wells', back_populates='logs')

# Создание всех таблиц
try:
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы")
except Exception as e:
    print(f"Ошибка при создании таблиц: {e}")

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()


session.close()