import plotly.graph_objects as go
from dash import Input, Output
import re
from ranking_plots import get_rank_10, create_ranking_plot
from map import Map

class AirQualityCallbacks:
    """
    A class to handle the callbacks for the Air Quality Dashboard.

    Attributes:
        app: The Dash application instance.
        data: The air quality data used in the dashboard (excel file input). 

    Methods:
        generate_folium_map(filtered_data, selected_pollutant):
            Generates a Folium map with heatmap data.
        set_callbacks():
            Sets up the Dash callbacks to handle user interactions and update the dashboard.
    """

    def __init__(self, app, data):
        """
        Initializes the AirQualityCallbacks with the given Dash app and data.

        Args:
            app: The Dash application instance.
            data: The air quality data.
        """
        self.app = app
        self.data = data
        self.set_callbacks()

    def generate_folium_map(self, filtered_data, selected_pollutant):
        # Generate a Folium map with heatmap data
        world_map = Map()
        heatmap_data = filtered_data[['latitude', 'longitude', selected_pollutant]].dropna().values.tolist()
        world_map.add_heatmap(heatmap_data)
        world_map.save('map.html')
        return open('map.html', 'r').read()

    def set_callbacks(self):
        @self.app.callback(
            Output('indicator-graphic', 'figure'),
            Output('bar-graph-matplotlib', 'src'),
            Output('bar-graph-matplotlib_bottom', 'src'),
            Output('folium-map', 'srcDoc'),
            Input('pollutant-dropdown', 'value'),
            Input('continent-dropdown', 'value'),
            Input('from-to', 'value'),
            Input('station-type-checklist', 'value'),
            Input('data-type-radio', 'value')
        )
        def update_graph(selected_pollutant, selected_continent, selected_year, selected_station_types, selected_data_type):
            """
            Updates the graphs and map based on the user input.

            Args:
                selected_pollutant: The pollutant selected from the dropdown.
                selected_continent: The continent selected from the dropdown.
                selected_year: The range of years selected.
                selected_station_types: The types of stations selected from the checklist.
                selected_data_type: The data type selected (concentration or AQI).

            Returns:
                A tuple containing the updated figure for the main plot, the top ranking bar graph,
                the bottom ranking bar graph, and the HTML for the Folium map.
            """
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
                return fig, None, None, open('map.html', 'r').read()

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
                    y=top_ranked_10[selected_pollutant].index,
                    x=top_ranked_10[selected_pollutant].values,
                    ranking_type='top',
                    title=(f'Top 10 most polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_top,
                    text=top_ranked_10[selected_pollutant].values)

                fig_bar_bottom_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    y=bottom_ranked_10[selected_pollutant].index,
                    x=bottom_ranked_10[selected_pollutant].values,
                    ranking_type='bottom',
                    title=(f'Top 10 least polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_bottom,
                    text=bottom_ranked_10[selected_pollutant].values)

                return fig, fig_bar_top_10, fig_bar_bottom_10, self.generate_folium_map(filtered_df, selected_pollutant)

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
                    y=top_ranked_10[selected_pollutant].index,
                    x=top_ranked_10[selected_pollutant].values,
                    ranking_type='top',
                    title=(f'Top 10 most polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_top,
                    text=top_ranked_10[selected_pollutant].values)

                fig_bar_bottom_10 = create_ranking_plot(
                    selected_data_type=selected_data_type,
                    y=bottom_ranked_10[selected_pollutant].index,
                    x=bottom_ranked_10[selected_pollutant].values,
                    ranking_type='bottom',
                    title=(f'Top 10 least polluted cities in {self.data.continent_dict[selected_continent]} ({selected_from_year}-{selected_to_year})\n'
                           '(average values across timeframe are shown; low value is better)'),
                    xlabel=f'{self.data.legend[selected_pollutant]}',
                    color=color_bottom,
                    text=bottom_ranked_10[selected_pollutant].values)

                return fig, fig_bar_top_10, fig_bar_bottom_10, self.generate_folium_map(filtered_df, selected_pollutant)

