The file calculate_aqi_test.py performs a unittest for the function calculate_aqi() from the module datahandling.

The function calculate_aqi expects a pollutant_type of type string and concentrations, a list or numpy array of pollutant concentrations. With those it calculates a list of aqi values, an index for airquality.    

The test makes sure to assert correct calculations for aqi values across the three different pollutant types. It also asserts that a negaative value results in an aqi of 0. This is preferred to not break visualization even if negative values dont make sense and you could argue it should raise an error. The test also asserts that the wrong data types raise a type error. In order to do this the following code was added to the function itself.  
```
if type(pollutant_type) not in [str]:
        raise TypeError("Pollutant has to be a string (either no2,pm10 or pm25)")
    
if not isinstance(concentrations, (list,np.ndarray)):
        raise TypeError("concentrations has to be a list or a numpy array.")
```

This is useful as it is easy to forget that one cannot call calculate aqi with an int or float as a concentration value. Additionally asserting the results makes sure that the calculation is performed correctly even if someone were to alter the lerp function or use outdated reakpoints for the aqi value in the function.


