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
