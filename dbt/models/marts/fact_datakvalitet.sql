-- Datakvalitet aggregert per enhet og måned, langt format.
--
-- Langt framfor bredt fordi antallet kvalitetsdimensjoner kommer til å vokse.
-- Et bredt format tvinger en modellendring hver gang noen finner en ny feil;
-- et langt format tar den nye feilen som en ny rad.

with f as (

    select * from {{ ref('fact_henvisning') }}

),

grunnlag as (

    select
        enhet_kode,
        maned,
        count(*)                            as antall_rader,
        sum(flagg_prioritet_default)        as n_prioritet_default,
        sum(flagg_enhetsnavn_avvik)         as n_enhetsnavn_avvik,
        sum(flagg_duplikat)                 as n_duplikat,
        sum(flagg_manglende_slutt)          as n_manglende_slutt,
        sum(flagg_arsskifte)                as n_arsskifte,
        sum(flagg_kode_tvetydig)            as n_kode_tvetydig
    from f
    group by 1, 2

),

langt as (

    select enhet_kode, maned, 'Validitet'      as dimensjon,
           'Prioritet satt til forvalgt verdi' as maling,
           n_prioritet_default as antall_avvik, antall_rader
    from grunnlag
    union all
    select enhet_kode, maned, 'Konsistens',
           'Enhetsnavn avviker fra kodeverk',
           n_enhetsnavn_avvik, antall_rader from grunnlag
    union all
    select enhet_kode, maned, 'Unikhet',
           'Duplikat ved overføring mellom enheter',
           n_duplikat, antall_rader from grunnlag
    union all
    select enhet_kode, maned, 'Kompletthet',
           'Ventetid slutt ikke registrert',
           n_manglende_slutt, antall_rader from grunnlag
    union all
    select enhet_kode, maned, 'Aktualitet',
           'Registrert i årsskiftevinduet 27.-31.12',
           n_arsskifte, antall_rader from grunnlag
    union all
    select enhet_kode, maned, 'Entydighet',
           'Diagnosekode med skiftende betydning',
           n_kode_tvetydig, antall_rader from grunnlag

)

select
    enhet_kode,
    maned,
    dimensjon,
    maling,
    antall_avvik,
    antall_rader,
    round(100.0 * antall_avvik / nullif(antall_rader, 0), 2) as andel_avvik_pst
from langt
