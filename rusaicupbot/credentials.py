credentials = {
    "games_start_from": 54399,
    "info_path": "info.json",
    "contest_num": 2
}

try:
    import rusaicupbot.real_credentials as rc
    credentials.update(rc.credentials)
except:
    print("No credentials found")
