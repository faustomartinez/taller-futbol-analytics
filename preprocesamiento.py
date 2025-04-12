# La idea de este archivo sería que filtremos los datos un poco para que despues en el notebook ya nos queden lindos

import pandas as pd
import numpy as np

df_bundesliga = pd.read_csv("datasets/player_stats_bundesliga.csv")
df_laliga = pd.read_csv("datasets/player_stats_laliga.csv")
df_ligue1 = pd.read_csv("datasets/player_stats_ligue1.csv")
df_premierleague = pd.read_csv("datasets/player_stats_premierleague.csv")
df_seriea = pd.read_csv("datasets/player_stats_seriea.csv")

df_stats = pd.concat([df_bundesliga,df_laliga,df_ligue1,df_premierleague,df_seriea],ignore_index=True)

#
# print(df_stats.shape)
# Resultado: 44107 filas, 239 columnas

df_players_values = pd.read_csv("datasets/players.csv")


# Crear columna combinada en df_players_values para hacer match con df_stats
df_players_values['full_name'] = df_players_values['first_name'] + ' ' + df_players_values['last_name']

# Hacer el merge de los dataframes
df = pd.merge(
    df_stats,
    df_players_values[['first_name', 'last_name', 'full_name', 'market_value_in_eur', 'highest_market_value_in_eur']],
    left_on='Player',
    right_on='full_name',
    how='inner'
)

#print(df.shape)
# Resultado: 39510 filas, 246 columnas. Perdimos cerca de 5000 jugadores [lo cual es lógico porque no todos vienen con el mismo nombre]
# Es probable que este merge sea mejorable, y espero no haber perdido jugadores importantes, pero por ahora lo dejo así.
#print(df.head())

# Eliminamos los jugadores de los cuales no tenemos su valor de mercado en euros
df = df.dropna(subset=["market_value_in_eur"])

# Ordeno el dataframe segun valor de mercado en euros para hacerlo más divertido
df = df.sort_values('market_value_in_eur', ascending=False)

# Elimino duplicados
df = df.drop_duplicates(subset=["Player"], keep="first")

# Utilizamos este comando para veriticar cuantos jugadores tienen datos faltantes en cada columna
#with pd.option_context("display.max_rows",None):
#    print(df.isna().sum())

# Dan todas 0 asi que no elimino columnas

df = df.drop(columns=[df.columns[0]])
df.to_csv("datasets_procesados/df.csv", index=False)


## Quiero también el dataframe que tiene solo columnas con datos numéricos
df_num = df.select_dtypes(include=['number'])
df_num.to_csv("datasets_procesados/df_num.csv", index=False)


## Vamos a quedarnos con el DataFrame con los jugadores más caros asi es ploteable
df_caros = df[df["market_value_in_eur"]>30000000]
df_caros.to_csv("datasets_procesados/df_caros.csv", index=False)
df_caros_num = df.select_dtypes(include=['number'])
df_caros_num.to_csv("datasets_procesados/df_caros_num.csv", index=False)

# ! Considerar eliminar (muchas) columnas y hacer sus nombres más legibles [i.e. stats_Gls -> goles, stats_G-PK -> goles_sin_penales, etc.]

# Selección de columnas importantes
keep = [
    'Player',              # 1. Nombre del jugador
    'stats_Squad',         # 2. Equipo
    'stats_Comp',          # 3. Competición
    'stats_Pos',           # 4. Posición
    'stats_Age',           # 5. Edad
    'stats_MP',            # 6. Partidos jugados
    'stats_Min',           # 7. Minutos jugados
    'stats_Gls',           # 8. Goles anotados
    'stats_Ast',           # 9. Asistencias
    'stats_xG',            # 10. Expected Goals
    'stats_xAG',           # 11. Expected Assists
    'stats_npxG',          # 12. Non-penalty xG
    'market_value_in_eur', # 13. Valor de mercado
    'passing_Cmp',         # 14. Pases completados
    'passing_Att',         # 15. Intentos de pase
    'passing_Cmp%',        # 16. % de pases completados
    'passing_TotDist',     # 17. Distancia total de pases
    'passing_PrgDist',     # 18. Distancia progresiva
    'passing_KP',          # 19. Pases clave
    'defense_Tkl',         # 20. Entradas totales
    'defense_Int',         # 21. Intercepciones
    'defense_Blocks',      # 22. Bloqueos
    'stats_CrdY',          # 23. Tarjetas amarillas
    'stats_CrdR',          # 24. Tarjetas rojas
    'stats_G+A',           # 25. Goles + Asistencias
    'stats_xG+xAG',        # 26. xG + xAG
    'playingtime_90s',     # 27. Equivalente a 90 minutos
    'defense_TklW',        # 28. Entradas ganadas
    'passing_CrsPA',       # 29. Asistencias desde centros
    'shooting_Sh',         # 30. Tiros
    'shooting_SoT'         # 31. Tiros al arco
]

# Crear un nuevo dataframe solo con las columnas seleccionadas
df_reducido = df[keep]

# Renombrar las columnas para que sean más descriptivas y legibles
df_reducido = df_reducido.rename(columns={
    'Player': 'Jugador',
    'stats_Squad': 'Equipo',
    'stats_Comp': 'Competición',
    'stats_Pos': 'Posición',
    'stats_Age': 'Edad',
    'stats_MP': 'Partidos',
    'stats_Min': 'Minutos',
    'stats_Gls': 'Goles',
    'stats_Ast': 'Asistencias',
    'stats_xG': 'xG',
    'stats_xAG': 'xAG',
    'stats_npxG': 'npxG',
    'market_value_in_eur': 'ValorMercado',
    'passing_Cmp': 'PasesCompletados',
    'passing_Att': 'IntentosPase',
    'passing_Cmp%': 'PctPasesCompletados',
    'passing_TotDist': 'DistanciaTotalPases',
    'passing_PrgDist': 'DistanciaProgresiva',
    'passing_KP': 'PasesClave',
    'defense_Tkl': 'Entradas',
    'defense_Int': 'Intercepciones',
    'defense_Blocks': 'Bloqueos',
    'stats_CrdY': 'TarjetasAmarillas',
    'stats_CrdR': 'TarjetasRojas',
    'stats_G+A': 'Goles_Asistencias',
    'stats_xG+xAG': 'xG_xAG',
    'playingtime_90s': 'Equiv_90min',
    'defense_TklW': 'EntradasGanadas',
    'passing_CrsPA': 'AsistDesdeCruzados',
    'shooting_Sh': 'Tiros',
    'shooting_SoT': 'TirosAlArco'
})


df_reducido['Minutos'] = (
    df_reducido['Minutos']
    .astype(str)
    .str.replace('.', '', regex=False)  # Elimina puntos si existen (opcional)
    .str.replace(',', '', regex=False)  # Elimina comas (ej: "2,480" → "2480")
)
df_reducido['Minutos'] = pd.to_numeric(df_reducido['Minutos'], errors='coerce')

# Opcional: Puedes guardar este dataframe para usarlo en el notebook
df_reducido.to_csv("datasets_procesados/df_reducido.csv", index=False)

# Visualizamos las primeras filas para confirmar
print(df_reducido.head())

