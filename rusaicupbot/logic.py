import json
import os
import queue
import logging

from rusaicupbot.game import is_game_complete

log = logging.getLogger()


class Logic(object):
    def __init__(self, info_path):
        self._subs = {}
        self._subs_by_user = {}
        self._top = []
        self._games = []
        self._updated_games = []
        self._sent_incomplete = set()
        self._sent_games = set()
        self._info_path = info_path
        self._load_info()

        self.crawler = None

        self._notification_queue = queue.Queue()

    def top(self, number=50):
        return self._top[:number]

    def positions(self, names):
        return [p for p in self._top if p["player"] in names]

    def _load_info(self):
        if self._info_path is None:
            return
        if os.path.exists(self._info_path):
            with open(self._info_path) as infile:
                info = json.load(infile)
                self._subs_by_user = {
                    int(k): v
                    for k, v in info["subs_by_user"].items()
                }
                self._subs = info["subs"]
                self._sent_games = set(info["sent_games"])

    def _dump_info(self):
        if self._info_path is None:
            return
        with open(self._info_path, "w") as outfile:
            info = {}
            info["subs_by_user"] = self._subs_by_user
            info["subs"] = self._subs
            info["sent_games"] = list(self._sent_games) + list(
                self._sent_incomplete)
            json.dump(info, outfile, indent=4)

    def subscribe(self, user, player):
        if player not in self._subs:
            self._subs[player] = []
        if user not in self._subs_by_user:
            self._subs_by_user[user] = []
        self._subs[player].append(user)
        self._subs_by_user[user].append(player)
        self._dump_info()

    def unsubscribe(self, user, player):
        if player in self._subs and user in self._subs[player]:
            self._subs[player].remove(user)
        if user in self._subs_by_user and player in self._subs_by_user[user]:
            self._subs_by_user[user].remove(player)
        self._dump_info()

    def subscriptions(self):
        return self._subs

    def subscriptions_by_user(self, user):
        return self._subs_by_user.get(user, [])

    def send_game(self, game, is_update):
        recepients = []
        for player in game["scores"].keys():
            recepients.extend(self._subs.get(player, []))
        recepients = set(recepients)
        log.info("recepients for game {}: {}".format(
            game["game_id"], ", ".join(map(str, recepients))))

        if (recepients and
            self.crawler is not None and
            game.get("token") is not None):
                teams = self.crawler.crawl_teams(game["token"])
                for player in game["scores"].keys():
                    if player in teams:
                        game["scores"][player]["team"] = teams[player]

        for user in set(recepients):
            self._notification_queue.put(
                {
                    "is_update": is_update,
                    "game": game,
                    "user": user
                })

    def update_games(self, games):
        for game in games:
            game_id = game["game_id"]
            if game_id in self._sent_games:
                continue
            if game_id in self._sent_incomplete:
                if is_game_complete(game):
                    self.send_game(game, is_update=True)
                    self._sent_games.add(game_id)
            else:
                self.send_game(game, is_update=False)
                if is_game_complete(game):
                    self._sent_games.add(game_id)
                else:
                    self._sent_incomplete.add(game_id)
        self._dump_info()

    def get_next_notification_task(self):
        try:
            return self._notification_queue.get_nowait()
        except queue.Empty:
            return None

    def update_top(self, top):
        self._top = top
