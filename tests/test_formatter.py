import unittest
from rusaicupbot.formatter import format_game, format_top


class TestFormatter(unittest.TestCase):
    def test_game(self):
        game = {
            "game_id": 1234,
            "scores": {
                "some_man": {
                    "game_score": 3421,
                    "game_place": 2,
                    "delta": -21
                },
                "aaa2": {
                    "game_score": 13513,
                    "game_place": 1,
                    "delta": 13
                },
                "aaa3": {
                    "game_score": 1341,
                    "game_place": 3,
                    "delta": 15
                }
            }
        }
        formatted = format_game(game)
        self.assertEqual(
            "http://russianaicup.ru/game/view/1234\n\n"
            "1  aaa2 13513 +13\n"
            "2  some_man 3421 -21\n"
            "3  aaa3 1341 +15",
            formatted)

    def test_top(self):
        top = [("Mr.Smile", 9000), ("somebody", 3000)]
        formatted = format_top(top)
        self.assertEqual(
            "1    Mr.Smile 9000\n"
            "2    somebody 3000",
            formatted)
