import LanusStats

fbref = LanusStats.Fbref()

# Obtenemos todos los df de las 5 grandes ligas, y de la MLS
fbref.get_all_player_season_stats("Serie A", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Premier League", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Bundesliga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("La Liga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Ligue 1", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("MLS", "2024", save_csv=True)