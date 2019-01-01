import time
import threading
import logging
import traceback
from collections import defaultdict

import telegram

from rusaicupbot.formatter import format_game

DELAY_SEC = 0.5

log = logging.getLogger()


class Notifier(object):
    def __init__(self, logic):
        self.logic = logic
        self.thread = None
        self.stopped = None
        self.message_ids = defaultdict(dict)

    def notify(self, user, game):
        try:
            log.info("Notifying {} about game {}".format(
                user, game["game_id"]))
            message = self.logic.bot.sendMessage(
                user,
                format_game(game, self.logic.subscriptions_by_user(user)),
                parse_mode=telegram.ParseMode.HTML,
                disable_web_page_preview=True)
            self.message_ids[user][game["game_id"]] = message.message_id
        except Exception:
            log.error(traceback.format_exc())

    def update_notify(self, user, game):
        try:
            log.info("Updating notification for user {} about game {}".format(
                user, game["game_id"]))
            message_id = self.message_ids[user].get(game["game_id"])
            if message_id is None:
                log.error(
                    "Couldn't find message_id to update "
                    "notification for user {} about game {}".format(
                        user, game["game_id"]))
                return
            del self.message_ids[user][game["game_id"]]
            self.logic.bot.editMessageText(
                chat_id=user,
                message_id=message_id,
                text=format_game(game, self.logic.subscriptions_by_user(user)),
                parse_mode=telegram.ParseMode.HTML,
                disable_web_page_preview=True)
        except Exception:
            log.error(traceback.format_exc())

    def notify_current(self):
        task = self.logic.get_next_notification_task()
        if task is None:
            return False
        log.debug("notification task exists")
        if task["is_update"]:
            self.update_notify(task["user"], task["game"])
        else:
            self.notify(task["user"], task["game"])
        return True

    def run(self, stopped):
        while not stopped.is_set():
            time.sleep(DELAY_SEC)
            self.notify_current()

    def start(self):
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, args=(self.stopped,))
        self.thread.start()
        return self.thread

    def stop(self):
        self.stopped.set()
