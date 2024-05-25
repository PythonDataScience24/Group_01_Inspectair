import base64
import regex as re
import numpy as np
import pandas as pd
from math import floor
from datahandling import *
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('agg')

def get_rank_10(df, selected_pollutant, selected_data_type):
    """
    Function which gets the top 10 values (both highest and lowest) for a selected 
    pollutant per city, as well as the corresponging AQI colour palettes
    
    Input: 
    df: a dataframe prefiltered with the correct timespan, containing the relevant data for the ranking
    selected_pollutant: a string indicating which pollutant is selected (e.g. no2)
    selected_datatypes: a string indicating data type ['Concentration', 'AQI]

    Output: 
    list of top 10 values (=most polluted), list of bottom 10 values(=least polluted), 
    list color palette for top 10 values, list color palette for worst 10 values
    
    """
    # Get mean pollutant per city in prefiltered timeframe
    mean_pollution_city = pd.pivot_table(data=df, index=['city'], aggfunc='mean', values=selected_pollutant)
    # Extract top 10 (=most polluted) and bottom 10 (=least polluted) cites
    top_ranked_10 = mean_pollution_city.sort_values(by=selected_pollutant, ascending=False)[0:10]
    bottom_ranked_10 = mean_pollution_city.sort_values(by=selected_pollutant, ascending=False)[-9:]
    # Reverse sorting order for horizontal barplot
    top_ranked_10 = top_ranked_10.sort_values(by=selected_pollutant)
    bottom_ranked_10 = bottom_ranked_10.sort_values(by=selected_pollutant, ascending=True)

    # Define different colour palettes for selected data type AQI and concentration
    if str(selected_data_type)=='AQI':
                # Assign color palette to AQI values
                color_top = [assign_aqi_message(value)[1] for value in top_ranked_10[selected_pollutant].values]
                color_bottom = [assign_aqi_message(value)[1] for value in bottom_ranked_10[selected_pollutant].values]
    else:
         # Use red and green for concentration plots
         color_top = 10*['#cb4154']
         color_bottom = 10*['#a3e77f']
    return top_ranked_10, bottom_ranked_10, color_top, color_bottom

def create_ranking_plot(selected_data_type, x, y, ranking_type, text=None, xlabel=None, color=None, title=None):
    """
    Function which creates a ranking plot using matplotlib (horizontal barplot).
    The plot is saved to a temporary buffer and emebeded into html as an image. 
    
    Input: 
    selected_data_type: a string indicating data type ['Concentration', 'AQI]
    x: list of float or int to plot as x values in horizontal barplot
    y: list of float or int to plot as y values in horizontal barplot
    ranking_type: string indicating type of plot ['top', 'bottom']
    text: List of strings, will be displayed as text next to the bars
    xlabel: String containing labelling for x-axis
    color: list of 10 string color values for the bars
    title: string indicating plot title

    Output:
    Graph as img emdedded into html
    """
    
    # Format the city names - introduce line breaks for long names
    y_formatted = len(y)*[0]
    for i, city_name in enumerate(y):
        if " " in city_name and len(city_name) > 14:
            # Find all indices of spaces
            indices = [m.start() for m in re.finditer(' ', city_name)]
            # Use the space approx. in the middle to introduce linebreak
            which_index = floor(len(indices)/2)
            insert_linebreak = indices[which_index]
            # Introduce linebreak
            city_name = city_name[:insert_linebreak] + '\n' + city_name[insert_linebreak+1:]
            y_formatted[i] = city_name
        else:
            y_formatted[i] = city_name
    
    # Separate plots depening on the selected data type (AQI or concentration)
    if str(selected_data_type == 'Concentration'):
        fig, ax = plt.subplots(figsize = (12,6))
        # Create horizontal barplot
        plt.barh(y_formatted, np.log10(x), color=color, edgecolor='black')
        plt.xlabel(f'Log10 {xlabel}')
        plt.title(title)
        # Set equal xlims for both plots in log units
        if ranking_type == 'top':
            global xlim_log
            xlim_max = np.max(np.log10(x))+1.5
            xlim_log = [-xlim_max, xlim_max]
            # Add legend to the plot
            legend_labels = {'Log10 most polluted': '#cb4154', 'Log10 least polluted': '#a3e77f', 'NON-transformed numbers': 'black'}
            legend_handles = [plt.Line2D([0], [0], color=color, linewidth=3, linestyle='-') for label, color in legend_labels.items()]
            plt.legend(legend_handles, legend_labels.keys(), title='Legend', loc='upper left')
        plt.xlim(xlim_log)
        plt.gca().spines['top'].set_visible(False) 
        plt.gca().spines['right'].set_visible(False) 

        # Add non-transformed values to the plot as text
        for i in range(len(y)):
            # Correct offset for negative log values
            offset_correction_factor = xlim_log[1]/6.39
            text_offset = (len(str(round(text[i], 3)))+0.6)* 0.1* offset_correction_factor
            if x[i] < 1: 
                # Display text left of bar for negative log values
                plt.text(x=(np.log10(x[i])-text_offset), y=i, s=round(text[i], 3), va = 'center', color = 'black')
            else:
                # Display text right of bar for positive log values
                plt.text(x=(np.log10(x[i])+0.05), y=i, s=round(text[i], 3), va = 'center', color = 'black')

    
    if str(selected_data_type)=='AQI':
        fig, ax = plt.subplots(figsize = (12,6))
        # Create horizontal barplot
        plt.barh(y_formatted, x, color=color, edgecolor='black')
        plt.xlabel(xlabel)
        plt.title(title)   
        plt.xlim([0,500])
        # Add explanation for the AQI values as label
        legend_labels = {'good': 'green', 'moderate': 'yellow', 'unhealthy to sens. groups': 'orange',
                         'unhealthy': 'orange', 'very unhealthy': 'purple', 'hazardous': 'maroon'}
        legend_handles = [plt.Line2D([0], [0], color=color, linewidth=3, linestyle='-') for label, color in legend_labels.items()]
        plt.legend(legend_handles, legend_labels.keys(), title='AQI color scheme')
        plt.gca().spines['top'].set_visible(False) 
        plt.gca().spines['right'].set_visible(False) 

        # Add the values to the plots as text
        for i in range(len(y)):
           plt.text(x=(x[i]+1), y=i, s=round(text[i], 2), va = 'baseline')

    # Save the plot to temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    final_graph = f'data:image/png;base64,{fig_data}'
    return final_graph

