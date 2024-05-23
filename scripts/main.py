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
current_directory= os.getcwd()

directory = os.path.join(current_directory)
os.chdir(directory)

class AirQualityDashboard:
    """
    A class that defines a dashboard to visualize data.

    Attributes:
        data: An instance of AirQualityData containing the air quality data.
        app: The Dash application instance.
        layout: The layout of the dashboard defining position and style of components.
        callbacks: The callbacks to handle user interactions with elements and plots.

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
        Runs Dash on the specified port
        """
        self.app.run_server(debug=False, port=8002)


if __name__ == '__main__':
    DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"who_ambient_air_quality_database_version_2024_(v6.1).xlsx")
    
    try:
        # Attempt to create an instance of the AirQualityDashboard and run the server
        DASHBOARD = AirQualityDashboard(DATA_FILE_PATH)
        DASHBOARD.run_server()
    except FileNotFoundError as e:
        # Handle the case where data file does not exist
        print(f"Error: The file '{DATA_FILE_PATH}' does not exist. Please check the file path and try again.")
    except Exception as e:
        # Handle any other exceptions during initialization
        print(f"Error: {e}")
