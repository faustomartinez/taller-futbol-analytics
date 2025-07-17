import pandas as pd
import numpy as np
from itertools import combinations
from collections import defaultdict
from sklearn.preprocessing import MinMaxScaler

class LigaSimulator:
    def __init__(self, teams_data):
        """
        Inicializa el simulador con los datos de los equipos.
        teams_data: DataFrame con estadísticas de los equipos.
        """
        if 'Squad' not in teams_data.columns:
            raise ValueError("El DataFrame debe contener una columna 'Squad' con los nombres de los equipos.")
            
        self.teams_data = teams_data.set_index('Squad')
        self.team_strengths = {}
        self.results = []
        
        # Definimos estadísticas ofensivas y defensivas
        self.attack_stats = {
            # Métricas de efectividad
            'Gls': 0.20,       # Goles marcados
            'npxG': 0.15,      # Goles esperados sin penales (más representativo)
            'xG': 0.10,        # Goles esperados totales
    
            # Métricas de creación
            'Ast': 0.10,       # Asistencias
            'xAG': 0.08,       # Asistencias esperadas
            'SCA': 0.10,       # Shot Creating Actions (acciones que crean disparos)
            'GCA': 0.07,       # Goal Creating Actions (acciones que crean goles)
    
            # Métricas de progresión
            'PrgC': 0.05,      # Progressive Carries (avances con balón)
            'PrgP': 0.05,      # Progressive Passes (pases progresivos)
    
            # Métricas de finalización
            'SoT%': 0.05,      # Porcentaje de disparos a puerta
            'G/Sh': 0.05,      # Goles por disparo (eficiencia)
            }
    
        self.defense_stats = {
            # Métricas de prevención
            'GA': -0.25,       # Goles en contra (negativo)
            'PSxG': -0.15,     # Post-Shot xG (calidad de disparos permitidos)
    
            # Métricas del portero
            'Save%': 0.15,     # Porcentaje de paradas
            'CS%': 0.10,       # Porcentaje de porterías a cero
    
            # Métricas de recuperación
            'Tkl': 0.08,       # Tackles totales
            'TklW': 0.07,      # Tackles ganados
            'Int': 0.08,       # Intercepciones
            'Recov': 0.05,     # Recuperaciones
    
            # Métricas de control
            'Blocks': 0.07,    # Bloqueos (Blocks.1)
            'Clr': 0.05,       # Despejes
    
            # Penalizaciones
            'Err': -0.05,      # Errores que llevan a disparos (negativo)
            }

        # Validar que las columnas existen y limpiar los datos
        self._validate_and_clean_data()

    # Lista de estádisticas para elegir en el modelo
    # Para buscar el significado de cada una, se puede consultar en FBRef

    ['Squad', '# Pl', 'Age', 'Poss', 'MP', 'Starts', 'Min', '90s', 'Gls', 'Ast', 'G+A', 'G-PK', 
     'PK', 'PKatt', 'CrdY', 'CrdR', 'xG', 'npxG', 'xAG', 'npxG+xAG', 'PrgC', 'PrgP', 'Gls.1', 'Ast.1', 
     'G+A.1', 'G-PK.1', 'G+A-PK', 'xG.1', 'xAG.1', 'xG+xAG', 'npxG.1', 'npxG+xAG.1', 'Squad.1', '# Pl.1', 
     'MP.1', 'Starts.1', 'Min.1', '90s.1', 'GA', 'GA90', 'SoTA', 'Saves', 'Save%', 'W', 'D', 'L', 'CS', 
     'CS%', 'PKatt.1', 'PKA', 'PKsv', 'PKm', 'Save%.1', 'Squad.2', '# Pl.2', '90s.2', 'GA.1', 'PKA.1', 
     'FK', 'CK', 'OG', 'PSxG', 'PSxG/SoT', 'PSxG+/-', '/90', 'Cmp', 'Att', 'Cmp%', 'Att (GK)', 'Thr', 
     'Launch%', 'AvgLen', 'Att.1', 'Launch%.1', 'AvgLen.1', 'Opp', 'Stp', 'Stp%', '#OPA', '#OPA/90', 
     'AvgDist', 'Squad.3', '# Pl.3', '90s.3', 'Gls.2', 'Sh', 'SoT', 'SoT%', 'Sh/90', 'SoT/90', 'G/Sh', 
     'G/SoT', 'Dist', 'FK.1', 'PK.1', 'PKatt.2', 'xG.2', 'npxG.2', 'npxG/Sh', 'G-xG', 'np:G-xG', 
     'Squad.4', '# Pl.4', '90s.4', 'Cmp.1', 'Att.2', 'Cmp%.1', 'TotDist', 'PrgDist', 'Cmp.2', 'Att.3', 
     'Cmp%.2', 'Cmp.3', 'Att.4', 'Cmp%.3', 'Cmp.4', 'Att.5', 'Cmp%.4', 'Ast.2', 'xAG.2', 'xA', 'A-xAG', 
     'KP', '1/3', 'PPA', 'CrsPA', 'PrgP.1', 'Squad.5', '# Pl.5', '90s.5', 'Att.6', 'Live', 'Dead', 'FK.2', 
     'TB', 'Sw', 'Crs', 'TI', 'CK.1', 'In', 'Out', 'Str', 'Cmp.5', 'Off', 'Blocks', 'Squad.6', '# Pl.6', 
     '90s.6', 'SCA', 'SCA90', 'PassLive', 'PassDead', 'TO', 'Sh.1', 'Fld', 'Def', 'GCA', 'GCA90', 
     'PassLive.1', 'PassDead.1', 'TO.1', 'Sh.2', 'Fld.1', 'Def.1', 'Squad.7', '# Pl.7', '90s.7', 'Tkl', 
     'TklW', 'Def 3rd', 'Mid 3rd', 'Att 3rd', 'Tkl.1', 'Att.7', 'Tkl%', 'Lost', 'Blocks.1', 'Sh.3', 
     'Pass', 'Int', 'Tkl+Int', 'Clr', 'Err', 'Squad.8', '# Pl.8', 'Poss.1', '90s.8', 'Touches', 'Def Pen', 
     'Def 3rd.1', 'Mid 3rd.1', 'Att 3rd.1', 'Att Pen', 'Live.1', 'Att.8', 'Succ', 'Succ%', 'Tkld', 'Tkld%', 
     'Carries', 'TotDist.1', 'PrgDist.1', 'PrgC.1', '1/3.1', 'CPA', 'Mis', 'Dis', 'Rec', 'PrgR', 
     'Squad.9', '# Pl.9', 'Age.1', 'MP.2', 'Min.2', 'Mn/MP', 'Min%', '90s.9', 'Starts.2', 'Mn/Start', 
     'Compl', 'Subs', 'Mn/Sub', 'unSub', 'PPM', 'onG', 'onGA', '+/-', '+/-90', 'onxG', 'onxGA', 'xG+/-', 
     'xG+/-90', 'Squad.10', '# Pl.10', '90s.10', 'CrdY.1', 'CrdR.1', '2CrdY', 'Fls', 'Fld.2', 'Off.1', 
     'Crs.1', 'Int.1', 'TklW.1', 'PKwon', 'PKcon', 'OG.1', 'Recov', 'Won', 'Lost.1', 'Won%']

    def _validate_and_clean_data(self):
        """
        Función interna para validar y preparar los datos.
        """
        all_needed_stats = list(self.attack_stats.keys()) + list(self.defense_stats.keys())
        
        for stat in all_needed_stats:
            if stat not in self.teams_data.columns:
                print(f"⚠️ Advertencia: La columna de estadística '{stat}' no se encontró en los datos. Será ignorada.")

    def calculate_team_strength(self):
        """
        Calcula la fuerza de ataque y defensa de cada equipo.
        """

        # Primero, identificamos qué estadísticas realmente existen en nuestros datos
        attack_stats_available = {stat: weight for stat, weight in self.attack_stats.items() 
                              if stat in self.teams_data.columns}
        defense_stats_available = {stat: weight for stat, weight in self.defense_stats.items() 
                              if stat in self.teams_data.columns}
    
        # Lista de todas las estadísticas disponibles
        available_stats = list(attack_stats_available.keys()) + list(defense_stats_available.keys())
    
        if not available_stats:
            raise ValueError("No se encontró ninguna de las estadísticas relevantes. No se puede calcular la fuerza.")
    
    
        # Seleccionamos SOLO las columnas que necesitamos
        data_to_normalize = self.teams_data[available_stats].copy()

        # Usamos MinMaxScaler para normalizar las estadísticas
        scaler = MinMaxScaler()
        normalized_data = scaler.fit_transform(data_to_normalize)

        # Creamos el DataFrame normalizado
        normalized_stats = pd.DataFrame(
            normalized_data,
            columns=available_stats,
            index=self.teams_data.index
        )    
        for team in self.teams_data.index:
            attack_strength = 0
            defense_strength = 0
            
            # Calcular fuerza de ataque
            for stat, weight in self.attack_stats.items():
                if stat in normalized_stats.columns:
                    attack_strength += normalized_stats.loc[team, stat] * weight
            
            # Calcular fuerza de defensa
            for stat, weight in self.defense_stats.items():
                if stat in normalized_stats.columns:
                    # El peso de GA es negativo, por lo que resta fuerza defensiva
                    if stat == 'GA':
                         # Invertimos la métrica, pues un valor normalizado alto en GA es malo
                        defense_strength += (1 - normalized_stats.loc[team, stat]) * abs(weight)
                    else:
                        defense_strength += normalized_stats.loc[team, stat] * weight

            self.team_strengths[team] = {
                'attack': attack_strength,
                'defense': defense_strength
            }


    
    def simulate_match(self, team1, team2, available_teams):
        """
        Simula un partido entre dos equipos usando su fuerza de ataque y defensa.
        team1 es el equipo local.
        Modelo auto-escalable que se adapta a cualquier liga.
        """
        
        strength1 = self.team_strengths.get(team1)
        strength2 = self.team_strengths.get(team2)
    
        # Calcular escala dinámica de la liga actual
        # Usar solo los equipos disponibles para esta simulación
        all_attacks = [self.team_strengths[team]['attack'] for team in available_teams]
        all_defenses = [self.team_strengths[team]['defense'] for team in available_teams]
    
        # Usar mediana (más robusto que promedio)
        median_attack = np.median(all_attacks)
        median_defense = np.median(all_defenses)
    
        # Calcular ratios relativos a la mediana
        ratio_attack1 = strength1['attack'] / median_attack
        ratio_defense1 = strength1['defense'] / median_defense
        ratio_attack2 = strength2['attack'] / median_attack
        ratio_defense2 = strength2['defense'] / median_defense
    
        # Base de goles adaptativa según la "potencia" de la liga
        league_strength = median_attack / median_defense
        base_goals = 1.3 * league_strength  # Limitar para evitar ligas muy locas
    
        # Ventaja del local
        home_advantage = 1.08  
    
        # Goles esperados usando RATIOS en lugar de valores absolutos
        lambda1 = base_goals * ratio_attack1 / ratio_defense2 * home_advantage
        lambda2 = base_goals * ratio_attack2 / ratio_defense1
    
        # Límites ajustados
        if lambda1 < 0.02 or lambda2 < 0.02:
            print(f"⚠️ Advertencia: Goles esperados muy bajos para {team1} vs {team2}. Ajustando valores.")
            lambda1 = max(0.02, lambda1)
            lambda2 = max(0.02, lambda2)
    
        # Generar goles usando la distribución de Poisson
        goals1 = np.random.poisson(lambda1)
        goals2 = np.random.poisson(lambda2)
    
        if goals1 > goals2:
            result = 'W1'
        elif goals1 < goals2:
            result = 'W2'
        else:
            result = 'D'
        
        return goals1, goals2, result
    

    """
    def simulate_match(self, team1, team2, avaible_teams):
        
        
        Simula un partido entre dos equipos usando su fuerza de ataque y defensa.
        team1 es el equipo local.
        
        
        strength1 = self.team_strengths.get(team1)
        strength2 = self.team_strengths.get(team2)
        
        # Parámetros del modelo
        home_advantage = 1.08  # El equipo local tiene un 15% más de probabilidad de marcar
        base_goals = 1.3       # Goles promedio en un partido neutral
        
        # Goles esperados para el equipo 1 (local)
        # Depende de su ATAQUE vs la DEFENSA del rival
        lambda1 = base_goals * strength1['attack'] / strength2['defense'] * home_advantage
        
        # Goles esperados para el equipo 2 (visitante)
        # Depende de su ATAQUE vs la DEFENSA del rival
        lambda2 = base_goals * strength2['attack'] / strength1['defense']
        
        # Aseguramos que lambda no sea extremadamente bajo o cero para evitar resultados imposibles
        if lambda1 < 0.2 or lambda2 < 0.2:
            print(f"⚠️ Advertencia: Goles esperados muy bajos para {team1} vs {team2}. Ajustando valores.")
            lambda1 = max(0.2, lambda1)
            lambda2 = max(0.2, lambda2)
        
        # Generar goles usando la distribución de Poisson
        goals1 = np.random.poisson(lambda1)
        goals2 = np.random.poisson(lambda2)
        
        if goals1 > goals2:
            result = 'W1'
        elif goals1 < goals2:
            result = 'W2'
        else:
            result = 'D'
            
        return goals1, goals2, result
    """
    
    def simulate_season(self, teams_list, rounds=2):
        """
        Simula una temporada completa
        teams_list: lista de equipos a incluir
        rounds: número de vueltas (1 = todos contra todos una vez, 2 = ida y vuelta)
        """
        # Filtrar equipos disponibles
        available_teams = [team for team in teams_list if team in self.team_strengths]
        
        if len(available_teams) < 2:
            return None
        
        # Inicializar tabla de posiciones
        league_table = defaultdict(lambda: {
            'played': 0, 'won': 0, 'drawn': 0, 'lost': 0,
            'goals_for': 0, 'goals_against': 0, 'goal_difference': 0,
            'points': 0
        })
        
        self.results = []
        matchday = 1
        
        # Generar calendario
        for round_num in range(rounds):
            # Todos contra todos
            for team1, team2 in combinations(available_teams, 2):
                if round_num == 1:  # En la vuelta 2, intercambiar local/visitante
                    team1, team2 = team2, team1
                
                goals1, goals2, result = self.simulate_match(team1, team2, available_teams)
                
                # Actualizar estadísticas
                league_table[team1]['played'] += 1
                league_table[team2]['played'] += 1
                league_table[team1]['goals_for'] += goals1
                league_table[team1]['goals_against'] += goals2
                league_table[team2]['goals_for'] += goals2
                league_table[team2]['goals_against'] += goals1
                
                if result == 'W1':
                    league_table[team1]['won'] += 1
                    league_table[team1]['points'] += 3
                    league_table[team2]['lost'] += 1
                elif result == 'W2':
                    league_table[team2]['won'] += 1
                    league_table[team2]['points'] += 3
                    league_table[team1]['lost'] += 1
                else:  # Empate
                    league_table[team1]['drawn'] += 1
                    league_table[team1]['points'] += 1
                    league_table[team2]['drawn'] += 1
                    league_table[team2]['points'] += 1
                
                # Calcular diferencia de goles
                league_table[team1]['goal_difference'] = league_table[team1]['goals_for'] - league_table[team1]['goals_against']
                league_table[team2]['goal_difference'] = league_table[team2]['goals_for'] - league_table[team2]['goals_against']
                
                # Guardar resultado
                self.results.append({
                    'matchday': matchday,
                    'home_team': team1,
                    'away_team': team2,
                    'home_goals': goals1,
                    'away_goals': goals2,
                    'result': result
                })
                
                matchday += 1
        
        # Convertir a DataFrame y ordenar según puntos, diferencia de goles y goles a favor
        table_df = pd.DataFrame(league_table).T
        table_df = table_df.sort_values(['points', 'goal_difference', 'goals_for'], ascending=[False, False, False])
        table_df['position'] = range(1, len(table_df) + 1)
        
        return table_df
    
    def display_results(self, table_df):
        """
        Muestra los resultados de la simulación
        """
        print("\n" + "="*80)
        print("TABLA DE POSICIONES FINAL (TOP 10)")
        print("="*80)
        
        # Mostrar tabla completa
        display_table = table_df.copy()

        # Agregar columnas de ataque y defensa
        display_table['attack'] = display_table.index.map(lambda x: self.team_strengths[x]['attack'])
        display_table['defense'] = display_table.index.map(lambda x: self.team_strengths[x]['defense'])

        display_table = display_table[['position', 'played', 'won', 'drawn', 'lost', 
                                       'goals_for', 'goals_against', 'goal_difference', 
                                       'points', 'attack', 'defense']]
        
        # Renombrar columnas
        display_table.columns = ['Pos', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'DG', 'Pts', 'Ataque', 'Defensa']
        
        # Formatear las columnas de ataque y defensa
        display_table['Ataque'] = display_table['Ataque'].round(3)
        display_table['Defensa'] = display_table['Defensa'].round(3)


        print(display_table.head(10).to_string())
        
        # Estadísticas interesantes
        print("\n" + "="*80)
        print("ESTADÍSTICAS DESTACADAS")
        print("="*80)
        
        champion = table_df.index[0]
        print(f"🏆 CAMPEÓN: {champion} ({table_df.loc[champion, 'points']} puntos)")
        
        max_goals_team = table_df.loc[table_df['goals_for'].idxmax()]
        print(f"⚽ Más goles a favor: {max_goals_team.name} ({max_goals_team['goals_for']} goles)")
        
        min_goals_against_team = table_df.loc[table_df['goals_against'].idxmin()]
        print(f"🛡️ Menos goles en contra: {min_goals_against_team.name} ({min_goals_against_team['goals_against']} goles)")
        
        if len(table_df) > 3:
            relegated = table_df.tail(3).index.tolist()
            print(f"📉 Descenso: {', '.join(relegated)}")

def liga_simulator_montecarlo(data_file, teams_list, n_simulations=100, rounds=2):
    """
    Ejecuta múltiples simulaciones para obtener resultados más robustos
    
    Parámetros:
    - data_file: DataFrame con datos de equipos
    - teams_list: lista de equipos a simular
    - n_simulations: número de simulaciones a ejecutar (default: 100)
    - rounds: vueltas del torneo (default: 2)
    
    Retorna:
    - DataFrame con resultados promedios de las simulaciones
    """
    # Cargar datos
    if isinstance(data_file, str):
        df = pd.read_csv(data_file)
    else:
        df = data_file
    
    # Crear simulador base
    simulator = LigaSimulator(df)
    simulator.calculate_team_strength()
    
    # Almacenar resultados
    all_positions = defaultdict(list)
    all_points = defaultdict(list)
    championships = defaultdict(int)
    relegations = defaultdict(int)
    top_4 = defaultdict(int)
    
    print(f"Ejecutando {n_simulations} simulaciones...")

    for i in range(n_simulations):
        if (i + 1) % 20 == 0:
            print(f"  Simulación {i + 1}/{n_simulations}")
        
        # Simular temporada
        table = simulator.simulate_season(teams_list, rounds)
    
        if table is not None:
            # Registrar resultados
            for team in table.index:
                position = table.loc[team, 'position']
                points = table.loc[team, 'points']
            
                all_positions[team].append(position)
                all_points[team].append(points)
            
                if position == 1:
                    championships[team] += 1
                if position <= 4:
                    top_4[team] += 1
                if position > len(table) - 3:
                    relegations[team] += 1
    
    # Crear tabla de resultados
    results = []
    for team in teams_list:
        if team in all_positions:
            results.append({
                'Equipo': team,
                'Pos_Promedio': np.mean(all_positions[team]),
                'Ataque' : simulator.team_strengths[team]['attack'],
                'Defensa' : simulator.team_strengths[team]['defense'],
                'Desv_Std': np.std(all_positions[team]),
                'Pos_Mejor': min(all_positions[team]),
                'Pos_Peor': max(all_positions[team]),
                'Puntos_Prom': np.mean(all_points[team]),
                'Veces_Campeon': championships[team],
                'Prob_Campeon%': championships[team] / n_simulations * 100,
                'Prob_Top4%': top_4[team] / n_simulations * 100,
                'Prob_Descenso%': relegations[team] / n_simulations * 100
            })
    
    # Crear DataFrame y ordenar
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Pos_Promedio')
    results_df['Ranking'] = range(1, len(results_df) + 1)

    # Reordenar columnas
    cols = ['Ranking'] + [col for col in results_df.columns if col != 'Ranking']
    results_df = results_df[cols]
    
    # Formatear
    results_df['Pos_Promedio'] = results_df['Pos_Promedio'].round(1)
    results_df['Ataque'] = results_df['Ataque'].round(3)
    results_df['Defensa'] = results_df['Defensa'].round(3)
    results_df['Desv_Std'] = results_df['Desv_Std'].round(2)
    results_df['Puntos_Prom'] = results_df['Puntos_Prom'].round(1)
    results_df['Prob_Campeon%'] = results_df['Prob_Campeon%'].round(1)
    results_df['Prob_Top4%'] = results_df['Prob_Top4%'].round(1)
    results_df['Prob_Descenso%'] = results_df['Prob_Descenso%'].round(1)

    # Mostrar resultados
    print("\n" + "="*100)
    print(f"RESULTADOS DE {n_simulations} SIMULACIONES (TOP 10)")
    print("="*100)
    print(results_df.head(10).to_string(index=False))

    # Análisis
    print("\n" + "="*80)
    print("ANÁLISIS")
    print("="*80)
    
    favorito = results_df.iloc[0]
    print(f"🏆 FAVORITO: {favorito['Equipo']} ({favorito['Prob_Campeon%']:.1f}% prob. de ser campeón)")
    
    if len(results_df) > 3:
        en_riesgo = results_df[results_df['Prob_Descenso%'] > 20].sort_values('Prob_Descenso%', ascending=False)
        if not en_riesgo.empty:
            print(f"⚠️ EN RIESGO DE DESCENSO: {', '.join(en_riesgo['Equipo'].tolist())}")
    
    return results_df

def liga_simulator(data_file, teams_list, rounds=2):
    """
    Simula una temporada de liga y muestra los resultados
    
    Retorna:
    - DataFrame con la tabla final
    - Objeto simulador para análisis adicional
    """
    # Cargar datos
    if isinstance(data_file, str):
        df = pd.read_csv(data_file)
    else:
        df = data_file
    
    # Crear simulador
    simulator = LigaSimulator(df)
    simulator.calculate_team_strength()
    
    # Simular temporada
    table = simulator.simulate_season(teams_list, rounds)

    results = table.copy()

    results['attack'] = results.index.map(lambda x: simulator.team_strengths[x]['attack'])
    results['defense'] = results.index.map(lambda x: simulator.team_strengths[x]['defense'])

    results = results[['position', 'played', 'won', 'drawn', 'lost', 
                    'goals_for', 'goals_against', 'goal_difference', 
                    'points', 'attack', 'defense']]
        
    # Renombrar columnas
    results.columns = ['Pos', 'PJ', 'G', 'E', 'P', 'GF', 'GC', 'DG', 'Pts', 'Ataque', 'Defensa']
        
    # Formatear las columnas de ataque y defensa
    results['Ataque'] = results['Ataque'].round(3)
    results['Defensa'] = results['Defensa'].round(3)
    
    if table is not None:
        # Mostrar resultados
        simulator.display_results(table)
    else:
        print("Error: No se pudo simular la temporada. Verifica que los equipos existan en los datos.")
    
    return results, simulator




# Ejemplo de uso

"""
df_premier = pd.read_csv("datasets/team_stats_premierleague.csv")
df_seriea = pd.read_csv("datasets/team_stats_seriea.csv")
df_bundesliga = pd.read_csv("datasets/team_stats_bundesliga.csv")
df_laliga = pd.read_csv("datasets/team_stats_laliga.csv")
df_argentina = pd.read_csv("datasets/team_stats_argentina.csv")
df_ligue1 = pd.read_csv("datasets/team_stats_ligue1.csv")
df_mls = pd.read_csv("datasets/team_stats_mls.csv")

df_equipos = pd.read_csv("datasets_procesados/df_equipos.csv")

lista_equipos = df_premier['Squad'].tolist()

tabla_general, simulador = liga_simulator(df_equipos, lista_equipos)
"""