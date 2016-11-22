def format_top(results):
    return "\n".join("{}{} {} {}".format(
        i + 1,
        " " * (4 - len(str(i))),
        kv[0],
        kv[1]) for i, kv in enumerate(results))


def format_game(game):
    formatted = []
    formatted.append("http://russianaicup.ru/game/view/{}\n".format(
        game["game_id"]))
    for player, game_info in sorted(
            game["scores"].items(), key=lambda item: -item[1]["game_score"]):
        formatted.append("{}{} {} {} {}{}".format(
            game_info["game_place"],
            " " if game_info["game_place"] < 10 else "",
            player,
            game_info["game_score"],
            "+" if game_info["delta"] > 0 else "",
            game_info["delta"]))
    return "\n".join(formatted)
