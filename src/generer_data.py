"""
Genererer et syntetisk henvisningsdatasett for Fjordhelse HF.

Datasettet er IKKE ekte. Det finnes ingen pasienter bak disse radene.
Formålet er å vise hva bestemte registreringsfeil gjør med et styringstall,
og feilene er derfor lagt inn med vilje og i kjent omfang.

Seed er fast. Kjører du skriptet to ganger, får du identiske filer.
Det er et krav: en analyse som ikke kan reproduseres, kan ikke etterprøves.

De seks innebygde feilene, med fasit i FEILRATER nedenfor:

  1. obligatorisk_default   Feltet «prioritet» er obligatorisk i fagsystemet,
                            og derfor alltid utfylt. En andel er utfylt med
                            systemets forvalgte verdi, ikke med et reelt valg.
  2. kodeverk_skifte        Diagnosekoden R51 betyr noe annet etter revisjonen
                            01.07.2024 enn før. Samme kode, to betydninger.
  3. duplikat_overforing    Ved overføring mellom enheter opprettes henvisningen
                            på nytt i mottakende enhet uten at den første lukkes.
  4. manglende_slutt        «ventetid slutt» er ikke registrert. Pasienten er
                            behandlet, men systemet regner henvisningen som
                            ventende, og den teller som fristbrudd.
  5. arsskifte_klump        Registreringer hoper seg opp de siste dagene i
                            desember. Tidspunktet for registrering sier da mer
                            om rapporteringsfrister enn om pasientforløpet.
  6. enhet_omdopt           En enhet skifter navn ved omorganisering. Koden er
                            uendret. Kobling på navn mister radene.

Kjøres med:  python src/generer_data.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20260907
ANTALL_HENVISNINGER = 420_000
START = date(2022, 1, 1)
SLUTT = date(2025, 12, 31)

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "data" / "raw"

# Fasit. Rapporten skal komme fram til omtrent disse tallene på egen hånd.
FEILRATER = {
    "obligatorisk_default": 0.22,
    "kodeverk_skifte": 0.04,
    "duplikat_overforing": 0.015,
    "manglende_slutt": 0.08,
    "arsskifte_klump": 0.06,
    "enhet_omdopt": 1.00,  # gjelder én enhet, hele perioden etter omorg.
}

# Registreringspraksis varierer mellom enheter. Det er den viktigste
# antakelsen i hele datasettet: en enhet kan se dårlig ut på fristbrudd fordi
# den registrerer dårlig, ikke fordi den behandler seint. Multiplikatorene
# under skrur på feilraten per enhet, og gjør at rangeringen av enheter
# endrer seg når tallet kvalitetssikres.
#
#   BUP og TSB   små enheter, lite merkantil støtte, svak sluttregistrering
#   ORT          mye overføring til og fra andre enheter, flest duplikater
#   ONK          tett forløpsoppfølging, best registrering i foretaket
#   REH          omorganisert underveis, alt henger etter i den perioden
ENHET_FAKTOR = {
    "KIR": {"manglende_slutt": 0.9, "obligatorisk_default": 1.0, "duplikat_overforing": 1.0},
    "MED": {"manglende_slutt": 1.1, "obligatorisk_default": 1.2, "duplikat_overforing": 0.9},
    "ORT": {"manglende_slutt": 1.0, "obligatorisk_default": 0.8, "duplikat_overforing": 3.2},
    "ONK": {"manglende_slutt": 0.25, "obligatorisk_default": 0.3, "duplikat_overforing": 0.4},
    "BUP": {"manglende_slutt": 2.6, "obligatorisk_default": 1.9, "duplikat_overforing": 0.7},
    "DPS": {"manglende_slutt": 1.4, "obligatorisk_default": 1.5, "duplikat_overforing": 0.8},
    "TSB": {"manglende_slutt": 2.9, "obligatorisk_default": 2.1, "duplikat_overforing": 1.1},
    "REH": {"manglende_slutt": 1.8, "obligatorisk_default": 1.6, "duplikat_overforing": 1.4},
}

# Enhetene i det fiktive foretaket. «gyldig_fra» styrer omdøpingen.
ENHETER = [
    ("KIR", "Kirurgisk avdeling", "Somatikk", None),
    ("MED", "Medisinsk avdeling", "Somatikk", None),
    ("ORT", "Ortopedisk avdeling", "Somatikk", None),
    ("ONK", "Onkologisk avdeling", "Somatikk", None),
    ("BUP", "Barne- og ungdomspsykiatrisk poliklinikk", "PHBU", None),
    ("DPS", "Distriktspsykiatrisk senter Fjordbyen", "PHV", None),
    ("TSB", "Rus- og avhengighetspoliklinikk", "TSB", None),
    # Feil 6: samme kode, nytt navn fra 01.01.2024.
    ("REH", "Avdeling for fysikalsk medisin", "Somatikk", date(2024, 1, 1)),
]
REH_NYTT_NAVN = "Avdeling for rehabilitering og fysikalsk medisin"

PRIORITETER = ["Rettighetspasient", "Uten rett til helsehjelp"]
PRIORITET_DEFAULT = "Ikke vurdert"  # feltets forvalgte verdi i fagsystemet

OMSORGSNIVA = ["Poliklinikk", "Dagbehandling", "Døgnbehandling"]

# Feil 2: R51 skifter betydning ved revisjon av kodeverket.
KODEVERK_SKIFTE_DATO = date(2024, 7, 1)
DIAGNOSER = [
    ("K80", "Gallestein"),
    ("M17", "Artrose i kne"),
    ("I25", "Kronisk iskemisk hjertesykdom"),
    ("F32", "Depressiv episode"),
    ("F41", "Angstlidelse"),
    ("F19", "Psykiske lidelser ved blandet rusmiddelbruk"),
    ("C50", "Ondartet svulst i bryst"),
    ("R51", None),  # betydning avhenger av dato, settes under
]
R51_FOR = "Hodepine"
R51_ETTER = "Hodepine, uspesifisert"

REGISTRANTER = [f"BRUKER{n:03d}" for n in range(1, 61)]


def virkedager(fra: date, antall: int) -> date:
    """Legger til virkedager, slik et pasientforløp faktisk beveger seg."""
    d = fra
    lagt_til = 0
    while lagt_til < antall:
        d += timedelta(days=1)
        if d.weekday() < 5:
            lagt_til += 1
    return d


def pseudonym(n: int) -> str:
    """Stabil, ikke-reverserbar id. Understreker at raden ikke peker på noen."""
    return hashlib.sha256(f"fjordhelse-{SEED}-{n}".encode()).hexdigest()[:12]


def generer() -> tuple[list[dict], dict]:
    rng = random.Random(SEED)
    UT.mkdir(parents=True, exist_ok=True)

    dager = (SLUTT - START).days
    rader: list[dict] = []
    teller = {k: 0 for k in FEILRATER}

    for i in range(1, ANTALL_HENVISNINGER + 1):
        kode, navn, omrade, omdopt_fra = rng.choice(ENHETER)
        faktor = ENHET_FAKTOR[kode]

        # Grunnfordeling over perioden, deretter feil 5 på toppen.
        mottatt = START + timedelta(days=rng.randint(0, dager))
        klumpet = False
        if rng.random() < FEILRATER["arsskifte_klump"]:
            aar = rng.choice([2022, 2023, 2024, 2025])
            mottatt = date(aar, 12, rng.randint(27, 31))
            klumpet = True
            teller["arsskifte_klump"] += 1

        # Feil 6: navnet følger datoen, koden gjør ikke.
        if omdopt_fra is not None and mottatt >= omdopt_fra:
            navn_paa_raden = REH_NYTT_NAVN
        else:
            navn_paa_raden = navn

        vurdert = virkedager(mottatt, rng.randint(1, 12))
        frist_dager = rng.choice([28, 42, 56, 84, 112])
        frist = virkedager(vurdert, frist_dager)

        # Feil 1: obligatorisk felt, men forvalgt verdi.
        if rng.random() < FEILRATER["obligatorisk_default"] * faktor["obligatorisk_default"]:
            prioritet = PRIORITET_DEFAULT
            teller["obligatorisk_default"] += 1
        else:
            prioritet = rng.choices(PRIORITETER, weights=[0.78, 0.22])[0]

        # Reelt behandlingstidspunkt. De fleste innenfor frist.
        faktisk_ventet = max(1, int(rng.gauss(frist_dager * 0.72, frist_dager * 0.30)))
        slutt_reell = virkedager(vurdert, faktisk_ventet)

        # Forløp som ikke rekker å bli ferdig innen uttrekksdatoen er reelt
        # pågående. Det er ikke en registreringsfeil, og datoen skal derfor
        # ikke klippes til periodeslutt — det ville gitt negativ ventetid.
        paagaaende = slutt_reell > SLUTT

        # Feil 4: registreringen av «ventetid slutt» uteblir.
        if paagaaende:
            ventetid_slutt = None
        elif rng.random() < FEILRATER["manglende_slutt"] * faktor["manglende_slutt"]:
            ventetid_slutt = None
            teller["manglende_slutt"] += 1
        else:
            ventetid_slutt = slutt_reell

        diag_kode, diag_tekst = rng.choice(DIAGNOSER)
        if diag_kode == "R51":
            diag_tekst = R51_ETTER if mottatt >= KODEVERK_SKIFTE_DATO else R51_FOR
            teller["kodeverk_skifte"] += 1

        # Registreringstidspunktet finnes selv om sluttdatoen mangler.
        # Det er nettopp derfor det kan brukes som bevis på at noen har
        # vært i kontakt med forløpet.
        registrert_dato = vurdert if paagaaende else slutt_reell
        registrert = datetime.combine(
            registrert_dato, datetime.min.time()
        ) + timedelta(hours=rng.randint(7, 20), minutes=rng.randint(0, 59))

        rad = {
            "henvisning_id": f"H{i:07d}",
            "pasient_pseudonym": pseudonym(rng.randint(1, 95_000)),
            "enhet_kode": kode,
            "enhet_navn": navn_paa_raden,
            "tjenesteomrade": omrade,
            "henvisning_mottatt": mottatt.isoformat(),
            "vurdert_dato": vurdert.isoformat(),
            "frist_dato": frist.isoformat(),
            "ventetid_slutt": ventetid_slutt.isoformat() if ventetid_slutt else "",
            "prioritet": prioritet,
            "omsorgsniva": rng.choice(OMSORGSNIVA),
            "diagnose_kode": diag_kode,
            "diagnose_tekst": diag_tekst,
            "registrert_av": rng.choice(REGISTRANTER),
            "registrert_tidspunkt": registrert.isoformat(sep=" ", timespec="seconds"),
            "kilde_system": "FJORD-EPJ",
        }
        rader.append(rad)

        # Feil 3: duplikat ved overføring. Ny id, samme innhold, annen enhet.
        if rng.random() < FEILRATER["duplikat_overforing"] * faktor["duplikat_overforing"]:
            ny_kode, ny_navn, ny_omrade, ny_omdopt = rng.choice(ENHETER)
            if ny_kode != kode:
                dup = dict(rad)
                dup["henvisning_id"] = f"H{i:07d}-K"
                dup["enhet_kode"] = ny_kode
                dup["enhet_navn"] = (
                    REH_NYTT_NAVN
                    if (ny_omdopt is not None and mottatt >= ny_omdopt)
                    else ny_navn
                )
                dup["tjenesteomrade"] = ny_omrade
                rader.append(dup)
                teller["duplikat_overforing"] += 1

    rng.shuffle(rader)

    fasit = {
        "generert": datetime.now().isoformat(timespec="seconds"),
        "seed": SEED,
        "antall_rader": len(rader),
        "antall_henvisninger_for_duplikater": ANTALL_HENVISNINGER,
        "periode": {"fra": START.isoformat(), "til": SLUTT.isoformat()},
        "innebygde_feil": {
            k: {"planlagt_rate": FEILRATER[k], "antall_rader": teller[k]}
            for k in FEILRATER
            if k != "enhet_omdopt"
        },
        "enhet_omdopt": {
            "enhet_kode": "REH",
            "navn_for": "Avdeling for fysikalsk medisin",
            "navn_etter": REH_NYTT_NAVN,
            "gyldig_fra": "2024-01-01",
        },
        "kodeverk_skifte": {
            "kode": "R51",
            "betydning_for": R51_FOR,
            "betydning_etter": R51_ETTER,
            "revisjonsdato": KODEVERK_SKIFTE_DATO.isoformat(),
        },
        "enhetsfaktor": ENHET_FAKTOR,
        "merknad": "Syntetiske data. Ingen reelle pasienter. Feilratene er grunnrater som skaleres per enhet med enhetsfaktor.",
    }
    return rader, fasit


def main() -> None:
    rader, fasit = generer()

    csv_sti = UT / "henvisninger.csv"
    with csv_sti.open("w", newline="", encoding="utf-8") as f:
        skriver = csv.DictWriter(f, fieldnames=list(rader[0].keys()))
        skriver.writeheader()
        skriver.writerows(rader)

    fasit["sha256"] = hashlib.sha256(csv_sti.read_bytes()).hexdigest()
    (UT / "fasit.json").write_text(
        json.dumps(fasit, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Skrev  {csv_sti}")
    print(f"Rader  {fasit['antall_rader']:,}".replace(",", " "))
    print(f"sha256 {fasit['sha256'][:16]}...")
    print()
    print("Innebygde feil:")
    for navn, d in fasit["innebygde_feil"].items():
        print(f"  {navn:<24} {d['antall_rader']:>8,} rader".replace(",", " "))
    print("  enhet_omdopt             REH bytter navn 01.01.2024")


if __name__ == "__main__":
    main()
