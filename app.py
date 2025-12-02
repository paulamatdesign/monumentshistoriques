import streamlit as st
import pandas as pd
import altair as alt
import unicodedata
import re

st.set_page_config("Répartition des Monuments Historiques", initial_sidebar_state="collapsed")

st.title("Répartition des Monuments Historiques")

st.caption("Réusage des [données OpenData](https://www.data.gouv.fr/datasets/immeubles-proteges-au-titre-des-monuments-historiques-2/reuses_and_dataservices)")

df = pd.read_csv("data/merimee.csv", sep="|")

st.write(df)

def normalize_text(text):

    text = text.replace("-", " ")
    text = text.replace(",", " ")
    text = re.sub(r"\(.*?\)", "", text)
    
    text_no_accents = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    return text_no_accents.lower().strip().capitalize()
    
def no_comma(text):
    if ";" in text:
        return text.split(";", 1)[0]
    else:
        return text
    
def extraire_prec_siecle(text):
    mot = "siecle"
    if mot in text:
        idx = text.rfind(mot)  # dernière occurrence

        if idx == -1:
            return None  # "siècle" absent

        # indice de début des 4 caractères précédents
        start = max(0, idx - 4)
        return text[start:idx]
    else:
        return text
    
def first_word(texte):
    return texte.strip().split()[0] if texte.strip() else ""
    
def regroup(text):
    terms = [
        "Neolithique",
        "Paleolithique",
        "Gallo-romain",
        "Moyen Age",
        "Age du bronze",
        "Age du fer"
    ]
    
    for term in terms:
        if term in text:
            return term
        elif term.lower() in text:
            return term
        
    text = text.replace("3 000 av. j. c. a 900 apr. j. c.", "Age du bronze")
    text = text.replace("Moyen Age", "Moyen age")

    return text  # only happens if none matched

df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].astype(str)
df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].apply(normalize_text)
df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].apply(no_comma)
df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].apply(extraire_prec_siecle)
df["Siecle_de_la_campagne_principale_de_construction"] = df["Siecle_de_la_campagne_principale_de_construction"].apply(regroup)

df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].astype(str)
df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].apply(no_comma)
df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].apply(first_word)
df["Denomination_de_l_edifice"] = df["Denomination_de_l_edifice"].apply(normalize_text)

st.write(df["Siecle_de_la_campagne_principale_de_construction"].unique())

plot = alt.Chart(df).mark_circle().encode(
    y='Denomination_de_l_edifice:N',
    x='Siecle_de_la_campagne_principale_de_construction:N',
    size='count():Q',
    color=alt.Color("count():Q").scale(scheme="blueorange").legend(None)
)

st.altair_chart(plot)