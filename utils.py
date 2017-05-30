# -*- coding: utf-8 -*-

import shelve
import config


def set_user_mode(chat_id, mode):
    """
    Записывает в хранилище режим работы для чата
    :param chat_id: id юзера
    :param mode: режим для юзера
    """
    with shelve.open(config.mode_shelve_name) as storage:
        storage[str(chat_id)] = mode


def get_user_mode(chat_id):
    """
    Возвращает режим, установленный юзером
    :param chat_id: id чата
    :return: (str or None) режим
    """
    with shelve.open(config.mode_shelve_name) as storage:
        try:
            answer = storage[str(chat_id)]
            return answer
        except KeyError:
            return None
