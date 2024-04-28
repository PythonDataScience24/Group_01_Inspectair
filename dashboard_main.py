from dash import Dash, html, dcc, Input, Output, callback 
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
matplotlib.use('agg')
import os

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

    dcc.Graph(id='indicator-graphic')
])

    # values from dropdown list
@callback(
    Output('indicator-graphic', 'figure'),
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
        title = pollutant + ' Concentration Across Different Continents',
        xaxis_title = 'Year',
        yaxis_title = legends[pollutant],
        legend_title = 'Region',
        template = 'plotly_white'
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=False, port=8002)
