import LanusStats

fbref = LanusStats.Fbref()

fbref.get_all_player_season_stats("Serie A", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Premier League", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Bundesliga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("La Liga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Ligue 1", "2024-2025", save_csv=True)