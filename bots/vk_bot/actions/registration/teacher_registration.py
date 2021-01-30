from vkbottle import Text, Keyboard, KeyboardButtonColor
from vkbottle.bot import Bot, Message
from tools import keyboards

prep_reg = {}


async def start_prep_reg(bot: Bot, ans: Message, state, storage):
    """Вхождение в стейт регистрации преподавателей"""

    chat_id = ans.from_id
    message_inst = ans.text
    prep_reg[chat_id] = []
    storage.save_or_update_vk_user(chat_id=chat_id, institute=message_inst, course='None')
    await ans.answer(f'Вы выбрали: {message_inst}\n')
    await ans.answer('📚Кто постигает новое, лелея старое,\n'
                     'Тот может быть учителем.\n'
                     'Конфуций')

    await ans.answer('Введите своё ФИО полностью.\n'
                     'Например: Корняков Михаил Викторович', keyboard=keyboards.back_for_prep())
    await bot.state_dispenser.set(ans.peer_id, state.PREP_REG)


async def reg_prep(bot: Bot, ans: Message, storage):
    """Регистрация преподавателя"""
    chat_id = ans.from_id
    message = ans.text
    page = 1

    if message == "Назад к институтам":
        await ans.answer('Назад к институтам', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))
        storage.delete_vk_user_or_userdata(chat_id)
        await bot.state_dispenser.delete(ans.peer_id)
        return

    prep_list = storage.get_prep(message)

    if prep_list:
        prep_name = prep_list[0]['prep']
        storage.save_or_update_vk_user(chat_id=chat_id, group=prep_name, course='None')
        await bot.state_dispenser.delete(ans.peer_id)
        await ans.answer(f'Вы успешно зарегистрировались, как {prep_name}!😊\n\n'
                         'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n',
                         keyboard=keyboards.make_keyboard_start_menu())
        return

    # Если преподавателя не нашли
    elif not prep_list and not prep_reg[chat_id]:
        # Делим введенное фио на части и ищем по каждой в базе
        prep_list = []
        prep_list_2 = []
        for name_unit in message.split():
            for i in storage.get_register_list_prep(name_unit):
                prep_list.append(i['prep'])
            if prep_list and prep_list_2:
                prep_list_2 = list(set(prep_list) & set(prep_list_2))
            elif prep_list and not prep_list_2:
                prep_list_2 = prep_list
            prep_list = []
        if not prep_list_2:
            prep_list_2 = None
        prep_list_reg = [page, prep_list_2]
        prep_reg[chat_id] = prep_list_reg
        if prep_reg[chat_id][1]:
            prep_list_2 = prep_reg[chat_id][1]
            keyboard = Keyboard(one_time=False)
            for i in prep_list_2[:8]:
                keyboard.row()
                keyboard.add(Text(label=i), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()
            keyboard.add(Text(label='Назад к институтам'), color=KeyboardButtonColor.PRIMARY)
            if len(prep_list_2) > 8:
                keyboard.add(Text(label='Далее'), color=KeyboardButtonColor.PRIMARY)
            await ans.answer('Возможно Вы имели в виду', keyboard=keyboard)
            return
        else:
            storage.delete_vk_user_or_userdata(chat_id)
            await ans.answer('Мы не смогли найти вас в базе преподавателей.\n'
                             'Возможно вы неверно ввели своё ФИО.',
                             keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))
            await bot.state_dispenser.delete(ans.peer_id)

    if message == 'Далее':
        prep_reg[chat_id][0] += 1
        page = prep_reg[chat_id][0]
        prep_list_2 = prep_reg[chat_id][1]
        keyboard = Keyboard(one_time=False)
        if len(prep_list_2) - (page - 1) * 8 >= 8:
            for i in prep_list_2[(page - 1) * 8:(page - 1) * 8 + 8]:
                keyboard.row()
                keyboard.add(Text(label=i['prep']), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()
            keyboard.add(Text(label='Назад'), color=KeyboardButtonColor.PRIMARY)
            keyboard.add(Text(label='Далее'), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()
            keyboard.add(Text(label='Назад к институтам'), color=KeyboardButtonColor.PRIMARY)
        else:
            for i in prep_list_2[(page - 1) * 8: len(prep_list_2)]:
                keyboard.row()
                keyboard.add(Text(label=i), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()
            keyboard.add(Text(label='Назад'), color=KeyboardButtonColor.PRIMARY)
            keyboard.add(Text(label='Назад к институтам'), color=KeyboardButtonColor.PRIMARY)
        await ans.answer(f'Страница {page}', keyboard=keyboard)

    elif message == 'Назад':
        prep_reg[chat_id][0] -= 1
        page = prep_reg[chat_id][0]
        prep_list_2 = prep_reg[chat_id][1]
        keyboard = Keyboard(one_time=False)
        for i in prep_list_2[(page - 1) * 8:page * 8]:
            keyboard.row()
            keyboard.add(Text(label=i), color=KeyboardButtonColor.PRIMARY)
        keyboard.row()
        if page != 1:
            keyboard.add(Text(label='Назад'), color=KeyboardButtonColor.PRIMARY)
            keyboard.add(Text(label='Далее'), color=KeyboardButtonColor.PRIMARY)
            keyboard.row()
            keyboard.add(Text(label='Назад к институтам'), color=KeyboardButtonColor.PRIMARY)
        elif page == 1:
            keyboard.add(Text(label='Назад к институтам'), color=KeyboardButtonColor.PRIMARY)
            keyboard.add(Text(label='Далее'), color=KeyboardButtonColor.PRIMARY)
        await ans.answer(f'Страница {page}', keyboard=keyboard)

    return
