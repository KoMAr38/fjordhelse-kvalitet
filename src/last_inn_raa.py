"""Laster den genererte CSV-fila inn i DuckDB som kilde for dbt."""
from pathlib import Path
import duckdb

ROT = Path(__file__).resolve().parent.parent
CSV = ROT / "data" / "raw" / "henvisninger.csv"
DB = ROT / "data" / "fjordhelse.duckdb"

def main() -> None:
    if not CSV.exists():
        raise SystemExit(f"Fant ikke {CSV}. Kjoer src/generer_data.py foerst.")
    con = duckdb.connect(str(DB))
    con.execute("create schema if not exists raa")
    con.execute(
        "create or replace table raa.henvisninger as "
        f"select * from read_csv_auto('{CSV.as_posix()}', header=true, all_varchar=true)"
    )
    n = con.execute("select count(*) from raa.henvisninger").fetchone()[0]
    print(f"Lastet {n:,} rader inn i raa.henvisninger".replace(",", " "))
    con.close()

if __name__ == "__main__":
    main()
