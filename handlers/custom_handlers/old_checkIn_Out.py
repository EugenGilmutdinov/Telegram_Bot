@bot.message_handler(state=UserInfoState.checkIn_Out)
def get_dates(message: Message) -> None:
    try:
        if len(message.text) != 11:
            raise ValueError
        else:
            dates_str = message.text.split(' ')  # 17.07 20.07
            checkIn = dates_str[0].split('.')
            checkOut = dates_str[1].split('.')
            int_checkIn = list(map(lambda x: int(x), checkIn))
            int_checkOut = list(map(lambda x: int(x), checkOut))
            month_days = [calendar.monthrange(2022, int_checkIn[1])[1], calendar.monthrange(2022, int_checkOut[1])[1]]
            checkIn = ['2022', checkIn[1], checkIn[0]]  # 2022-07-17
            checkOut = ['2022', checkOut[1], checkOut[0]]  # 2022-07-20
            date1 = date(int(checkOut[0]), int(checkOut[1]), int(checkOut[2]))
            date2 = date(int(checkIn[0]), int(checkIn[1]), int(checkIn[2]))
            num_days = date1 - date2
            num_days = str(num_days).split()[0]
            print(f"Кол-во дней - {num_days}")
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['num_days'] = num_days
            if int_checkIn[0] <= month_days[0] and int_checkOut[0] <= month_days[1]:
                dates = checkIn + checkOut
                with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                    data['checkIn_Out'] = dates
                bot.send_message(message.chat.id, f'Даты подходят - {data["checkIn_Out"]}')
                if data['command'] == '/bestdeal':  # переход в /bestdeal.py
                    bot.send_message(message.chat.id, 'Введите диапазон цен через пробел (RUB),\n'
                                                      'пример: 1000 30000')
                    bot.set_state(message.from_user.id, UserInfoState.price_range)
                else:
                    bot.send_message(message.chat.id,
                                     'Теперь выберете количество отелей, которые необходимо вывести (не более 10)',
                                     reply_markup=num_hotels.total_hotels())  # inline keyboard
            else:
                raise OverflowError
    except (ValueError, OverflowError):
        bot.reply_to(message, text='Дата введена неверно,\n'
                                   'попробуйте ещё раз!\n'
                                   'Пример: 17.08 25.08')