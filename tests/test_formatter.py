import unittest
from rusaicupbot.formatter import format_game, format_top


class TestFormatter(unittest.TestCase):
    def test_game(self):
        game = {
            "game_id": 1234,
            "creator": "System",
            "scores": {
                "some_man": {
                    "score": 3421,
                    "place": 2,
                    "delta": -21
                },
                "aaa2": {
                    "score": 13513,
                    "place": 1,
                    "delta": None
                },
                "aaa3": {
                    "score": 1341,
                    "place": 3,
                    "delta": 15
                }
            }
        }
        formatted = format_game(game, ["aaa2", "aaa3"])
        self.assertEqual(
            "http://russianaicup.ru/game/view/1234\n\n"
            "Создатель: System\n"
            "1  * aaa2 13513 [?]\n"
            "2  some_man 3421 -21\n"
            "3  * aaa3 1341 +15",
            formatted)

    def test_top(self):
        top = [
            {"player": "Mr.Smile", "rating": 9000},
            {"player": "somebody", "rating": 3000}]
        formatted = format_top(top)
        self.assertEqual(
            "1    Mr.Smile 9000\n"
            "2    somebody 3000",
            formatted)
