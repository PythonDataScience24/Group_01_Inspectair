## Changes for the week 16.05.24 - employing abstraction and decomposition

We split up the dashboard_main.py into several modules.
 - main.py  
   takes over the previous function of dashboard_main.py as the file that is run bringing all the components together - it initializes the dashboard components and runs the server.
 - datahandling.py  
   contains helper functions for the aqi calculation for the different pollutants (loads and preprocesses the data).
 - data_manager.py  
   reads in the data table, and processes it.
 - layout_manager.py  
   defines the layout for the dashboard
 - callback_manager.py  
   handles interaction of the user with the dashboard and generates the plots depending on selection
 - ranking_plots.py  
   contains helper functions for generating the ranking plots.
 - (map_generation to come)  
   will handle the folium map with geographical information.

Defined classes:
Class AirQualityDashboard: Controls the dashboard components, it contains: 
 - __init__ method: initializes the data, layout, and callbacks
 - run_server method: runs the Dash server

Class AirQualityCallbacks: Set up callbacks for dashboard, it contains:
 - __init__ method: takes Dash app instance and data object and initializes the callbacks
 - set_callbacks method: defines callback functions (update_graph which responds to changes in users selections and filters the data accordingly) 

 Class AirQualityLayout: set up the dashboard layout
 - __init__ method: takes the Dash app instance and data object and initializes the layout
 - set_layout method: defines the layout using Dash HTML and Bootstrap components (this includes dropdowns, rangeslider, checklist and radioitems and graphs)

Class AirQualityData: handles the data-related operations
 - __init__ method: loads the data from an Excel file, calculates AQI value for all pollutants (PM2.5, PM10, NO2) and initializes dictionaries and lists to use in the dashboard.

Splitting up the dashboard_main allows for a lot more readable code that can be kept short and capsulated. It makes it easier to work on for us. The dependencies of the project currently are such that main.py relies
on layout_manager, data_manager and callback_manager. Callback_manager relies on ranking_plots to generate the plots and data_manager relies on datahandling to calculate aqi.

Additionally a lot of the components of the dash were separated into their own classes (e.g layout, callback, data). This abstraction makes it easier if we were to add a second datasheet or a different set of layout. It also allowed us to more easily decompose the dashboard_main file into the different modules and improve code readability and reusability.
   
