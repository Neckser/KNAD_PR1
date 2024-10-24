from qrcode.console_scripts import error_correction
import wifi_qrcode_generator.generator
import io
from telebot import *
import qrcode
import sqlite3
import datetime

bot=TeleBot('8024489123:AAGcKDNvCpVEA4zdPwgTIgd91f-8lvS8VIs')

connection = sqlite3.connect('QR_database')
cursor=connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
number INTEGER,
username TEXT,
user_ask TEXT,
state TEXT,
execution TEXT,
time DATETIME
)
''')
connection.commit()
connection.close()



Create_button=types.KeyboardButton('Создать QR-код')
RE_button=types.KeyboardButton('Перезапустить бота')
link = types.KeyboardButton('QR на Ссылку')
wifi = types.KeyboardButton('QR на WI-FI')
texty = types.KeyboardButton('QR на Текст')

one_murkup=types.ReplyKeyboardMarkup(resize_keyboard=True)
choosing=types.ReplyKeyboardMarkup(resize_keyboard=True)

one_murkup.add(RE_button,Create_button)
choosing.add(link,wifi,texty)

login=''
password=''

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,'Выберите что вы хотите делать',reply_markup=one_murkup)

@bot.message_handler(func= lambda message: message.text=='Создать QR-код')
def user_give__qrdata(message):
    bot.send_message(message.chat.id,'Выберите какой тип qr кода вы хотите сделать',reply_markup=choosing)

@bot.message_handler(func=lambda message: message.text == 'QR на Ссылку')
def link_data(message):
    bot.send_message(message.chat.id,'Отправьте ссылку')
    bot.register_next_step_handler(message,qr_create_link)

def qr_create_link(message):
    qr_data = message.text
    state = 'Not_created'
    execut='Нет ошибок'
    try:
        qr = qrcode.QRCode(
            version =1,
            error_correction = qrcode.constants.ERROR_CORRECT_L,
            box_size = 10,
            border = 4
        )
        qr.add_data(qr_data)
        qr.make(fit = True)
        img = qr.make_image(fill= 'black', back_color = 'White')

        with io.BytesIO() as output:
            img.save(output, format='PNG')
            img_bytes = output.getvalue()

        bot.send_photo(message.chat.id, img_bytes, caption=f'''Ваш QR-код на {qr_data}
-----''')
        state = 'Good'
    except Exception as e:
        state = 'Bad'
        execut=str(e)
        bot.send_message(message.chat.id,'Произошла ошибка, QR код мог не создасться, попробуйте ещё раз')
    connection = sqlite3.connect('QR_database')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (number,username,user_ask,state,execution,time) VALUES (?,?,?,?,?,?)',(message.chat.id, message.from_user.username,qr_data,state,execut,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, 'Чтобы снова сгенерировать QR код нажмите кнопку⬇️⬇️')



@bot.message_handler(func = lambda message: message.text=='QR на WI-FI')
def wifi_data(message):
    bot.send_message(message.chat.id,'Напишите Название WIFI')
    bot.register_next_step_handler(message,wifi_login)
def wifi_login(message):
    global login
    login=message.text
    bot.send_message(message.chat.id,'Теперь напишите пароль для этой wifi сети')
    bot.register_next_step_handler(message,wifi_password)
def wifi_password(message):
    global password
    password=message.text
    qr_wifi(message)

def qr_wifi(message):
    try:
        QR = wifi_qrcode_generator.generator.wifi_qrcode(ssid=login, hidden=False, authentication_type='WPA',password=password)
        state = 'Not_created'
        execut = 'Нет ошибок'
        img = QR.make_image(fill='black', back_color='White')
        with io.BytesIO() as output:
            img.save(output, format='PNG')
            img_bytes = output.getvalue()
bot.send_photo(message.chat.id, img_bytes, caption=f'''Ваш QR-код на ваш WI-FI:{login}
     -----''')
        state = 'Good'
    except Exception as e:
        state = 'Bad'
        execut = str(e)
        bot.send_message(message.chat.id,
                         'Произошла ошибка, QR код мог не создасться, попробуйте ещё раз')
    connection = sqlite3.connect('QR_database')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (number,username,user_ask,state,execution,time) VALUES (?,?,?,?,?,?)', (
        message.chat.id, message.from_user.username,str(login+'/'+password), state, execut,
        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, 'Чтобы снова сгенерировать QR код нажмите кнопку⬇️⬇️')




@bot.message_handler(func = lambda message: message.text == 'QR на Текст')
def text_data(message):
    bot.send_message(message.chat.id,'Напишите текст,который вы хотите сохранить в QR коде')
    bot.register_next_step_handler(message,qr_text)

def qr_text(message):
    qr_data = message.text
    state = 'Not_created'
    execut = 'Нет ошибок'
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='White')

        with io.BytesIO() as output:
            img.save(output, format='PNG')
            img_bytes = output.getvalue()

        bot.send_photo(message.chat.id, img_bytes, caption=f'''Ваш QR-код на ваш текст:{qr_data}
    -----''')
        state = 'Good'
    except Exception as e:
        state = 'Bad'
        execut = str(e)
        bot.send_message(message.chat.id,
                         'Произошла ошибка, QR код мог не создасться, попробуйте ещё раз')
    connection = sqlite3.connect('QR_database')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO users (number,username,user_ask,state,execution,time) VALUES (?,?,?,?,?,?)', (
    message.chat.id, message.from_user.username, qr_data, state, execut,
    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    connection.commit()
    connection.close()
    bot.send_message(message.chat.id, 'Чтобы снова сгенерировать QR код нажмите кнопку⬇️⬇️')


@bot.message_handler(func= lambda message: message.text=='Перезапустить бота')
def re(message):
    start(message)

'''
       \`-._           __
        \\  -..____,.'  .
         :`.         /    \`.
         :  )       :      : \
          ;'        '   ;  |  :
          )..      .. .:.`.;  :
         /::...  .:::...   ` ;
         ; _ '    __        /:\
         :o>   /\o_>      ;:. .
        -. ;   ..--- /:.   \
        === \_/   ;=====_.':.     ;
         ,/'`--'...`--....        ;
              ;                    ;
            .'                      ;
          .'                        ;
        .'     ..     ,      .       ;
       :       ::..  /      ;::.     |
      /      `.;::.  |       ;:..    ;
     :         |:.   :       ;:.    ;
     :         ::     ;:..   |.    ;
      :       :;      :::....|     |
      /\     ,/ \      ;:::::;     ;
    .:. \:..|    :     ; '.--|     ;
   ::.  :''  `-.,,;     ;'   ;     ;
.-'. _.'\      / `;      \,__:      \
`---'    `----'   ;      /    \,.,,,/
                   ----     
'''


bot.polling(non_stop=True)