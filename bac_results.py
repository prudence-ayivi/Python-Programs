import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt
import folium

#Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Dashboard des statistiques du Bac de 2019 à 2023"

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Initialize the map 
benin_map=folium.Map(location=[6, 2], zoom_start=3)

# Load and Read the data with pandas
excel_file = 'Bac_Benin_2019_2023.xlsx'
data_par_serie = pd.read_excel(excel_file, sheet_name='Par Série')
data_par_departement = pd.read_excel(excel_file, sheet_name='Par Département')
# Convert the 'Year' column to string for consistency
data_par_serie['Year'] = data_par_serie['Year'].astype(str)
data_par_departement['Year'] = data_par_departement['Year'].astype(str)

# # Save the data to CSV files
# data_per_series =  pd.read_csv('bac_benin_par_serie.csv')
# data_per_dept = pd.read_csv('bac_benin_par_departement.csv')

# Create the dropdown menu options
dropdown_option = [
    {'label': 'Statistiques annuelles', 'value': 'Année'},
]
# List of years 
year_list = [i for i in range(2019, 2023, 1)]

#---------------------------------------------------------------------------------------
# Create the layout of the app
app.layout = html.Div([
    html.H1("Dashboard des statistiques du Bac de 2019 à 2023", style={'textAlign': 'left', 'color': '#503D36', 'fontSize': 24}),#Include style for title
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options= dropdown_option,
            value='Selectionné Statistics',
            placeholder='Select a report type', 
            style={'textAlign': 'center', 'width': '80%', 'fontSize': 20}
        )
    ]),
    html.Div(dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value='Select-year', 
            placeholder='Select-year',
            style={'textAlign': 'center', 'width': '80%', 'fontSize': 20}
        )),
    html.Div([
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex'}),])
])

# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics',component_property='value'))

def update_input_container(selected_statistics):
    if selected_statistics =='Statistiques annuelles': 
        return False
    else: 
        return True

#Callback for plotting
# Define the callback function to update the input container based on the selected statistics
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), Input(component_id='select-year', component_property='value')])


def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Statistiques annuelles':
        # Filter the data for yearly statistics
        year_data = data_par_serie[data_par_serie['Year'] == input_year]
    # else: 
    #     if selected_years == 'Yearly Statistics':
    #         year_data = data[data['Year']]


# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)