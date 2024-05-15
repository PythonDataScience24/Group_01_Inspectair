from dash import Dash, html, dcc, Input, Output, callback 
import sys
import dash_bootstrap_components as dbc  
import pandas as pd   
import plotly.graph_objects as go
import matplotlib
matplotlib.use('agg')
import os
import numpy as np
import re

os.getcwd()
directory = "C:\inspectair\Group_01_Inspectair"
os.chdir(directory)

from ranking_plots import *
from datahandling import *


class AirQualityData:
    def __init__(self, data_path, sheet_name="Update 2024 (V6.1)"):
        self.df = pd.read_excel(data_path, sheet_name=sheet_name)
        self.df["pm25_aqi"] = pd.DataFrame(calculate_aqi("pm25", (self.df["pm25_concentration"]).to_numpy()))
        self.df["pm10_aqi"] = pd.DataFrame(calculate_aqi("pm10", (self.df["pm10_concentration"]).to_numpy()))
        self.df["no2_aqi"] = pd.DataFrame(calculate_aqi("no2", (self.df["no2_concentration"]).to_numpy()))

        self.legend = {
            'pm10_concentration': 'PM10 Concentration',
            'pm25_concentration': 'PM2.5 Concentration',
            'no2_concentration': 'NO2 Concentration',
            'pm10_aqi': 'PM10 AQI',
            'pm25_aqi': 'PM2.5 AQI',
            'no2_aqi': 'NO2 AQI'
        }

        self.continent_dict = {
            '': 'World',
            '1_Afr': 'Africa',
            '2_Amr': 'Americas',
            '3_Sear': 'South-East Asia',
            '4_Eur': 'Europe',
            '5_Emr': 'Eastern Mediterranean',
            '6_Wpr': 'Western Pacific',
            '7_NonMS': 'Non-member state'
        }
        self.reverse_continent_dict = {value: key for key, value in self.continent_dict.items()}

        self.pollutant_type = {
            'pm10_concentration': 'PM10 Concentration',
            'pm25_concentration': 'PM2.5 Concentration',
            'no2_concentration': 'NO2 Concentration'
        }
        self.reverse_pollutant_type = {value: key for key, value in self.pollutant_type.items()}

        self.station_type = {
            'all': ['all'],
            'Rural': ['Rural'],
            'Urban': ['Fond Urbain', 'Urban Traffic', 'Urban', 'Urban Traffic/Residential And Commercial Area'],
            'Residential': ['Residential - industrial','Residential And Commercial Area', 'Urban Traffic/Residential And Commercial Area'],
            'Suburban': ['Suburban'],
            'Industrial': ['Residential - industrial', 'Industrial'],
            'Background': ['Background'],
            'Traffic': ['Traffic', 'Urban Traffic/Residential And Commercial Area']
        }

        self.reverse_station_type = {}
        for key, values in self.station_type.items():
            for value in values:
                self.reverse_station_type[value] = key

        self.continents_options = [{'label': name, 'value': key} for key, name in self.continent_dict.items()]
        self.pollutants_options = [{'label': name, 'value': key} for key, name in self.pollutant_type.items()]
        self.stations_options = [{'label': name, 'value': key} for key, name in self.station_type.items()]

        all_years = np.array(((self.df["year"].dropna().unique()).astype(int)), dtype=str)
        all_years = np.append(all_years, 'all')
        self.years_options = [{'label': name, 'value': name} for name in all_years]


class AirQualityLayout:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.set_layout()

    def set_layout(self):
        self.app.layout = html.Div([
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Label('Pollutant:', style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='pollutant-dropdown',
                            options=self.data.pollutants_options,
                            value='pm25_concentration'
                        )
                    ], style={'margin-top': '10px'}),
                    width=5,
                    style={'margin-left': '40px'}
                ),
                dbc.Col(
                    html.Div([
                        html.Label('Region:', style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='continent-dropdown',
                            options=self.data.continents_options,
                            value=list(self.data.continent_dict.keys())[0]
                        )
                    ], style={'margin-top': '10px'}),
                    width=5
                ),
            ], style={'background-color': '#d3d3d3', 
                      'border': '1px solid #ddd', 
                      'border-radius': '5px',
                      'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                      'padding-bottom': '20px'}),

            html.Div([
                html.Label('Time Span:', style={'font-weight': 'bold','margin-left': '20px'}),
                dcc.RangeSlider(
                    id='from-to',
                    min=2013,
                    max=2022,
                    value=[2015, 2020],
                    marks={i: str(i) for i in range(2013, 2023, 1)}
                )
            ], style={'margin-top': '10px', 'margin-bottom': '10px', 'margin-left': '20px', 'margin-right': '20px'}),

            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Label('Station type(s):', style={'font-weight': 'bold'}),
                        dcc.Checklist(
                            id='station-type-checklist',
                            options=[{'label': key, 'value': key} for key in self.data.station_type.keys()],
                            value=['all'],
                            inline=True
                        )
                    ], style={'margin-top': '10px', 'margin-bottom': '10px'}),
                    width=6, style={'margin-left': '40px'}
                ),
                dbc.Col(
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
                    width=4
                ),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id='indicator-graphic'), width=8),
                dbc.Col([
                    html.Img(id='bar-graph-matplotlib', style={'max-width': '100%', 'height': 'auto'}),
                    html.Img(id='bar-graph-matplotlib_bottom', style={'max-width': '100%', 'height': 'auto'})
                ], width=4),
            ]),
        ])


class AirQualityCallbacks:
    def __init__(self, app, data):
        self.app = app
        self.data = data
        self.set_callbacks()

    def set_callbacks(self):
        @self.app.callback(
            Output('indicator-graphic', 'figure'),
            Output('bar-graph-matplotlib', 'src'),
            Output('bar-graph-matplotlib_bottom', 'src'),
            Input('pollutant-dropdown', 'value'),
            Input('continent-dropdown', 'value'),
            Input('from-to', 'value'),
            Input('station-type-checklist', 'value'),
            Input('data-type-radio', 'value')
        )
        def update_graph(selected_pollutant, selected_continent, selected_year, selected_station_types, selected_data_type):
            selected_from_year = selected_year[0]
            selected_to_year = selected_year[1]
            colors = ['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue']
            filtered_df = self.data.df.copy()

            if not selected_station_types:
                fig = go.Figure()
                fig.update_layout(
                    title="No station type selected",
                    xaxis={"visible": False},
                    yaxis={"visible": False},
                    annotations=[{
                        "text": "No station type selected - please select a station type to view data.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 16}
                    }],
                    template='plotly_white'
                )
                return fig, None, None

            if selected_station_types.count('all') == 0:
                filtered_df = filtered_df.dropna(subset=['type_of_stations'])
                pattern = '|'.join(r'\b{}\b'.format(re.escape(word)) for word in selected_station_types)
                filtered_df = filtered_df[filtered_df['type_of_stations'].str.contains(pattern, na=False)]

            if str(selected_data_type) == 'AQI':
                selected_pollutant = selected_pollutant.replace("concentration", "aqi")

            if selected_from_year != 'all':
                filtered_df = filtered_df[filtered_df['year'] >= int(selected_from_year)]
            if selected_to_year != 'all':
                filtered_df = filtered_df[filtered_df['year'] <= int(selected_to_year)]

            fig = go.Figure()

            if selected_continent == '':
                regions = filtered_df['who_region'].unique()
                for region in regions:
                    regional_data = filtered_df[filtered_df['who_region'] == region]
                    df_pollutant_mean_year = regional_data.pivot_table(index='year', values=selected_pollutant, aggfunc='mean')
                    fig.add_trace(go.Scatter(
                        x=df_pollutant_mean_year.index,
                        y=df_pollutant_mean_year[selected_pollutant],
                        mode='lines',
                        name=self.data.continent_dict[region],
                        line=dict(color=colors[regions.tolist().index(region) % len(colors)])
                    ))
                fig.update_layout(
                    title=self.data.legend[selected_pollutant] + ' Across Different Continents',
                    xaxis_title='Year',
                    yaxis_title=self.data.legend[selected_pollutant],
                    legend_title='Region',
                    template='plotly_white'
                )

                top_ranked_10, bottom_ranked_10, color_top, color_bottom = get_rank_10(df=filtered_df,
                                                                                       selected_pollutant=selected_pollutant,
                                                                                       selected_data_type=selected_data_type)
                fig_bar_top_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    x=top_ranked_10[selected_pollutant].index,
                    y=top_ranked_10[selected_pollutant].values,
                    title=(f'Top 10 most polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_top,
                    text=top_ranked_10[selected_pollutant].values)

                fig_bar_bottom_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    x=bottom_ranked_10[selected_pollutant].index,
                    y=bottom_ranked_10[selected_pollutant].values,
                    title=(f'Top 10 least polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_bottom,
                    text=bottom_ranked_10[selected_pollutant].values)

                return fig, fig_bar_top_10, fig_bar_bottom_10

            else:
                filtered_df = filtered_df[filtered_df['who_region'] == selected_continent]
                filtered_df = filtered_df.dropna(subset=[selected_pollutant])
                
                countries = filtered_df['country_name'].unique()
                colors = ['brown', 'red', 'purple', 'pink', 'green', 'black', 'blue', 'orange', 'grey']
                for country in countries:
                    country_data = filtered_df[filtered_df['country_name'] == country]
                    if not country_data.empty:
                        df_pollutant_mean_year = country_data.pivot_table(index='year', values=selected_pollutant, aggfunc='mean')
                        fig.add_trace(go.Scatter(
                            x=df_pollutant_mean_year.index,
                            y=df_pollutant_mean_year[selected_pollutant],
                            mode='lines',
                            name=country,
                            line=dict(color=colors[countries.tolist().index(country) % len(colors)])
                        ))

                fig.update_layout(
                    title=self.data.legend[selected_pollutant] + ' Concentration Across Different Countries in ' + self.data.continent_dict[selected_continent],
                    xaxis_title='Year',
                    yaxis_title=self.data.legend[selected_pollutant],
                    legend_title='Country',
                    template='plotly_white'
                )

                top_ranked_10, bottom_ranked_10, color_top, color_bottom = get_rank_10(df=filtered_df,
                                                                                       selected_pollutant=selected_pollutant,
                                                                                       selected_data_type=selected_data_type)
                fig_bar_top_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    x=top_ranked_10[selected_pollutant].index,
                    y=top_ranked_10[selected_pollutant].values,
                    title=(f'Top 10 most polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_top,
                    text=top_ranked_10[selected_pollutant].values)

                fig_bar_bottom_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    x=bottom_ranked_10[selected_pollutant].index,
                    y=bottom_ranked_10[selected_pollutant].values,
                    title=(f'Top 10 least polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_bottom,
                    text=bottom_ranked_10[selected_pollutant].values)

                return fig, fig_bar_top_10, fig_bar_bottom_10


class AirQualityDashboard:
    def __init__(self, data_path, sheet_name="Update 2024 (V6.1)"):
        self.data = AirQualityData(data_path, sheet_name)
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout = AirQualityLayout(self.app, self.data)
        self.callbacks = AirQualityCallbacks(self.app, self.data)

    def run_server(self):
        self.app.run_server(debug=False, port=8002)


if __name__ == '__main__':
    data_path = os.path.join("who_ambient_air_quality_database_version_2024_(v6.1).xlsx")
    dashboard = AirQualityDashboard(data_path)
    dashboard.run_server()
