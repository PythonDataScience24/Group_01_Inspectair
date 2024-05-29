from dash import html, dcc, Input, Output, get_asset_url
import dash_bootstrap_components as dbc
from map import Map

class AirQualityLayout:
    """
    A class to define the layout and callbacks for the Air Quality Dashboard.

    Attributes:
    ----------
    app : Dash
        The Dash app instance.
    data : Data
        An object containing data and options for pollutants, continents, and station types.

    Methods:
    -------
    set_layout():
        Sets the layout of the Dash app.
    set_callbacks():
        Defines the callbacks for interactivity in the Dash app.
    """
    def __init__(self, app, data):
        """
        Constructs all the necessary attributes for the AirQualityLayout object.

        Parameters:
        ----------
        app : Dash
            The Dash app instance.
        data : Data
            An object containing data and options for pollutants, continents, and station types.
        """
        self.app = app
        self.data = data
        self.set_layout()
        self.set_callbacks()

    def set_layout(self):
        """
        Sets the layout of the Dash app including pollutant selection, region selection, time span slider,
        station type checklist, data type radio buttons, and the plots for the indicator graphic and bar graphs.
        Creates the Folium map and save it as an HTML file
        """
        # Create the Folium map and save it as an HTML file
        world_map = Map()
        initial_heatmap_data = self.data.df[['latitude', 'longitude', 'pm25_concentration']].dropna().values.tolist()
        world_map.add_heatmap(initial_heatmap_data)
        world_map.save('map.html')

        self.app.layout = html.Div([
            # Pollutant selection row
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
                    width=4,
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
                    width=4
                ),
                # Logo
                dbc.Col(
                    html.Div([
                        html.Img(src=get_asset_url('logonotext.png'), style={'height': '68px', 'width': 'auto', 'margin-top': '10px', 'margin-left': 'auto'})
                    ], style={
                    'display': 'flex',
                    'justify-content': 'flex-end',
                    'align-items': 'center',
                    'height': '100%'
                    }),
                    width={"size": 2, "order": "last", "offset": 3},
                    style={'margin-left': '145px'}
                ),
            ], style={'background-color': '#d3d3d3', 
                      'border': '1px solid #ddd', 
                      'border-radius': '5px',
                      'box-shadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                      'padding-bottom': '20px'}),
            # Time selection
            html.Div([
                html.Label('Time Span:', style={'font-weight': 'bold','margin-left': '20px'}),
                dcc.RangeSlider(
                    id='from-to',
                    min=2013,
                    max=2022,
                    step=1,
                    value=[2015, 2020],
                    allowCross=False,
                    marks={i: str(i) for i in range(2013, 2023, 1)}
                )
            ], style={'margin-top': '10px', 'margin-bottom': '10px', 'margin-left': '20px', 'margin-right': '20px'}),
            # Row for station choice and data type
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Label('Station Type(s):', style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='station-type-checklist',
                            options=[{'label': key, 'value': key} for key in self.data.station_type.keys()],
                            value=['all'],
                            multi=True
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
            # Row for the plots
            dbc.Row([
                dbc.Col(dcc.Graph(id='indicator-graphic'), width="auto"),
                dbc.Col([
                    html.Img(id='bar-graph-matplotlib', style={'max-width': '100%', 'height': 'auto'}),
                    html.Img(id='bar-graph-matplotlib_bottom', style={'max-width': '100%', 'height': 'auto'})
                ], width=5),
            ]),
            # Add the Folium map 
            dbc.Row([
                dbc.Col(
                    html.Iframe(
                        id='folium-map',
                        srcDoc=open('map.html', 'r').read(),
                        width='100%',
                        height='600'
                    ),
                    width={"size":10, "offset":1})
            ], style={'margin-top': '20px'}),
            # Disclaimer
            dbc.Row([
                dbc.Col(
                    html.Div(
                        "Disclaimer: The data provided is for informational purposes only and provided as an example. The data is neither updated nor is it complete. Additionally location information is skewed and heavily biased according to locations of measurement stations.",
                        style={
                            'font-size': '12px',
                            'background-color': '#FFFFED',
                            'border': '1px solid #ddd',
                            'border-radius': '5px',
                            'padding': '10px',
                            'margin-top': '20px',
                        }
                    )
                )
            ])
        ])

    def set_callbacks(self):
        """
        Sets up the Dash callbacks to handle user interactions and update the dashboard.
        """
        @self.app.callback(
            Output('station-type-checklist', 'options'),
            Input('station-type-checklist', 'value')
        )
        def update_checklist(selected_values):
            """
            Updates the checklist options based on the selected station types.

            Parameters:
            ----------
            selected_values : list
                List of selected station types.

            Returns:
            -------
            list
                Updated list of checklist options with appropriate enabling/disabling.
            """
            options = [{'label': key, 'value': key} for key in self.data.station_type.keys()] 
            if 'all' in selected_values:
                for option in options:
                    if option['value'] != 'all':
                        option['disabled'] = True
            else:
                for option in options:
                    option['disabled'] = False
            return options
