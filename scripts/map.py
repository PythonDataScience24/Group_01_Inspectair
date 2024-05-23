import folium
from folium.plugins import MarkerCluster
from folium.plugins import HeatMap

class Map:

    def __init__(self, start_coords=[20, 0], zoom_start=2, max_zoom=2):
        self.map = folium.Map(location=start_coords, zoom_start=zoom_start, max_zoom=max_zoom)

    def add_marker(self, location, popup=None, tooltip=None):
        folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(self.map)

    def add_clustered_markers(self, locations, popups=None, tooltips=None):
        marker_cluster = MarkerCluster().add_to(self.map)
        for i, location in enumerate(locations):
            popup = popups[i] if popups else None
            tooltip = tooltips[i] if tooltips else None
            folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(marker_cluster)
    
    def add_heatmap(self, locations, radius=10, blur=15, max_zoom=2):

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

        # Add custom legend to map in html as folium does not have a native tool to do it
        legend_html = '''
        <div style="position: fixed;
                    bottom: 50px; left: 50px; width: 100px; height: 190px; 
                    border:2px solid grey; z-index:9999; font-size:14px;
                    padding: 10px;">
        <p style="margin: 0; font-weight: bold;">AQI index<br></p>
        <p style="margin: 0;">
            <i style="background:green; width: 20px; height: 20px; display: inline-block;"></i> 0-50<br>
            <i style="background:yellow; width: 20px; height: 20px; display: inline-block;"></i> 51-100<br>
            <i style="background:orange; width: 20px; height: 20px; display: inline-block;"></i> 101-150<br>
            <i style="background:red; width: 20px; height: 20px; display: inline-block;"></i> 151-200<br>
            <i style="background:purple; width: 20px; height: 20px; display: inline-block;"></i> 201-300<br>
            <i style="background:maroon; width: 20px; height: 20px; display: inline-block;"></i> 301-500
        </p>
        </div>
        ''' 
        self.map.get_root().html.add_child(folium.Element(legend_html))
        self.map = folium.LayerControl().add_to(self.map)

    def save(self, file_path='map.html'):
        self.map.save(file_path)

    def get_map(self):
        return self.map
