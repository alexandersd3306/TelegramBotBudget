import telebot
import webbrowser

bot = telebot.TeleBot('6718438841:AAHIJrlEZzqKUGVOuumZVhN5h26mjV2n7zI')

@bot.message_handler(commands=['git'])
def main(message):
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, вот мой гит хаб')
    webbrowser.open('https://github.com/alexandersd3306')

@bot.message_handler(commands=['telega'])
def main(message):
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, вот телеграм разработчика')
    webbrowser.open('https://t.me/phoenix_wb')

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name}, я твой помощник, и буду тебе помогать мониторить твои расходы и доходы' )

@bot.message_handler(commands=['help'])
def main(message):
    bot.send_message(message.chat.id, '<b>Help</b>:<em> write me the <u>amount</u> of money</em>', parse_mode='html' )
 
@bot.message_handler()
def main(message):
    if message.text.lower() == 'привет' or message.text.lower() == 'приветик': 
        bot.send_message(message.chat.id, f'Привет!, {message.from_user.first_name} {message.from_user.last_name}')
    elif message.text.lower() == 'ид' or message.text.lower() == 'id':
        bot.reply_to(message, f'Вот твой ID!: {message.from_user.id}')



bot.polling(none_stop=True)