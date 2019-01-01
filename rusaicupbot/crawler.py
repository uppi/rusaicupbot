import threading
import time
import logging
import traceback
import json
from contextlib import closing

import requests
from lxml import html

log = logging.getLogger()

STANDINGS_XPATH_TR = '//div[@class="commonBottom"]/table/tbody/tr'
GAMES_XPATH_GAME = '//div[@class="commonBottom"]/table/tbody/tr'

LABELS = ("place", "player", "games", "won_perc", "rating", "delta")

SLEEP_TIME_SEC = 180


class Crawler(object):
    def __init__(self, logic, games_start_from, contest_num):
        self.logic = logic
        self.logic.crawler = self
        self.thread = None
        self.stopped = None
        self.contest_num = contest_num
        self.games_start_from = games_start_from

    def run(self, stopped):
        while not stopped.is_set():
            try:
                top = self.crawl_top()
                games = self.crawl_games()
                self.logic.update_top(top)
                self.logic.update_games(games)
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

    def crawl_top(self):
        log.info("Crawling standings")
        standings = []
        first_place = None
        page = 1
        while True:
            try:
                page_standings = self.crawl_standings_page(page)
                if page_standings[0]["place"] == first_place:
                    log.info("Ended crawling standings at page {}".format(
                        page))
                    break
                first_place = page_standings[0]["place"]
                standings += page_standings
                page += 1
            except:
                log.error(traceback.format_exc())
                break
            time.sleep(1.1)
        return standings

    def crawl_games(self):
        log.info("Crawling games until game {}".format(self.games_start_from))
        games = []
        new_start_from = None
        page = 1
        found = False
        while not found:
            try:
                page_new_start, page_games = self.crawl_games_page(page)
                if page_new_start is not None:
                    log.debug("So we setting new start from {} to {}".format(
                        page_new_start, new_start_from))
                    new_start_from = page_new_start
                for game in page_games:
                    if game["game_id"] <= self.games_start_from:
                        found = True
                    games.append(game)
                if found:
                    break
                    log.info("Ended crawling games at page {}".format(page))
                page += 1
            except:
                log.error(traceback.format_exc())
            time.sleep(0.5)
        previous_games_start = self.games_start_from
        if new_start_from is not None:
            self.games_start_from = new_start_from
        elif games:
            self.games_start_from = games[0]["game_id"]

        if self.games_start_from < previous_games_start:
            log.eror("START < PREVIOUS START: {}, {}".format(
                self.games_start_from, previous_games_start))
            self.games_start_from = previous_games_start
        else:
            log.info("New start from is {}".format(self.games_start_from))
        return games

    def crawl_standings_page(self, pagenum):
        players = []
        log.info("Crawling standings page {} for contest {}".format(
            pagenum, self.contest_num))

        page = requests.get(
            'http://russianaicup.ru/contest/{}/standings/page/{}'.format(
                self.contest_num, pagenum))
        tree = html.fromstring(page.content)
        for tr in tree.xpath(STANDINGS_XPATH_TR):
            try:
                tc = tr.text_content().split()
                if tc[3] == '/':
                     del tc[3:5]
                player = dict(zip(LABELS, tc))
                for k, v in list(player.items()):
                    if k != "player":
                        try:
                            if v == '-':
                                v = '0'
                            v = int(v) if "." not in v else float(v.replace("%", ""))
                        except Exception:
                            log.warning("Exception while parsing {}, fallback to 0".format(v))
                        player[k] = v
                players.append(player)
            except Exception:
                log.error("Couldn't parse player: {}".format(
                    tr.text_content()))
                log.error("Couldn't parse player (splitted): {}".format(
                    tr.text_content().split()))
                log.error(traceback.format_exc())

        return players

    def crawl_games_page(self, pagenum):
        games = []
        new_start = None
        log.info("Crawling games page {} for contest {}".format(
            pagenum, self.contest_num))

        page = requests.get(
            'http://russianaicup.ru/contest/{}/games/page/{}'.format(
                self.contest_num, pagenum))
        tree = html.fromstring(page.content)
        try:
            for tr in tree.xpath(GAMES_XPATH_GAME):
                tds = tr.xpath("td")
                game_id = int(tds[0].text_content().strip())

                if "Game is testing now" in tr.text_content():
                    log.info("Skipping game {}, still testing".format(game_id))
                    new_start = game_id
                    continue

                kind = tds[1].text_content().strip()
                creator = tds[3].text_content().strip()
                players = tds[4].text_content().split()
                scores = tds[6].text_content().split()
                places = tds[7].text_content().split()
                deltas = tds[8].text_content().split()
                token = tds[9].xpath("div")[0].get("data-token")
                if not deltas:
                    deltas = [None] * 10
                    log.debug("Game {} is not ready yet".format(players))
                    new_start = game_id
                data = list(zip(players, scores, places, deltas))

                game = {
                    "game_id": game_id,
                    "kind": kind,
                    "creator": creator,
                    "token": token,
                    "scores": {
                        player: {
                            "player": player,
                            "score": int(score),
                            "place": int(place),
                            "delta": int(delta) if delta is not None else None
                        } for player, score, place, delta in data
                    }
                }

                log.info("Adding game {}".format(game_id))
                games.append(game)
        except Exception:
            log.info(traceback.format_exc())
        log.debug("Page new start is {}".format(new_start))
        return (new_start, games)

    def crawl_teams(self, token):
        log.info("Crawling teams for {}".format(token))
        url = "http://russianaicup.ru/boombox/data/games/{}?tick=0&fields=tickIndex,players,wizards".format(token)
        try:
            with closing(requests.get(url, stream=True)) as r:
                for l in r.iter_lines():
                    return {p['name']: p['faction'] for p in json.loads(l.decode())["players"]}
        except:
            log.warning(traceback.format_exc())
            return {}
