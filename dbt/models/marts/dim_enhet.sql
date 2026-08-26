select
    enhet_kode,
    enhet_navn_kanonisk as enhet_navn,
    kortnavn,
    tjenesteomrade,
    cast(er_psykisk_helse as boolean) as er_psykisk_helse
from {{ ref('enhet_oppslag') }}
