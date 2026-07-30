"""Idempotent pg8000 e-tally ingestion."""
from pathlib import Path
import pandas as pd
from src.ingestion.reference_db_connection import get_reference_connection, reference_cursor
REQUIRED={'campaign_date','team_id','settlement_id','ward_code','lga_name','target_population_under5','doses_administered'}
def ingest_etally(path: Path):
 e=pd.read_csv(path); missing=REQUIRED-set(e.columns)
 if missing: raise ValueError(f'Missing e-tally columns: {sorted(missing)}')
 if e.duplicated(['campaign_date','team_id','settlement_id']).any(): raise ValueError('Duplicate e-tally reporting keys found.')
 c=get_reference_connection()
 try:
  with reference_cursor(c) as cur:
   cur.execute(Path(__file__).resolve().parents[2].joinpath('database','coverage_reconciliation.sql').read_text())
   cur.execute('SELECT settlement_id FROM raw.settlements'); linked={r[0] for r in cur.fetchall()}
   rows=[(r.campaign_date,r.team_id,r.settlement_id,r.ward_code,None if pd.isna(r.lga_name) else r.lga_name,r.target_population_under5,r.doses_administered,i) for i,r in enumerate(e.itertuples(index=False),2)]
   matched=[r for r in rows if r[2] in linked]; unmatched=[r for r in rows if r[2] not in linked]
   cur.executemany("""INSERT INTO raw.etally_records (campaign_date,team_id,settlement_id,ward_code,lga_name,target_population_under5,doses_administered,source_file,source_row_number) VALUES (%s,%s,%s,%s,%s,%s,%s,'etally_daily.csv',%s) ON CONFLICT (source_file,source_row_number) DO UPDATE SET campaign_date=EXCLUDED.campaign_date,team_id=EXCLUDED.team_id,settlement_id=EXCLUDED.settlement_id,ward_code=EXCLUDED.ward_code,lga_name=EXCLUDED.lga_name,target_population_under5=EXCLUDED.target_population_under5,doses_administered=EXCLUDED.doses_administered""",matched)
   cur.executemany("""INSERT INTO raw.etally_records_unmatched (campaign_date,team_id,settlement_id,ward_code,lga_name,target_population_under5,doses_administered,source_file,source_row_number) VALUES (%s,%s,%s,%s,%s,%s,%s,'etally_daily.csv',%s) ON CONFLICT (source_file,source_row_number) DO UPDATE SET campaign_date=EXCLUDED.campaign_date,team_id=EXCLUDED.team_id,settlement_id=EXCLUDED.settlement_id,ward_code=EXCLUDED.ward_code,lga_name=EXCLUDED.lga_name,target_population_under5=EXCLUDED.target_population_under5,doses_administered=EXCLUDED.doses_administered""",unmatched)
  c.commit()
 except Exception: c.rollback(); raise
 finally: c.close()
 return len(e)
