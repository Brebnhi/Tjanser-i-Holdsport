# Tjanser – Aalborg Volley

Laver automatisk tjans-kalendere til Holdsport ud fra tjanselisten og de
officielle kampprogrammer fra `resultater.volleyball.dk`.

En kamp og dens tjans hænger sammen på **kampnummeret**. Flytter turnerings-
systemet en kamp, flytter tjansen med — først her, natten efter i Holdsport.

## Hvad der bliver bygget

| Fil | Indhold |
|---|---|
| `docs/feeds/<HOLD>-<ANTAL>pers.ics` | Ét kalender-feed pr. hold og deltagerantal |
| `docs/index.html` | Live-overblik: dækning, huller, flyttede kampe, feed-adresser |
| `docs/status.json` | Rådata bag siden |

Ét feed pr. **hold og antal**, fordi Holdsport sætter maks. antal deltagere
én gang pr. import. Et hold med både liga- og divisionstjanser får derfor to feeds.

## Reglerne

- **Volleyligaen-hjemmekampe (D1):** 6 personer, mødetid 45 minutter før kampstart.
  Kommentar: 2 boldlangere, 2 sekretærer, 1 til entré, 1 til speaker.
- **Alle øvrige kampe:** 4 personer, mødetid 30 minutter før kampstart.
  Kommentar: 2 boldlangere og 2 sekretærer — ingen entré eller speaker.
- **Stævner** (U17, Kids/Teen, U15, NM i Mix) kommer ikke med, da de ikke findes
  i kampprogrammet. Sæt `INCLUDE_STAEVNER=1`, hvis de alligevel skal med.

## Opsætning (én gang)

1. **Opret repoet.** Nyt, *offentligt* repo på GitHub — Holdsport skal kunne
   hente feed'ene, og GitHub Pages er kun gratis på offentlige repos.
   Læg alle filer herfra ind (træk og slip virker fint i browseren).
2. **Slå Pages til.** Settings → Pages → Source: **GitHub Actions**.
3. **Kør robotten første gang.** Actions → *Opdater tjans-kalendere* → Run workflow.
4. **Hent adresserne.** Åbn `https://<dit-brugernavn>.github.io/<repo>/` — alle
   feed-adresser står i tabellen "Feeds til Holdsport".
5. **Importér i Holdsport,** ét feed ad gangen på det hold der har tjansen:
   Kalender → Mere → Importer kampprogram → *Importer kampprogram fra et WebCal feed*.
   Indsæt adressen, sæt **maks. antal deltagere** til tallet i tabellen, og slå
   **automatisk opdatering én gang i døgnet** til.

Robotten kører derefter hver nat af sig selv.

## Når tjanselisten skal rettes

Rediger `data/tjanser.csv` direkte på GitHub og gem — så kører robotten igen.

Vil du hellere blive i Google Sheets: Filer → Del → Udgiv på nettet → vælg arket
og formatet **CSV**. Læg adressen ind under Settings → Secrets and variables →
Actions → Variables som `SHEET_CSV_URL`. Så læses listen derfra i stedet, og
regnearket er facit.

## Overvågning

Efter hver kørsel sammenholdes kampprogrammet med tjanselisten. Er der en
hjemmekamp uden hold på tjans — eller en tjans hvis kamp er forsvundet —
oprettes ét GitHub-issue med listen, og GitHub sender en mail. Issuet lukker
sig selv, når hullet er lukket. Er alt dækket, sker der ingenting.

## Kolonner i `data/tjanser.csv`

`kampnr, runde, dag, dato (DD-MM-ÅÅ), tid (TT:MM), raekke, pulje, hjemmehold,
udehold, spillested, antal, tjans`

`tjans` er holdet der **har** tjansen. `antal` styrer både maks. deltagere og
mødetiden (6 → 45 min før, ellers 30 min før). Rækker uden `kampnr` regnes som
stævner.
