-- Kvalitetssikringen skal aldri gi flere fristbrudd enn rårapporteringen.
-- Slår denne ut, har logikken i fact_henvisning snudd fortegn et sted.
select
    sum(fristbrudd_rapportert)      as raa,
    sum(fristbrudd_kvalitetssikret) as kvalitetssikret
from {{ ref('fact_henvisning') }}
having sum(fristbrudd_kvalitetssikret) > sum(fristbrudd_rapportert)
