# -*- coding: utf-8 -*-
import config
import credentials
import telebot
import constants
import utils
from telebot import types


bot = telebot.TeleBot(credentials.token)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, constants.greeting_md, parse_mode='Markdown')


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id, constants.help_md, parse_mode='Markdown')


@bot.message_handler(commands=['repeater', 'nuff'])
def set_mode(message):
    utils.set_user_mode(message.chat.id, message.text[1:])
    bot.send_message(message.chat.id, "Bot mode was set to {}.".format(message.text[1:]))


@bot.message_handler(commands=['advert'])
def show_ad(message):
    keyboard = types.InlineKeyboardMarkup()
    bank_button = types.InlineKeyboardButton(text="Банк", url="www.tinkoff.ru")
    ins_button = types.InlineKeyboardButton(text="Страхование", url="www.tinkoffinsurance.ru")
    loans_button = types.InlineKeyboardButton(text="Потребкредиты", url="www.tinkoff.loans")
    keyboard.add(bank_button, ins_button, loans_button)
    bot.send_message(message.chat.id, 'Немного рекламы', reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    mode = utils.get_user_mode(message.chat.id)
    if mode == 'repeater':
        bot.send_message(message.chat.id, message.text)
    elif mode == 'nuff':
        bot.send_message(message.chat.id, constants.nuff_said, parse_mode='Markdown')


if __name__ == '__main__':
    bot.polling(none_stop=True)
