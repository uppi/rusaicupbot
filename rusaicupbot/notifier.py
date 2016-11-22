from rusaicupbot.formatter import format_game


class Notifier(object):
    def __init__(self, bot):
        self.bot = bot

    def notify(self, user, game):
        self.bot.sendMessage(user, format_game(game))
