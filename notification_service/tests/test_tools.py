import unittest
from datetime import datetime

import tools


class TestToolsMethods(unittest.TestCase):

    def test_add_user_to_submit(self):
        input_value = {
            'chat_id': 123456789,
            'group': 'ИБб-18-1',
            'notifications': 5,
            'day_now': 'четверг',
            'time_now': datetime(hour=14, minute=30, year=2021, month=2, day=3),
            'week': 'even'
        }
        expected = {
            'chat_id': 123456789,
            'group': 'ИБб-18-1',
            'week': 'even',
            'day': 'четверг',
            'notifications': 5,
            'time': '14:35'}

        result = tools.forming_user_to_submit(**input_value)

        self.assertEqual(result, expected)

    def test_check_that_user_has_reminder_enabled_for_the_current_time_notTheTime_False(self):
        input_value = {
            'time_now': datetime(hour=14, minute=30, year=2021, month=2, day=3),
            'user_day_reminder_time': ['14:40']
        }

        result = tools.check_that_user_has_reminder_enabled_for_the_current_time(**input_value)

        self.assertFalse(result)

    def test_check_that_user_has_reminder_enabled_for_the_current_time_emptyList_False(self):
        input_value = {
            'time_now': datetime(hour=14, minute=30, year=2021, month=2, day=3),
            'user_day_reminder_time': []
        }

        result = tools.check_that_user_has_reminder_enabled_for_the_current_time(**input_value)

        self.assertFalse(result)

    def test_check_that_user_has_reminder_enabled_for_the_current_time_True(self):
        input_value = {
            'time_now': datetime(hour=14, minute=50, year=2021, month=2, day=3),
            'user_day_reminder_time': ['14:50']
        }

        result = tools.check_that_user_has_reminder_enabled_for_the_current_time(**input_value)

        self.assertTrue(result)

    def test_forming_message_text_emptyList(self):
        input_value = {
            'lessons': [],
            'week': 'even',
            'time': '10:00'
        }
        expected = ''

        result = tools.forming_message_text(**input_value)

        self.assertEqual(result, expected)

    def test_forming_message_text(self):
        input_value = {
            'lessons': [
                {'time': '10:00', 'week': 'odd', 'name': 'Криптографические методы защиты информации',
                 'aud': ['Ж-313'], 'info': '( Лаб. раб. подгруппа 1 )', 'prep': ['Тюрнев Александр Сергеевич']}
            ],
            'week': 'odd',
            'time': '10:00'
        }
        expected = '-------------------------------------------\n' \
                   'Начало в 10:00\n' \
                   'Аудитория: Ж-313\n' \
                   'Криптографические методы защиты информации\n' \
                   '( Лаб. раб. подгруппа 1 ) Тюрнев Александр Сергеевич\n' \
                   '-------------------------------------------\n'

        result = tools.forming_message_text(**input_value)

        self.assertEqual(result, expected)

    def test_get_schedule_from_right_day(self):
        input_value = {
            'schedule': [
                {'day': 'понедельник', 'lessons': ['lessons_1']},
                {'day': 'среда', 'lessons': ['lessons_2']},
                {'day': 'четверг', 'lessons': ['lessons_3']}
            ],
            'day_now': 'среда',
        }
        expected = ['lessons_2']

        result = tools.get_schedule_from_right_day(**input_value)

        self.assertEqual(result, expected)

    def test_get_schedule_from_right_day_notRightDay(self):
        input_value = {
            'schedule': [
                {'day': 'понедельник', 'lessons': ['lessons_1']},
                {'day': 'среда', 'lessons': ['lessons_2']},
                {'day': 'четверг', 'lessons': ['lessons_3']}
            ],
            'day_now': 'вторник',
        }

        result = tools.get_schedule_from_right_day(**input_value)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
