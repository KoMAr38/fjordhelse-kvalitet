select
    diagnose_kode,
    cast(gyldig_fra as date) as gyldig_fra,
    cast(gyldig_til as date) as gyldig_til,
    diagnose_tekst,
    kodeverk_versjon,
    diagnose_kode || ' (' || kodeverk_versjon || ')' as diagnose_visning
from {{ ref('diagnose_kodeverk') }}
