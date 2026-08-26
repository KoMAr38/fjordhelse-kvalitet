# Datakvalitet i et fagsystem

Porteføljeprosjekt. Viser hva bestemte registreringsfeil gjør med et
styringstall, og hvordan feilene kan måles, testes og korrigeres.

**Dataene er syntetiske.** Det finnes ingen pasienter bak radene. De genereres
av `src/generer_data.py` med fast seed, og feilene er lagt inn med vilje og i
kjent omfang. Fasiten ligger i `data/raw/fasit.json`.

Dette er ikke en produksjonsløsning.

---

## Funnet

Andelen fristbrudd i det fiktive foretaket Fjordhelse HF:

| | Andel fristbrudd |
|---|---|
| Slik fagsystemet rapporterer | **24,1 %** |
| Etter kvalitetssikring | **14,4 %** |

Forskjellen er 42 489 henvisninger. 40 886 av dem skyldes at «ventetid slutt»
aldri ble registrert — pasienten er behandlet, men systemet regner forløpet
som ventende. De øvrige 1 603 er duplikater fra overføring mellom enheter.

Men hovedfunnet er ikke totalen. Det er rangeringen:

| Enhet | Rapportert | Rang | Kvalitetssikret | Rang |
|---|---|---|---|---|
| TSB | 32,6 % | 1 (verst) | 14,2 % | 8 (best) |
| BUP | 30,7 % | 2 | 14,3 % | 6 |
| Rehabilitering | 26,0 % | 3 | 14,3 % | 6 |
| DPS | 23,5 % | 4 | 14,5 % | 1 |
| Medisin | 21,9 % | 5 | 14,4 % | 4 |
| Ortopedi | 21,2 % | 6 | 14,4 % | 4 |
| Kirurgi | 20,7 % | 7 | 14,5 % | 1 |
| Onkologi | 16,5 % | 8 (best) | 14,5 % | 1 |

Rangeringen snur nesten fullstendig. Enheten som ser verst ut er den som
registrerer dårligst, ikke den som behandler seinest. Etter kvalitetssikring
ligger alle åtte enhetene mellom 14,2 og 14,5 prosent — forskjellen mellom dem
var aldri en forskjell i tjeneste.

**Konsekvensen for styring:** et fristbruddtall brukt til å sammenligne enheter
måler registreringspraksis minst like mye som ventetid. Brukes det uten
kvalitetssikring, belønnes de enhetene som registrerer godt og straffes de som
har minst merkantil støtte.

---

## De seks innebygde feilene

| # | Feil | Kvalitetsdimensjon | Hvorfor den er realistisk |
|---|---|---|---|
| 1 | «Prioritet» utfylt med forvalgt verdi | Validitet | Feltet er obligatorisk, så det er alltid utfylt. Obligatorisk er ikke det samme som vurdert. |
| 2 | Diagnosekode skifter betydning | Entydighet | R51 betyr noe annet etter revisjonen 01.07.2024. Koden alene er ikke en nøkkel. |
| 3 | Duplikat ved overføring | Unikhet | Henvisningen opprettes på nytt i mottakende enhet uten at den første lukkes. |
| 4 | «Ventetid slutt» ikke registrert | Kompletthet | Gir fristbrudd som ikke er reelle. Dokumentert problem i norsk spesialisthelsetjeneste. |
| 5 | Registreringer klumper seg i romjula | Aktualitet | Tidspunktet sier mer om rapporteringsfrister enn om forløpet. |
| 6 | Enhet skifter navn ved omorganisering | Konsistens | Koden er uendret. Kobling på navn mister radene. |

Feilratene skaleres per enhet. En liten enhet med lite merkantil støtte
registrerer dårligere enn en enhet med tett forløpsoppfølging. Det er den
antakelsen som gjør at rangeringen snur.

---

## Arkitektur

```
src/generer_data.py      syntetisk datasett, fast seed, fasit.json med sha256
        |
data/raw/henvisninger.csv        426 484 rader
        |
src/last_inn_raa.py      inn i DuckDB som raa.henvisninger
        |
dbt/                     staging -> intermediate -> marts
   staging               typing og opprydding, ingen forretningslogikk
   intermediate          ett flagg per kjent feil, én rad per henvisning
   marts                 fakta med fristbrudd regnet på to måter
        |
src/eksporter_mart.py    Parquet + CSV til Power BI
        |
powerbi/                 .pbip, semantisk modell som TMDL
```

Skillet mellom `intermediate` og `marts` er bevisst: først slås det fast hva
som er galt med raden, deretter regnes tallet to ganger. Blandes stegene, kan
ingen etterprøve forskjellen.

## Testene

41 tester kjører ved hvert bygg. Fire av dem er skrevet for dette prosjektet:

- `assert_kvalitetssikring_reduserer_fristbrudd` — kvalitetssikring skal aldri
  gi flere fristbrudd enn rårapporteringen. Slår den ut, har logikken snudd
  fortegn.
- `assert_ventetid_ikke_negativ` — ventetid slutt kan ikke ligge før
  vurderingsdatoen.
- `assert_ett_forlop_per_pasient_og_frist` — etter deduplisering skal én
  pasient ha ett forløp per mottaksdato og frist.
- `assert_alle_enheter_har_data` — en enhet som forsvinner ut av fakta er
  nesten alltid en brutt nøkkel, ikke en enhet uten aktivitet.

`assert_ventetid_ikke_negativ` fant en reell feil i generatoren under
utviklingen: forløp som ikke rakk å bli ferdig innen uttrekksdatoen fikk
sluttdatoen klippet til periodeslutt, noe som ga negativ ventetid for
henvisninger mottatt i desember. Feilen er rettet ved at slike forløp regnes
som pågående. Testen er beholdt.

---

## Slik kjører du det

```
1_INSTALLER.bat     installerer Python-pakker, 1-3 minutter
2_BYGG.bat          genererer data, bygger modellen, kjører 41 tester
```

Forventet på slutten:

```
Done. PASS=41 WARN=0 ERROR=0 SKIP=0
```

Rådatafila på 100 MB ligger ikke i repoet. Den gjenskapes eksakt av
generatoren, og `fasit.json` inneholder sha256 slik at gjenskapingen kan
kontrolleres.

---

## Kilder og lisens

Ingen eksterne data. Alt er generert.

Feilmønstrene er ikke oppdiktet. Ikke-reelle fristbrudd som følge av manglende
registrering av «ventetid slutt», og variasjon i registreringspraksis mellom
helseforetak, er begge dokumenterte problemstillinger i norsk
spesialisthelsetjeneste.

## Forbehold

Dette er et porteføljeprosjekt på syntetiske data, ikke en produksjonsløsning
og ikke en analyse av et virkelig foretak. Tallene er konstruert for å vise en
mekanisme, ikke for å beskrive en tilstand.
