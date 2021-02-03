import unittest

from reminder import Reminder


class TestReminderMethods(unittest.TestCase):

    def test_initReminder_wrongPlatform_Exception(self):
        input_value = {
            'bot_platform': 'wrong_platform',
            'bot': None,
            'storage': None
        }

        with self.assertRaises(ValueError):
            reminder = Reminder(**input_value)


    def test_initReminder_RightPlatformTg(self):
        input_value = {
            'bot_platform': 'tg',
            'bot': None,
            'storage': None
        }

        reminder = Reminder(**input_value)

        self.assertIsNotNone(reminder)

    def test_initReminder_RightPlatformVk(self):
        input_value = {
            'bot_platform': 'vk',
            'bot': None,
            'storage': None
        }

        reminder = Reminder(**input_value)

        self.assertIsNotNone(reminder)


if __name__ == '__main__':
    unittest.main()
