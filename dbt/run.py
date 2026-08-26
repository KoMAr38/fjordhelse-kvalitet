"""dbt-kjører. dbt har ingen __main__.py, så `python -m dbt` virker ikke.
Denne wrapperen kaller dbtRunner direkte og setter riktig exit-kode, slik at
.bat-fila kan stoppe på feil i stedet for å melde suksess uansett."""
import os
import sys
from pathlib import Path

os.environ.setdefault("DBT_PROFILES_DIR", str(Path(__file__).resolve().parent))

from dbt.cli.main import dbtRunner  # noqa: E402

res = dbtRunner().invoke(sys.argv[1:] or ["build"])
sys.exit(0 if res.success else 1)
