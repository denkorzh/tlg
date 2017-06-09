# -*- coding: utf-8 -*-

import credentials
import telebot
import constants
import utils
from utils import VariationsDB
import elements
from telebot import types

bot = telebot.TeleBot(credentials.token)


# handle /cancel
@bot.message_handler(commands=['cancel'])
def cancel_test(message):
    chat_id = message.chat.id
    test_id = utils.get_test_id(chat_id)
    utils.delete_test_id(chat_id)
    vdb = VariationsDB()
    vdb.delete_test_data(test_id)
    vdb.close()


# start conversation
@bot.message_handler(commands=['start'])
def start_message(message):
    utils.set_settings(message.chat.id, constants.default_settings)
    bot.send_message(message.chat.id, constants.greeting_md, reply_markup=elements.inline_keyboard_languages())


# choose user language in conversation start
@bot.callback_query_handler(func=lambda call: call.data[:18] == 'settings_language_')
def set_language(call):
    new_language = call.data.split('_')[-1]
    if new_language in constants.languages:
        utils.change_settings(call.message.chat.id, 'language', new_language)
    bot.answer_callback_query(call.id)


# handle /help
@bot.message_handler(commands=['help'])
def help_message(message):
    user_lang = utils.get_language(message.chat.id)
    bot.send_message(message.chat.id, constants.help_md[user_lang])


# user settings
# handle /settings
@bot.message_handler(commands=['settings'])
def settings_menu(message):
    user_lang = utils.get_language(message.chat.id)
    current_settings = utils.get_settings(message.chat.id)

    bot.send_message(message.chat.id,
                     text=constants.settings_md[user_lang].format(
                         current_settings['language'],
                         current_settings['alpha'],
                         current_settings['epsilon']
                     ),
                     reply_markup=elements.inline_keyboard_settings(),
                     parse_mode='Markdown'
                     )


# change language
@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def change_language(call):
    user_lang = utils.get_language(call.message.chat.id)
    bot.send_message(call.message.chat.id,
                     text=constants.input_language[user_lang],
                     reply_markup=elements.inline_keyboard_languages()
                     )
    bot.answer_callback_query(call.id)


# change alpha
@bot.callback_query_handler(func=lambda call: call.data == 'change_alpha')
def change_alpha(call):
    user_lang = utils.get_language(call.message.chat.id)
    msg = bot.send_message(call.message.chat.id,
                           text=constants.input_alpha[user_lang],
                           )
    bot.register_next_step_handler(msg, process_new_alpha)
    bot.answer_callback_query(call.id)


def process_new_alpha(message):
    global bot
    user_lang = utils.get_language(message.chat.id)
    try:
        new_alpha = float(message.text)
        assert 0 < new_alpha < 1
        utils.change_settings(message.chat.id, 'alpha', new_alpha)
    except:
        msg = bot.send_message(message.chat.id, text=constants.error_again[user_lang])
        bot.register_next_step_handler(msg, process_new_alpha)


# change epsilon
@bot.callback_query_handler(func=lambda call: call.data == 'change_epsilon')
def change_epsilon(call):
    user_lang = utils.get_language(call.message.chat.id)
    msg = bot.send_message(call.message.chat.id,
                           text=constants.input_epsilon[user_lang],
                           )
    bot.register_next_step_handler(msg, process_new_epsilon)
    bot.answer_callback_query(call.id)


def process_new_epsilon(message):
    global bot
    user_lang = utils.get_language(message.chat.id)
    try:
        new_epsilon = float(message.text)
        assert 0 < new_epsilon < 1
        utils.change_settings(message.chat.id, 'epsilon', new_epsilon)
    except:
        msg = bot.send_message(message.chat.id, text=constants.error_again[user_lang])
        bot.register_next_step_handler(msg, process_new_epsilon)


# handle /advert
@bot.message_handler(commands=['advert'])
def show_ad(message):
    keyboard = types.InlineKeyboardMarkup()
    bank_button = types.InlineKeyboardButton(text="Банк", url="www.tinkoff.ru")
    ins_button = types.InlineKeyboardButton(text="Страхование", url="www.tinkoffinsurance.ru")
    loans_button = types.InlineKeyboardButton(text="Потребкредиты", url="tinkoff.loans")
    # keyboard.add(bank_button, ins_button, loans_button)
    keyboard.row(bank_button)
    keyboard.row(ins_button)
    keyboard.row(loans_button)
    bot.send_message(message.chat.id, 'Немного рекламы', reply_markup=keyboard)


@bot.message_handler(commands=['newtest'])
def set_new_test(message):
    utils.set_test_id(message.chat.id, message.message_id)
    user_lang = utils.get_language(message.chat.id)
    msg = bot.send_message(message.chat.id, text=constants.input_control[user_lang])
    bot.register_next_step_handler(msg, process_control_input)


def process_control_input(message):
    vdb = VariationsDB()
    chat_id = message.chat.id
    test_id = utils.get_test_id(chat_id)
    user_lang = utils.get_language(chat_id)
    processed = utils.process_new_variation(vdb, test_id, message.text)
    if not processed:
        msg = bot.send_message(chat_id, text=constants.input_treatment[user_lang].format(1))
        bot.register_next_step_handler(msg, process_treatment_input)
    else:
        msg = bot.send_message(chat_id, text=constants.error_again[user_lang])
        bot.register_next_step_handler(msg, process_control_input)
    vdb.close()


def process_treatment_input(message):
    vdb = VariationsDB()
    chat_id = message.chat.id
    test_id = utils.get_test_id(chat_id)
    user_lang = utils.get_language(chat_id)
    var_num = vdb.get_current_number(test_id)
    if var_num > 1:
        bot.delete_message(chat_id, message.message_id - 2)
    if not utils.process_new_variation(vdb, test_id, message.text):
        # TODO: перепилить кнопки на reply - чтобы ничего кроме команд нельзя было ввести
        bot.send_message(message.chat.id, text='Продолжить?', reply_markup=elements.inline_keyboard_treatments())
    else:
        msg = bot.send_message(message.chat.id, text=constants.error_again[user_lang])
        bot.register_next_step_handler(msg, process_treatment_input)
    vdb.close()


@bot.callback_query_handler(func=lambda call: call.data == 'add_treatment')
def process_additional_treatment(call):
    vdb = VariationsDB()
    test_id = utils.get_test_id(call.message.chat.id)
    user_lang = utils.get_language(call.message.chat.id)
    var_num = vdb.get_current_number(test_id)
    msg = bot.send_message(call.message.chat.id, text=constants.input_treatment[user_lang].format(var_num))
    bot.register_next_step_handler(msg, process_treatment_input)
    bot.answer_callback_query(call.id)
    vdb.close()


@bot.callback_query_handler(func=lambda call: call.data == 'start_test')
def starting_calculus(call):
    vdb = VariationsDB()
    test_id = utils.get_test_id(call.message.chat.id)
    json_data = vdb.get_json(test_id)
    bot.answer_callback_query(call.id)
    bot.send_chat_action(call.message.chat.id, 'typing')
    bot.send_message(call.message.chat.id, text=json_data)  # TODO: сюда вписать начало вычисления теста
    utils.delete_test_id(call.message.chat.id)
    vdb.delete_test_data(test_id)
    vdb.close()


# @bot.message_handler(content_types=["text"])
# def repeat_all_messages(message):
#     mode = utils.get_user_mode(message.chat.id)
#     if mode == 'repeater':
#         bot.send_message(message.chat.id, message.text)
#     elif mode == 'nuff':
#         bot.send_message(message.chat.id, constants.nuff_said, parse_mode='Markdown')


# @bot.callback_query_handler(func=lambda call: True)
# def callback_inline(call):
#     if call.message:
#         if call.data == 'set_repeater_mode':
#             utils.set_user_mode(call.message.chat.id, 'repeater')
#             bot.answer_callback_query(call.id, 'repeater mode on')
#         elif call.data == 'set_nuff_mode':
#             utils.set_user_mode(call.message.chat.id, 'nuff')
#             bot.answer_callback_query(call.id, 'nuff mode on', show_alert=True)


@bot.inline_handler(func=lambda query: not len(query.query))
def empty_query(query):
    hint = 'Введи название режима работы'
    try:
        article = types.InlineQueryResultArticle(id='1',
                                                 title='Бот-безделушка',
                                                 input_message_content=types.InputTextMessageContent(
                                                     message_text='Да введи ж ты наконец!'
                                                 ),
                                                 description=hint
                                                 )
        bot.answer_inline_query(query.id, [article])
    except Exception as e:
        print(e)


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def advice_inline(query):
    repeater_image = 'https://raw.githubusercontent.com/denkorzh/tlg/dev/image/echo.png'
    nuff_image = 'https://raw.githubusercontent.com/denkorzh/tlg/dev/image/silence.jpg'

    repeater_article = types.InlineQueryResultArticle(id='repeater',
                                                      title='Repeater mode',
                                                      input_message_content=types.InputTextMessageContent(
                                                          message_text='/repeater'
                                                      ),
                                                      description='I will repeat everything',
                                                      thumb_url=repeater_image,
                                                      thumb_width=48,
                                                      thumb_height=48
                                                      )
    nuff_article = types.InlineQueryResultArticle(id='nuff',
                                                  title='Nuff said mode',
                                                  input_message_content=types.InputTextMessageContent(
                                                      message_text='/nuff'
                                                  ),
                                                  description='I will say nothing',
                                                  thumb_url=nuff_image,
                                                  thumb_width=61,
                                                  thumb_height=48
                                                  )
    error_article = types.InlineQueryResultArticle(id='error',
                                                   title='I have no such mode',
                                                   input_message_content=types.InputVenueMessageContent(
                                                       latitude=53.25,
                                                       longitude=34.37,
                                                       title='Умник, иди-ка отсюда',
                                                       address='Random place'
                                                   ),
                                                   description='Sorry, I have only two modes',
                                                   )

    inputed = query.query
    length = len(inputed)

    try:
        if inputed == 'repeater'[:length]:
            bot.answer_inline_query(query.id, [repeater_article], 60)
        elif inputed == 'nuff'[:length]:
            bot.answer_inline_query(query.id, [nuff_article], 60)
        else:
            bot.answer_inline_query(query.id, [error_article], 60)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    bot.polling(none_stop=True)
