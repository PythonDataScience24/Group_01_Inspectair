## Changes for the week 16.05.24 - employing abstraction and decomposition

We split up the dashboard_main.py into several modules.
 - main.py  
   takes over the previous function of dashboard_main.py as the file that is run bringing all the components together.
 - datahandling.py  
   contains functions for the aqi calculation for the different pollutants.  
 - data_manager.py  
   reads in the data table, and processes it.
 - layout_manager.py  
   defines the layout for the dashboard
 - callback_manager.py  
   handles interaction of the user with the dashboard and generates the plots depending on selection
 - ranking_plots.py  
   contains functions for generating the ranking plots.
 - (map_generation to come)  
   will handle the folium map with geographical information.


Splitting up the dashboard_main allows for a lot more readable code that can be kept short and capsulated. It makes it easier to work on for us. The dependencies of the project currently are such that main.py relies
on layout_manager, data_manager and callback_manager. Callback_manager relies on ranking_plots to generate the plots and data_manager relies on datahandling to calculate aqi.

Additionally a lot of the components of the dash were separeted into their own classes (e.g layout, callback, data). This abstraction makes it easier if we were to add a second datasheet or a different set of layout. It also allowed us to more easily decompose the dashboard_main file into the different modules.
   
