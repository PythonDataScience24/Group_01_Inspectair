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
    #function returns the top 10 and bottom 10 mean values for a selected pollutant
    #by city, as well as their corresponding AQI colour palettes

    mean_pollution_city = pd.pivot_table(data=df, index=['city'], aggfunc='mean', values=selected_pollutant)
    top_ranked_10 = mean_pollution_city.sort_values(by=selected_pollutant, ascending=False)[0:10]
    bottom_ranked_10 = mean_pollution_city.sort_values(by=selected_pollutant, ascending=False)[-9:]
    #reverse order for horizontal barplot
    top_ranked_10 = top_ranked_10.sort_values(by=selected_pollutant)
    bottom_ranked_10 = bottom_ranked_10.sort_values(by=selected_pollutant, ascending=False)

    #define different colour palettes for AQI and concentration
    if str(selected_data_type)=='AQI':
                color_top = [assign_aqi_message(value)[1] for value in top_ranked_10[selected_pollutant].values]
                color_bottom = [assign_aqi_message(value)[1] for value in bottom_ranked_10[selected_pollutant].values]
    else:
         color_top = '#3a77a5'
         color_bottom = '#3a77a5'
    return top_ranked_10, bottom_ranked_10, color_top, color_bottom

def create_ranking_plot(selected_data_type, x, y, ranking_type, xlim=None, text=None, xlabel=None, color=None, title=None):
    #function creates matplotlib ranking plot (horizontal barplot), 
    #saves it to temporary buffer and embeds the result into html
    
    #### format the city names - introduce line breaks for long names
    y_formatted = len(y)*[0]
    for i, city_name in enumerate(y):
        if " " in city_name and len(city_name) > 14:
            indices = [m.start() for m in re.finditer(' ', city_name)]
            which_index = floor(len(indices)/2)
            insert_linebreak = indices[which_index]
            city_name = city_name[:insert_linebreak] + '\n' + city_name[insert_linebreak+1:]
            y_formatted[i] = city_name
        else:
            y_formatted[i] = city_name
    

    #### separate the plots depening on the selected data type (AQI or concentration)
    if str(selected_data_type == 'Concentration'):
        fig, ax = plt.subplots(figsize = (12,6))
        plt.barh(y_formatted, np.log(x), color=color)
        plt.xlabel(f'log {xlabel}')
        plt.title(title)

        
        #set equal xlims for both plots in log units
        if ranking_type == 'top':
            global xlim_log
            xlim_log = [0, np.max(np.log(x))+1]
        legend_labels = {'Log transformed': 'blue', 'NON-transformed': 'red'}
        legend_handles = [plt.Line2D([0], [0], color=color, linewidth=3, linestyle='-') for label, color in legend_labels.items()]
        plt.legend(legend_handles, legend_labels.keys(), title='Legend')
        plt.xlim(xlim_log)
        plt.gca().spines['top'].set_visible(False) 
        plt.gca().spines['right'].set_visible(False) 
    
        for i in range(len(y)):
            plt.text(x=(np.log(x[i])+0.1), y=i, s=round(text[i], 2), va = 'baseline', color = 'red')

    if str(selected_data_type)=='AQI':
        fig, ax = plt.subplots(figsize = (12,6))
        plt.barh(y_formatted, x, color=color)
        plt.xlabel(xlabel)
        plt.title(title)   
        plt.xlim([0,500])
        #add explanation for the AQI values
        legend_labels = {'good': 'green', 'moderate': 'yellow', 'unhealthy to sens. groups': 'orange',
                         'unhealthy': 'orange', 'very unhealthy': 'purple', 'hazardous': 'maroon'}
        legend_handles = [plt.Line2D([0], [0], color=color, linewidth=3, linestyle='-') for label, color in legend_labels.items()]
        plt.legend(legend_handles, legend_labels.keys(), title='AQI color scheme')
        plt.gca().spines['top'].set_visible(False) 
        plt.gca().spines['right'].set_visible(False) 

    
        #add the non transformed values to the plots as text for easier interpretation
        for i in range(len(y)):
           plt.text(x=(x[i]+1), y=i, s=round(text[i], 2), va = 'baseline')

    #save the plot to temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    final_graph = f'data:image/png;base64,{fig_data}'
    return final_graph

