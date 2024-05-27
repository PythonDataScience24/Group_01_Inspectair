"""
datahandling.py

Contains auxilliary functions for the data cleanup of the airpollution spreadsheet
and defines aqi values.
"""

import numpy as np

# Airquality is given as aqi for ease of data intepretation
def lerp(low_aqi, high_aqi, low_conc, high_conc, conc):
    """
    Function that performs linear interpolation between high and low concentration for the aqi.

    Args:
        low_aqi: lower threshold of aqi  corresponding to low conc
        high_aqi: upper threshold of aqi corresponding to high conc
        low_conc: low concentraition corresponding to low aqi
        high_conc: high concentration corresponding to high aqi
        conc: concentration that aqi is interpolated for

    Returns:
        float corrsponding to the interpolated value at concentration conc
    """
    return low_aqi + (conc - low_conc) * (high_aqi - low_aqi) / (high_conc - low_conc)

def calculate_aqi(pollutant_type, concentrations):
    """
    Calculates AQIs based on the pollutant type and a list of concentrations.

    Args:
        pollutant_type (str): The pollutant type, either 'no2', 'pm25', or 'pm10'.
        concentrations (list or np.ndarray): List or numpy array of the concentrations for which AQI is to be calculated.

    Returns:
        list: List of AQI values for the given concentrations.
    """
    if type(pollutant_type) not in [str]:
        raise TypeError("Pollutant has to be a string (either no2,pm10 or pm25)")
    
    if not isinstance(concentrations, (list,np.ndarray)):
        raise TypeError("concentrations has to be a list or a numpy array.")
    
    aqi_values = []
    for conc in concentrations:
        if np.isnan(conc):
            aqi_values.append(None)
            continue

        conc = max(conc, 0)

        # Define pollutant types and their thresholds
        if pollutant_type == 'no2':
            breakpoints = [(0, 53, 0, 50), (54, 100, 51, 100), (101, 360, 101, 150),
                           (361, 649, 151, 200), (650, 1249, 201, 300),
                           (1250, 1649, 301, 400), (1650, 2049, 401, 500)]
        elif pollutant_type == 'pm25':
            breakpoints = [(0.0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                           (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300),
                           (250.5, 350.4, 301, 400), (350.5, 500.4, 401, 500)]
        elif pollutant_type == 'pm10':
            breakpoints = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                           (255, 354, 151, 200), (355, 424, 201, 300),
                           (425, 529, 301, 400), (530, 604, 401, 500)]
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
    Function to assign message and color based on AQI.

    Args:
        aqi (int): Integer representing AQI value.

    Returns:
        tuple: Two strings, pollution hazard and color.
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
