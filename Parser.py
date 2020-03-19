def get_full_schedule(user_info):
    # user_info будет таким:
    # user_info = {'chat_id': chat_id, 'inst': 'ИИТиАД', 'course': '2 курс',
    #                  'group': 'ИБб-18-1'}
    # Если в базе данных какое-то поле пустое, то в словаре будет пустая строка или None

    schedule = 'Чилим 😘😴😎'
    # В каком виде будет schedule (словарь, список или строка) решим
    # Можно как-то так:
    # {'пн':
    #   [
    #       {'date':'16 марта', 'time':'8:15', 'name':'Физика', 'teacher': 'Иванов Иван Иванович', 'aud':'Ж-113'},
    #       {'date':'16 марта', 'time':'10:00', 'name':'Матан', 'teacher': 'Петров Петр Петрович','aud':'К-201'}
    #   ],
    #   'вт': [{}], 'ср': [{}], 'чт': [{}], 'пт': [None], 'сб': [{}], 'вс': [None]}
    # И ещё как-то определять чётная или не чётная неделя (мб с сайта сразу тянуть нужную) -
    # в html коде указано в какую неделю проходит пара
    return schedule
