import folium
from folium.plugins import MarkerCluster, HeatMap

class Map:

    def __init__(self, start_coords=[20, 0], zoom_start=2, max_zoom=2):
        self.map = folium.Map(location=start_coords, zoom_start=zoom_start, max_zoom=max_zoom)
        self.layers = []  # Keep track of layers for the layer control

    def add_marker(self, location, popup=None, tooltip=None):
        marker = folium.Marker(location=location, popup=popup, tooltip=tooltip)
        marker.add_to(self.map)
        self.layers.append(marker)  # Add marker to the layers list

    def add_clustered_markers(self, locations, popups=None, tooltips=None):
        marker_cluster = MarkerCluster()
        for i, location in enumerate(locations):
            popup = popups[i] if popups else None
            tooltip = tooltips[i] if tooltips else None
            folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(marker_cluster)
        marker_cluster.add_to(self.map)
        self.layers.append(marker_cluster)  # Add marker cluster to the layers list
    
    def add_heatmap(self, locations, radius=10, blur=15, max_zoom=2, layer_name='Heatmap'):
        gradient = {
            1.0: "maroon",
            0.75: "purple",
            0.5: "red",
            0.35: "orange",
            0.24: "yellow",
            0.0: "green"
        }
        heatmap = HeatMap(locations, radius=radius, blur=blur, max_zoom=max_zoom, gradient=gradient, name=layer_name)
        heatmap.add_to(self.map)
        self.layers.append(heatmap)  # Add heatmap to the layers list

        # Add custom legend to map 
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

    def update_layer_control(self):
        # Remove any existing LayerControl
        for child in self.map._children:
            if isinstance(self.map._children[child], folium.LayerControl):
                self.map._children.pop(child)
                break
        # Add a new LayerControl
        folium.LayerControl().add_to(self.map)

    def save(self, file_path='map.html'):
        self.update_layer_control()  # Ensure LayerControl is updated before saving
        self.map.save(file_path)

    def get_map(self):
        self.update_layer_control()  # Ensure LayerControl is updated before returning the map
        return self.map

