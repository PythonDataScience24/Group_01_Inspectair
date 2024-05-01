# Import packages
import base64
from io import BytesIO
from dash import Dash, html, dcc, Input, Output, callback 
from math import ceil
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc  
matplotlib.use('agg')
import os
import numpy as np

os.getcwd()
#directory = "C:\inspectair\Group_01_Inspectair"
#os.chdir(directory)

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

    dcc.Graph(id='indicator-graphic'),
dbc.Row([
    dbc.Col(
        html.Img(id='bar-graph-matplotlib'),
        style={'padding': '50px'},
        width=16),
        

    dbc.Col(
        html.Img(id='bar-graph-matplotlib_bottom'),
        style={'padding': '50px'},
        width=16),
        
])
])

# Values from dropdown list
@callback(
    Output('indicator-graphic', 'figure'),
    Output('bar-graph-matplotlib', 'src'),
    Output('bar-graph-matplotlib_bottom', 'src'),
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

    #extract top 10 polluted cities (for now only most recent year = 2022)
    dff_2022 = dff[dff.year == 2022]
    #add log pollutant entry to dataframe
    dff_2022[f'log_{pollutant}'] = np.log(dff_2022[pollutant])
    #create complete list of pollutants including log pollutants
    log_pollutants = ["pm25_aqi", "pm10_aqi", "no2_aqi", f'log_{pollutant}']
    mean_city_2022 = pd.pivot_table(data=dff_2022, index=['city'], aggfunc='mean', values=log_pollutants)
    top_ranked_10 = mean_city_2022.sort_values(by=pollutant, ascending=False)[0:10]
    #reverse order for horizontal barplot
    top_ranked_10 = top_ranked_10.sort_values(by=pollutant)
    
    
    #extract 10 least polluted cities (for now only most recent year)
    bottom_ranked_10 = mean_city_2022.sort_values(by=pollutant, ascending=True)[0:10]
    #reverse order for horizontal barplot
    bottom_ranked_10 = bottom_ranked_10.sort_values(by=pollutant, ascending=False)
    
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

    #build the top 10 ranking plot
    color_palette_top_10 = [
    "#FFFF00", "#FFEA00", "#FFD400", "#FFBF00", "#FFAA00",
    "#FF9500", "#FF8000", "#FF6A00", "#FF5500", "#FF4000"]
    fig_top_10 = plt.figure(figsize=(10, 5), constrained_layout=True)
    #define xlim as max value of top ranked log pollutant
    xlim = ceil(np.max(top_ranked_10[f'log_{pollutant}'].values))
    #create horizontal barplot
    plt.barh(top_ranked_10[f'log_{pollutant}'].index, top_ranked_10[f'log_{pollutant}'].values, color=color_palette_top_10)
    plt.xlabel(f'Log {legends[pollutant]}')
    plt.title(('Top 10 most polluted cities in 2022 (average values are shown; low value is better)\n'
               'NON-transformed numbers are shown in plot'))    
    plt.xlim([0,xlim])
    plt.gca().spines['top'].set_visible(False) 
    plt.gca().spines['right'].set_visible(False) 
    #add the non transformed values to the plot as text
    s = top_ranked_10[pollutant].values
    x = top_ranked_10[f'log_{pollutant}'].values
    for i in range(len(x)):
        plt.text(x=(x[i]+0.1), y=i, s=round(s[i], 2), va='baseline')
        
    # Save figure to a temporary buffer.
    buf = BytesIO()
    fig_top_10.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib = f'data:image/png;base64,{fig_data}'#
    
    #build bottom 10 ranking plot
    color_palette_bottom_10 = [
    "#e6ff66", "#ccff33", "#b3ff00", "#99e600", "#80cc00", 
    "#66b300", "#4d9900","#338000", "#1a6600", "#004d00"]
    #build horizontal barplot
    fig_bottom_10 = plt.figure(figsize=(10, 5), constrained_layout=True)
    #create horizontal barplot
    plt.barh(bottom_ranked_10[f'log_{pollutant}'].index, bottom_ranked_10[f'log_{pollutant}'].values, 
             color=color_palette_bottom_10)
    plt.xlabel(f'Log {legends[pollutant]}')
    plt.title(('Top 10 least polluted cities in 2022 (average values are shown; low value is better)\n'
               'NON-transformed numbers are shown in plot'))
    plt.xlim([0,xlim])
    plt.gca().spines['top'].set_visible(False) 
    plt.gca().spines['right'].set_visible(False) 

    #add the non transformed values to the plot as text
    s = bottom_ranked_10[pollutant].values
    x = bottom_ranked_10[f'log_{pollutant}'].values
    for i in range(len(x)):
        plt.text(x=(x[i]+0.1), y=i, s=round(s[i], 2), va='baseline')
    

    # Save figure to a temporary buffer.
    buf = BytesIO()
    fig_bottom_10.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib_bottom = f'data:image/png;base64,{fig_data}'
    
    return fig, fig_bar_matplotlib, fig_bar_matplotlib_bottom


if __name__ == '__main__':
    app.run_server(debug=False, port=8002)
