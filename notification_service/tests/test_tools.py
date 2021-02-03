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

    def test_check_the_reminder_time_notTheTime_False(self):
        input_value = {
            'time_now': datetime(hour=14, minute=30, year=2021, month=2, day=3),
            'user_day_reminder_time': ['14:40']
        }

        result = tools.check_the_reminder_time(**input_value)

        self.assertFalse(result)

    def test_check_the_reminder_time_emptyList_False(self):
        input_value = {
            'time_now': datetime(hour=14, minute=30, year=2021, month=2, day=3),
            'user_day_reminder_time': []
        }

        result = tools.check_the_reminder_time(**input_value)

        self.assertFalse(result)

    def test_check_the_reminder_time_True(self):
        input_value = {
            'time_now': datetime(hour=14, minute=50, year=2021, month=2, day=3),
            'user_day_reminder_time': ['14:50']
        }

        result = tools.check_the_reminder_time(**input_value)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
