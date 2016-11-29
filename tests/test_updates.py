import unittest
from rusaicupbot.notifier import Notifier
from rusaicupbot.logic import Logic
from collections import namedtuple


class TestUpdates(unittest.TestCase):
    def test_1(self):
        game1 = {
            "game_id": 1,
            "creator": "System",
            "scores": {
                "aaa2": {
                    "score": 13513,
                    "place": 1,
                    "delta": None
                },
                "aaa3": {
                    "score": 1341,
                    "place": 3,
                    "delta": None
                }
            }
        }

        game2 = {
            "game_id": 2,
            "creator": "System",
            "scores": {
                "aaa2": {
                    "score": 135,
                    "place": 1,
                    "delta": -5
                },
                "aaa4": {
                    "score": 1341,
                    "place": 3,
                    "delta": 2
                }
            }
        }

        game1_upd = {
            "game_id": 1,
            "creator": "System",
            "scores": {
                "aaa2": {
                    "score": 13513,
                    "place": 1,
                    "delta": 5
                },
                "aaa3": {
                    "score": 1341,
                    "place": 3,
                    "delta": -5
                }
            }
        }

        games = [game1, game2]
        games_upd = [game1_upd, game2]

        logic = Logic(None)
        notifier = Notifier(logic)

        logic.subscribe(123, "aaa2")
        logic.subscribe(124, "aaa3")

        updated = []
        notified = []

        class mockbot:
            idx = 0

            def sendMessage(self, user, msg, **kwargs):
                notified.append((user, msg))
                mockbot.idx += 1
                return namedtuple('Message', ['message_id'])(
                    message_id=mockbot.idx)

            def editMessageText(self, user, msg_id, msg, **kwargs):
                updated.append((user, msg_id, msg))
        logic.bot = mockbot()

        logic.update_games(games)

        self.assertFalse(logic._notification_queue.empty())

        self.assertTrue(notifier.notify_current())
        self.assertTrue(notifier.notify_current())
        self.assertTrue(notifier.notify_current())
        self.assertFalse(notifier.notify_current())

        self.assertEqual(len(notified), 3)
        self.assertEqual(len(updated), 0)

        logic.update_games(games_upd)

        self.assertTrue(notifier.notify_current())
        self.assertTrue(notifier.notify_current())
        self.assertFalse(notifier.notify_current())

        self.assertEqual(len(notified), 3)
        self.assertEqual(len(updated), 2)
