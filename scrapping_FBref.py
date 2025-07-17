import LanusStats

fbref = LanusStats.Fbref()

# Obtenemos los datos de todos los jugadores de las ligas más importantes

fbref.get_all_player_season_stats("Serie A", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Premier League", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Bundesliga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("La Liga", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("Ligue 1", "2024-2025", save_csv=True)
fbref.get_all_player_season_stats("MLS", "2024", save_csv=True)

# Obtenemos todos los datos de todos los equipos de las ligas más importantes

fbref.get_all_teams_season_stats("Serie A", "2024-2025", save_csv=True)
fbref.get_all_teams_season_stats("Premier League", "2024-2025", save_csv=True)
fbref.get_all_teams_season_stats("Bundesliga", "2024-2025", save_csv=True)
fbref.get_all_teams_season_stats("La Liga", "2024-2025", save_csv=True)
fbref.get_all_teams_season_stats("Ligue 1", "2024-2025", save_csv=True)
fbref.get_all_teams_season_stats("MLS", "2024", save_csv=True)
fbref.get_all_teams_season_stats("Primera Division Argentina", "2024", save_csv=True)