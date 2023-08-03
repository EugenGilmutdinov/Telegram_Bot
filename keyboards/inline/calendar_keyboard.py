import locale
import calendar
from datetime import date, timedelta
from keyboards.inline.filters_calendar import calendar_factory, calendar_factory_ch_day, calendar_zoom
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

EMTPY_FIELD = '1'
WEEK_DAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Cб', 'Вск']
MONTHS = [(1, 'Январь'), (2, 'Февраль'), (3, 'Март'), (4, 'Апрель'), (5, 'Май'),
          (6, 'Июнь'), (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'), (10, 'Октябрь'),
          (11, 'Ноябрь'), (12, 'Декабрь')]

locale.setlocale(
    category=locale.LC_ALL,
    locale="Russian"
)


def generate_calendar_days(year: int, month: int) -> InlineKeyboardMarkup:
    '''
    Функция для генерации календарных дней в инлайн-клавиатуре

    :param year: int - год
    :param month: int - месяц
    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=7)
    today = date.today()

    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=month, day=1).strftime('%b %Y').title(),
            callback_data=EMTPY_FIELD
        )
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=day,
            callback_data=EMTPY_FIELD
        )
        for day in WEEK_DAYS
    ])

    for week in calendar.Calendar().monthdayscalendar(year=year, month=month):
        week_buttons = []
        for day in week:
            day_name = ' '
            full_date = EMTPY_FIELD
            if day == today.day and today.year == year and today.month == month:
                day_name = '🔘'
                full_date = date(year=year, month=month, day=day).strftime('%Y-%m-%d')
            elif day != 0:
                day_name = str(day)
                full_date = date(year=year, month=month, day=day).strftime('%Y-%m-%d')
            week_buttons.append(
                InlineKeyboardButton(
                    text=day_name,
                    callback_data=full_date
                )
            )
        keyboard.add(*week_buttons)

    previous_date = date(year=year, month=month, day=1) - timedelta(days=1)
    next_date = date(year=year, month=month, day=1) + timedelta(days=31)

    keyboard.add(
        InlineKeyboardButton(
            text='Пред мес',
            callback_data=calendar_factory.new(year=previous_date.year, month=previous_date.month)
        ),
        InlineKeyboardButton(
            text='Отдалить',
            callback_data=calendar_zoom.new(year=year)
        ),
        InlineKeyboardButton(
            text='След мес',
            callback_data=calendar_factory.new(year=next_date.year, month=next_date.month)
        ),
    )

    return keyboard


def chosen_calendar_day(ch_year: int, ch_month: int, ch_day: int) -> InlineKeyboardMarkup:
    '''
    Функция для генерации календарных дней с учётом уже выбранной первой даты

    :param ch_year: int - выбранный год
    :param ch_month: int - выбранный месяц
    :param ch_day: int - выбранный день
    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=7)
    today = date.today()
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=ch_year, month=ch_month, day=1).strftime('%b %Y').title(),
            callback_data=EMTPY_FIELD
        )
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=day,
            callback_data=EMTPY_FIELD
        )
        for day in WEEK_DAYS
    ])

    for week in calendar.Calendar().monthdayscalendar(year=ch_year, month=ch_month):
        week_buttons = []
        for day in week:
            day_name = ' '

            full_date = EMTPY_FIELD
            if day == ch_day and today.year == ch_year and today.month == ch_month:
                day_name = "✔️"
            elif day == today.day and today.year == ch_year and today.month == ch_month:
                day_name = '🔘'
            elif day != 0:
                day_name = str(day)
            if (day == ch_day and today.year == ch_year and today.month == ch_month) \
                    or (day == today.day and today.year == ch_year and today.month == ch_month) \
                    or (day != 0):
                chose_date = date(year=ch_year, month=ch_month, day=ch_day).strftime('%Y-%m-%d')
                second_date = date(year=ch_year, month=ch_month, day=day).strftime('%Y-%m-%d')
                full_date = f"{chose_date}, {second_date}"
            week_buttons.append(
                InlineKeyboardButton(
                    text=day_name,
                    callback_data=full_date
                )
            )
        keyboard.add(*week_buttons)

    previous_date = date(year=ch_year, month=ch_month, day=1) - timedelta(days=1)
    next_date = date(year=ch_year, month=ch_month, day=1) + timedelta(days=31)

    keyboard.add(
        InlineKeyboardButton(
            text='Пред мес',
            callback_data=calendar_factory_ch_day.new(year=previous_date.year, month=previous_date.month, day=ch_day)
        ),
        InlineKeyboardButton(
            text='Отдалить',
            callback_data=calendar_zoom.new(year=ch_year)
        ),
        InlineKeyboardButton(
            text='След мес',
            callback_data=calendar_factory_ch_day.new(year=next_date.year, month=next_date.month, day=ch_day)
        ),
    )

    return keyboard


def generate_calendar_months(year: int) -> InlineKeyboardMarkup:
    '''
    Функция для генерации календарных месяцев в году

    :param year: int - год
    :return: InlineKeyboardMarkup - инлайн-клавиатура
    '''
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton(
            text=date(year=year, month=1, day=1).strftime('Год %Y'),
            callback_data=EMTPY_FIELD
        )
    )
    keyboard.add(*[
        InlineKeyboardButton(
            text=month,
            callback_data=calendar_factory.new(year=year, month=month_number)
        )
        for month_number, month in MONTHS
    ])
    keyboard.add(
        InlineKeyboardButton(
            text='Пред год',
            callback_data=calendar_zoom.new(year=year - 1)
        ),
        InlineKeyboardButton(
            text='След год',
            callback_data=calendar_zoom.new(year=year + 1)
        )
    )
    return keyboard
