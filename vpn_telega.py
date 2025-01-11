import mysql.connector
from mysql.connector import Error
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

class DatabaseHandler:
    def __init__(self, host, user, password, database, port=3307, charset='utf8mb4', collation='utf8mb4_unicode_ci'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.charset = charset
        self.collation = collation
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                charset=self.charset,
                collation=self.collation
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error: {e}")

    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Disconnected from MySQL database")

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def fetch_one(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

    def fetch_all(self, query, params=None):
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()

class UserHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def check_user(self, telegram_id):
        query = "SELECT * FROM users WHERE telegram_id = %s"
        return self.db_handler.fetch_one(query, (telegram_id,))

    def add_user(self, telegram_id, username):
        query = "INSERT INTO users (telegram_id, username) VALUES (%s, %s)"
        self.db_handler.execute_query(query, (telegram_id, username))

class MenuHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    async def show_menu(self, update: Update, context: CallbackContext):
        menu = ReplyKeyboardMarkup([['Мои ключи', 'Продлить'], ['Подключить VPN', 'Помощь']], resize_keyboard=True)
        await update.message.reply_text("Выберите пункт меню:", reply_markup=menu)

    async def handle_menu(self, update: Update, context: CallbackContext):
        text = update.message.text
        if text == 'Мои ключи':
            await self.show_my_keys(update, context)
        elif text == 'Продлить':
            await self.show_extend_menu(update, context)
        elif text == 'Подключить VPN':
            await self.show_vpn_connect(update, context)
        elif text == 'Помощь':
            await self.show_help(update, context)

    async def show_my_keys(self, update: Update, context: CallbackContext):
        telegram_id = update.message.from_user.id
        query = "SELECT vpn_key FROM vpn_access_keys WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = %s)"
        keys = self.db_handler.fetch_all(query, (telegram_id,))
        if keys:
            message = "Ваши ключи:\n" + "\n".join([key[0] for key in keys])
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("У вас отсутствуют ключи", reply_markup=ReplyKeyboardMarkup([['Получить ключ']], resize_keyboard=True))

    async def show_extend_menu(self, update: Update, context: CallbackContext):
        menu = ReplyKeyboardMarkup([['1 месяц - 150 руб', '3 месяца - 400 руб'], ['6 месяцев - 715 руб', '1 год - 1200 руб']], resize_keyboard=True)
        await update.message.reply_text("Выберите срок продления:", reply_markup=menu)

    async def show_vpn_connect(self, update: Update, context: CallbackContext):
        telegram_id = update.message.from_user.id
        query = "SELECT vpn_key FROM vpn_access_keys WHERE user_id = (SELECT user_id FROM users WHERE telegram_id = %s)"
        keys = self.db_handler.fetch_all(query, (telegram_id,))
        if keys:
            await update.message.reply_text(f"У вас уже есть {len(keys)} ключей", reply_markup=ReplyKeyboardMarkup([['Заказать еще ключ']], resize_keyboard=True))
        else:
            await update.message.reply_text("У вас отсутствуют ключи", reply_markup=ReplyKeyboardMarkup([['Получить ключ']], resize_keyboard=True))

    async def show_help(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Как подключиться к VPN: ...")

class Bot:
    def __init__(self, token, db_handler):
        self.token = token
        self.db_handler = db_handler
        self.user_handler = UserHandler(db_handler)
        self.menu_handler = MenuHandler(db_handler)

    async def start(self, update: Update, context: CallbackContext):
        telegram_id = update.message.from_user.id
        username = update.message.from_user.username
        user = self.user_handler.check_user(telegram_id)
        if not user:
            self.user_handler.add_user(telegram_id, username)
        await self.menu_handler.show_menu(update, context)

    async def handle_message(self, update: Update, context: CallbackContext):
        await self.menu_handler.handle_menu(update, context)

    def run(self):
        application = Application.builder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        application.run_polling()

if __name__ == "__main__":
    db_handler = DatabaseHandler(
        host="localhost",
        user="root",
        password="",
        database="vpn_telega",
        port=3307,
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )
    db_handler.connect()

    bot = Bot(token="7753890665:AAHcwEnhlPkjN2XvBJWbmd1mOEL4Z39hmtM", db_handler=db_handler)
    bot.run()

    db_handler.disconnect()