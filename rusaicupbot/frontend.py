# coding utf-8
import logging
import logging.handlers
import traceback

from telegram.ext import Updater, CommandHandler


from rusaicupbot.logic import Logic
from rusaicupbot.credentials import credentials
from rusaicupbot.formatter import format_top, format_positions

from rusaicupbot.crawler import Crawler
from rusaicupbot.notifier import Notifier


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)
log = logging.getLogger()

log.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)

rot_handler = logging.handlers.RotatingFileHandler("logs/easyci.log")

rot_handler.setFormatter(formatter)
rot_handler.setLevel(logging.INFO)

log.addHandler(handler)
log.addHandler(rot_handler)


logic = Logic(credentials["info_path"])

crawler = Crawler(logic,
                  credentials["games_start_from"],
                  credentials["contest_num"])
notifier = Notifier(logic)

HELP_TEXT = ("Статистика: /top\n"
             "/top N - статистика по N первым участникам.\n"
             "Пример: /top 50\n\n"
             "/pos - позиции игроков, на которых вы подписаны.\n"
             "/pos user1 user2 user3 - позиции игроков, "
             "перечисленных через пробел.\n\n"
             "Чтобы подписаться на результаты игр с участием USERNAME, "
             "используйте команду /subscribe USERNAME.\n"
             "Чтобы отписаться, используйте команду /unsubscribe USERNAME.\n\n"
             "Чтобы посмотреть свои подписки, "
             "используйте команду /subscriptions.\n\n"
             "Если что, пишите @upppi\n"
             "https://github.com/uppi/rusaicupbot")


def show_help(bot, update):
    """
    Show help.
    """
    chat_id = update.message.chat_id
    bot.sendMessage(chat_id, HELP_TEXT)


def show_subscriptions(bot, update):
    """
    Show subscriptions.
    """
    user_id = update.message.from_user.id
    subs = logic.subscriptions_by_user(user_id)
    if not subs:
        bot.sendMessage(user_id, "У вас нет подписок.")
    else:
        bot.sendMessage(user_id, "Вы подписаны на {}.".format(
            ", ".join(subs)))


def top(bot, update):
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    top_args = []
    if text != "/top":
        try:
            top_args.append(
                int(text[len("/top "):].strip()))
        except Exception:
            bot.sendMessage(chat_id, "Некорректный формат запроса.")
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


def pos(bot, update):
    """
    Show position.
    """
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    player_names = text[len("/pos "):].split()
    if not player_names:
        player_names = logic.subscriptions_by_user(user_id)
    if not player_names:
        bot.sendMessage(user_id, "У вас нет подписок и вы никого не указали.")
    else:
        positions = logic.positions(player_names)
        if not positions:
            bot.sendMessage(user_id, "Указанные имена некорректны.")
        else:
            bot.sendMessage(user_id, format_positions(positions))


def subscribe(bot, update):
    """
    Subscribe to user USERNAME updates.

    `/subscribe username` command.
    """
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    player_name = text[len("/subscribe "):]
    if not player_name:
        bot.sendMessage(
            user_id,
            "После /subscribe напишите имя игрока, "
            "на которого хотите подписаться.\n"
            "Пример:\n/subscribe username")
        return

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
    if not player_name:
        bot.sendMessage(
            user_id,
            "После /unsubscribe напишите имя игрока, "
            "на которого хотите подписаться.\n"
            "Пример:\n/unsubscribe username")
        return

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
        CommandHandler('top', top), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('pos', pos), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('subscribe', subscribe), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('unsubscribe', unsubscribe), group=0)
    updater.dispatcher.add_handler(
        CommandHandler('subscriptions', show_subscriptions), group=0)

    updater.dispatcher.add_error_handler(error)

    logic.bot = updater.bot

    try:
        crawler.start()
        notifier.start()

        updater.start_polling()
        updater.idle()
    finally:
        crawler.stop()
        notifier.stop()


def main():
    run(credentials["TELEGRAM_BOT_TOKEN"])
