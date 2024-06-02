import psycopg2
import lasio
import io

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname='geologml',
    user='kate',
    password='kate',
    host='localhost',
    port='5432'
)

cur = conn.cursor()
cur.execute("SELECT file_content FROM well_logging WHERE id = 1")
file_content = cur.fetchone()[0]

# Преобразование memoryview в bytes и затем в строку
file_bytes = bytes(file_content)
file_str = file_bytes.decode('utf-8')
file_io = io.StringIO(file_str)

# Чтение через lasio
las = lasio.read(file_io)

# Просмотр данных
print(las.curves)

# Закрытие подключения
cur.close()
conn.close()