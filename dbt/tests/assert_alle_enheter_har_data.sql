-- Hver enhet i oppslagstabellen skal finnes igjen i fakta. En enhet som
-- forsvinner ut er nesten alltid en nøkkel som er brutt, ikke en enhet
-- uten aktivitet.
select e.enhet_kode
from {{ ref('dim_enhet') }} e
left join {{ ref('fact_henvisning') }} f on e.enhet_kode = f.enhet_kode
group by e.enhet_kode
having count(f.henvisning_id) = 0
