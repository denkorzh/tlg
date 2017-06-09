# -*- coding: utf-8 -*-

"""
Часто встречающиеся клавиатуры
"""

from telebot import types


def inline_keyboard_languages():
    keyboard = types.InlineKeyboardMarkup()
    rus_button = types.InlineKeyboardButton(text='🇷🇺 Русский', callback_data='settings_language_rus')
    keyboard.add(rus_button)
    return keyboard


def reply_keyboard_digits():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.row(*[types.KeyboardButton(str(i)) for i in range(7, 10)])
    keyboard.row(*[types.KeyboardButton(str(i)) for i in range(4, 7)])
    keyboard.row(*[types.KeyboardButton(str(i)) for i in range(1, 4)])
    keyboard.row(*[types.KeyboardButton(c) for c in ['0', '.']])
    return keyboard


def inline_keyboard_settings():
    keyboard = types.InlineKeyboardMarkup()
    language_button = types.InlineKeyboardButton(text='language', callback_data='change_language')
    alpha_button = types.InlineKeyboardButton(text='α alpha', callback_data='change_alpha')
    epsilon_button = types.InlineKeyboardButton(text='ε epsilon', callback_data='change_epsilon')
    keyboard.add(language_button, alpha_button, epsilon_button)
    return keyboard


def inline_keyboard_treatments():
    keyboard = types.InlineKeyboardMarkup()
    one_more_button = types.InlineKeyboardButton(text='+1', callback_data='add_treatment')
    test_button = types.InlineKeyboardButton(text='Start Test', callback_data='start_test')
    keyboard.add(one_more_button, test_button)
    return keyboard
