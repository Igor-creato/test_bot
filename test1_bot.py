from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import mysql.connector

# Функция для подключения к MariaDB
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",  # Хост базы данных
        port=3307,         # Порт базы данных (по умолчанию 3306)
        user="root",       # Имя пользователя базы данных
        password="",  # Пароль пользователя базы данных
        database="telegram_bot",    # Имя базы данных
        charset="utf8mb4",         # Указываем кодировку
        collation="utf8mb4_general_ci"  # Указываем поддерживаемую collation
    )

# Функция для сохранения ID пользователя в базу данных
def save_user_id(user_id):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()
        query = "INSERT INTO users (user_id) VALUES (%s)"
        cursor.execute(query, (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        print("ID пользователя успешно сохранен в базу данных.")
    except mysql.connector.Error as err:
        print(f"Ошибка при сохранении ID пользователя: {err}")

# Функция, которая будет вызываться при команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    await update.message.reply_text(f'Ваш ID: {user_id}')

    # Сохраняем ID пользователя в базу данных
    save_user_id(user_id)

def main() -> None:
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = Application.builder().token("7753890665:AAHcwEnhlPkjN2XvBJWbmd1mOEL4Z39hmtM").build()

    # Регистрируем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()