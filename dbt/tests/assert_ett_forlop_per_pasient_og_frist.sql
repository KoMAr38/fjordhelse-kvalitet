-- Etter deduplisering skal én pasient ha ett forløp per mottaksdato og frist.
select pasient_pseudonym, henvisning_mottatt, frist_dato, count(*) as antall
from {{ ref('fact_henvisning') }}
where teller_i_nevner = 1
group by 1, 2, 3
having count(*) > 1
