def is_game_complete(game):
    return all(g["delta"] is not None for g in game["scores"].values())
