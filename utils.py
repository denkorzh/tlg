# -*- coding: utf-8 -*-

import shelve
import config
import sqlite3


def set_shelve_value(shelf, key, value):
    """
    Делает запись в хранилизе
    :param shelf: имя хранилища
    :param key: ключ
    :param value: значение
    """
    with shelve.open(shelf) as storage:
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


def delete_shelve_value(shelf, key):
    """
    Удаляет запись из хранилища по ключу
    :param shelf: имя хранилища
    :param key: ключ
    """
    with shelve.open(shelf) as storage:
        try:
            del storage[str(key)]
        except KeyError:
            pass


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


def delete_test_id(chat_id):
    """
    Удаляет запись о текущет тесте для юзера
    :param chat_id: id юзера
    """
    delete_shelve_value(config.test_id_shelve, chat_id)


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


class SQLighter:
    """
    Класс для работы с БД, содержащей вариации
    """
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def insert_rows(self, table, rows):
        """
        Позволяет вставить в таблицу table массив строк rows
        """
        query = "insert into {} values ("
        query += "?," * len(rows[0])
        query = query[:-1] + ")"
        query = query.format(table)

        self.cursor.executemany(query, rows)
        self.connection.commit()

    def delete_rows_by_key(self, table, key, value):
        """
        Удаляет из таблицы table все строки, в которых поле key принимает значение value
        
        :type value: Iterable
        """
        query = """
        delete from {}
        where {} = ?
        """.format(table, key)
        self.cursor.execute(query, value)
        self.connection.commit()

    def count_rows(self, table, key, value):
        """
        Выдает количество строк в таблице table, в которых поле key принимает значение value
        """
        query = """
        select count(*)
        from {}
        where {} = ?
        """.format(table, key)
        response = self.cursor.execute(query, [value]).fetchall()
        return int(response[0][0])

    def close(self):
        self.connection.close()


class VariationsDB(SQLighter):
    """
    Класс для работы с БД, содержащей вариации
    """
    def __init__(self):
        super(VariationsDB, self).__init__(config.variations_db)

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.close()

    def get_current_number(self, test_id):
        """
        Возвращает текущее количество вариаций в тесте
        :param test_id: id теста
        """
        return self.count_rows('variations', 'test_id', test_id)

    def insert_variation(self, test_id, total, success):
        """
        Вставить очередную вариацию в таблицу
        """
        num_var = self.get_current_number(test_id)
        self.insert_rows('variations', [(test_id, num_var, total, success)])

    def delete_test_data(self, test_id):
        """
        Удалить все записи о тесте
        """
        self.delete_rows_by_key('variations', 'test_id', [test_id])

    def get_json(self, test_id):
        """
        Возвращает json со всеми вариациями теста
        """
        import json

        query = """
        select variation_num, total, success
        from variations
        where test_id = ?
        order by variation_num asc
        """

        response = self.cursor.execute(query, [test_id]).fetchall()
        d = dict()

        for row in response:
            variation_num, total, success = row
            d[str(variation_num)] = {'total': int(total),
                                     'success': int(success),
                                     'data': None,
                                     'group': None
                                     }
        return json.dumps(d)


def process_new_variation(db: VariationsDB, test_id: str, s: str):
    """
    Обрабатывает пользовательский ввод и вносит вариацию в БД
    :param db: БД с вариациями
    :param test_id: id теста
    :param s: пользовательский ввод
    """

    try:
        s = list(map(int, s.split()))
    except Exception as e:
        print(e)
        return 1

    total, success = max(s[0], s[1]), min(s[0], s[1])

    try:
        db.insert_variation(test_id, total, success)
        return 0
    except Exception as e:
        print(e)
        return 3
