-- Rått uttrekk gjort typet og ryddet. Ingen forretningslogikk her.
--
-- Det eneste som skjer av betydning: tom streng i «ventetid_slutt» blir NULL.
-- Fagsystemet eksporterer et uregistrert felt som tom streng, og en tom
-- streng er ikke det samme som ukjent. Blandes de to, forsvinner hele
-- problemstillingen prosjektet handler om.

with kilde as (

    select * from {{ source('raa', 'henvisninger') }}

),

typet as (

    select
        trim(henvisning_id)                             as henvisning_id,
        trim(pasient_pseudonym)                         as pasient_pseudonym,
        upper(trim(enhet_kode))                         as enhet_kode,
        trim(enhet_navn)                                as enhet_navn_som_registrert,
        trim(tjenesteomrade)                            as tjenesteomrade_som_registrert,

        cast(henvisning_mottatt as date)                as henvisning_mottatt,
        cast(vurdert_dato as date)                      as vurdert_dato,
        cast(frist_dato as date)                        as frist_dato,

        case
            when ventetid_slutt is null then null
            when trim(ventetid_slutt) = '' then null
            else cast(ventetid_slutt as date)
        end                                             as ventetid_slutt,

        trim(prioritet)                                 as prioritet,
        trim(omsorgsniva)                               as omsorgsniva,
        upper(trim(diagnose_kode))                      as diagnose_kode,
        trim(diagnose_tekst)                            as diagnose_tekst_som_registrert,
        trim(registrert_av)                             as registrert_av,
        cast(registrert_tidspunkt as timestamp)         as registrert_tidspunkt,
        trim(kilde_system)                              as kilde_system

    from kilde

)

select * from typet
