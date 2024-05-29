import folium
from folium.plugins import MarkerCluster, HeatMap

class Map:
    """
    A class to create and manage an interactive map with various layers like markers, 
    clustered markers, and heatmaps using the Folium library (Python wrapper for the JavaScript library Leaflet).

    Attributes:
        map (folium.Map): The Folium map object.
        layers (list): List to keep track of layers for the layer control.
        station_selected (bool): Boolean to track if any station type is selected.

    Methods:
        __init__(start_coords=[20, 0], zoom_start=2, max_zoom=2):
            Initializes the Map object with starting coordinates, initial zoom level, and maximum zoom level.
        add_marker(location, popup=None, tooltip=None, layer_name='Marker'):
            Adds a single marker to the map.
        add_clustered_markers(locations, popups=None, tooltips=None, layer_name='Clustered Markers'):
            Adds clustered markers to the map.
        add_heatmap(locations, radius=10, blur=15, max_zoom=2, layer_name='Heatmap'):
            Adds a heatmap layer to the map.
        update_layer_control():
            Updates the LayerControl to reflect the current layers on the map.
        set_station_type_selection(selected):
            Sets the station type selection status.
        should_display_map():
            Determines if the map should be displayed based on station type selection.
        save(file_path='map.html'):
            Saves the map to an HTML file. If no layers are added, displays a logo instead of the map.
        get_map():
            Returns the current map object if layers are added, otherwise returns None.
    """

    def __init__(self, start_coords=[20, 0], zoom_start=2, max_zoom=2):
        """
        Initialize the Map object.

        Parameters:
        start_coords (list): The starting coordinates for the map [latitude, longitude].
        zoom_start (int): Initial zoom level for the map.
        max_zoom (int): Maximum zoom level for the map.
        """
        self.map = folium.Map(location=start_coords, zoom_start=zoom_start, max_zoom=max_zoom)
        # Keep track of layers for the layer control
        self.layers = []
        self.station_selected = True

    def add_marker(self, location, popup=None, tooltip=None, layer_name='Marker'):
        """
        Add a single marker to the map.

        Parameters:
        location (list): Coordinates of the marker [latitude, longitude].
        popup (str, optional): Popup text for the marker.
        tooltip (str, optional): Tooltip text for the marker.
        layer_name (str): Name of the layer in the LayerControl.
        """
        feature_group = folium.FeatureGroup(name=layer_name)
        marker = folium.Marker(location=location, popup=popup, tooltip=tooltip)
        marker.add_to(feature_group)
        feature_group.add_to(self.map)
        self.layers.append(feature_group)

    def add_clustered_markers(self, locations, popups=None, tooltips=None, layer_name='Clustered Markers'):
        """
        Add clustered markers to the map.

        Parameters:
        locations (list): List of coordinates for the markers [[lat1, lon1], [lat2, lon2], ...].
        popups (list, optional): List of popup texts corresponding to the markers.
        tooltips (list, optional): List of tooltip texts corresponding to the markers.
        layer_name (str): Name of the layer in the LayerControl.
        """
        marker_cluster = MarkerCluster(name=layer_name)
        for i, location in enumerate(locations):
            popup = popups[i] if popups else None
            tooltip = tooltips[i] if tooltips else None
            folium.Marker(location=location, popup=popup, tooltip=tooltip).add_to(marker_cluster)
        marker_cluster.add_to(self.map)
        self.layers.append(marker_cluster)

    def add_heatmap(self, locations, radius=10, blur=15, max_zoom=2, layer_name='Heatmap'):
        """
        Add a heatmap layer to the map.

        Parameters:
        locations (list): List of coordinates for the heatmap [[lat1, lon1], [lat2, lon2], ...].
        radius (int): Radius of each point on the heatmap.
        blur (int): Amount of blur for the heatmap points.
        max_zoom (int): Maximum zoom level for the heatmap.
        layer_name (str): Name of the layer in the LayerControl.
        """
        gradient = {
            1.0: "maroon",
            0.75: "purple",
            0.5: "red",
            0.35: "orange",
            0.24: "yellow",
            0.0: "green"
        }
        heatmap = HeatMap(locations, radius=radius, blur=blur, max_zoom=max_zoom, gradient=gradient, name=layer_name)
        # Add heatmap as a raster layer to the map
        heatmap.add_to(self.map) 
        # Add layer control to the heatmap
        self.layers.append(heatmap) 

        # Add custom legend to map in html as there is no native tool in folium
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
        """
        Update the LayerControl to reflect the current layers on the map.
        """
        # Remove any existing LayerControl
        for child in self.map._children:
            if isinstance(self.map._children[child], folium.LayerControl):
                self.map._children.pop(child)
                break
        # Add a new LayerControl
        folium.LayerControl().add_to(self.map)

    def set_station_type_selection(self, selected):
        """
        Set the station type selection status.

        Parameters:
        selected (bool): True if a pollutant is selected, False otherwise.
        """
        self.station_selected = selected

    def should_display_map(self):
        """
        Determine if the map should be displayed based on station type selection.

        Returns:
        bool: True if one or multiple stations are selected, False otherwise.
        """
        return self.station_selected 

    def save(self, file_path='map.html'):
        """
        Save the map to an HTML file. If no layers are added, display a logo instead of the map.

        Parameters:
        file_path (str): The file path to save the map.
        """
        if self.should_display_map():
            # Ensure Layer control is updated before saving
            self.update_layer_control()  
            self.map.save(file_path)
        else:
             # Return the path to the GIF file
            gif_path = "no_data.html"
            with open(gif_path, "w") as f:
                f.write('<img src="no_data.html">') 
                
    def get_map(self):
        """
        Get the current map object.

        Returns:
        folium.Map: The current map object if layers are added, otherwise None.
        """
        if self.should_display_map():
            # Ensure Layer control is updated before returning the map
            self.update_layer_control()  
            return self.map
        else:
            return None
