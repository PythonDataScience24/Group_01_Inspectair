import base64
import pandas as pd
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

def create_ranking_plot(x, y, xlim=None, text=None, xlabel=None, color=None, title=None):
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
    #for i in range(len(x)):
    #   plt.text(x=(y[i]+0.1), y=i, s=round(text[i], 2), va='baseline')

    #save the plot to temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    fig_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    final_graph = f'data:image/png;base64,{fig_data}'
    return final_graph

