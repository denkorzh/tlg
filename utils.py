# -*- coding: utf-8 -*-

import shelve
import config


def set_shelve_value(shelf, key, value):
    """
    Делает запись в хранилизе
    :param shelf: имя хранилища
    :param key: ключ
    :param value: значение
    """
    with shelve.open(shelf) as storage:
        # print('setting...')
        storage[str(key)] = value


def get_shelve_value(shelf, key):
    """
    Возвращает запись из хранилища по ключу
    :param shelf: имя хранилища
    :param key: ключ
    :return: запись, если она существует, иначе None
    """
    with shelve.open(shelf) as storage:
        try:
            value = storage[str(key)]
            return value
        except KeyError:
            return None


def set_user_mode(chat_id, mode):
    """
    Записывает в хранилище режим работы для чата
    :param chat_id: id юзера
    :param mode: режим для юзера
    """
    set_shelve_value(config.mode_shelve_name, chat_id, mode)


def get_user_mode(chat_id):
    """
    Возвращает режим, установленный юзером
    :param chat_id: id чата
    :return: (str or None) режим
    """
    return get_shelve_value(config.mode_shelve_name, chat_id)


def set_test_id(chat_id, message_id):
    """
    Записывает в хранилище id нового теста пользователя.
    :param chat_id: id юзера
    :param message_id: id сообщения, в котором запросили новый тест
    """
    with shelve.open(config.test_id_shelve) as storage:
        storage[str(chat_id)] = str(chat_id) + '_' + str(message_id)


def get_test_id(chat_id):
    """
    Возвращает id текущего теста для пользователя.
    :param chat_id: id юзера
    :return: id теста
    """
    with shelve.open(config.test_id_shelve) as storage:
        try:
            test_id = storage[str(chat_id)]
            return test_id
        except KeyError:
            return None


def set_settings(chat_id, settings):
    """
    Записывает в хранилище настройки для конкретного юзера.
    :param chat_id: id чата 
    :param dict settings: настройки
    """
    set_shelve_value(config.settings_shelve, chat_id, settings)


def get_settings(chat_id):
    """
    Возвращает словарь настроек для конкретного юзера.
    :param chat_id: id юзера
    :return: словарь настроек
    """
    return get_shelve_value(config.settings_shelve, chat_id)


def change_settings(chat_id, key, value):
    """
    Изменяет настройку по ключу.
    :param chat_id: id юзера
    :param key: название настройки
    :param value: новое значение настройки
    """
    import constants
    settings = get_settings(chat_id)
    if not settings:
        settings = constants.default_settings
    settings[key] = value
    set_settings(chat_id, settings)


def get_language(chat_id):
    """
    Получает язык пользователя
    :param chat_id: id юзера
    :return: язык пользователя
    """
    return get_settings(chat_id)['language']
