
import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium

def scarica_attivita_osm(località, filtro=None):
    query = f"""
    [out:json][timeout:25];
    area["name"="{località}"]->.searchArea;
    (
      node["shop"](area.searchArea);
      node["amenity"](area.searchArea);
    );
    out body;
    """
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})
    data = response.json()

    attività = []
    for elem in data["elements"]:
        tags = elem.get("tags", {})
        if "name" in tags:
            tipo = tags.get("shop") or tags.get("amenity") or "Altro"
            attività.append({
                "nome": tags["name"],
                "tipo": tipo,
                "lat": elem.get("lat"),
                "lon": elem.get("lon"),
            })

    df = pd.DataFrame(attività)
    if filtro and filtro != "Tutti":
        df = df[df["tipo"] == filtro]
    return df

# Interfaccia Streamlit
st.set_page_config(page_title="Attività Commerciali a Ragusa", layout="wide")
st.title("📍 Mappa delle Attività Commerciali - Ragusa")

località = st.text_input("Inserisci il nome della città", "Ragusa")
df = scarica_attivita_osm(località)

tipi = ["Tutti"] + sorted(df["tipo"].unique().tolist())
filtro = st.selectbox("Filtra per tipo di attività", tipi)

df_filtrato = df if filtro == "Tutti" else df[df["tipo"] == filtro]

st.markdown(f"**{len(df_filtrato)} attività trovate.**")

# Mostra tabella
st.dataframe(df_filtrato, use_container_width=True)

# Esportazione CSV
st.download_button(
    label="📁 Scarica CSV",
    data=df_filtrato.to_csv(index=False),
    file_name=f'attività_{località.lower()}.csv',
    mime='text/csv'
)

# Mappa
if not df_filtrato.empty:
    mappa = folium.Map(location=[df_filtrato["lat"].mean(), df_filtrato["lon"].mean()], zoom_start=13)
    for _, row in df_filtrato.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"{row['nome']} ({row['tipo']})",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mappa)
    st_folium(mappa, width=900, height=600)
else:
    st.warning("Nessuna attività trovata con questo filtro.")
