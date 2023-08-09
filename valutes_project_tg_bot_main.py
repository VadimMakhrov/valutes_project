import telebot
from telebot import types
from valutes_project_tg_token import tg_token
import valutes_project_settings as prset
from valutes_project_lib import drawing_to_tg

bot = telebot.TeleBot(token=tg_token,parse_mode=None)

params_current: dict = {'valutes':prset.params_default['button_valutes'], \
                'period':prset.params_default['button_period'], \
                'show_min_max_plot':prset.params_default['show_min_max'], \
                'night_theme':prset.params_default['night_theme']}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton('Valutes')
    markup.add(btn)
    bot.send_message(message.chat.id, text='Hello, {0.first_name}'.format(message.from_user),reply_markup=markup)
@bot.message_handler(content_types=['text'])
def func(message):
    for i in prset.buttons_first_valutes:
        # кнопки с валютами
        if (message.text == i):
            params_current['valutes'] = i
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            default = types.KeyboardButton('Default')
            markup.add(default, *[types.KeyboardButton(btn) for btn in prset.buttons_second_times])
            bot.send_message(message.chat.id, text='Now {}'.format(params_current['valutes']), reply_markup=markup)
    for i in prset.buttons_second_times:
        # кнопки с периодами
        if (message.text == i):
            params_current['period'] = i
            drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                          period=params_current['period'], \
                          show_min_max_plot=params_current['show_min_max_plot'], \
                          night_theme=params_current['night_theme'])
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            if params_current['night_theme']:
                btn1 = types.KeyboardButton('Night ON')
            else:
                btn1 = types.KeyboardButton('Night OFF')
            btn2 = types.KeyboardButton('Drawing')
            btn3 = types.KeyboardButton('Change parameters')
            back = types.KeyboardButton('Come back')
            markup.add(btn1, btn2, btn3, back)
            bot.send_message(message.chat.id, text='Period {}'.format(params_current['period']), reply_markup=markup)
    if (message.text == 'Valutes'):
        drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                         period=params_current['period'], \
                         show_min_max_plot=params_current['show_min_max_plot'], \
                         night_theme=params_current['night_theme'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Night OFF')
        btn2 = types.KeyboardButton('Drawing')
        btn3 = types.KeyboardButton('Change parameters')
        back = types.KeyboardButton('Come back')
        markup.add(btn1, btn2, btn3, back)
        text:str = 'Night OFF/Night ON - change plot theme\nDrawing - Drawing plot\nChange parameters - you can choose your parameters\nCome back - back to the main menu'
        bot.send_message(message.chat.id, text=text, reply_markup=markup)
    elif (message.text == 'Drawing'):
        drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                         period=params_current['period'], \
                         show_min_max_plot=params_current['show_min_max_plot'], \
                         night_theme=params_current['night_theme'])
    elif (message.text == 'Night OFF'):
        params_current['night_theme'] = True
        drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                         period=params_current['period'], \
                         show_min_max_plot=params_current['show_min_max_plot'], \
                         night_theme=params_current['night_theme'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Night ON')
        btn2 = types.KeyboardButton('Drawing')
        btn3 = types.KeyboardButton('Change parameters')
        back = types.KeyboardButton('Come back')
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text='Night theme ON', reply_markup=markup)
    elif (message.text == 'Night ON'):
        params_current['night_theme'] = False
        drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                         period=params_current['period'], \
                         show_min_max_plot=params_current['show_min_max_plot'], \
                         night_theme=params_current['night_theme'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton('Night OFF')
        btn2 = types.KeyboardButton('Drawing')
        btn3 = types.KeyboardButton('Change parameters')
        back = types.KeyboardButton('Come back')
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text='Night theme OFF', reply_markup=markup)
    elif (message.text == 'Change parameters'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        default = types.KeyboardButton('Default')
        markup.add(default, *[types.KeyboardButton(btn) for btn in prset.buttons_first_valutes])
        bot.send_message(message.chat.id, text='Choose valute', reply_markup=markup)
    elif (message.text == 'Default'):
        params_current['valutes'] = prset.params_default['button_valutes']
        params_current['period'] = prset.params_default['button_period']
        drawing_to_tg(message, bot=bot, valutes=params_current['valutes'], \
                         period=params_current['period'], \
                         show_min_max_plot=params_current['show_min_max_plot'], \
                         night_theme=params_current['night_theme'])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if params_current['night_theme']:
            btn1 = types.KeyboardButton('Night ON')
        else:
            btn1 = types.KeyboardButton('Night OFF')
        btn2 = types.KeyboardButton('Drawing')
        btn3 = types.KeyboardButton('Change parameters')
        back = types.KeyboardButton('Come back')
        markup.add(btn1, btn2, btn3, back)
        bot.send_message(message.chat.id, text='Set default parameters', reply_markup=markup)
    elif (message.text == 'Come back'):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn = types.KeyboardButton('Valutes')
        markup.add(btn)
        bot.send_message(message.chat.id, text='You come back', reply_markup=markup)

bot.infinity_polling()
