-- Ett flagg per kjent registreringsfeil, én rad per henvisning.
--
-- Flaggene er bevisst holdt adskilt fra beregningen av fristbrudd. Først slår
-- vi fast hva som er galt med raden, deretter regner vi to ganger: én gang
-- slik fagsystemet ville rapportert, og én gang etter kvalitetssikring.
-- Blandes de to stegene, kan ingen etterprøve forskjellen.

with h as (

    select * from {{ ref('stg_henvisning') }}

),

enhet as (

    select * from {{ ref('enhet_oppslag') }}

),

kodeverk as (

    select
        diagnose_kode,
        cast(gyldig_fra as date) as gyldig_fra,
        cast(gyldig_til as date) as gyldig_til,
        diagnose_tekst,
        kodeverk_versjon
    from {{ ref('diagnose_kodeverk') }}

),

-- Duplikat ved overføring: samme pasient, samme mottaksdato, samme frist,
-- men opprettet på nytt i mottakende enhet. Den først registrerte beholdes.
duplikat as (

    select
        henvisning_id,
        row_number() over (
            partition by pasient_pseudonym, henvisning_mottatt, frist_dato
            order by registrert_tidspunkt, henvisning_id
        ) as forlopsnummer
    from h

),

koblet as (

    select
        h.*,

        e.enhet_navn_kanonisk,
        e.kortnavn,
        e.tjenesteomrade,
        e.er_psykisk_helse,

        k.diagnose_tekst    as diagnose_tekst_gjeldende,
        k.kodeverk_versjon,

        d.forlopsnummer,

        -- 1. Obligatorisk felt fylt med forvalgt verdi.
        case when h.prioritet = 'Ikke vurdert' then 1 else 0 end
            as flagg_prioritet_default,

        -- 2. Navnet i kilden avviker fra kanonisk navn for koden.
        case when h.enhet_navn_som_registrert <> e.enhet_navn_kanonisk then 1 else 0 end
            as flagg_enhetsnavn_avvik,

        -- 3. Duplikat ved overføring mellom enheter.
        case when d.forlopsnummer > 1 then 1 else 0 end
            as flagg_duplikat,

        -- 4. Ventetid slutt mangler.
        case when h.ventetid_slutt is null then 1 else 0 end
            as flagg_manglende_slutt,

        -- 5. Registrert i årsskiftevinduet 27.-31. desember.
        case
            when extract(month from h.henvisning_mottatt) = 12
             and extract(day from h.henvisning_mottatt) >= 27
            then 1 else 0
        end as flagg_arsskifte,

        -- 6. Koden har skiftet betydning i løpet av perioden.
        case when h.diagnose_kode = 'R51' then 1 else 0 end
            as flagg_kode_tvetydig

    from h
    left join enhet    as e on h.enhet_kode = e.enhet_kode
    left join kodeverk as k
           on h.diagnose_kode = k.diagnose_kode
          and h.henvisning_mottatt between k.gyldig_fra and k.gyldig_til
    left join duplikat as d on h.henvisning_id = d.henvisning_id

)

select * from koblet
