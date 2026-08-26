-- Faktatabell på henvisningsnivå, med fristbrudd regnet på to måter.
--
--   fristbrudd_rapportert    slik fagsystemet ville rapportert det:
--                            en henvisning uten registrert «ventetid slutt»
--                            regnes som fortsatt ventende, og passert frist
--                            gir fristbrudd.
--
--   fristbrudd_kvalitetssikret
--                            duplikater er fjernet, og rader der pasienten
--                            beviselig er behandlet innen fristen, men der
--                            sluttregistreringen mangler, regnes ikke som
--                            fristbrudd. Beviset er registrert_tidspunkt:
--                            en registrering finnes, altså har noen vært i
--                            kontakt med forløpet.
--
-- Forskjellen mellom de to er hele poenget med prosjektet.

{% set idag = var('dagens_dato') %}

with f as (

    select * from {{ ref('int_henvisning_flagget') }}

),

beregnet as (

    select
        henvisning_id,
        pasient_pseudonym,
        enhet_kode,
        kortnavn,
        enhet_navn_kanonisk,
        tjenesteomrade,
        er_psykisk_helse,

        henvisning_mottatt,
        vurdert_dato,
        frist_dato,
        ventetid_slutt,
        date_trunc('month', henvisning_mottatt)             as maned,

        prioritet,
        omsorgsniva,
        diagnose_kode,
        diagnose_tekst_gjeldende,
        kodeverk_versjon,
        registrert_av,
        registrert_tidspunkt,

        flagg_prioritet_default,
        flagg_enhetsnavn_avvik,
        flagg_duplikat,
        flagg_manglende_slutt,
        flagg_arsskifte,
        flagg_kode_tvetydig,

        -- Faktisk ventetid der den finnes.
        case
            when ventetid_slutt is not null
            then date_diff('day', vurdert_dato, ventetid_slutt)
        end as ventetid_dager,

        -- Slik systemet rapporterer.
        case
            when ventetid_slutt is not null and ventetid_slutt > frist_dato then 1
            when ventetid_slutt is null and cast('{{ idag }}' as date) > frist_dato then 1
            else 0
        end as fristbrudd_rapportert,

        -- Etter kvalitetssikring.
        case
            when flagg_duplikat = 1 then 0
            when ventetid_slutt is not null and ventetid_slutt > frist_dato then 1
            when ventetid_slutt is null
                 and cast(registrert_tidspunkt as date) <= frist_dato then 0
            when ventetid_slutt is null
                 and cast(registrert_tidspunkt as date) > frist_dato then 1
            else 0
        end as fristbrudd_kvalitetssikret,

        -- Teller kun rader som skal med i nevneren etter kvalitetssikring.
        case when flagg_duplikat = 1 then 0 else 1 end as teller_i_nevner

    from f

)

select * from beregnet
