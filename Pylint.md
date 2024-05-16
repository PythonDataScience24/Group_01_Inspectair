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

</details>

   
