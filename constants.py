# -*- coding: utf-8 -*-

greeting_md = """
Hello!
This is ABTestBot.
Select your language
"""

help_md = {
    'rus': """Для того, чтобы начать новый тест, используйте команду /newtest.
Чтобы в любой момент прервать процесс, используйте команду /cancel.
Если вы хотите изменить настройки теста, используйте /settings.
Снова вызвать это меню можно командой /help.
""",
}

settings_md = {
    'rus': """Сейчас установлены следующие настройки:
  - язык: {0}
  - уровень значимости проверки гипотезы α: {1}
  - порог сравнения апостериорных вероятностей ε: {2}
      
Чтобы изменить настройки, нажмите на соответствующую кнопку
"""
}

input_language = {
    'rus': """Выберите язык""",
}

input_alpha = {
    'rus': """Выберите новый уровень значимости α в интервале от 0 до 1""",
}

input_epsilon = {
    'rus': """Выберите новый байесовский порог ε в интервале от 0 до 1""",
}

error_again = {
    'rus': """Ошибка. Попробуйте еще раз""",
    'eng': """An error occurred. Try again"""
}

input_control = {'rus': 'Введите через пробел количество всех и успешных попыток в контрольной вариации'}

input_treatment = {'rus': 'Введите через пробел количество всех и успешных попыток в тестовой вариации №{:d}'}

default_settings = {'language': 'eng',
                    'alpha': 0.05,
                    'epsilon': 0.9
                    }

language_button_rus_text = "🇷🇺 Русский"

languages = {language_button_rus_text: 'rus'}

one_more_treatment_button_text = {
    'rus': """🆕 Добавить вариацию"""
}

stop_input_treatment_button_text = {
    'rus': """🆗 Проверить ввод"""
}

if_continue_input = {
    'rus': """Продолжить?"""
}