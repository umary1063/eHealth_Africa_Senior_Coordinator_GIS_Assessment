"""Stable ReportLab A3 PDF renderer using the PostGIS evidence layers."""
from __future__ import annotations

import json
import math
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfgen import canvas

from src.ingestion.reference_db_connection import get_reference_connection, reference_cursor
from src.project_paths import project_root


def _features(connection, sql: str):
    with reference_cursor(connection) as cursor:
        cursor.execute(sql)
        names = [item[0] for item in cursor.description]
        return [dict(zip(names, row)) for row in cursor.fetchall()]


def _rings(geometry):
    if geometry["type"] == "Polygon": return geometry["coordinates"]
    if geometry["type"] == "MultiPolygon": return [ring for polygon in geometry["coordinates"] for ring in polygon]
    return []


def _extent(features):
    values = [coordinate for row in features for ring in _rings(json.loads(row["geom"])) for coordinate in ring]
    xs, ys = zip(*values)
    return min(xs), min(ys), max(xs), max(ys)


def _marker(pdf, x, y, colour, shape):
    pdf.setFillColor(HexColor(colour)); pdf.setStrokeColor(HexColor("#303030")); pdf.setLineWidth(0.25)
    if shape == "circle": pdf.circle(x, y, 2.0, fill=1, stroke=1)
    elif shape == "triangle":
        path = pdf.beginPath(); path.moveTo(x, y + 2.5); path.lineTo(x - 2.3, y - 2); path.lineTo(x + 2.3, y - 2); path.close(); pdf.drawPath(path, fill=1, stroke=1)
    elif shape == "square": pdf.rect(x - 2, y - 2, 4, 4, fill=1, stroke=1)
    else:
        path = pdf.beginPath(); path.moveTo(x, y + 2.5); path.lineTo(x - 2.5, y); path.lineTo(x, y - 2.5); path.lineTo(x + 2.5, y); path.close(); pdf.drawPath(path, fill=1, stroke=1)


def _box(pdf, x, y, width, height, title, lines):
    pdf.setFillColor(HexColor("#F4F7FA")); pdf.setStrokeColor(HexColor("#AAB7C4")); pdf.roundRect(x, y, width, height, 4, fill=1, stroke=1)
    pdf.setFillColor(HexColor("#1F4E79")); pdf.setFont("Helvetica-Bold", 8); pdf.drawString(x + 7, y + height - 14, title)
    pdf.setFillColor(HexColor("#263238")); pdf.setFont("Helvetica", 6.6)
    for index, line in enumerate(lines): pdf.drawString(x + 7, y + height - 27 - index * 8, line)


def build_pdf() -> Path:
    output = project_root() / "cartography" / "A3_layout.pdf"; output.parent.mkdir(exist_ok=True)
    connection = get_reference_connection()
    try:
        lgas = _features(connection, "SELECT lga_name, ST_AsGeoJSON(ST_Transform(geom,32632)) geom FROM reference.lgas")
        wards = _features(connection, "SELECT ward_name, ST_AsGeoJSON(ST_Transform(geom,32632)) geom FROM reference.wards")
        settlements = _features(connection, """SELECT r.reconciliation_class, ST_X(ST_Transform(s.geom,32632)) x, ST_Y(ST_Transform(s.geom,32632)) y
            FROM raw.settlements s JOIN processed.settlement_coverage_reconciliation r ON s.settlement_id=r.settlement_id""")
        inaccessible = _features(connection, """SELECT ST_X(ST_Transform(s.geom,32632)) x, ST_Y(ST_Transform(s.geom,32632)) y
            FROM raw.inaccessible_settlements i JOIN raw.settlements s ON s.settlement_id=i.settlement_id""")
    finally:
        connection.close()
    page_w, page_h = landscape(A3); pdf = canvas.Canvas(str(output), pagesize=(page_w, page_h)); pdf.setTitle("Q1 Campaign Coverage Reconciliation and GPS-Derived Visit Evidence")
    map_x, map_y, map_w, map_h = 42, 215, 760, 520
    xmin, ymin, xmax, ymax = _extent(lgas); pad_x, pad_y = (xmax - xmin) * .04, (ymax - ymin) * .04; xmin -= pad_x; xmax += pad_x; ymin -= pad_y; ymax += pad_y
    scale = min(map_w / (xmax - xmin), map_h / (ymax - ymin)); used_w, used_h = (xmax - xmin) * scale, (ymax - ymin) * scale; ox, oy = map_x + (map_w-used_w)/2, map_y + (map_h-used_h)/2
    def xy(x, y): return ox + (x - xmin) * scale, oy + (y - ymin) * scale
    pdf.setFillColor(white); pdf.setStrokeColor(HexColor("#263238")); pdf.rect(map_x, map_y, map_w, map_h, fill=1, stroke=1)
    # Coordinate grid.
    pdf.setStrokeColor(HexColor("#D5DEE5")); pdf.setLineWidth(.25); pdf.setFont("Helvetica", 5.5); pdf.setFillColor(HexColor("#607D8B"))
    grid_start_x, grid_start_y = math.ceil(xmin/10000)*10000, math.ceil(ymin/10000)*10000
    for value in range(int(grid_start_x), int(xmax), 10000):
        px, _ = xy(value, ymin); pdf.line(px, map_y, px, map_y + map_h); pdf.drawCentredString(px, map_y - 9, f"{value/1000:.0f}k")
    for value in range(int(grid_start_y), int(ymax), 10000):
        _, py = xy(xmin, value); pdf.line(map_x, py, map_x + map_w, py); pdf.drawRightString(map_x - 5, py - 2, f"{value/1000:.0f}k")
    for collection, colour, width in [(wards, "#97A6B2", .22), (lgas, "#283F54", .8)]:
        pdf.setStrokeColor(HexColor(colour)); pdf.setLineWidth(width)
        for row in collection:
            for ring in _rings(json.loads(row["geom"])):
                path = pdf.beginPath(); first = xy(*ring[0]); path.moveTo(*first)
                for point in ring[1:]: path.lineTo(*xy(*point))
                pdf.drawPath(path, stroke=1, fill=0)
    styles = {
        "GPS visited / e-tally reported": ("#238B45", "circle", "GPS + e-tally: corroborated visit"),
        "GPS visited / no e-tally report": ("#41AB5D", "circle", "GPS visit; no e-tally report"),
        "GPS unvisited / e-tally reported": ("#E6550D", "triangle", "No GPS visit evidence; e-tally reported"),
        "GPS unvisited / no e-tally report": ("#CB181D", "square", "No GPS or e-tally visit evidence"),
        "GPS ambiguous / e-tally reported": ("#756BB1", "diamond", "Ambiguous GPS attribution"),
        "GPS ambiguous / no e-tally report": ("#756BB1", "diamond", "Ambiguous GPS attribution"),
    }
    for row in settlements:
        colour, symbol, _ = styles[row["reconciliation_class"]]; _marker(pdf, *xy(row["x"], row["y"]), colour, symbol)
    pdf.setStrokeColor(black); pdf.setLineWidth(.7)
    for row in inaccessible:
        x, y = xy(row["x"], row["y"]); pdf.line(x-2.5,y-2.5,x+2.5,y+2.5); pdf.line(x-2.5,y+2.5,x+2.5,y-2.5)
    pdf.setFillColor(HexColor("#17365D")); pdf.setFont("Helvetica-Bold", 17); pdf.drawString(42, 800, "Campaign Coverage Reconciliation and GPS-Derived Visit Evidence")
    pdf.setFillColor(HexColor("#37474F")); pdf.setFont("Helvetica", 9); pdf.drawString(42, 782, "Senior Coordinator, Data and GIS Analytics Technical Assessment | baseline_30m visit classification | 9-13 March 2026")
    pdf.setFillColor(HexColor("#172B4D")); pdf.setFont("Helvetica-Bold", 14); pdf.drawCentredString(774, 714, "N"); pdf.setFont("Helvetica", 18); pdf.drawCentredString(774, 694, "▲")
    # Scale bar: 20 km.
    bar_w = 20000 * scale; sx, sy = map_x + 15, map_y + 15; pdf.setFillColor(black); pdf.rect(sx, sy, bar_w/2, 5, fill=1, stroke=0); pdf.setFillColor(white); pdf.rect(sx+bar_w/2, sy, bar_w/2, 5, fill=1, stroke=1); pdf.setFillColor(black); pdf.setFont("Helvetica", 6); pdf.drawString(sx, sy-8, "0"); pdf.drawCentredString(sx+bar_w/2, sy-8, "10 km"); pdf.drawRightString(sx+bar_w, sy-8, "20 km")
    # Evidence legend.
    lx, ly = 830, 715; pdf.setFillColor(HexColor("#1F4E79")); pdf.setFont("Helvetica-Bold", 10); pdf.drawString(lx, ly, "Observed evidence classes")
    pdf.setFont("Helvetica", 7); seen = set(); offset = 0
    for _, (colour, symbol, label) in styles.items():
        if label in seen: continue
        yy = ly - 18 - offset*18; _marker(pdf, lx+6, yy+2, colour, symbol); pdf.setFillColor(HexColor("#263238")); pdf.drawString(lx+17, yy, label); seen.add(label); offset += 1
    yy = ly - 18 - offset*18; pdf.setStrokeColor(black); pdf.line(lx+3,yy-2,lx+9,yy+4); pdf.line(lx+3,yy+4,lx+9,yy-2); pdf.setFillColor(HexColor("#263238")); pdf.drawString(lx+17,yy,"Inaccessible settlement")
    pdf.setFillColor(HexColor("#1F4E79")); pdf.setFont("Helvetica-Bold", 9); pdf.drawString(830, 550, "Interpretation")
    pdf.setFillColor(HexColor("#263238")); pdf.setFont("Helvetica", 7)
    for index, line in enumerate(["Symbols show observed evidence, not proof of", "service delivery or non-performance.", "", "GPS-unvisited means no confirmed GPS visit", "evidence under the baseline method; it does not", "establish that a settlement was genuinely missed."]): pdf.drawString(830, 536-index*10, line)
    _box(pdf, 42, 65, 245, 105, "Global spatial statistic", ["Primary k=8 Global Moran's I = 0.046612", "Expected I = -0.000420 | z = 4.821064", "999 permutations | p = 0.001"])
    _box(pdf, 300, 65, 245, 105, "Local Moran interpretation", ["Exploratory screening patterns are not statistically", "significant after FDR correction. No confirmed local", "hotspots are shown or inferred."])
    _box(pdf, 558, 65, 590, 105, "Uncertainty and decision use", ["Absence of GPS evidence is not evidence of operational failure. Potential causes include logger non-use or failure, signal loss,", "attribution uncertainty, timing or identifier mismatch, and processing limitations. Prioritize rapid verification before assuming non-performance."])
    pdf.setFillColor(HexColor("#455A64")); pdf.setFont("Helvetica", 6.5); pdf.drawString(42, 42, "Projection: EPSG:32632 (WGS 84 / UTM zone 32N) | Sources: GPS tracks, settlement masterlist, e-tally, inaccessible-settlement list, administrative boundaries.")
    pdf.drawString(42, 31, "Method: baseline_30m attribution; 30 m tolerance; 3-point, 15-minute continuous visit-episode rule. Absence of GPS evidence is not evidence of operational failure.")
    pdf.drawString(42, 20, "Cartographer: Yahaya Umar Muhammad | Date: 30 July 2026")
    pdf.save(); return output


if __name__ == "__main__": print(build_pdf())
