-- Ventetid slutt kan ikke ligge før vurderingsdatoen.
select henvisning_id, vurdert_dato, ventetid_slutt, ventetid_dager
from {{ ref('fact_henvisning') }}
where ventetid_dager < 0
