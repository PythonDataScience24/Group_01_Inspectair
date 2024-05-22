import os
import sys
import unittest

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.append(script_path)

from datahandling import calculate_aqi

class TestAqi(unittest.TestCase):
    def test_calculate_aqi(self):
        self.assertEqual(calculate_aqi("no2",[78,217]),[77,123],"Should be [77,123]")
        self.assertEqual(calculate_aqi("pm25",[35.4]),[100],"Should be [100]")
        self.assertEqual(calculate_aqi("pm25",[-22]),[0],"Should be [0]")
        self.assertEqual(calculate_aqi("pm10",[177]),[112],"Should be [112]")

    def test_input_value(self):
        self.assertRaises(TypeError,calculate_aqi,222,[78,217])
        self.assertRaises(TypeError,calculate_aqi,"pm25",78)



