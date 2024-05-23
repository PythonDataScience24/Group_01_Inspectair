import pandas as pd
import numpy as np
from datahandling import calculate_aqi

class AirQualityData:
    """
    A class to handle the loading and processing of air quality data.

    Attributes:
        df: A pandas DataFrame containing the air quality data.
        legend: A dictionary for mapping pollutant columns to their full names.
        continent_dict: A dictionary mapping continent codes to their names.
        reverse_continent_dict: A dictionary mapping continent names to their codes.
        pollutant_type: A dictionary for mapping pollutant columns to their full names.
        reverse_pollutant_type: A dictionary mapping pollutant names to their column names.
        station_type: A dictionary for mapping station types to their specific types.
        reverse_station_type: A dictionary mapping specific station types to their general categories.
        continents_options: A list of dictionaries for continent options for dropdown menus.
        pollutants_options: A list of dictionaries for pollutant options for dropdown menus.
        stations_options: A list of dictionaries for station type options for dropdown menus.
        years_options: A list of dictionaries for year options for dropdown menus.

    Methods:
        __init__(data_path, sheet_name="Update 2024 (V6.1)"):
            Initializes the AirQualityData with the given data path and sheet name.
    """

    def __init__(self, data_path, sheet_name="Update 2024 (V6.1)"):
        """
        Initializes the AirQualityData with the given data path and sheet name.

        Args:
            data_path (str): The path to the data file.
            sheet_name (str): The sheet name in the Excel file. Defaults to "Update 2024 (V6.1)".
        """
        
        file_path = data_path
        self.df = pd.read_excel(data_path, sheet_name=sheet_name)
        self.df["pm25_aqi"] = pd.DataFrame(calculate_aqi("pm25", (self.df["pm25_concentration"]).to_numpy()))
        self.df["pm10_aqi"] = pd.DataFrame(calculate_aqi("pm10", (self.df["pm10_concentration"]).to_numpy()))
        self.df["no2_aqi"] = pd.DataFrame(calculate_aqi("no2", (self.df["no2_concentration"]).to_numpy()))

        self.legend = {
            'pm10_concentration': 'PM10 Concentration',
            'pm25_concentration': 'PM2.5 Concentration',
            'no2_concentration': 'NO2 Concentration',
            'pm10_aqi': 'PM10 AQI',
            'pm25_aqi': 'PM2.5 AQI',
            'no2_aqi': 'NO2 AQI'
        }

        self.continent_dict = {
            '': 'World',
            '1_Afr': 'Africa',
            '2_Amr': 'Americas',
            '3_Sear': 'South-East Asia',
            '4_Eur': 'Europe',
            '5_Emr': 'Eastern Mediterranean',
            '6_Wpr': 'Western Pacific',
            '7_NonMS': 'Non-member state'
        }
        self.reverse_continent_dict = {value: key for key, value in self.continent_dict.items()}

        self.pollutant_type = {
            'pm10_concentration': 'PM10 Concentration',
            'pm25_concentration': 'PM2.5 Concentration',
            'no2_concentration': 'NO2 Concentration'
        }
        self.reverse_pollutant_type = {value: key for key, value in self.pollutant_type.items()}

        self.station_type = {
            'all': ['all'],
            'Rural': ['Rural'],
            'Urban': ['Fond Urbain', 'Urban Traffic', 'Urban', 'Urban Traffic/Residential And Commercial Area'],
            'Residential': ['Residential - industrial','Residential And Commercial Area', 'Urban Traffic/Residential And Commercial Area'],
            'Suburban': ['Suburban'],
            'Industrial': ['Residential - industrial', 'Industrial'],
            'Background': ['Background'],
            'Traffic': ['Traffic', 'Urban Traffic/Residential And Commercial Area']
        }

        self.reverse_station_type = {}
        for key, values in self.station_type.items():
            for value in values:
                self.reverse_station_type[value] = key

        self.continents_options = [{'label': name, 'value': key} for key, name in self.continent_dict.items()]
        self.pollutants_options = [{'label': name, 'value': key} for key, name in self.pollutant_type.items()]
        self.stations_options = [{'label': name, 'value': key} for key, name in self.station_type.items()]

        all_years = np.array(((self.df["year"].dropna().unique()).astype(int)), dtype=str)
        all_years = np.append(all_years, 'all')
        self.years_options = [{'label': name, 'value': name} for name in all_years]