import os

# Change path to your path
#os.getcwd()
#directory = "path\to\here\inspectair\Group_01_Inspectair"
#os.chdir(directory)

from dash import Dash
import dash_bootstrap_components as dbc
from data_manager import AirQualityData
from layout_manager import AirQualityLayout
from callback_manager import AirQualityCallbacks

class AirQualityDashboard:
    def __init__(self, data_path, sheet_name="Update 2024 (V6.1)"):
        self.data = AirQualityData(data_path, sheet_name)
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.layout = AirQualityLayout(self.app, self.data)
        self.callbacks = AirQualityCallbacks(self.app, self.data)

    def run_server(self):
        self.app.run_server(debug=False, port=8002)


if __name__ == '__main__':
    data_path = os.path.join("who_ambient_air_quality_database_version_2024_(v6.1).xlsx")
    dashboard = AirQualityDashboard(data_path)
    dashboard.run_server()