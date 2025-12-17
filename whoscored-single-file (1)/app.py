
import re
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

st.set_page_config(page_title="WhoScored | Análisis de Partido", layout="wide")

# ---------- SIDEBAR ----------
st.sidebar.title("WhoScored – Partido")
url = st.sidebar.text_input("URL del partido WhoScored")
home_color = st.sidebar.color_picker("Color equipo local", "#E65B51")
away_color = st.sidebar.color_picker("Color equipo visitante", "#3D7CCB")
st.sidebar.markdown("Created by John Triguero")

# ---------- FUNCTIONS ----------
def get_match_id(url):
    m = re.search(r"Matches/(\d+)", url)
    return m.group(1) if m else None

def load_match_data(url):
    match_id = get_match_id(url)
    api_url = f"https://www.whoscored.com/matchCentre/getMatchCentreData?matchId={match_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(api_url, headers=headers)
    r.raise_for_status()
    return r.json()

def plot_passing_network(events, team_id, color):
    passes = [e for e in events if e["type"]["displayName"]=="Pass" and e["teamId"]==team_id]
    df = pd.DataFrame([{"p":e["playerId"],"r":e.get("receiverId"),"x":e["x"],"y":e["y"]}
                       for e in passes if "receiverId" in e])
    if df.empty:
        return None
    avg = df.groupby("p")[["x","y"]].mean()
    links = Counter(zip(df["p"],df["r"]))

    fig, ax = plt.subplots(figsize=(6,4))
    for (p1,p2),v in links.items():
        if p1 in avg.index and p2 in avg.index:
            ax.plot([avg.loc[p1,"x"],avg.loc[p2,"x"]],
                    [avg.loc[p1,"y"],avg.loc[p2,"y"]],
                    color=color, alpha=0.5)
    ax.scatter(avg["x"],avg["y"],s=300,color=color)
    ax.text(0.99,0.01,"Created by John Triguero",
            transform=ax.transAxes,ha="right",va="bottom",fontsize=8,color="gray")
    ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
    return fig

# ---------- MAIN ----------
st.title("WhoScored – Análisis de Partido")

if not url:
    st.info("Introduce la URL de WhoScored")
    st.stop()

data = load_match_data(url)
events = data["events"]
home = data["home"]
away = data["away"]

st.subheader(f"{home['name']} vs {away['name']}")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Red de pases – Local")
    fig = plot_passing_network(events, home["teamId"], home_color)
    if fig:
        st.pyplot(fig)

with col2:
    st.markdown("### Red de pases – Visitante")
    fig = plot_passing_network(events, away["teamId"], away_color)
    if fig:
        st.pyplot(fig)
