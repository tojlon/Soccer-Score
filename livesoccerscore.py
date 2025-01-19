import streamlit as st
import requests
import pandas as pd

# Définir votre clé d'accès API
API_KEY = "5ff8d97bc26743f48288a4b88bf86e9c"
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
                
                # Utiliser 'home' et 'away' à l'intérieur de 'fullTime'
                score_home = match["score"]["fullTime"]["home"]
                score_away = match["score"]["fullTime"]["away"]
                
                date = match["utcDate"]
                status = match["status"]
                
                match_data.append([home_team, away_team, score_home, score_away, date, status])
            except KeyError as e:
                st.error(f"Clé manquante : {e} dans le match {match}")
        
        if match_data:
            df = pd.DataFrame(
                match_data,
                columns=["Home Team", "Away Team", "Home Score", "Away Score", "Date", "Finished/In Play"]
            )
             # Diviser la colonne Date en deux colonnes : Date et Heure
            df[['Date', 'Heure']] = df['Date'].str.split('T', expand=True)
            df['Heure'] = df['Heure'].str.replace('Z', '')

             # Appliquer un style pour changer la couleur de fond des lignes "IN_PLAY"
            def highlight_in_play(row):
                if row['Finished/In Play'] == 'IN_PLAY':
                    return ['background-color: lightgreen'] * len(row)
                return [''] * len(row)

            styled_df = df.style.apply(highlight_in_play, axis=1)
            st.write(styled_df.to_html(), unsafe_allow_html=True)

        else:
            st.info("No game today")
    else:
        st.info("No game today or error in fetching data")

# Titre de l'application
st.title("Games of the Day")

# Menu de navigation entre les ligues
page = st.sidebar.radio(
    "Choose your league",
    ["Ligue 1", "Premier League", "Bundesliga"]
)

# Mapping des ligues avec leurs identifiants de compétition
competitions = {
    "Ligue 1": 2015,          # ID de la Ligue 1
    "Premier League": 2021,   # ID de la Premier League
    "Bundesliga": 2002        # ID de la Bundesliga
}

# Obtenez les matchs pour la ligue choisie
st.header(f"{page}")
competition_id = competitions[page]
matches = get_matches(competition_id)
if matches:
    display_matches(matches)