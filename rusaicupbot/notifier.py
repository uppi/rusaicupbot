import time
import threading
import logging
import traceback

from rusaicupbot.formatter import format_game

SLEEP_TIME_SEC = 20
START_DELAY_SEC = 20

log = logging.getLogger()


class Notifier(object):
    def __init__(self, logic):
        self.logic = logic
        self.thread = None
        self.stopped = None

    def notify(self, user, game):
        log.info("Notifying {} about game {}".format(user, game["game_id"]))
        self.logic.bot.sendMessage(
            user,
            format_game(game, self.logic.subscriptions_by_user(user)))

    def handle_new_games(self, games, subs):
        log.info("Notifying about {} games".format(len(games)))
        log.info("Subs: {}".format(subs))
        for game in games:
            recepients = []
            for player in game["scores"].keys():
                recepients.extend(subs.get(player, []))
            log.info("Found {} recepients for game {}, players: {}".format(
                len(recepients), game["game_id"], " ".join(
                    game["scores"].keys())))
            for recepient in set(recepients):
                self.notify(recepient, game)

    def run(self, stopped):
        time.sleep(START_DELAY_SEC)
        while not stopped.is_set():
            try:
                log.info("Another round of notifications")
                games = self.logic.games()
                subs = self.logic.subscriptions()
                self.handle_new_games(games, subs)
                time.sleep(SLEEP_TIME_SEC)
            except Exception:
                log.error(traceback.format_exc())

    def start(self):
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.run, args=(self.stopped,))
        self.thread.start()
        return self.thread

    def stop(self):
        self.stopped.set()
