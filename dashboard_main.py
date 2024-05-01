# Import packages
from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
matplotlib.use('agg')
import os
import numpy as np

os.getcwd()
directory = "C:\inspectair\Group_01_Inspectair"
os.chdir(directory)

# https://dash.plotly.com/basic-callbacks
app = Dash(__name__)

# Use your path to the excel file with data (this will be changed later to an online version or possibly a real time version)
df = pd.read_excel(".//who_ambient_air_quality_database_version_2024_(v6.1).xlsx", sheet_name="Update 2024 (V6.1)")

# Airquality are usually measured in aqi when target app audience are general public for ease of data intepretation and we will do that here using lerp and calculate_aqi function
def lerp(low_aqi, high_aqi, low_conc, high_conc, conc):
    return low_aqi + (conc - low_conc) * (high_aqi - low_aqi) / (high_conc - low_conc)

def calculate_aqi(pollutant_type, concentrations):
    aqi_values = []
    for conc in concentrations:
        if np.isnan(conc):
            aqi_values.append(None)
            continue
        
        conc = max(conc, 0)
        
        # define pollutant types and their thresholds
        if pollutant_type == 'no2':
            breakpoints = [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150),
                           (361, 649, 151, 200), (650, 1249, 201, 300), (1250, 1649, 301, 400),
                           (1650, 2049, 401, 500)]
        elif pollutant_type == 'pm25':
            breakpoints = [(0.0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                           (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400),
                           (350.5, 500.4, 401, 500)]
        elif pollutant_type == 'pm10':
            breakpoints = [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                           (55.5, 150.4, 151, 200), (150.5, 100.4, 201, 300), (100.5, 350.4, 301, 400),
                           (350.5, 500.4, 401, 500)]
        else:
            raise ValueError("Unsupported pollutant type")

        # Default AQI if concentration is beyond the highest range
        aqi = 500  
        for (low_conc, high_conc, low_aqi, high_aqi) in breakpoints:
            if low_conc <= conc <= high_conc:
                aqi = lerp(low_aqi, high_aqi, low_conc, high_conc, conc)
                break
        
        aqi_values.append(round(aqi))
    
    return aqi_values

# Applying function to pollutants data and add aqi converted data to the columns
df["pm25_aqi"] = pd.DataFrame(calculate_aqi("pm25", (df["pm25_concentration"]).to_numpy()))
df["pm10_aqi"] = pd.DataFrame(calculate_aqi("pm10", (df["pm10_concentration"]).to_numpy()))
df["no2_aqi"] = pd.DataFrame(calculate_aqi("no2", (df["no2_concentration"]).to_numpy()))

# Define data column to fetch on dropdown interactive filter
pollutants=["pm25_aqi", "pm10_aqi", "no2_aqi"]
pollutants_options = [{'label': name, 'value': name} for name in pollutants]

# App layout
app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='indicator-dropdown',
                options=pollutants_options,
                value=pollutants[0]
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

    ]),

    dcc.Graph(id='indicator-graphic')
])

# Values from dropdown list
@callback(
    Output('indicator-graphic', 'figure'),
    Input('indicator-dropdown', 'value')
    )

# Update graphs interactively
def update_graph(pollutant):

    # Define dictionaries for continents
    regions_dict = {
        '1_Afr': 'African',
        '2_Amr': 'Americas',
        '3_Sear': 'South-East Asia',
        '4_Eur': 'Europe',
        '5_Emr': 'Eastern Mediterranean',
        '6_Wpr': 'Western Pacific',
        '7_NonMS': 'non-member state'
    }

    # Define legends dictionary
    legends = {
        'pm25_aqi': 'pm 10 aqi',
        'pm10_aqi': 'pm 2.5 aqi',
        'no2_aqi': 'NO2 aqi'
    }

    colors=['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue']
    columns=['year']
    indices=['who_region']

    # Data cleaning (dropping rows with no relevant data)
    dff=df.dropna(subset=['iso3', 'year'])
    dff=dff.drop_duplicates()
    dff=dff.drop_duplicates(subset=['iso3', 'city', 'year', 'pm10_concentration', 'pm25_concentration', 'no2_concentration'])

    df_pollutant_mean_year = pd.pivot_table(data=dff, index=indices, columns=columns, aggfunc='mean', values=pollutants)

    # First graph plotting
    fig = go.Figure()
    table_for_plot = df_pollutant_mean_year[pollutant].T
    for region in df["who_region"].unique():
        fig.add_trace(go.Scatter(
            x=table_for_plot.index,
            y=table_for_plot[region],
            mode='lines',
            name=regions_dict[region],
            line=dict(color=colors[df["who_region"].unique().tolist().index(region)])
        ))

    fig.update_layout(
        title = pollutant + ' aqi Across Different Continents',
        xaxis_title = 'Year',
        yaxis_title = legends[pollutant],
        legend_title = 'Region',
        template = 'plotly_white'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=False, port=8002)
