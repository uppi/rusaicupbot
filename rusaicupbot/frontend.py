# coding utf-8
import logging
import traceback

from telegram.ext import Updater, CommandHandler


from rusaicupbot.logic import Logic
from rusaicupbot.credentials import BOT_TOKEN
from rusaicupbot.formatter import format_top


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
log = logging.getLogger()


logic = Logic()

HELP_TEXT = ("Статистика: /top\n"
             "Команда /top N - статистика по N первым участникам.\n"
             "Пример: /top 50\n\n"
             "Чтобы подписаться на результаты игр с участием USERNAME, "
             "используйте команду /subscribe USERNAME.\n"
             "Пример: /subscribe Mr.Smile\n\n"
             "Чтобы отписаться, используйте команду /unsubscribe USERNAME.\n\n"
             "Если что, пишите @upppi\n"
             "https://github.com/uppi/rusaicupbot")


def show_help(bot, update):
    """
    Show help.
    """
    bot.sendMessage(HELP_TEXT)


def top(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    top_args = []
    if text != "/top":
        try:
            top_args.append(
                int(text[len("/top "):].strip()))
        except Exception:
            bot.sendMessage(chat_id, "Некорректный формат запроса. ")
            log.error(
                "Error while getting top for {} with args {} for: {}".format(
                    chat_id,
                    top_args,
                    traceback.format_exc()))
    try:
        bot.sendMessage(
            chat_id,
            format_top(logic.top(*top_args)))
    except:
        bot.sendMessage(chat_id, "Произошла ошибка. Мы уже разбираемся.")
        log.error(
            "Error while getting top for {} with args {} for: {}".format(
                chat_id,
                top_args,
                traceback.format_exc()))


def subscribe(bot, update):
    """
    Subscribe to user USERNAME updates.

    `/subscribe username` command.
    """
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    player_name = text[len("/subscribe "):]

    try:
        logic.subscribe(user_id, player_name)
        bot.sendMessage(
            user_id,
            "Вы подписались на игры с участием {}.".format(player_name))
    except Exception:
        bot.sendMessage(user_id, "Произошла ошибка. Мы уже разбираемся.")
        log.error("Error while subscribing {} to {}: {}".format(
            user_id,
            player_name,
            traceback.format_exc()))


def unsubscribe(bot, update):
    """
    Unsubscribe from user USERNAME updates.

    `/unsubscribe username` command.
    """
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    player_name = text[len("/unsubscribe "):]

    try:
        logic.unsubscribe(user_id, player_name)
        bot.sendMessage(
            user_id,
            "Вы отписались от игр с участием {}.".format(player_name))
    except Exception:
        bot.sendMessage(user_id, "Произошла ошибка. Мы уже разбираемся.")
        log.error("Error while unsubscribing {} from {}: {}".format(
            user_id,
            player_name,
            traceback.format_exc()))


def error(bot, update, error):
    logging.warning("Update {} caused error {}".format(update, error))


def run(token):
    """
    Start telegram bot.
    """

    updater = Updater(token)
    updater.dispatcher.add_handler(
        CommandHandler('help', show_help), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('start', show_help), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('subscribe', subscribe), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('unsubscribe', unsubscribe), group=0)

    updater.dispatcher.add_error_handler(error)

    logic.bot = updater.bot

    updater.start_polling()
    updater.idle()


def main():
    run(BOT_TOKEN)


if __name__ == '__main__':
    main()
