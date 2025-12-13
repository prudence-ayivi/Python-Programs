import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import folium
import json
import os

# Initialisation de l'app Dash
app = dash.Dash(__name__)
app.title = "Dashboard Bac Bénin 2019-2023"
app.config.suppress_callback_exceptions = True

# Charger les données
excel_file = 'Bac_Benin_2019_2023.xlsx'
df_departement = pd.read_excel(excel_file, sheet_name='Par Département')
df_serie = pd.read_excel(excel_file, sheet_name='Par Série')

# Normalisation des types
df_departement['Année'] = df_departement['Année'].astype(str)
df_serie['Année'] = df_serie['Année'].astype(str)

# Liste des années disponibles
available_years = sorted(df_departement['Année'].unique())

# Localisation approximative des départements (à compléter ou ajuster selon précision souhaitée)
departement_locations = {
    'Alibori': [11.5, 3.0],
    'Atacora': [10.3, 1.4],
    'Atlantique': [6.5, 2.2],
    'Borgou': [9.5, 2.6],
    'Collines': [8.5, 2.2],
    'Donga': [9.8, 1.6],
    'Kouffo': [6.9, 1.7],
    'Littoral': [6.35, 2.4],
    'Mono': [6.6, 1.6],
    'Ouémé': [6.7, 2.6],
    'Plateau': [7.4, 2.7],
    'Zou': [7.1, 2.2],
}

# Fonction : créer la carte du Bénin avec les données pour une année donnée
def create_benin_map(year):
    data_year = df_departement[df_departement['Année'] == year]
    
    # Charger le GeoJSON
    with open("bj.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)
    
    # Dictionnaire des infos par département
    info_par_dept = {}
    for _, row in data_year.iterrows():
        dept = row['Département']
        total = row['Total']
        taux = row['Taux de Réussite (%)']
        hommes = row['Masculin'] if 'Masculin' in row and year != "2019" else None
        femmes = row['Féminin'] if 'Féminin' in row and year != "2019" else None
        info_par_dept[dept] = {
            'total': total,
            'taux': taux,
            'Masculin': hommes,
            'Féminin': femmes
        }

    # Création de la carte centrée sur le Bénin
    benin_map = folium.Map(location=[9.3, 2.3], zoom_start=5)

    # Fonction de style dynamique
    def style_function(feature):
        dept = feature['properties']['name']
        taux = info_par_dept.get(dept, {}).get('taux', 0)
        color = "green" if taux > 50 else "red"
        return {
            'fillOpacity': 0.6,
            'weight': 1,
            'color': 'black',
            'fillColor': color
        }

    # Fonction popup HTML
    def popup_function(dept):
        if dept not in info_par_dept:
            return f"<b>{dept}</b><br>Données non disponibles"
        info = info_par_dept[dept]
        popup = f"<b>{dept}</b><br>Inscrits : {info['total']}<br>Taux de réussite : {info['taux']}%"
        if info['Masculin'] is not None and info['Féminin'] is not None:
            popup += f"<br>Hommes : {info['Masculin']}<br>Femmes : {info['Féminin']}"
        return popup

    # Ajouter les départements à la carte
    folium.GeoJson(
        geojson_data,
        name="Départements",
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['name'],
            aliases=['Département :'],
            localize=True
        )
    ).add_to(benin_map)

    # Ajouter les popups personnalisés par département
    # for feature in geojson_data['features']:
    #     dept = feature['properties']['name']
    #     coords = feature['geometry']['coordinates'][0][0]  # Premier point de la géométrie
    #     lon, lat = coords[0], coords[1]
    #     popup_html = popup_function(dept)
    #     folium.Marker(
    #         location=[lat, lon],
    #         icon=folium.DivIcon(html=f"<div style='display:none'></div>"),  # invisible marker
    #         popup=popup_html
    #     ).add_to(benin_map)

        # Ajouter les vrais popups avec les infos dynamiques
    for feature in geojson_data['features']:
        dept = feature['properties']['name']
        coords = feature['geometry']['coordinates'][0][0]
        lon, lat = coords[0], coords[1]
        popup_html = popup_function(dept)
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color="blue", icon="info-sign"),
            popup=folium.Popup(popup_html, max_width=200)
        ).add_to(benin_map)


    map_file = "assets/benin_map.html"
    os.makedirs("assets", exist_ok=True)
    benin_map.save(map_file)
    return map_file
    data_year = df_departement[df_departement['Année'] == year]
    benin_map = folium.Map(location=[9.3, 2.3], zoom_start=7)

    for _, row in data_year.iterrows():
        dept = row['Département']
        inscrits = row['Total']
        taux = row['Taux de Réussite (%)']
        if dept in departement_locations:
            lat, lon = departement_locations[dept]
            folium.CircleMarker(
                location=[lat, lon],
                radius=10,
                popup=folium.Popup(f"<b>{dept}</b><br>Inscrits : {inscrits}<br>Taux de réussite : {taux}%", max_width=250),
                color="blue",
                fill=True,
                fill_color="green" if taux > 50 else "red",
                fill_opacity=0.7
            ).add_to(benin_map)

    map_file = "assets/benin_map.html"
    os.makedirs("assets", exist_ok=True)
    benin_map.save(map_file)
    return map_file

# Générer carte initiale
initial_map_path = create_benin_map("2019")

# Fonction : calcul du total national pour l'année
def get_global_stats(year):
    data_year = df_departement[df_departement['Année'] == year]
    total_inscrits = data_year['Total'].sum()
    # Moyenne pondérée du taux de réussite par rapport aux inscrits
    total_pondere = (data_year['Taux de Réussite (%)'] * data_year['Total']).sum()
    taux_global = total_pondere / total_inscrits if total_inscrits > 0 else 0
    return int(total_inscrits), round(taux_global, 2)

# Layout
app.layout = html.Div([
    html.H1("Dashboard Bac Bénin (2019 - 2023)", style={'textAlign': 'center'}),
    
    html.Div([
        # Carte du Bénin
        html.Iframe(
            id='benin-map',
            srcDoc=open(initial_map_path, 'r', encoding='utf-8').read(),
            width='100%',
            height='500'
        ),

        # Panneau à droite
        html.Div([
            html.Label("Sélectionnez l’année :", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': y, 'value': y} for y in available_years],
                value='2019',
                clearable=False
            ),
            html.Br(),
            html.Div(id='global-stats', style={
                'padding': '10px',
                'border': '1px solid #ccc',
                'borderRadius': '8px',
                'backgroundColor': '#f9f9f9',
                'fontWeight': 'bold'
            })
        ], style={'width': '30%', 'marginLeft': '20px'})
    ], style={'display': 'flex', 'gap': '20px', 'margin': '20px'}),
])

# Callback : mise à jour de la carte et du panneau info
@app.callback(
    [Output('benin-map', 'srcDoc'),
     Output('global-stats', 'children')],
    [Input('year-dropdown', 'value')]
)
def update_dashboard(year):
    map_path = create_benin_map(year)
    with open(map_path, 'r', encoding='utf-8') as f:
        map_html = f.read()

    total_inscrits, taux_reussite = get_global_stats(year)
    global_stats_text = f"Total inscrits : {total_inscrits:,}  |  Taux de réussite national : {taux_reussite}%"

    return map_html, global_stats_text

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
