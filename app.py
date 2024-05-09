from dash import Dash, html, dcc, Input, Output, callback 
import sys
sys.path.append('C:\\inspectair\\Group_01_Inspectair')
from datahandling import *
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
matplotlib.use('agg')
import os
import numpy as np
import re

os.getcwd()
directory = 'C:\\inspectair\\Group_01_Inspectair'
os.chdir(directory)

# Load the data
df = pd.read_excel(os.path.join(directory, "who_ambient_air_quality_database_version_2024_(v6.1).xlsx"), sheet_name="Update 2024 (V6.1)")

# Applying function to pollutants data and add aqi converted data to the columns
df["pm25_aqi"] = pd.DataFrame(calculate_aqi("pm25", (df["pm25_concentration"]).to_numpy()))
df["pm10_aqi"] = pd.DataFrame(calculate_aqi("pm10", (df["pm10_concentration"]).to_numpy()))
df["no2_aqi"] = pd.DataFrame(calculate_aqi("no2", (df["no2_concentration"]).to_numpy()))

legend = {
    'pm10_concentration': 'PM10 Concentration',
    'pm25_concentration': 'PM2.5 Concentration',
    'no2_concentration': 'NO2 Concentration',
    'pm10_aqi': 'PM10 AQI',
    'pm25_aqi': 'PM2.5 AQI',
    'no2_aqi': 'NO2 AQI'
}

# Dictionaries for mapping
continent_dict = {
    '': 'World',
    '1_Afr': 'Africa',
    '2_Amr': 'Americas',
    '3_Sear': 'South-East Asia',
    '4_Eur': 'Europe',
    '5_Emr': 'Eastern Mediterranean',
    '6_Wpr': 'Western Pacific',
    '7_NonMS': 'Non-member state'
}
reverse_continent_dict = {value: key for key, value in continent_dict.items()}

pollutant_type = {
    'pm10_concentration': 'PM10 Concentration',
    'pm25_concentration': 'PM2.5 Concentration',
    'no2_concentration': 'NO2 Concentration'
}
reverse_pollutant_type = {value: key for key, value in pollutant_type.items()}

station_type = {
    'all': ['all'],
    'Rural': ['Rural'],
    'Urban': ['Fond Urbain', 'Urban Traffic', 'Urban', 'Urban Traffic/Residential And Commercial Area'],
    'Residential': ['Residential - industrial','Residential And Commercial Area', 'Urban Traffic/Residential And Commercial Area'],
    'Suburban': ['Suburban'],
    'Industrial': ['Residential - industrial', 'Industrial'],
    'Background': ['Background'],
    'Traffic': ['Traffic', 'Urban Traffic/Residential And Commercial Area']
}

reverse_station_type = {}
for key, values in station_type.items():
    for value in values:
        reverse_station_type[value] = key

# Create options for dropdowns
continents_options = [{'label': name, 'value': key} for key, name in continent_dict.items()]
pollutants_options = [{'label': name, 'value': key} for key, name in pollutant_type.items()]
stations_options = [{'label': name, 'value': key} for key, name in station_type.items()]

all_years = np.array(((df["year"].dropna().unique()).astype(int)), dtype=str)
all_years = np.append(all_years, 'all')
years_options = [{'label': name, 'value': name} for name in all_years]

# Initialize app and layout
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label('Pollutant:', style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='pollutant-dropdown',
            options=pollutants_options,
            value='pm25_concentration'
        )
    ], style={'margin-top': '10px'}),

    html.Div([
        html.Label('Region:', style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='continent-dropdown',
            options=continents_options,
            value=list(continent_dict.keys())[0]  # Make sure keys are ordered if this is Python < 3.7
        )
    ], style={'margin-top': '10px'}),

    html.Div([
        html.Label('From:', style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='from-dropdown',
            options=years_options,
            value='all'
        )
    ], style={'margin-top': '10px', 'margin-bottom': '10px'}),

    html.Div([
        html.Label('To:', style={'font-weight': 'bold'}),
        dcc.Dropdown(
            id='to-dropdown',
            options=years_options,
            value='all'
        )
    ], style={'margin-top': '10px', 'margin-bottom': '10px'}),

    html.Div([
        html.Label('Station type(s):', style={'font-weight': 'bold'}),
        dcc.Checklist(
            id='station-type-checklist',
            options=[{'label': key, 'value': key} for key in station_type.keys()],
            value=['all'],
            inline=True
        )
    ], style={'margin-top': '10px', 'margin-bottom': '10px'}),

    html.Div([
        html.Label('Data Type:', style={'font-weight': 'bold'}),
        dcc.RadioItems(
            id='data-type-radio',
            options=[
                {'label': 'Concentration', 'value': 'Concentration'},
                {'label': 'AQI', 'value': 'AQI'}
            ],
            value='Concentration',
            inline=True
        )
    ], style={'margin-top': '10px', 'margin-bottom': '10px'}),

    dcc.Graph(id='indicator-graphic')
])

# Callback to update the graph based on dropdown selections
@callback(
    Output('indicator-graphic', 'figure'),
        Input('pollutant-dropdown', 'value'),
        Input('continent-dropdown', 'value'),
        Input('from-dropdown', 'value'),
        Input('to-dropdown', 'value'),
        Input('station-type-checklist', 'value'),
        Input('data-type-radio', 'value'))

def update_graph(selected_pollutant, selected_continent, selected_from_year, selected_to_year, selected_station_types, selected_data_type):

    colors=['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue']
    filtered_df = df.copy()

    # Return empty figure if nothing is selected
    if not selected_station_types:
        fig = go.Figure()
        fig.update_layout(
            title="No station type selected",
            xaxis={"visible": False},  # Hide x-axis
            yaxis={"visible": False},  # Hide y-axis
            annotations=[{
                "text": "No station type selected - please select a station type to view data.",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }],
            template='plotly_white'
        )
        return fig
        
    ####################
    ## Data filtering ##
    ####################
    #selected_station_types = ['Residential - industrial', 'Industrial']

    if selected_station_types.count('all') == 0:
        filtered_df = filtered_df.dropna(subset=['type_of_stations'])
        # Filter for type of data using regex
        pattern = '|'.join(r'\b{}\b'.format(re.escape(word)) for word in selected_station_types)
        # Filter the DataFrame using the pattern
        filtered_df = filtered_df[filtered_df['type_of_stations'].str.contains(pattern, na=False)]

    # Select type of data (concentration or AQI)
    if str(selected_data_type)=='AQI':
        selected_pollutant = selected_pollutant.replace("concentration", "aqi")

    # Filter by year range
    if selected_from_year != 'all':
        filtered_df = filtered_df[filtered_df['year'] >= int(selected_from_year)]
    if selected_to_year != 'all':
        filtered_df = filtered_df[filtered_df['year'] <= int(selected_to_year)]

    #######################
    ## Generate the plot ##
    #######################

    fig = go.Figure()

    if selected_continent == '':

        regions = filtered_df['who_region'].unique()
        for region in regions:
            regional_data = filtered_df[filtered_df['who_region'] == region]
            df_pollutant_mean_year = regional_data.pivot_table(index = 'year', values = selected_pollutant, aggfunc = 'mean')
            fig.add_trace(go.Scatter(
                x = df_pollutant_mean_year.index,
                y = df_pollutant_mean_year[selected_pollutant],
                mode = 'lines',
                name = continent_dict[region],
                line = dict(color=colors[regions.tolist().index(region) % len(colors)])
            ))
        fig.update_layout(
            title = legend[selected_pollutant] + ' Across Different Continents',
            xaxis_title = 'Year',
            yaxis_title = legend[selected_pollutant],
            legend_title = 'Region',
            template = 'plotly_white'
        )

    else:
        filtered_df = filtered_df[filtered_df['who_region'] == selected_continent]

        # drop column without data to prevent error in plot
        filtered_df = filtered_df.dropna(subset=[selected_pollutant])
        
        countries = filtered_df['country_name'].unique()
        colors=['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue', 'orange', 'grey']
        for country in countries:
            
            country_data = filtered_df[filtered_df['country_name'] == country]
            if not country_data.empty:
                df_pollutant_mean_year = country_data.pivot_table(index = 'year', values = selected_pollutant, aggfunc = 'mean')
                fig.add_trace(go.Scatter(
                    x = df_pollutant_mean_year.index,
                    y = df_pollutant_mean_year[selected_pollutant],
                    mode = 'lines',
                    name = country,
                    line = dict(color=colors[countries.tolist().index(country) % len(colors)])
                ))
        fig.update_layout(
            title = legend[selected_pollutant] + ' Concentration Across Different Countries in' + continent_dict[selected_continent],
            xaxis_title = 'Year',
            yaxis_title = legend[selected_pollutant],
            legend_title = 'country',
            template = 'plotly_white'
        )        
        return fig
    return fig

# Run the server
if __name__ == '__main__':
    app.run_server(debug=False, port=8002)
