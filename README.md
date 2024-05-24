## Air quality Inspectair Dashboard <img src = "https://github.com/nam32/airquality/assets/146727878/5eb1f532-bfe0-47cb-a70c-73d6dd505e1b" width="31" height="27"> :
The Inspectair Dashboard is a Python-based application designed to visualize air quality data, including particulate matter (PM2.5, PM10) and nitrogen dioxide (NO2) levels. The dashboard displays data for cities, countries, and continents over days, months, and years, providing an accessible and easy-to-understand graphical representation.

<img src = "https://github.com/nam32/airquality/assets/146727878/70016f01-2fa7-4442-bb6e-cdefbc3bbec4" width="220" height="220">

Core features and functionality:
- Provide statistical and graphical representation of the data
- Visualization of polutants on world map per country

Extra features:
- Interactive app form

Presequisites:
- pip (Python package installer)
- Python

# How to get started
- Go to the <img src = "https://github.com/PythonDataScience24/Group_01_Inspectair/assets/146727878/1cb8851c-42a5-45b8-8f7d-28039a4d1a43" width="45" height="15">
 button on the top right on github and download the zipped folder, unzip it and navigate to the folder on terminal.
- Navigate to the terminal and enter the command: pip install -r install_requirements.txt
- Execute ***main.py*** located in the **scripts** folder in terminal using the command: python main.py - this will result in a url - open your web browser and go to http://127.0.0.1:8002 to see the Dashboard.

# User guide
### Parameter selection
- To get started, choose a **pollutant** and a **region**.
- Choose a **time span** ranging from 2013 to 2022, the **type of weather station** you are interested in and the **type of data** you want to see (pollutant concentration or air quality index).
### Output
- On the **left** an interactive plot showing the pollutant concentration across the years can be seen, the interactive legend can be seen on the right of the plot, clicking the name of the region makes it disappear and viceversa, doubling clicking it hides the rest.
- On the **right** two rankings can be seen, the top ranking shows the most polluted areas and the bottom ranking shows the least polluted areas from the chosen weather stations.
- At the **bottom** of the page an interactive map can be seen, the heatmap layer which can be removed with the button on the top right corner of the map indicates the level of pollution in the air on the regions selected.
### Interpretability and disclaimers
- There can be a bias created by the heterogeneity of the amount of weather stations present in different countries, this means that some regions will not display any pollution due to a lack of weather stations and therefore a lack of data availability to actually get a measurement of the air quality. 

# Built With:
Programming languages:

[![Python 3.9.13](https://img.shields.io/badge/Python-3.9.13-blue)](https://www.python.org/downloads/release/python-3913/)  <img src = "https://github.com/PythonDataScience24/Group_01_Inspectair/assets/146727878/b7d12eed-aff4-41c0-981c-25d4d78bbef8" width="42" height="24">

Libraries used for generating visualizations:

[![Matplotlib 3.9.0](https://img.shields.io/badge/Matplotlib-3.9.0-orange)](https://matplotlib.org/stable/users/prev_whats_new/whats_new_3.7.1.html)  <img src = "https://github.com/PythonDataScience24/Group_01_Inspectair/assets/146727878/c83effe2-6e1e-4a1f-9bf3-a199752b5fcb" width="27" height="25">

[![Plotly 5.22](https://img.shields.io/badge/Plotly-5.22-red)](https://github.com/plotly/plotly.py/releases/tag/v5.22.0) <img src = "https://github.com/PythonDataScience24/Group_01_Inspectair/assets/146727878/e4d20f34-78bc-4180-a306-6d7c3a2b0cfc" width="38" height="25"> 

[![Folium 0.16.0](https://img.shields.io/badge/Folium-0.16.0-brightgreen)](https://github.com/python-visualization/folium/releases/tag/v0.16.0) <img src = "https://github.com/PythonDataScience24/Group_01_Inspectair/assets/146727878/cb8513f7-909e-4ea8-94a8-7b291ccd6857"  width="30" height="25">

# Authors:
- Tim Schlatter - Timsched
- Titaporn Janjumratsang - nam32
- Hector Arribas Arias - Hecthor1999
- Julian Niklaus - JuNi-2000
# License:
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details
