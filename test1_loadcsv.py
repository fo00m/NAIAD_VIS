
# script pour charger CSV et visualiser les points de drones (localisation pour chque instant)

from qgis.core import (
    QgsVectorLayer, QgsProject, QgsField, QgsFeature, 
    QgsPointXY, QgsGeometry, QgsCoordinateReferenceSystem
)
import csv

# Define file path (Change this to your CSV file)
csv_file = "C:/Users/Po/Documents/drone_naiad/drone_trajectory_mock_utc.csv"



# Define layer URI
uri = f"file:///{csv_file}?delimiter=,&xField=longitude&yField=latitude&crs=EPSG:4326"

# Load CSV as a QGIS vector layer
csv_layer = QgsVectorLayer(uri, "Drone Trajectories", "delimitedtext")

# Check if the layer loaded successfully
if not csv_layer.isValid():
    print("Error: Failed to load CSV file into QGIS.")
else:
    print("CSV successfully loaded into QGIS.")

# Add the layer to QGIS
QgsProject.instance().addMapLayer(csv_layer)
