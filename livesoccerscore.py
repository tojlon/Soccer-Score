import streamlit as st
import requests
import pandas as pd

# Configure page layout
st.set_page_config(layout="wide")

# Définir votre clé d'accès API
try:
    API_KEY = st.secrets["API_KEY"]
except KeyError:
    st.error("API key is missing. Please check your secrets configuration.")
    st.stop()  # Arrêtez l'application pour qu'elle ne continue pas sans une clé API valide
BASE_URL = "https://api.football-data.org/v4/matches"


# Fonction pour obtenir les résultats des matchs d'une ligue spécifique
def get_matches(competition_id):
    headers = {"X-Auth-Token": API_KEY}
    params = {
        "competitions": competition_id,  # ID de la compétition
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    
    # # Affichage de la réponse de l'API pour déboguer
    # st.write(f"URL de la requête: {response.url}")  # Affiche l'URL de la requête API
    # st.write(f"Code de réponse: {response.status_code}")  # Affiche le code de statut HTTP
    
    if response.status_code == 200:
        data = response.json()
        # Vérification du contenu renvoyé
        # st.write("Réponse de l'API:",data)
        return data
    else:
        st.error(f"Erreur lors de la récupération des données: {response.status_code}")
        return None

from datetime import datetime
import pytz

# Fonction pour afficher les matchs sous forme de tableau
def display_matches(matches):
    if matches and "matches" in matches:
        if st.sidebar.checkbox('Click to activate debug mode'):
            st.write("Structure des données de l'API :")
            st.write(matches)  # Affiche l'objet complet renvoyé par l'API
        
        match_data = []
        for match in matches["matches"]:
            try:
                home_team = match["homeTeam"]["name"]
                away_team = match["awayTeam"]["name"]
                score_home = match["score"]["fullTime"]["home"]
                score_away = match["score"]["fullTime"]["away"]
                date = match["utcDate"]
                status = match["status"]
                referees = match["referees"][0]["name"] if match["referees"] else "N/A"
                referees_nationality = match["referees"][0]["nationality"] if match["referees"] else "N/A"
                match_data.append([home_team, away_team, score_home, score_away, date, status, referees, referees_nationality])
            except KeyError as e:
                st.error(f"Clé manquante : {e} dans le match {match}")
        
        if match_data:
            df = pd.DataFrame(
                match_data,
                columns=["Home Team", "Away Team", "Home Score", "Away Score", "Date (UTC)", "Status", "Referee", "Ref Nationality"]
            )
            
            # Convertir UTC en heure de Paris
            paris = pytz.timezone('Europe/Paris')  # Fuseau horaire Paris
            df['Date (UTC)'] = pd.to_datetime(df['Date (UTC)'])

            # Vérifiez si la date et l'heure sont sensibles au fuseau horaire
            if df['Date (UTC)'].dt.tz is None:
                df['Date (UTC)'] = df['Date (UTC)'].dt.tz_localize('UTC')  # Localize if not already aware
            
            # Convertir le fuseau horaire en heure de Paris
            df['Date (Paris)'] = df['Date (UTC)'].dt.tz_convert(paris)
            
            # Extraire l'heure en heure de Paris
            df['Time (Paris)'] = df['Date (Paris)'].dt.strftime('%H:%M:%S')

            # Supprimer les colonnes inutiles (Date et Date (Paris))
            df.drop(columns=['Date (UTC)', 'Date (Paris)'], inplace=True)

            # Rearrange columns to move 'Time (Paris)' to the first position
            df = df[['Time (Paris)', 'Home Team', 'Away Team', 'Home Score', 'Away Score', 'Status', 'Referee', 'Ref Nationality']]

            # Afficher le tableau avec uniquement les informations pertinentes
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No game today")
    else:
        st.info("No game today or error in fetching data")

# Titre de l'application
st.title("Games of the Day")

# Local paths to league logos
league_logos = {
    "Ligue 1 McDonald's": "logos/Logo_Ligue1.png",
    "Premier League": "logos/Logo_PL.png",
    "Bundesliga": "logos/Logo_Bundesliga.png",
    "LaLiga": "logos/Logo_LaLiga.png",
    "Champions League": "logos/Logo_CL.png",
    "Europa League": "logos/Logo_EL.png",
}

# Menu de navigation entre les ligues
page = st.sidebar.radio(
    "Select League",
    ["Ligue 1 McDonald's", "Premier League", "Bundesliga", "LaLiga", "Champions League", "Europa League"]
)
competitions = {
    "Ligue 1 McDonald's": 2015, # ID de la Ligue 1
    "Premier League": 2021,     # ID de la Premier League
    "Bundesliga": 2002,         # ID de la Bundesliga
    "LaLiga": 2014,             # ID de La Liga
    "Champions League": 2001,   # ID de la Champions League
    "Europa League": 2148       # ID de l'Europa League
}

# Display the logo and name of the selected league at the top of the page
st.image(league_logos[page], width=150)  # Adjust the width for better display

# Obtenez les matchs pour la ligue choisie
competition_id = competitions[page]
matches = get_matches(competition_id)
if matches:
    display_matches(matches)