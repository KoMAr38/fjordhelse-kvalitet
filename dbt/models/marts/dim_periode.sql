-- Månedstabell over hele analyseperioden. Bygges fra en datoserie framfor
-- fra fakta, slik at måneder uten henvisninger fortsatt finnes i modellen.
with dager as (
    select unnest(generate_series(
        date '2022-01-01',
        date '2025-12-01',
        interval 1 month
    )) as maned_dato
)
select
    cast(maned_dato as date)                                     as maned,
    extract(year from maned_dato)                                as aar,
    extract(month from maned_dato)                               as maned_nr,
    strftime(maned_dato, '%Y-%m')                                as maned_etikett,
    cast(extract(year from maned_dato) * 100
       + extract(month from maned_dato) as integer)              as sortering,
    case
        when extract(month from maned_dato) <= 4 then 1
        when extract(month from maned_dato) <= 8 then 2
        else 3
    end                                                          as tertial
from dager
