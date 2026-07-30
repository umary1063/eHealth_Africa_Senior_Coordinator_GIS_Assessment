"""Generate the editable QGIS A3 layout for the Q1 technical map."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from qgis.PyQt.QtCore import QRectF
from qgis.PyQt.QtGui import QColor, QFont
from qgis.core import (
    QgsApplication, QgsCoordinateReferenceSystem, QgsDataSourceUri, QgsFillSymbol,
    QgsLayoutExporter, QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemMap, QgsLayoutItemPage,
    QgsLayoutItemScaleBar, QgsLayoutItemMapGrid, QgsLayoutPoint, QgsLayoutSize, QgsLineSymbol,
    QgsMarkerSymbol, QgsPrintLayout, QgsProject, QgsRendererCategory, QgsCategorizedSymbolRenderer,
    QgsSingleSymbolRenderer, QgsUnitTypes, QgsVectorLayer,
)

from src.ingestion.db_connection import load_local_environment
from src.project_paths import project_root


def _postgres_layer(schema: str, relation: str, geometry: str, key: str, name: str) -> QgsVectorLayer:
    load_local_environment()
    uri = QgsDataSourceUri()
    uri.setConnection(
        os.environ.get("POSTGRES_HOST", "localhost"), os.environ.get("POSTGRES_PORT", "5432"),
        os.environ.get("POSTGRES_DB", "eha_q1"), os.environ.get("POSTGRES_USER", "eha_q1_user"),
        os.environ["POSTGRES_PASSWORD"],
    )
    uri.setDataSource(schema, relation, geometry, "", key)
    layer = QgsVectorLayer(uri.uri(False), name, "postgres")
    if not layer.isValid():
        raise RuntimeError(f"Unable to load map layer: {name}")
    return layer


def _label(layout: QgsPrintLayout, text: str, x: float, y: float, w: float, h: float, size: float, bold=False, color="#172B4D"):
    item = QgsLayoutItemLabel(layout)
    item.setText(text); item.setFont(QFont("Aptos", round(size), QFont.Weight.Bold if bold else QFont.Weight.Normal))
    item.setFontColor(QColor(color)); item.adjustSizeToText()
    item.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    item.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(item)
    return item


def _box(layout: QgsPrintLayout, title: str, body: str, x: float, y: float, w: float, h: float):
    _label(layout, title, x + 2, y + 1.5, w - 4, 6, 8, bold=True, color="#1F4E79")
    _label(layout, body, x + 2, y + 8, w - 4, h - 10, 6.6, color="#263238")


def _strip_password(qgz_path: Path):
    """Remove credentials from the editable project after the PDF is rendered."""
    import zipfile
    import tempfile
    with zipfile.ZipFile(qgz_path, "r") as source:
        entries = {name: source.read(name) for name in source.namelist()}
    for name, value in list(entries.items()):
        if name.endswith(".qgs"):
            text = value.decode("utf-8")
            text = re.sub(r"password='[^']*'", "password=''", text)
            text = re.sub(r"password=([^\s&]+)", "password=", text)
            entries[name] = text.encode("utf-8")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".qgz") as temp:
        temporary = Path(temp.name)
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as target:
        for name, value in entries.items(): target.writestr(name, value)
    temporary.replace(qgz_path)


def build_map() -> tuple[Path, Path]:
    root = project_root(); output_dir = root / "cartography"; output_dir.mkdir(exist_ok=True)
    qgz_path = output_dir / "A3_layout.qgz"; pdf_path = output_dir / "A3_layout.pdf"
    project = QgsProject.instance(); project.clear(); project.setCrs(QgsCoordinateReferenceSystem("EPSG:32632"))

    lgas = _postgres_layer("reference", "lgas", "geom", "lga_code", "LGA boundaries")
    wards = _postgres_layer("reference", "wards", "geom", "ward_code", "Ward boundaries")
    settlements_sql = """(SELECT s.settlement_id, s.settlement_name, s.geom,
        r.gps_visit_status, r.etally_report_status, r.reconciliation_class, r.gps_confidence_status
        FROM raw.settlements s JOIN processed.settlement_coverage_reconciliation r
        ON s.settlement_id = r.settlement_id)"""
    settlements = _postgres_layer("", settlements_sql, "geom", "settlement_id", "Settlement evidence classes")
    inaccessible_sql = """(SELECT i.inaccessible_settlement_id, i.security_classification, s.geom
        FROM raw.inaccessible_settlements i JOIN raw.settlements s ON s.settlement_id = i.settlement_id)"""
    inaccessible = _postgres_layer("", inaccessible_sql, "geom", "inaccessible_settlement_id", "Inaccessible settlements")

    lgas.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({"color": "255,255,255,0", "outline_color": "40,40,40", "outline_width": "0.8"})))
    wards.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({"color": "255,255,255,0", "outline_color": "130,130,130", "outline_width": "0.25"})))
    classes = [
        ("GPS visited / e-tally reported", "GPS + e-tally: corroborated visit", "#238B45", "circle", "2.4"),
        ("GPS visited / no e-tally report", "GPS visit; no e-tally report", "#41AB5D", "circle", "2.4"),
        ("GPS unvisited / e-tally reported", "No GPS visit evidence; e-tally reported", "#E6550D", "triangle", "2.8"),
        ("GPS unvisited / no e-tally report", "No GPS or e-tally visit evidence", "#CB181D", "square", "2.4"),
        ("GPS ambiguous / e-tally reported", "Ambiguous GPS; e-tally reported", "#756BB1", "diamond", "2.8"),
        ("GPS ambiguous / no e-tally report", "Ambiguous GPS; no e-tally report", "#756BB1", "diamond", "2.8"),
    ]
    categories = []
    for value, label, color, shape, size in classes:
        symbol = QgsMarkerSymbol.createSimple({"name": shape, "color": color, "outline_color": "#303030", "outline_width": "0.15", "size": size})
        categories.append(QgsRendererCategory(value, symbol, label))
    settlements.setRenderer(QgsCategorizedSymbolRenderer("reconciliation_class", categories))
    inaccessible.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name": "cross", "color": "#000000", "size": "3.0", "outline_width": "0.6"})))
    for layer in (lgas, wards, settlements, inaccessible): project.addMapLayer(layer)

    layout = QgsPrintLayout(project); layout.initializeDefaults(); layout.setName("A3 Technical Evidence Layout")
    page = layout.pageCollection().page(0); page.setPageSize("A3", QgsLayoutItemPage.Orientation.Landscape)
    project.layoutManager().addLayout(layout)
    _label(layout, "Campaign Coverage Reconciliation and GPS-Derived Visit Evidence", 10, 7, 280, 10, 15, True)
    _label(layout, "Senior Coordinator, Data and GIS Analytics Technical Assessment | baseline_30m visit classification | 9-13 March 2026", 10, 18, 390, 6, 7)
    map_item = QgsLayoutItemMap(layout); map_item.setFrameEnabled(True)
    map_item.setLayers([lgas, wards, settlements, inaccessible]); map_item.setCrs(QgsCoordinateReferenceSystem("EPSG:32632"))
    extent = lgas.extent(); extent.scale(1.05); map_item.setExtent(extent)
    map_item.attemptMove(QgsLayoutPoint(10, 30, QgsUnitTypes.LayoutMillimeters)); map_item.attemptResize(QgsLayoutSize(258, 174, QgsUnitTypes.LayoutMillimeters)); layout.addLayoutItem(map_item)
    grid = QgsLayoutItemMapGrid("UTM grid", map_item); map_item.grids().addGrid(grid); grid.setEnabled(True); grid.setIntervalX(10000); grid.setIntervalY(10000); grid.setGridLineColor(QColor("#B0BEC5")); grid.setGridLineWidth(0.1)

    legend = QgsLayoutItemLegend(layout); legend.setLinkedMap(map_item); legend.setTitle("Observed evidence classes")
    legend.model().setRootGroup(project.layerTreeRoot().clone()); legend.attemptMove(QgsLayoutPoint(274, 34, QgsUnitTypes.LayoutMillimeters)); legend.attemptResize(QgsLayoutSize(135, 80, QgsUnitTypes.LayoutMillimeters)); layout.addLayoutItem(legend)
    scale = QgsLayoutItemScaleBar(layout); scale.setLinkedMap(map_item); scale.setStyle("Single Box"); scale.setUnits(QgsUnitTypes.DistanceKilometers); scale.setNumberOfSegments(4); scale.setUnitsPerSegment(5); scale.setUnitLabel("km"); scale.applyDefaultSize(); scale.attemptMove(QgsLayoutPoint(14, 207, QgsUnitTypes.LayoutMillimeters)); layout.addLayoutItem(scale)
    _label(layout, "N\n▲", 250, 207, 12, 20, 12, True)
    _box(layout, "Global spatial statistic", "Primary k=8 Global Moran's I = 0.046612\nExpected I = -0.000420 | z = 4.821064\n999 permutations | p = 0.001", 10, 224, 98, 37)
    _box(layout, "Local Moran interpretation", "Exploratory screening patterns are not statistically significant after FDR correction. No confirmed local hotspots are shown or inferred.", 112, 224, 98, 37)
    _box(layout, "Uncertainty and decision use", "Absence of GPS evidence is not evidence of operational failure. It may reflect logger non-use or failure, signal loss, attribution uncertainty, timing or identifier mismatch, or processing limitations. Prioritize rapid verification before assuming non-performance.", 214, 224, 196, 37)
    _label(layout, "Projection: EPSG:32632 (WGS 84 / UTM zone 32N) | Sources: GPS tracks, settlement masterlist, e-tally, inaccessible-settlement list, and administrative boundaries.\nMethod: baseline_30m settlement attribution; symbols show observed evidence, not proof of service delivery or non-performance.\nCartographer: Yahaya Umar Muhammad | Date: 30 July 2026", 10, 266, 400, 13, 6.5)

    if not project.write(str(qgz_path)): raise RuntimeError("Unable to save QGIS project.")
    # QGIS's Windows PDF exporter is unstable in this installation. The same
    # evidence layers are rendered by generate_a3_pdf.py after this project is saved.
    _strip_password(qgz_path)
    return qgz_path, pdf_path


if __name__ == "__main__":
    app = QgsApplication([], False); app.initQgis()
    try:
        qgz, pdf = build_map(); print(qgz); print(pdf)
    finally:
        app.exitQgis()
