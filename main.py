import telebot
import webbrowser
from telebot import types
import sqlite3


user_state = {}
typyy = None
name = None

bot = telebot.TeleBot('6718438841:AAHIJrlEZzqKUGVOuumZVhN5h26mjV2n7zI')

@bot.message_handler(commands=['git'])
def main(message):
        #redirect to github
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, вот мой гит хаб')
    webbrowser.open('https://github.com/alexandersd3306')

@bot.message_handler(commands=['telega'])
def main(message):
    #redirect to site(telegram)
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, вот телеграм разработчика')
    webbrowser.open('https://t.me/phoenix_wb')

@bot.message_handler(commands=['start'])
def start(message):
    #db connect
    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, user_name varchar(200), Data date, type varchar(50), sum int)')
    conn.commit()
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, сейчас тебя зарегистрируем')
    bot.register_next_step_handler(message, user_name)

    cur.close()
    conn.close()



#db function 
def user_name(message):
    global name 
    name = message.from_user.first_name
    markup = types.ReplyKeyboardMarkup()
    btn2 = types.KeyboardButton('Доходы')
    btn3 = types.KeyboardButton('Расходы')
    markup.add
    bot.send_message(message.chat.id,'Введите тип транзакции', reply_markup=markup)
    bot.register_next_step_handler(message, type)

def type(message):
    global typyy
    typyy = message.text.strip()
    bot.send_message(message.chat.id,'Введите тип транзакции')
    bot.register_next_step_handler(message, summa)

def summa(message):
    sum = message.text.strip()


    conn = sqlite3.connect('information.sql')
    cur = conn.cursor()
    cur.execute(f'INSERT INTO users (user_name, type, sum) VALUES ({name}, {typyy}, {sum})')
    conn.commit()
    cur.close()
    conn.close()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Список пользователей', callback_data='all_users'))
    bot.send_message(message.chat.id, 'Вы успешно зарегистрировались!', reply_markup=markup)


        
    



# keyboard loading 
@bot.message_handler()
def mainmenu(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Личный кабинет')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Добавить')
    btn3 = types.KeyboardButton('Узнать ID')
    markup.add(types.InlineKeyboardButton('Список пользователей', callback_data='all_users'))
    bot.send_message(message.chat.id,'Вот что я могу', reply_markup=markup)

    user_state[message.chat.id] = "waiting_for_click"


@bot.message_handler(func=lambda message: user_state.get(message.chat.id) == "waiting_for_click")
def on_click(message):
    if message.text == 'Личный кабинет':
        bot.send_message(message.chat.id, 'Личный кабинет')
    elif message.text == 'Добавить':
        bot.send_message(message.chat.id, 'Добавить')
    elif message.text == 'Узнать ID':
        bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name} {message.from_user.last_name}, Вот твой ID!: {message.from_user.id}')
    
    user_state[message.chat.id] = "waiting_for_click"
        
@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b>:I am your assistant, and I will help you monitor your expenses and income, <em> write me the <u>amount</u> of money</em>', parse_mode='html' )

@bot.message_handler(content_types=['photo'])
def main(message):
    bot.reply_to(message, '<b>Hello</b>, i can not open your image', parse_mode='html' )
 
@bot.message_handler()
def main(message):
    if message.text.lower() == 'привет' or message.text.lower() == 'приветик': 
        bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name} {message.from_user.last_name}')
    elif message.text.lower() == 'ид' or message.text.lower() == 'id':
        bot.reply_to(message, f'Привет!, {message.from_user.first_name} {message.from_user.last_name}, Вот твой ID!: {message.from_user.id}')

bot.polling(none_stop=True)