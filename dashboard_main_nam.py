import base64
from io import BytesIO
from dash import Dash, html, dcc, Input, Output, callback 
from math import ceil
import pandas as pd   
import numpy as np
import plotly.graph_objects as go
import matplotlib
import matplotlib.pyplot as plt
import dash_bootstrap_components as dbc  
matplotlib.use('agg')
import os
import matplotlib.ticker as ticker

#os.getcwd()
#directory = "C:\\airquality"
#os.chdir(directory)

# https://dash.plotly.com/basic-callbacks
app = Dash(__name__)

# use your path to the excel file with data
df = pd.read_excel(".//who_ambient_air_quality_database_version_2024_(v6.1).xlsx", sheet_name="Update 2024 (V6.1)")
pollutants=['pm10_concentration', 'pm25_concentration', 'no2_concentration']
pollutants_options = [{'label': name, 'value': name} for name in pollutants]

pollutants=['pm10_concentration', 'pm25_concentration', 'no2_concentration']
pollutants_options = [{'label': name, 'value': name} for name in pollutants]

# app layout
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

    # values from dropdown list
@callback(
    Output('indicator-graphic', 'figure'),
    Output('bar-graph-matplotlib', 'src'),
    Output('bar-graph-matplotlib_bottom', 'src'),
    Input('indicator-dropdown', 'value')
    )

def update_graph(pollutant):

    # define dictionaries
    regions_dict = {
        '1_Afr': 'African',
        '2_Amr': 'Americas',
        '3_Sear': 'South-East Asia',
        '4_Eur': 'Europe',
        '5_Emr': 'Eastern Mediterranean',
        '6_Wpr': 'Western Pacific',
        '7_NonMS': 'non-member state'
    }

    legends = {
        'pm10_concentration': 'pm 10 concentration',
        'pm25_concentration': 'pm 2.5 concentration',
        'no2_concentration': 'NO2 concentration'
    }

    colors=['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue']
    columns=['year']
    indices=['who_region']

    dff=df.dropna(subset=['iso3', 'year'])
    dff=dff.drop_duplicates()
    dff=dff.drop_duplicates(subset=['iso3', 'city', 'year', 'pm10_concentration', 'pm25_concentration', 'no2_concentration'])

    df_pollutant_mean_year = pd.pivot_table(data=dff, index=indices, columns=columns, aggfunc='mean', values=pollutants)

    
    #extract top 10 polluted cities (for now only most recent year)
    dff_2022 = dff[dff.year == 2022]
    dff_2022[f'log_{pollutant}'] = np.log(dff_2022[pollutant])
    log_pollutants = ['pm10_concentration', 'pm25_concentration', 'no2_concentration',
                      f'log_{pollutant}']
    mean_city_2022 = pd.pivot_table(data=dff_2022, index=['city'], aggfunc='mean', values=log_pollutants)
    top_ranked_10 = mean_city_2022.sort_values(by=pollutant, ascending=False)[0:10]
    #reverse order for horizontal barplot
    top_ranked_10 = top_ranked_10.sort_values(by=pollutant)
    
    
    #extract 10 least polluted cities (for now only most recent year)
    bottom_ranked_10 = mean_city_2022.sort_values(by=pollutant, ascending=True)[0:10]
    #reverse order for horizontal barplot
    bottom_ranked_10 = bottom_ranked_10.sort_values(by=pollutant, ascending=False)

    fig = go.Figure()
    table_for_plot = df_pollutant_mean_year[pollutant].T
    for region in df["who_region"].unique():
        fig.add_trace(go.Scatter(
            x=table_for_plot.index,
            y=table_for_plot[region],
            mode='lines',
            name=regions_dict[region],
            line=dict(color=colors[df["who_region"].unique().tolist().index(region)])
        ))#
    fig.update_layout(
        title = pollutant + ' Concentration Across Different Continents',
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
    xlim = ceil(np.max(top_ranked_10[f'log_{pollutant}'].values))
    plt.barh(top_ranked_10[f'log_{pollutant}'].index, top_ranked_10[f'log_{pollutant}'].values, color=color_palette_top_10)
    plt.xlabel(f'Log {legends[pollutant]}')
    plt.title('Top 10 most polluted cities in 2022 (average values are shown; low value is better)')
    plt.xlim([0,xlim])
    plt.gca().spines['top'].set_visible(False) 
    plt.gca().spines['right'].set_visible(False) 
    #add the non transformed values to the as text
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
    plt.barh(bottom_ranked_10[f'log_{pollutant}'].index, bottom_ranked_10[f'log_{pollutant}'].values, 
             color=color_palette_bottom_10)
    plt.xlabel(f'Log {legends[pollutant]}')
    plt.title('Top 10 least polluted cities in 2022 (average values are shown; low value is better)')
    plt.xlim([0,xlim])
    plt.gca().spines['top'].set_visible(False) 
    plt.gca().spines['right'].set_visible(False) 

    #add the non transformed values to the plot as text
    s = bottom_ranked_10[pollutant].values
    x = bottom_ranked_10[f'log_{pollutant}'].values
    for i in range(len(x)):
        plt.text(x=(x[i]+0.1), y=i, s=round(s[i], 2), va='baseline')
    plt.legend(loc="upper right")

    # Save figure to a temporary buffer.
    buf = BytesIO()
    fig_bottom_10.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    fig_bar_matplotlib_bottom = f'data:image/png;base64,{fig_data}'
    
    return fig, fig_bar_matplotlib, fig_bar_matplotlib_bottom

if __name__ == '__main__':
    app.run_server(debug=False, port=8002)
    
