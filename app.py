import streamlit as st
import pandas as pd
import altair as alt
import unicodedata
import re

st.set_page_config("Répartition des Monuments Historiques", initial_sidebar_state="collapsed")

st.title("Répartition des Monuments Historiques")

st.caption("Réusage des [données OpenData](https://www.data.gouv.fr/datasets/immeubles-proteges-au-titre-des-monuments-historiques-2/reuses_and_dataservices)")

raw = pd.read_csv("data/merimee.csv", sep="|")

df = pd.DataFrame()

keep = [
    "Autre_appellation_de_l_edifice",
    "Commune_forme_index",
    "Commune_forme_editoriale",
    "Denomination_de_l_edifice",
    "Siecle_de_la_campagne_principale_de_construction",
    "Description_de_l_edifice",
    "Domaine",
    "Departement_format_numerique",
    "Departement_en_lettres",
    "Historique",
    "Liens_externes",
    "Region"
]

df = raw[keep].copy()

st.write(raw)

import re
import unicodedata

def norm_siecle(x: str) -> str:
    if not isinstance(x, str):
        x = str(x)

    # 1) Remove commas, hyphens, parentheses content
    x = x.replace("-", " ")
    x = x.replace(",", " ")
    x = re.sub(r"\(.*?\)", "", x)

    # 2) Remove accents
    x = ''.join(
        c for c in unicodedata.normalize('NFD', x)
        if unicodedata.category(c) != 'Mn'
    )

    # 3) Normalize case and strip
    x = x.lower().strip()

    # 4) Cut at first ";" if present
    if ";" in x:
        x = x.split(";", 1)[0].strip()

    # 5) If "siecle" is present, keep the 4 chars before last occurrence
    mot = "siecle"
    if mot in x:
        idx = x.rfind(mot)
        # idx can't be -1 here, mot in x already checked
        start = max(0, idx - 4)
        x = x[start:idx].strip()

    # 6) Map to known periods if possible
    terms = [
        "neolithique",
        "paleolithique",
        "gallo romain",
        "moyen age",
        "age du bronze",
        "age du fer",
    ]

    for term in terms:
        if term in x:
            x = term
            break

    # 7) Specific replacements (now everything is lowercase, no accents)
    x = x.replace("3 000 av. j. c. a 900 apr. j. c.", "age du bronze")
    x = x.replace("moyen age", "moyen age")  # already that, but you can adjust if needed

    # 8) Final formatting: capitalize first letter
    x = x.strip().capitalize()

    return x

def norm_denom(x):
    # 1) If ";" present, keep only before first ";"
    if ";" in x:
        x = x.split(";", 1)[0]

    # 2) Keep only the first word
    x = x.strip().split()[0] if x.strip() else ""

    # 3) Replace "-" and "," with spaces
    x = x.replace("-", " ")
    x = x.replace(",", " ")

    # 4) Remove parentheses and their content
    x = re.sub(r"\(.*?\)", "", x)

    # 5) Remove accents
    x = ''.join(
        c for c in unicodedata.normalize('NFD', x)
        if unicodedata.category(c) != 'Mn'
    )

    # 6) Normalize case: lower then capitalize first letter
    x = x.lower().strip().capitalize()

    return x

df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].astype(str)
df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].apply(norm_siecle)

df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].astype(str)
df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].apply(norm_denom)

st.write(df["Siecle_de_la_campagne_principale_de_construction"].unique())

plot = alt.Chart(df).mark_circle().encode(
    y='Denomination_de_l_edifice:N',
    x='Siecle_de_la_campagne_principale_de_construction:N',
    size='count():Q',
    color=alt.Color("count():Q").scale(scheme="blueorange").legend(None)
)

st.altair_chart(plot)
