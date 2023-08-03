from loader import bot
import handlers
from loguru import logger
from telebot.custom_filters import StateFilter
from keyboards.inline.filters_calendar import bind_filters
from utils.set_bot_commands import set_default_commands


print("Бот запущен!")


logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")


if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    bind_filters(bot)
    set_default_commands(bot)
    bot.infinity_polling()
