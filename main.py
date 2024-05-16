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
