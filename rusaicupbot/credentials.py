credentials = {
    "games_start_from": 42028,
    "info_path": "info.json"
}

try:
    import rusaicupbot.real_credentials as rc
    credentials.update(rc.credentials)
except:
    print("No credentials found")
