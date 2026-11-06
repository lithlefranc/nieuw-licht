# Nieuw licht op de nachtelijke stad – code bij het proefschrift

Deze repository bevat de code voor de dataverwerking, -analyse, figuren en tabellen van het proefschrift
*Nieuw licht op de nachtelijke stad. Een digitale geschiedenis van de straat (Antwerpen, 1876–1939)*
(Lith Lefranc, Universiteit Antwerpen).

## Data
De ruwe data staan op Zenodo: https://zenodo.org/records/12805005. Voor de data waar de notebooks op draaien kan je contact opnemen met Lith.Lefranc@UAntwerpen.be. De notebooks verwachten de data in de map `data/`
(zie hieronder).

De modellen waarmee de data verwerkt werden:
- HTR-modellen (ARletta): https://doi.org/10.5281/zenodo.11191457
- NER-modellen: https://huggingface.co/emanjavacas/robbert-2023-dutch-large-adapted-coarse.ner
  (NER-coarse) en https://huggingface.co/emanjavacas/robbert-2023-dutch-large-adapted-fine.ner
  (NER-fine)

## Installatie
De notebooks zijn gedraaid met Python 3.11. De gebruikte pakketversies staan in `requirements.txt`


## Structuur
De notebooks zijn geordend per hoofdstuk uit het proefschrift.

| Notebook | Afbeeldingen en tabellen |
|---|---|
| `src/H2/2.1_wijkgrenzen` | fig 2.1 |
| `src/H2/2.1_processen_verbaal` | fig 2.2 |
| `src/H2/2.1_vervolgingen_per_wijk` | fig 2.3 |
| `src/H3/3.6_data_in_vogelvlucht` | fig 3.5, 3.6, 3.8, 3.9; tab 3.6 |
| `src/H3/3.6_taalherkenning` | fig 3.7 |
| `src/H4/4.1_ner_scores` | fig 4.1 |
| `src/H5/5.1-5.3_gender_leeftijd_klasse` | fig 5.1–5.6; tab 5.1, 5.2 |
| `src/H6/6.1_kaarten_straatverlichting` | fig 6.6, 6.7 |
| `src/H6/6.1-6.3_lantaarns_en_nachtaandeel` | fig 6.3, 6.10 |
| `src/H6/6.2_nachtaandeel_per_wijk` | fig 6.11, 6.12 |
| `src/H6/6.2_infrastructuurmodel` | fig 6.13, 6.14 |
| `src/H6/6.3_twee_straten` | fig 6.15–6.17 |
| `src/H7/7.1_gender_leeftijd_zichtbaarheid` | fig 7.1; tab 7.1 |
| `src/H7/7.1b_aandeel_vrouwen_spline` | fig 7.2 |
| `src/H7/7.2_grenzen_nachtelijke_beweging` | fig 7.3, 7.4 |
| `src/H7/7.3_gender_en_sociabiliteit` | tab 7.2, 7.3 |
| `src/H7/7.4_nachtelijke_praktijken` | fig 7.6 |
| `src/H8/8.1_wordembeddings/8.1_semantisch_veld` | fig 8.2–8.4; tab 8.1, 8.2; annex 10.3 |
| `src/H8/8.1_wordembeddings/8.1_variantenlijst` | (variantenlijst) |
| `src/H8/8.2_evaluatie_taalmodel` | tab 8.3 |
| `src/H8/8.2_vergelijking_taalmodel_variantenlijst` | (cijfers in §8.2) |
| `src/H8/8.2_zeroshottoets/8.2_zeroshottoets` | tab 8.2 |
| `src/H8/8.3_tijdstip_geluidsoverlast` | fig 8.5–8.7 |
| `src/H8/8.3_geluidsoverlast_per_wijk_en_pv` | fig 8.8, 8.9 |
| `src/H8/8.3_sociale_verschillen` | fig 8.10 |
| `src/H8/8.4_geluidspraktijken` | fig 8.11, 8.12 |
| `src/H8/8.5_klankruimtes` | fig 8.13 |

## Volgorde van de verwerking
1. **NER-nabewerking** (`src/H4/4.1_ner_nabewerking/`, Python-scripts 1–4): van getagde XML naar tabellen.
2. **Normalisering en disambiguering** (`src/H4/4.2_normalisering/`): datum, tijd, leeftijd,
   beroep (HISCO/HISCLASS), geboorteplaats, locatie en gender. `TIME_ASTRO-correct` voegt de
   astronomische tijd toe (dag, schemering, nacht).
3. **Analyses en figuren**: de notebooks per hoofdstuk hierboven.

De notebooks in stap 1 en 2 en `src/H8/8.1_wordembeddings/8.1_variantenlijst.ipynb` maken data
aan; ze zijn niet opnieuw gedraaid voor deze versie. Let op: `8.1_variantenlijst` overschrijft de
variantenlijst die `8.2_vergelijking_taalmodel_variantenlijst` gebruikt.

In `src/H8/8.2_zeroshottoets` staan de cellen met de taalmodelruns in commentaar. De notebook vertrekt van de
bewaarde modelantwoorden in `data/H8/llm/zeroshottoets/`. 
