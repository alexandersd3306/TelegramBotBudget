import telebot
import webbrowser
from telebot import types
import sqlite3
from datetime import datetime

user_state = {} # Переменная для хранения состояний пользователей
bot = telebot.TeleBot('6718438841:AAHIJrlEZzqKUGVOuumZVhN5h26mjV2n7zI') # api bot 

conn = sqlite3.connect('information.sql')
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name VARCHAR(200),
        Data DATE,
        type VARCHAR(50),
        sum INTEGER
    );
''')

conn.commit()
conn.close()


@bot.message_handler(commands=['start'])
def on_start_command(message):
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    user_name = message.from_user.first_name     # Проверка, зарегистрирован ли пользователь
    cur.execute('SELECT id FROM users WHERE user_name = ?', (user_name,))
    existing_user = cur.fetchone()

    if existing_user:
        bot.send_message(message.chat.id, f'Привет, {user_name}! Ты уже зарегистрирован')
    else:
        cur.execute('CREATE TABLE IF NOT EXISTS users (id PRIMARY KEY AUTOINCREMENT, user_name VARCHAR(200), Data DATE, type VARCHAR(50), sum INTEGER)')
        conn.commit()        # Создание таблицы, если она еще не существует

        data = datetime.now().strftime('%Y-%m-%d')        # Вставка нового пользователя с значениями по умолчанию
        cur.execute('INSERT INTO users (user_name, Data, type, sum) VALUES (?, ?, ?, ?)', (user_name, data, 'None', None))
        conn.commit()

        bot.send_message(message.chat.id, f'Привет, {user_name}!Поздравляю, ты зарегистрирован')
    cur.close()
    conn.close()

@bot.message_handler(commands=['add'])
def on_any_message(message):# При сообщении /add открываем меню "Доходы" и "Расходы"
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Доходы')
    btn2 = types.KeyboardButton('Расходы')
    markup.row(btn1, btn2)
    bot.send_message(message.chat.id, '<b>Выберите: </b>', reply_markup=markup, parse_mode="html" )
    user_state[message.chat.id] = "waiting_for_click"


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_click")
def on_click(message):
    if message.text in ['Доходы', 'Расходы']: # Обрабатываем выбор между Доходами и Расходами
        user_state[message.chat.id] = "waiting_for_type"
        user_state['type'] = message.text.strip()
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, f'Отлично! Вы выбрали {user_state["type"]}. Теперь введите сумму:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f'Введено сообщение, повторите его: {message.text}')
        user_state[message.chat.id] = message.text

@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_type") # Обработчик для ввода суммы
def enter_sum_handler(message): # Сохранение введенной суммы в базу данных
    current_date = datetime.now().strftime('%Y-%m-%d')
    sum_value = message.text.strip()
    user_id = message.from_user.id
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (user_name, type, sum, Data) VALUES (?, ?, ?, ?)', (message.from_user.first_name, user_state['type'], sum_value, current_date))
    conn.commit()
    cur.close()
    bot.send_message(message.chat.id, f'Транзакция успешно добавлена в базу данных! Теперь вы можете продолжить', reply_markup=create_main_keyboard())
    user_state[message.chat.id] = "waiting_for_click"


def create_main_keyboard(): # Функция для создания клавиатуры выбора между Доходами и Расходами
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Доходы')
    btn2 = types.KeyboardButton('Расходы')
    markup.add(btn1, btn2)
    return markup




@bot.message_handler(commands=['status'])
def get_status(message):# Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    income_button = types.KeyboardButton("Доходы")
    expense_button = types.KeyboardButton("Расходы")
    markup.add(income_button, expense_button)

    bot.send_message(message.chat.id, "Выберите тип информации:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['Доходы', 'Расходы'])
def handle_income_expense(message):
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    transaction_type = message.text    # Получаем тип (доходы или расходы) из сообщения пользователя

    cur.execute('SELECT * FROM users WHERE type = ?', (transaction_type,))     # Выполняем запрос к базе данных с учетом выбранного типа
    rows = cur.fetchall()

    cur.close()
    conn.close()

    if rows:
        response = f"Информация о {transaction_type.lower()}:\n"    # Отправка сообщения с информацией из базы данных
        for row in rows:
            response += f"ID: {row[0]}, Имя: {row[1]}, Дата: {row[2]}, Тип: {row[3]}, Сумма: {row[4]}\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, f"Нет информации о {transaction_type.lower()}")

    # Убираем клавиатуру после использования
    sent_message = bot.send_message(message.chat.id, "Клавиатура скрыта", reply_markup=types.ReplyKeyboardRemove())
    bot.delete_message(message.chat.id, sent_message.message_id)



@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b>:I am your assistant, and I will help you monitor your expenses and income, <em> write me the <u>amount</u> of money</em>', parse_mode='html' )

@bot.message_handler(content_types=['photo'])
def main(message):
    bot.reply_to(message, '<b>Hello</b>, i can not open your image', parse_mode='html' )

@bot.message_handler(commands=['git'])
def on_git_command(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, вот мой GitHub')
    webbrowser.open('https://github.com/alexandersd3306')

@bot.message_handler(commands=['telega'])
def on_telega_command(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}, вот мой Telegram')
    webbrowser.open('https://t.me/phoenix_wb')


bot.polling(none_stop=True)