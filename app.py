import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Initialisation de l'app
app = dash.Dash(__name__)
app.title = "Dashboard Bac Bénin 2019-2023"

# Chargement des données
df_dep = pd.read_excel('Bac_Benin_2019_2023.xlsx', sheet_name='Par Département')
df_serie = pd.read_excel('Bac_Benin_2019_2023.xlsx', sheet_name='Par Série')

# Normalisation des années
df_dep['Année'] = df_dep['Année'].astype(str)
df_serie['Année'] = df_serie['Année'].astype(str)

available_years = sorted(df_dep['Année'].unique())

# Layout
app.layout = html.Div([
    html.H1("Dashboard Bac Bénin (2019 - 2023)", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Sélectionnez une année :", style={'fontWeight': 'bold'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': y, 'value': y} for y in available_years],
            value='2023',
            clearable=False
        )
    ], style={'width': '300px', 'margin': 'auto'}),

    html.Br(),

    html.Div(id='graphs-container')
])

# Callback pour mettre à jour les graphiques en fonction de l'année sélectionnée
@app.callback(
    Output('graphs-container', 'children'),
    Input('year-dropdown', 'value')
)
def update_graphs(year):
    graphs = []

    ## 1. Évolution du taux de réussite global (2019–2023)
    df_dep['Taux * Total'] = df_dep['Taux de Réussite (%)'] * df_dep['Total']
    df_global = df_dep.groupby('Année').agg({
    'Taux * Total': 'sum',
    'Total': 'sum'
    }).reset_index()
    df_global['Taux Global'] = df_global['Taux * Total'] / df_global['Total']
    # fig1 = px.line(df_global, x='Année', y='Taux Global', markers=True, title="Évolution du taux de réussite global")

    # Graphe combiné
    fig1 = px.line(df_global, x='Année', y='Taux Global', markers=True, labels={'Taux Global': 'Taux de Réussite (%)'})
    fig1.update_traces(name='Taux de Réussite (%)', yaxis='y1')

    fig1.add_bar(x=df_global['Année'], y=df_global['Total'], name='Nombre d’inscrits', yaxis='y2', marker_color='lightblue')

    fig1.update_layout(
        title="Évolution du taux de réussite et du nombre d’inscrits (2019–2023)",
        yaxis=dict(title='Taux de Réussite (%)', range=[0, 100]),
        yaxis2=dict(title='Nombre d’inscrits', overlaying='y', side='right'),
        legend=dict(x=0.01, y=0.99),
    )

    graphs.append(dcc.Graph(figure=fig1))

        # 1b. Évolution des inscrits par série (toutes années)
    df_series_grouped = df_serie.groupby(['Année', 'Série'])['Inscrits'].sum().reset_index()
    fig1b = px.bar(df_series_grouped, x='Année', y='Inscrits', color='Série',
                   barmode='group', title="Évolution des inscrits par série (2019-2023)")

    # Disposition côte à côte de fig1 et fig1b
    graphs.append(html.Div([
        html.Div(dcc.Graph(figure=fig1), style={'width': '50%', 'display': 'inline-block'}),
        html.Div(dcc.Graph(figure=fig1b), style={'width': '50%', 'display': 'inline-block'})
    ]))


    ## 2. Taux par département pour l’année
    df_dep_year = df_dep[df_dep['Année'] == year]
    fig2 = px.bar(df_dep_year, x='Département', y='Taux de Réussite (%)', title=f"Taux de réussite par département ({year})", color='Taux de Réussite (%)', color_continuous_scale='Viridis')
    graphs.append(dcc.Graph(figure=fig2))

    ## 3. Répartition des admis par série
    df_serie_year = df_serie[df_serie['Année'] == year].copy()
    df_serie_year['Admis'] = (df_serie_year['Taux de réussite  (%)'] / 100) * df_serie_year['Inscrits']
    fig3 = px.pie(df_serie_year, names='Série', values='Admis', title=f"Répartition des admis par série ({year})")
    # 2b. Répartition des inscrits par série pour l’année sélectionnée
    fig2b = px.pie(df_serie_year, names='Série', values='Inscrits', title=f"Répartition des inscrits par série ({year})")
    graphs.append(dcc.Graph(figure=fig3))
    graphs.append(dcc.Graph(figure=fig2b))


    ## 4. Nombre d'inscrits par sexe par département (sauf 2019)
    if year != '2019' and 'Hommes' in df_dep.columns and 'Femmes' in df_dep.columns:
        df_sexe = df_dep_year[['Département', 'Hommes', 'Femmes']].set_index('Département')
        df_sexe = df_sexe.reset_index().melt(id_vars='Département', var_name='Sexe', value_name='Inscrits')
        fig4 = px.bar(df_sexe, x='Département', y='Inscrits', color='Sexe', barmode='group', title=f"Nombre d'inscrits par sexe ({year})")
        graphs.append(dcc.Graph(figure=fig4))

    ## 5. Taux de réussite par sexe (si dispo)
    if year != '2019' and 'Hommes' in df_dep.columns and 'Femmes' in df_dep.columns and 'Admis Hommes' in df_dep.columns:
        total_h = df_dep_year['Hommes'].sum()
        total_f = df_dep_year['Femmes'].sum()
        admis_h = df_dep_year['Admis Hommes'].sum()
        admis_f = df_dep_year['Admis Femmes'].sum()
        taux_h = (admis_h / total_h * 100) if total_h else 0
        taux_f = (admis_f / total_f * 100) if total_f else 0

        df_sex_taux = pd.DataFrame({
            'Sexe': ['Hommes', 'Femmes'],
            'Taux de réussite': [taux_h, taux_f]
        })
        fig5 = px.bar(df_sex_taux, x='Sexe', y='Taux de réussite', title=f"Taux de réussite par sexe ({year})", color='Sexe')
        graphs.append(dcc.Graph(figure=fig5))

    ## 6. Comparaison des séries
    fig6 = px.bar(df_serie_year, x='Série', y=['Inscrits', 'Admis'], barmode='group', title=f"Inscrits vs Admis par série ({year})")
    graphs.append(dcc.Graph(figure=fig6))

    return graphs

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
