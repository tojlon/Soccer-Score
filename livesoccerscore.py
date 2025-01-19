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
        if st.sidebar.checkbox('debug'):
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
                columns=["Équipe Maison", "Équipe Extérieure", "Score Maison", "Score Extérieur", "Date", "Statut"]
            )
             # Diviser la colonne Date en deux colonnes : Date et Heure
            df[['Date', 'Heure']] = df['Date'].str.split('T', expand=True)
            df['Heure'] = df['Heure'].str.replace('Z', '')
            st.dataframe(df)
        else:
            st.info("Aucun match à afficher.")
    else:
        st.info("Aucun match à afficher ou problème avec les données reçues.")

# Titre de l'application
st.title("Suivi des Résultats des Matchs de Football")

# Menu de navigation entre les ligues
page = st.sidebar.radio(
    "Choisir la compétition",
    ["Ligue 1", "Premier League", "Bundesliga"]
)

# Mapping des ligues avec leurs identifiants de compétition
competitions = {
    "Ligue 1": 2015,          # ID de la Ligue 1
    "Premier League": 2021,   # ID de la Premier League
    "Bundesliga": 2002        # ID de la Bundesliga
}

# Obtenez les matchs pour la ligue choisie
st.header(f"Matchs de la {page}")
competition_id = competitions[page]
matches = get_matches(competition_id)
if matches:
    display_matches(matches)