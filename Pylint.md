# Pylint.md

### main.py
    ************* Module main
    main.py:1:0: C0114: Missing module docstring (missing-module-docstring)
    main.py:5:0: C0103: Constant name "directory" doesn't conform to UPPER_CASE naming style (invalid-name)
    main.py:8:0: C0413: Import "from dash import Dash" should be placed at the top of the module (wrong-import-position)
    main.py:9:0: C0413: Import "import dash_bootstrap_components as dbc" should be placed at the top of the module (wrong-import-position)
    main.py:10:0: C0413: Import "from data_manager import AirQualityData" should be placed at the top of the module (wrong-import-position)
    main.py:11:0: C0413: Import "from layout_manager import AirQualityLayout" should be placed at the top of the module (wrong-import-position)
    main.py:12:0: C0413: Import "from callback_manager import AirQualityCallbacks" should be placed at the top of the module (wrong-import-position)
    main.py:14:0: C0115: Missing class docstring (missing-class-docstring)
    main.py:15:23: W0621: Redefining name 'data_path' from outer scope (line 26) (redefined-outer-name)
    main.py:21:4: C0116: Missing function or method docstring (missing-function-docstring)
    main.py:14:0: R0903: Too few public methods (1/2) (too-few-public-methods)
    main.py:26:4: C0103: Constant name "data_path" doesn't conform to UPPER_CASE naming style (invalid-name)
    main.py:27:4: C0103: Constant name "dashboard" doesn't conform to UPPER_CASE naming style (invalid-name)
    
    --------------------------------------------------------------------
    Your code has been rated at -0.95/10 (previous run: -0.95/10)

After changes:

    ************* Module main
    main.py:24:0: R0903: Too few public methods (1/2) (too-few-public-methods)
    
    ------------------------------------------------------------------
    Your code has been rated at 9.52/10 (previous run: 8.10/10, +1.43)

<details>
  <summary>The code</summary>

  ```python
  """
main.py

The script initializes the dashboard at http://127.0.0.1:8002

Modules:
    data_manager: manages data, requires data
    layout_manager: handles layout structure of the dash
    callback_manager: handles callbacks and plot generation

"""
import os
from dash import Dash 
import dash_bootstrap_components as dbc 
from data_manager import AirQualityData
from layout_manager import AirQualityLayout
from callback_manager import AirQualityCallbacks

# Change path to your path
os.getcwd()
DIRECTORY = "C:/Users/Tim/Documents/School/UBE_MSC_SEM2/Advanced_python/Inspectair/airquality"
os.chdir(DIRECTORY)

class AirQualityDashboard:
    """
    A class that defines a dashboard to visualize data.

    Attributes:
        data: An instance of AirQualityData containing the air quality data.
        app: The Dash application instance.
        layout: The layout of the dashboard defining position and style of components.
        callbacks:  The callbacks to handle user interactions with elements and plots.

    Methods:
        run_server(): Runs the Dash server on the specified port.
    """
    def __init__(self, data_path, sheet_name="Update 2024 (V6.1)"):
        self.data = AirQualityData(data_path, sheet_name)
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout = AirQualityLayout(self.app, self.data)
        self.callbacks = AirQualityCallbacks(self.app, self.data)

    def run_server(self):
        """
        Runs the dash on the specified port
        """
        self.app.run_server(debug=False, port=8002)


if __name__ == '__main__':
    DATA_FILE_PATH = os.path.join("who_ambient_air_quality_database_version_2024_(v6.1).xlsx")
    DASHBOARD = AirQualityDashboard(DATA_FILE_PATH)
    DASHBOARD.run_server()
 ```
</details>

### datahadling.py
      ************* Module datahandling
      datahandling.py:3:0: C0301: Line too long (178/100) (line-too-long)
      datahandling.py:13:0: C0303: Trailing whitespace (trailing-whitespace)
      datahandling.py:15:0: C0303: Trailing whitespace (trailing-whitespace)
      datahandling.py:23:0: C0301: Line too long (103/100) (line-too-long)
      datahandling.py:27:0: C0301: Line too long (103/100) (line-too-long)
      datahandling.py:33:17: C0303: Trailing whitespace (trailing-whitespace)
      datahandling.py:38:0: C0303: Trailing whitespace (trailing-whitespace)
      datahandling.py:40:0: C0303: Trailing whitespace (trailing-whitespace)
      datahandling.py:1:0: C0114: Missing module docstring (missing-module-docstring)
      datahandling.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
      datahandling.py:7:0: C0116: Missing function or method docstring (missing-function-docstring)
      datahandling.py:43:0: C0116: Missing function or method docstring (missing-function-docstring)
      datahandling.py:45:4: R1705: Unnecessary "elif" after "return" (no-else-return)
      
      -----------------------------------
      Your code has been rated at 6.39/10

   After changes:

      -------------------------------------------------------------------
      Your code has been rated at 10.00/10 (previous run: 9.72/10, +0.28)

<details>
  <summary>The code</summary>

  ```python
"""
datahandling.py

Contains auxilliary functions for the data cleanup of the airpollution spreadsheet
and defines aqi values.
"""

import numpy as np

# Airquality is given as aqi when target audience is general public for ease of data intepretation
def lerp(low_aqi, high_aqi, low_conc, high_conc, conc):
    """
    Function tha performs linear interpolation between high and low concentration for the aqi.

    Input:
        low_aqi: lower threshold of aqi  corresponding to low conc
        high_aqi: upper threshold of aqi corresponding to high conc
        low_conc: low concentraition corresponding to low aqi
        high_conc: high concentration corresponding to high aqi
        conc: concentration that aqi is interpolated for

    Output:
        float corrsponding to the interpolated value at concentration conc
    """
    return low_aqi + (conc - low_conc) * (high_aqi - low_aqi) / (high_conc - low_conc)

def calculate_aqi(pollutant_type, concentrations):
    """
    calculates aqis based on the pollutant and a list of concentrations

    Input:
        pollutant_type: string of the pollutant either no2, pm25 or pm10
        concentrations: list of the concentrations that aqi is to be calculated

    Output:
        aqi_values: list of aqi values at the concentrations given.
    """
    aqi_values = []
    for conc in concentrations:
        if np.isnan(conc):
            aqi_values.append(None)
            continue

        conc = max(conc, 0)

        # define pollutant types and their thresholds
        if pollutant_type == 'no2':
            breakpoints = [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150),
                           (361, 649, 151, 200), (650, 1249, 201, 300),
                           (1250, 1649, 301, 400), (1650, 2049, 401, 500)]
        elif pollutant_type == 'pm25':
            breakpoints = [(0.0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                           (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300),
                           (250.5, 350.4, 301, 400), (350.5, 500.4, 401, 500)]
        elif pollutant_type == 'pm10':
            breakpoints = [(0, 12, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                           (55.5, 150.4, 151, 200), (150.5, 100.4, 201, 300),
                           (100.5, 350.4, 301, 400), (350.5, 500.4, 401, 500)]
        else:
            raise ValueError("Unsupported pollutant type")

        # Default AQI if concentration is beyond the highest range
        aqi = 500
        for (low_conc, high_conc, low_aqi, high_aqi) in breakpoints:
            if low_conc <= conc <= high_conc:
                aqi = lerp(low_aqi, high_aqi, low_conc, high_conc, conc)
                break
        aqi_values.append(round(aqi))

    return aqi_values

def assign_aqi_message(aqi):
    """
    function to assign message and color based on AQI

    Input:
        aqi: Integer representing aqi value

    Output:
        2 strings, pollution hazard and colour
    """
    if aqi >= 250:
        return "hazardous", "maroon"
    if aqi >= 150:
        return "very unhealthy", "purple"
    if aqi >= 55:
        return "unhealthy", "red"
    if aqi >= 35:
        return "unhealthy to sensitive groups", "orange"
    if aqi >= 12:
        return "moderate", "yellow"
    return "good", "green"


 ```
</details>


Note: a lot more things to be fixed in the other modules.



   
