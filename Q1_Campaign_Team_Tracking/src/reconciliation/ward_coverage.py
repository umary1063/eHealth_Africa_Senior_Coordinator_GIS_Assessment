"""Build ward coverage from baseline settlement reconciliation."""
from src.ingestion.reference_db_connection import reference_cursor
def build_ward_coverage(connection):
 with reference_cursor(connection) as cur:
  cur.execute('DELETE FROM processed.ward_coverage_reconciliation')
  cur.execute("""INSERT INTO processed.ward_coverage_reconciliation SELECT ward_code,MAX(ward_name),MAX(lga_name),COUNT(*),COUNT(*) FILTER(WHERE gps_visit_status='visited'),COUNT(*) FILTER(WHERE gps_visit_status='ambiguous'),COUNT(*) FILTER(WHERE gps_visit_status='unvisited'),COUNT(*) FILTER(WHERE etally_report_status='reported'),ROUND(100.0*COUNT(*) FILTER(WHERE gps_visit_status='visited')/COUNT(*),2),ROUND(100.0*COUNT(*) FILTER(WHERE etally_report_status='reported')/COUNT(*),2),ROUND(ABS(100.0*COUNT(*) FILTER(WHERE gps_visit_status='visited')/COUNT(*)-100.0*COUNT(*) FILTER(WHERE etally_report_status='reported')/COUNT(*)),2),CASE WHEN COUNT(*) FILTER(WHERE discrepancy_flag)>0 THEN 'requires review' ELSE 'aligned' END,SUM(reported_doses_all_linked),SUM(reported_doses_plausible_only) FROM processed.settlement_coverage_reconciliation GROUP BY ward_code""")
