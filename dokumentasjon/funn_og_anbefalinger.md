# Fristbruddtallet før og etter kvalitetssikring

Notat til ledergruppen. Fjordhelse HF, syntetisk datagrunnlag.

---

## Sammendrag

Foretaket rapporterer 24,1 prosent fristbrudd. Etter kvalitetssikring av
datagrunnlaget er tallet 14,4 prosent. Forskjellen er 42 489 henvisninger.

Avviket skyldes ikke feil i beregningen, men i registreringen. Av de 42 489
radene skyldes 40 886 at «ventetid slutt» ikke er registrert — pasienten er
behandlet, men forløpet står åpent i fagsystemet og telles som ventende. De
resterende 1 603 er duplikater fra overføring mellom enheter.

Vi anbefaler ikke å endre det rapporterte tallet. Vi anbefaler å slutte å
bruke det til å sammenligne enheter, inntil registreringspraksisen er jevnet ut.

---

## 1. Rangering av enheter måler registrering, ikke tjeneste

Enhetene rangert på rapportert fristbrudd, og på det samme tallet etter
kvalitetssikring:

| Enhet | Rapportert | Kvalitetssikret | Endring i rang |
|---|---|---|---|
| TSB | 32,6 % | 14,2 % | fra verst til best |
| BUP | 30,7 % | 14,3 % | fra nest verst til delt sjette |
| Rehabilitering | 26,0 % | 14,3 % | ned fire plasser |
| DPS | 23,5 % | 14,5 % | opp tre plasser |
| Medisin | 21,9 % | 14,4 % | uendret |
| Ortopedi | 21,2 % | 14,4 % | opp to plasser |
| Kirurgi | 20,7 % | 14,5 % | opp seks plasser |
| Onkologi | 16,5 % | 14,5 % | fra best til delt best |

Etter kvalitetssikring ligger samtlige åtte enheter mellom 14,2 og 14,5
prosent. Spredningen på ni prosentpoeng i det rapporterte tallet forsvinner
helt. Den var en forskjell i hvor godt enhetene fører journal.

De to enhetene som ser verst ut, TSB og BUP, er de minste og har minst
merkantil støtte. Det er en forutsigbar sammenheng, og den betyr at et
usikret fristbruddtall systematisk peker på feil enheter.

## 2. Manglende sluttregistrering er den dominerende feilkilden

74 514 henvisninger mangler «ventetid slutt». For 67 165 av dem finnes det et
registreringstidspunkt før fristen, altså har noen vært i kontakt med forløpet
i tide. Av disse ville 40 886 ellers blitt talt som fristbrudd.

Andelen manglende sluttregistrering varierer fra 8,1 prosent i Onkologi til
27,8 prosent i TSB. Onkologi har tett forløpsoppfølging med faste kontrollpunkter;
det er den mest sannsynlige forklaringen på forskjellen, og den er en
organisatorisk forskjell, ikke en klinisk.

## 3. Obligatoriske felt gir ikke vurderte felt

«Prioritet» er obligatorisk i fagsystemet og derfor alltid utfylt. I 28,6 prosent
av radene står den forvalgte verdien «Ikke vurdert».

Et felt som ikke kan stå tomt, blir fylt ut. Det betyr ikke at noen har tatt
stilling. Rapporter som filtrerer på prioritet, filtrerer i praksis på hvem som
gadd å endre standardverdien.

## 4. Duplikater ved overføring

6 494 henvisninger finnes to ganger fordi de er opprettet på nytt i mottakende
enhet uten at den opprinnelige er lukket. Ortopedisk avdeling har over tre
ganger så mange som snittet, i tråd med at avdelingen har mest overføring til
og fra andre enheter.

Duplikatene blåser opp både teller og nevner, men ikke likt, og påvirker derfor
andelen.

## 5. Kodeverk og enhetsnavn

Diagnosekoden R51 skiftet betydning ved revisjonen 01.07.2024. En analyse som
grupperer på kode alene, slår sammen to ulike tilstander. Modellen løser dette
med gyldighetsperiode per kode.

Avdeling for fysikalsk medisin skiftet navn 01.01.2024 uten at koden endret
seg. En kobling på navn ville mistet halvannet års data for enheten. Modellen
kobler på kode og henter kanonisk navn fra en vedlikeholdt oppslagstabell.

---

## Anbefalinger

**1. Skill rapportert og kvalitetssikret tall i all styringsrapportering.**
Ikke erstatt det ene med det andre. Vis begge, med differansen. Differansen er
selv et styringstall: den måler registreringskvalitet.

**2. Slutt å rangere enheter på usikret fristbrudd.**
Inntil spredningen i manglende sluttregistrering er vesentlig mindre enn
dagens 20 prosentpoeng mellom beste og dårligste enhet, sier rangeringen mer om merkantile ressurser enn om ventetid.

**3. Sett opp ukentlig uttrekk av åpne forløp med passert frist.**
Listen sendes til enheten, ikke til ledelsen. De fleste radene lukkes ved at
noen bekrefter en behandling som allerede har funnet sted. Dette er den
billigste enkelttiltaket på lista.

**4. Fjern forvalgt verdi på obligatoriske vurderingsfelt.**
Et felt uten forvalgt verdi tvinger fram et valg. Er det ikke mulig i
fagsystemet, må «Ikke vurdert» rapporteres som egen kategori og ikke slås
sammen med de reelle verdiene.

**5. Bygg deduplisering inn i datagrunnlaget, ikke i hver rapport.**
Regelen for hvilken av to overførte henvisninger som gjelder, skal stå ett
sted. Står den i hver enkelt rapport, kommer de til å svare ulikt.

**6. Legg gyldighetsperiode på kodeverk i modellen.**
Ikke fordi R51 er viktig, men fordi neste revisjon kommer, og modellen bør tåle
den uten at gamle analyser stille blir feil.

---

## Metode

Datagrunnlaget er syntetisk, generert med fast seed og kjente feilrater.
Fasiten ligger i `data/raw/fasit.json`. Analysen gjenskaper feilratene fra
dataene alene, uten å lese fasiten — det er kontrollen på at metoden virker.

Kvalitetssikret fristbrudd er definert slik: duplikater fjernes, og en
henvisning uten registrert sluttdato regnes ikke som fristbrudd dersom det
finnes et registreringstidspunkt før fristen. Definisjonen er konservativ. Den
fanger ikke forløp der all registrering uteble.
