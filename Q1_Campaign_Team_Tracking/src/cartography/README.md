# Cartography

`generate_a3_map.py` produces the editable QGIS layout from PostGIS-resident Q1 evidence layers. It is run with the local QGIS Python launcher, not the Conda interpreter. `generate_a3_pdf.py` produces the final A3 PDF from the same evidence layers using ReportLab, avoiding an unstable native QGIS PDF-export path on this Windows installation. The project stores connection settings without a password; re-opening it elsewhere requires an authorised PostGIS connection.

The map differentiates observed evidence from operational inference. In particular, a GPS-unvisited symbol means no confirmed GPS visit evidence under the baseline method; it is not proof that a settlement was operationally missed.
