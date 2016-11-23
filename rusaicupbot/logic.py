import json
import os


class Logic(object):
    def __init__(self, info_path):
        self._subs = {}
        self._subs_by_user = {}
        self._top = []
        self._games = []
        self._sent_games = set()
        self._info_path = info_path
        self._load_info()

    def top(self, number=50):
        return self._top[:number]

    def _load_info(self):
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
        with open(self._info_path, "w") as outfile:
            info = {}
            info["subs_by_user"] = self._subs_by_user
            info["subs"] = self._subs
            info["sent_games"] = list(self._sent_games)
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
        if user in self._subs_by_user and player in self._subs[user]:
            self._subs_by_user[user].remove(player)
        self._dump_info()

    def subscriptions(self):
        return self._subs

    def subscriptions_by_user(self, user):
        return self._subs_by_user.get(user, [])

    def games(self):
        result = self._games
        self._games = []
        self._sent_games = self._sent_games.union(set(
            g["game_id"] for g in result))
        self._dump_info()
        return result

    def update_games(self, games):
        self._games += [
            g for g in games
            if g["game_id"] not in self._sent_games]

    def update_top(self, top):
        self._top = top
