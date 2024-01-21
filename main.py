import telebot
import webbrowser
from telebot import types
import sqlite3
from datetime import datetime

# Переменная для хранения состояний пользователей
user_state = {}

bot = telebot.TeleBot('6718438841:AAHIJrlEZzqKUGVOuumZVhN5h26mjV2n7zI')

@bot.message_handler(commands=['git'])
def on_git_command(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, вот мой GitHub')
    webbrowser.open('https://github.com/alexandersd3306')

@bot.message_handler(commands=['telega'])
def on_telega_command(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, вот мой Telegram')
    webbrowser.open('https://t.me/phoenix_wb')

@bot.message_handler(commands=['start'])
def on_start_command(message):
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    # Создание таблицы, если она еще не существует
    cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, user_name VARCHAR(200), Data DATE, type VARCHAR(50), sum INTEGER)')
    conn.commit()

    # Вставка нового пользователя с значениями по умолчанию
    user_name = message.from_user.first_name
    data = datetime.now().strftime('%Y-%m-%d')
    cur.execute('INSERT INTO users (user_name, Data, type, sum) VALUES (?, ?, ?, ?)', (user_name, data, '', None))
    conn.commit()

    bot.send_message(message.chat.id, f'Привет, {user_name}! Ты зарегистрирован.')

    # Закрытие соединения с базой данных
    cur.close()
    conn.close()

# Обработчик команды /create
@bot.message_handler(commands=['create'])
def create_handler(message):
    # Начало цепочки - спросить у пользователя, что он хочет добавить
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Доходы')
    btn2 = types.KeyboardButton('Расходы')
    btn3 = types.KeyboardButton('Личный кабинет')
    markup.row(btn1, btn2)
    markup.add(btn3)
    bot.send_message(message.chat.id, '<b>Выберите: </b>', reply_markup=markup, parse_mode="html" )
    user_state[message.chat.id] = "waiting_for_type"



@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_click")
def on_click(message):
    if message.text == 'Личный кабинет':
        # Отобразим кнопки "Расходы" и "Доходы" в Личном кабинете
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Расходы')
        btn2 = types.KeyboardButton('Доходы')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, 'Выберите тип транзакции в Личном кабинете', reply_markup=markup)
        
        # Установим состояние "waiting_for_type" для Личного кабинета
        user_state[message.chat.id] = "waiting_for_type_personal"
    else:
        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Расходы')
        btn2 = types.KeyboardButton('Доходы')
        markup.row(btn1, btn2)
        bot.send_message(message.chat.id, 'Выберите тип транзакции', reply_markup=markup)
        user_state[message.chat.id] = "waiting_for_type"
        
# Обработчик для выбора типа транзакции
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_type_personal")
def on_type_personal(message):
    # Обработка выбора типа транзакции в Личном кабинете
    user_state[message.chat.id] = "waiting_for_sum"
    user_state['type'] = message.text.strip()

    # Выводим все транзакции пользователя с выбранным типом
    user_id = message.from_user.id
    transactions = get_user_transactions(user_id, user_state['type'])

    if transactions:
        response = f"Транзакции {message.from_user.first_name} {message.from_user.last_name} ({user_id}) с типом '{user_state['type']}':\n"
        for transaction in transactions:
            response += f"ID: {transaction[0]}, Дата: {transaction[1]}, Сумма: {transaction[2]}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, f"У вас пока нет транзакций с типом {user_state['type']}")

# Обработчик для ввода суммы
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_sum")
def enter_sum_handler(message):
    # Сохранение введенной суммы в базу данных
    current_date = datetime.now().strftime('%Y-%m-%d')
    sum_value = message.text.strip()
    user_id = message.from_user.id
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (user_name, type, sum, Data) VALUES (?, ?, ?, ?)', (message.from_user.first_name, user_state['type'], sum_value, current_date))
    conn.commit()
    cur.close()
    conn.close()

    # Завершение цепочки и возврат в начальное состояние
    bot.send_message(message.chat.id, 'Транзакция успешно добавлена в базу данных!')
    user_state[message.chat.id] = "waiting_for_click"


# Обработчик для выбора типа транзакции вне Личного кабинета
@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_type")
def on_type(message):
    # Обработка выбора типа транзакции вне Личного кабинета
    user_state[message.chat.id] = "waiting_for_sum"
    user_state['type'] = message.text.strip()

    # Выводим все транзакции пользователя с выбранным типом
    user_id = message.from_user.id
    transactions = get_user_transactions(user_id, user_state['type'])

    if transactions:
        response = f"Транзакции {message.from_user.first_name} {message.from_user.last_name} ({user_id}) с типом '{user_state['type']}':\n"
        for transaction in transactions:
            response += f"ID: {transaction[0]}, Дата: {transaction[1]}, Сумма: {transaction[2]}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, f"У вас пока нет транзакций с типом {user_state['type']}")

# Функция для получения транзакций пользователя по ID и типу
def get_user_transactions(user_id, transaction_type):
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    cur.execute('SELECT id, Data,type, sum FROM users WHERE id=? AND type=?', (user_id, transaction_type))
    transactions = cur.fetchall()
    conn.close()
    return transactions


@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b>:I am your assistant, and I will help you monitor your expenses and income, <em> write me the <u>amount</u> of money</em>', parse_mode='html' )

@bot.message_handler(content_types=['photo'])
def main(message):
    bot.reply_to(message, '<b>Hello</b>, i can not open your image', parse_mode='html' )


@bot.message_handler(commands=['status'])
def get_status(message):
    # Подключение к базе данных
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()

    # Выполнение запроса
    cur.execute('SELECT * FROM users')
    rows = cur.fetchall()

    # Закрытие соединения с базой данных
    cur.close()
    conn.close()

    # Отправка сообщения с информацией из базы данных
    if rows:
        response = "Информация из базы данных:\n"
        for row in rows:
            response += f"ID: {row[0]}, Имя: {row[1]}, Дата: {row[2]}, Тип: {row[3]}, Сумма: {row[4]}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "База данных пуста.")


bot.polling(none_stop=True)
