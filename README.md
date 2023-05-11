# GISPointTools
Utility for projecting three dimensional survey data onto lines to generate station,offset formatted data.

This project is developed as a QGIS Processing Application to enable users to have a simple interface to project points to a polyline and output a simple CSV file with the polyline name, point number, station, offset, and description. The purpose of this utility it to enable the data to be usable by programs that require station-offset formats or for plotting survey data in graphing programs.

Use:
The user should draw alignments along the features surveyed in geomorphology applications this would typically be a stream centerline and cross-sections oriented perpendicular to the direction of flow. It is anticipated that the point data will be formatted so that there is a point number, description, and elevation attributed associated with each point.
