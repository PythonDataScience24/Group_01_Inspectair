# Import packages
import base64
from io import BytesIO
from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc  
matplotlib.use('agg')
import os
import numpy as np
import folium
import folium.plugins
import openpyxl as op
import math

os.getcwd()
#directory = "C:\inspectair\Group_01_Inspectair"
#os.chdir(directory)


# define bootsrap stylesheet
external_stylesheets = [dbc.themes.BOOTSTRAP]

# https://dash.plotly.com/basic-callbacks
app = Dash(__name__,external_stylesheets=external_stylesheets)

# Import data
df = pd.read_excel("who_ambient_air_quality_database_version_2024_(v6.1).xlsx", sheet_name="Update 2024 (V6.1)")

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

def assign_aqi_message(aqi):
    #  function to assign message and color based on AQI
    if aqi >= 250:
        return "hazardous", "maroon"
    elif aqi >= 150:
        return "very unhealthy", "purple"
    elif aqi >= 55:
        return "unhealthy", "red"
    elif aqi >= 35:
        return "unhealthy to sensitive groups", "orange"
    elif aqi >= 12:
        return "moderate", "yellow"
    else:
        return "good", "green"


# Applying function to pollutants data and add aqi converted data to the columns
df["pm25_aqi"] = pd.DataFrame(calculate_aqi("pm25", (df["pm25_concentration"]).to_numpy()))
df["pm10_aqi"] = pd.DataFrame(calculate_aqi("pm10", (df["pm10_concentration"]).to_numpy()))
df["no2_aqi"] = pd.DataFrame(calculate_aqi("no2", (df["no2_concentration"]).to_numpy()))

# Define data column to fetch on dropdown interactive filter
pollutants=["pm25_aqi", "pm10_aqi", "no2_aqi"]
pollutants_options = [{'label': name, 'value': name} for name in pollutants]


def create_ranking_plot(x, y, xlabel, color, title: str, xlim: list, text: list):
    #function creates matplotlib ranking plot (horizontal barplot), 
    #saves it to temporary buffer and embeds the result into html

    #create figure
    fig = plt.figure(figsize=(10, 5), constrained_layout=True)
    plt.barh(x, y, color=color)
    plt.xlabel(xlabel)
    plt.title(title)    
    plt.xlim(xlim)
    plt.gca().spines['top'].set_visible(False) 
    plt.gca().spines['right'].set_visible(False) 

    #add the non transformed values to the plot as text
    for i in range(len(x)):
       plt.text(x=(y[i]+0.1), y=i, s=round(text[i], 2), va='baseline')

    #save the plot to temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    final_graph = f'data:image/png;base64,{fig_data}'
    return final_graph


def update_map(selection):
    if selection == "pm25":
        data = data_pm25
    elif selection == "pm10":
        data = data_pm10
    elif selection == "no2":
        data = data_no2
    
    # Generate Folium heatmap based on data
    heatmap = folium.plugins.HeatMap(data, min_opacity=0.3, blur=30, gradient=gradient)
    m = folium.Map(location=[0, 0], zoom_start=2)
    heatmap.add_to(m)
    
    # Return the map HTML representation to update the iframe
    return m._repr_html_()

# Select a pollutant type
selection = "pm25"

# Check if the selection is valid
while selection not in ["pm25", "pm10", "no2"]:
    selection = input("Invalid selection. Please choose a pollutant type (pm25, pm10, no2): ").lower().strip()

# Initialize a Folium map centered around a specific location (e.g., world map)
m = folium.Map(location=[0, 0], zoom_start=2)  # Centered at (latitude, longitude), zoom level 2

# Create gradient dictionary based on AQI thresholds
gradient = {
    # the numbers for the gradient have to be between 0 and 1
    1.0: "maroon",        # Corresponds to normalized AQI value >= 250/500.4
    0.75: "purple",       # Corresponds to normalized AQI value >= 150/500.4
    0.5: "red",           # Corresponds to normalized AQI value >= 55/500.4
    0.35: "orange",       # Corresponds to normalized AQI value >= 35/500.4
    0.24: "yellow",       # Corresponds to normalized AQI value >= 12/500.4
    0.0: "green"          # Corresponds to normalized AQI value >= 0
}

# Create a heatmap based on the selected pollutant type
if selection == "pm25":
    # Filter data for PM2.5
    data_pm25 = df[["latitude", "longitude", "pm25_aqi"]].dropna()
    folium.plugins.HeatMap(data_pm25, min_opacity=0.1, blur=15, gradient=gradient).add_to(m)
    # Print the map
    m
elif selection == "pm10":
    # Filter data for PM10
    data_pm10 = df[["latitude", "longitude", "pm10_aqi"]].dropna()
    folium.plugins.HeatMap(data_pm10, min_opacity=0.1, blur=15, gradient=gradient).add_to(m)
     # Print the map
    m
elif selection == "no2":
    # Filter data for NO2
    data_no2 = df[["latitude", "longitude", "no2_aqi"]].dropna()
    folium.plugins.HeatMap(data_no2, min_opacity=0.1, blur=15, gradient=gradient).add_to(m)
     # Print the map
    m 


# control layers 
folium.TileLayer("OpenStreetMap").add_to(m)
folium.TileLayer(show=False).add_to(m)

folium.LayerControl().add_to(m)

# add legend to map



# App layout
app.layout = html.Div([
    
    #Filter Tags
    dbc.Row([
        dbc.Col(html.Div("Pollutant:"),width=6),
        dbc.Col(html.Div("From:"),width=6)
    ], style={'background-color': 'lightgray', 'padding': '2px', 'border-radius': '5px'}),
    #Dropdown filters
    dbc.Row([
        dbc.Col(
            html.Div([
                dcc.Dropdown(
                    id='indicator-dropdown',
                    options=pollutants_options,
                    value=pollutants[0]
                )
                
            ])
        ,width=6),
        dbc.Col(
            html.Div([
                dcc.Dropdown(
                    id='indicator-dropdown2',
                    options=pollutants_options,
                    value=pollutants[0]
                )
                
            ])
        ,width=6)
    ], style={'border': '1px solid black', 'padding': '10px', 'border-radius': '5px'}),

    #Row with the plots
    dbc.Row([
        #left column with graphs
        dbc.Col(dcc.Graph(id='indicator-graphic'),width=8),
        #right column with bar plots
        dbc.Col([
            html.Img(id='bar-graph-matplotlib',style={'max-width': '100%', 'height': 'auto'}),
            html.Img(id='bar-graph-matplotlib_bottom',style={'max-width': '100%', 'height': 'auto'})],width=4)
    ]),

    # Placeholder for displaying the Folium map
    html.Div([
        html.Iframe(id='map', srcDoc=m._repr_html_(), width='100%', height='500')
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

    ############### build the top 10 ranking plot ##################
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

    #get top 10 aqi values for current pollutant
    top_10_aqi= top_ranked_10[pollutant].values
    
    top_10_aqi_colors = []
    top_10_aqi_category = []
    #get the corresponding color palette and category to the aqi values
    for number in top_10_aqi:
        category, color = assign_aqi_message(number)
        top_10_aqi_colors.append(color)
        top_10_aqi_category.append(category)
    
    #define the parameters for the ranking plot plot
    x = top_ranked_10[f'log_{pollutant}'].index
    y = top_ranked_10[f'log_{pollutant}'].values
    title = ('Top 10 most polluted cities in 2022 (average values are shown; low value is better)\n'
             'NON-transformed numbers are shown in plot')
    xlim = [0, np.ceil(np.max(top_ranked_10[f'log_{pollutant}'].values))]
    #display non transformed numbers on plot as text
    text = top_ranked_10[pollutant].values
    xlabel = f'Log {legends[pollutant]}'
    #create a custom horizontal barplot
    fig_bar_matplotlib = create_ranking_plot(x=x, y=y, color= top_10_aqi_colors, title=title, xlim=xlim, 
                                             xlabel=xlabel, text=text)
   

    #build bottom 10 ranking plot
    #extract 10 least polluted cities (for now only most recent year)
    bottom_ranked_10 = mean_city_2022.sort_values(by=pollutant, ascending=True)[0:10]
    #reverse order for horizontal barplot
    bottom_ranked_10 = bottom_ranked_10.sort_values(by=pollutant, ascending=False)

    #get bottom 10 aqi values for current pollutant
    bottom_10_aqi= bottom_ranked_10[pollutant].values
    bottom_10_aqi_colors = []
    bottom_10_aqi_category = []

    #get the corresponding color palette and category to the aqi values
    for number in bottom_10_aqi:
        category, color = assign_aqi_message(number)
        bottom_10_aqi_colors.append(color)
        bottom_10_aqi_category.append(category)   

    #define parameters for ranking plot
    x = bottom_ranked_10[f'log_{pollutant}'].index
    y = bottom_ranked_10[f'log_{pollutant}'].values
    title = ('Top 10 least polluted cities in 2022 (average values are shown; low value is better)\n'
             'NON-transformed numbers are shown in plot')
    text = bottom_ranked_10[pollutant].values
    xlabel = f'Log {legends[pollutant]}'
    #create a custom horizontal barplot
    fig_bar_matplotlib_bottom = create_ranking_plot(x=x, y=y, color= bottom_10_aqi_colors, title=title, xlim=xlim, 
                                             xlabel=xlabel, text=text)
   
    return fig, fig_bar_matplotlib, fig_bar_matplotlib_bottom


if __name__ == '__main__':
    app.run_server(debug=True, port=8002)