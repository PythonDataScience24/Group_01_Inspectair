import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap

class Map:
    def __init__(self, start_coords=[20, 0], zoom_start=2):
        self.map = folium.Map(location=start_coords, zoom_start=zoom_start)

    def add_marker(self, location, popup=None, tooltip=None):
        folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(self.map)

    def add_clustered_markers(self, locations, popups=None, tooltips=None):
        marker_cluster = MarkerCluster().add_to(self.map)
        for i, location in enumerate(locations):
            popup = popups[i] if popups else None
            tooltip = tooltips[i] if tooltips else None
            folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(marker_cluster)
    
    def add_heatmap(self, locations, radius=10, blur=15, max_zoom=1):

        # Create gradient dictionary based on AQI thresholds
        gradient = {
            # the numbers for the gradient have to be between 0 and 1
            1.0: "maroon",        # Corresponds to normalized AQI value >= 250/500.4
            0.75: "purple",       # Corresponds to normalized AQI value >= 150/500.4
            0.5: "red",           # Corresponds to normalized AQI value >= 55/500.4
            0.35: "orange",       # Corresponds to normalized AQI value >= 35/500.4
            0.24: "yellow",       # Corresponds to normalized AQI value >= 12/500.4
            0.0: "green"          # Corresponds to normalized AQI value >= 0
        }

        
        HeatMap(locations, radius=radius, blur=blur, max_zoom=max_zoom, gradient=gradient).add_to(self.map)

    def save(self, file_path='map.html'):
        self.map.save(file_path)

    def get_map(self):
        return self.map
