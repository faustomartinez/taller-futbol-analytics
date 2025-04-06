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