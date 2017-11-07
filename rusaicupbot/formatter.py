def format_top(results):
    return "\n".join("{}{} {} {}".format(
        i + 1,
        " " * (5 - len(str(i + 1))),
        kv["player"],
        kv["rating"]) for i, kv in enumerate(results))


def format_positions(results):
    return "\n".join("{}{} {} {}".format(
        kv["place"],
        " " * (5 - len(str(kv["place"]))),
        kv["player"],
        kv["rating"]) for kv in results)


def _format_player(player, player_info, players_to_highlight):
    star = "* " if player in players_to_highlight else ""
    team_hl_1 = ""
    team_hl_2 = ""
    team = player_info.get("team")
    if team == "RENEGADES":
        team_hl_1 = "<i>"
        team_hl_2 = "</i>"
    elif team == "ACADEMY":
        team_hl_1 = "<b>"
        team_hl_2 = "</b>"
    return "".join([team_hl_1, star, player, team_hl_2])

def format_game(game, players_to_highlight):
    formatted = []
    formatted.append("http://russianaicup.ru/game/view/{}".format(
        game["game_id"]))
    formatted.append(game["kind"])
    formatted.append("Создатель: {}".format(game["creator"]))
    for player, game_info in sorted(
            game["scores"].items(), key=lambda item: -item[1]["score"]):
        formatted.append("{}{} {} {} {}{}".format(
            game_info["place"],
            " " if game_info["place"] < 10 else "",
            _format_player(player, game_info, players_to_highlight),
            game_info["score"],
            "+" if game_info["delta"] is not None and game_info["delta"] > 0
            else "",
            game_info["delta"] if game_info["delta"] is not None
            else ("[?]" if game["creator"] in ("System", "Система")
                  else "")))
    return "\n".join(formatted)
