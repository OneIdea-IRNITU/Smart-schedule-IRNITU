from vkbottle.bot import Message


async def sending_schedule(ans: Message, schedule_str: str):
    """Отправка расписания пользователю"""
    for schedule in schedule_str:
        await ans.answer(f'{schedule}')


async def sending_schedule_is_not_available(ans: Message):
    await ans.answer('Расписание временно недоступно\n'
                     'Попробуйте позже⏱')
