"""
Eksporterer mart-tabellene slik Power BI kan lese dem uten DuckDB installert.

Faktatabellen skrives som Parquet, ikke CSV. 426 000 rader som CSV blir rundt
100 MB og er for stort til å ligge i et Git-repo på en fornuftig måte. Som
Parquet blir den en brøkdel, den er typet, og Power Query leser den direkte.
Dimensjonene skrives som CSV fordi de er små og fordi det er en fordel at de
kan leses i nettleseren rett fra GitHub.
"""
from pathlib import Path
import duckdb

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "data" / "mart"

SOM_PARQUET = ["fact_henvisning"]
SOM_CSV = ["fact_datakvalitet", "dim_enhet", "dim_periode", "dim_diagnose"]


def main() -> None:
    UT.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(ROT / "data" / "fjordhelse.duckdb"), read_only=True)

    for t in SOM_PARQUET:
        sti = UT / f"{t}.parquet"
        con.execute(f"copy (select * from {t}) to '{sti}' (format parquet, compression zstd)")
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"{t + '.parquet':<28}{n:>10,} rader{sti.stat().st_size / 1e6:>9.1f} MB".replace(",", " "))

    for t in SOM_CSV:
        sti = UT / f"{t}.csv"
        con.execute(f"copy (select * from {t}) to '{sti}' (header, delimiter ',')")
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"{t + '.csv':<28}{n:>10,} rader{sti.stat().st_size / 1e6:>9.1f} MB".replace(",", " "))

    con.close()


if __name__ == "__main__":
    main()
