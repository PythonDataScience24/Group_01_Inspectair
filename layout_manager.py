from dash import html, dcc
import dash_bootstrap_components as dbc

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