import mysql.connector
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Хост базы данных
        port=3307,         # Порт базы данных (по умолчанию 3306)
        user="root",       # Имя пользователя базы данных
        password="",  # Пароль пользователя базы данных
        database="vpn_telega",    # Имя базы данных
        charset="utf8mb4",         # Указываем кодировку
        collation="utf8mb4_general_ci"  # Указываем поддерживаемую collation
    )