def format_top(results):
    return "\n".join("{}{} {} {}".format(
        i + 1,
        " " * (5 - len(str(i))),
        kv["player"],
        kv["rating"]) for i, kv in enumerate(results))


def format_positions(results):
    return "\n".join("{}{} {} {}".format(
        kv["place"],
        " " * (5 - len(str(kv["place"]))),
        kv["player"],
        kv["rating"]) for kv in results)


def format_game(game, players_to_highlight):
    formatted = []
    formatted.append("http://russianaicup.ru/game/view/{}\n".format(
        game["game_id"]))
    formatted.append("Создатель: {}".format(game["creator"]))
    for player, game_info in sorted(
            game["scores"].items(), key=lambda item: -item[1]["score"]):
        formatted.append("{}{} {} {} {}{}".format(
            game_info["place"],
            " " if game_info["place"] < 10 else "",
            player if player not in players_to_highlight else "* {}".format(
                player),
            game_info["score"],
            "+" if game_info["delta"] is not None and game_info["delta"] > 0
            else "",
            game_info["delta"] if game_info["delta"] is not None
            else ("[?]" if game["creator"] in ("System", "Система")
                  else "")))
    return "\n".join(formatted)
