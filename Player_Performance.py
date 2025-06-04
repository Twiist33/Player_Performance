"""

Ceci est la page principale du projet, veuillez trouver ci dessous une brève présentation du projet, ainsi que le code associé.
This is the main page of the project, please find below a brief presentation of the project, as well as the associated code.

"""

# Import des librairies / Importing libraries
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_option_menu import option_menu
import os
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# Charger les  fichiers PDF présent à la fin de la page d'acceuil / Load PDF files at the end of the home page
with open("documentation/Documentation_Player_Performance_France.pdf", "rb") as file:
    doc = file.read()
with open("documentation/Documentation_Player_Performance_English.pdf", "rb") as file:
    doc_eng = file.read()
with open("CV/CV_FR_Romain_Traboul.pdf", "rb") as file:
    cv_data_fr = file.read()
with open("CV/CV_ENG_Romain_Traboul.pdf", "rb") as file:
    cv_data_eng = file.read()

# Affichage du titre et du logo de l'application web / Display of web application title and logo
st.set_page_config(page_title="Player Performance 24/25 ⚽ ", page_icon="📊", layout="centered")


# Langue dans session_state / Language in session_state
if "lang" not in st.session_state:
    st.session_state["lang"] = "Français"

lang = st.sidebar.selectbox(
    "Choisissez votre langue / Choose your language", 
    ["Français", "English"]
)
st.session_state["lang"] = lang

# Création du menu horizontal / Horizontal menu at the top of the page /
menu = option_menu(
    menu_title=None,
    options=["Accueil", "Joueur", "Duel","Classement"] if lang == "Français" else
            ["Home", "Player", "F2F","Ranking"],
    icons=["house", "person", "crosshair","trophy"],
    orientation="horizontal",
)

# Affichage de la valeur du joueur / Player value display
def format_market_value(eur):
    if pd.isna(eur):
        return "-"
    if eur >= 1_000_000:
        return f"{eur / 1_000_000:.1f}M €"
    elif eur >= 1_000:
        return f"{eur / 1_000:.0f}K €"
    else:
        return f"{int(eur)} €"

# Dictionnaire de traduction des postes de joueurs et de leur pays / Translation dictionary for player positions and his country
position_translation = {
    "Second Striker": "Second Attaquant",
    "Centre-Forward": "Attaquant-Centre",
    "Right-Back": "Défenseur Droit",
    "Left-Back": "Défenseur Gauche",
    "Right Winger": "Ailier Droit",
    "Left Winger": "Ailier Gauche",
    "Right Midfield": "Milieu Droit",
    "Left Midfield": "Milieu Gauche",
    "Attacking Midfield": "Milieu Attaquant",
    "Goalkeeper": "Gardien",
    "Defensive Midfield": "Milieu Défensif",
    "Central Midfield": "Milieu Central",
    "Centre-Back": "Défenseur Central"
}

country_translation = {
    "Germany": "Allemagne",
    "Spain": "Espagne",
    "Italy": "Italie",
    "England": "Angleterre",
    "Netherlands": "Pays-Bas",
    "Brazil": "Brésil",
    "Argentina": "Argentine",
    "Belgium": "Belgique",
    "Croatia": "Croatie",
    "Switzerland": "Suisse",
    "Senegal": "Sénégal",
    "Cameroon": "Cameroun",
    "Morocco": "Maroc",
    "Albania": "Albanie",
    "Algeria": "Algérie",
    "Andorra": "Andorre",
    "Armenia": "Armenie",
    "Australia": "Australie",
    "Austria": "Autriche",
    "Bosnia-Herzegovina" : "Bosnie-Herzegovine",
    "Cameroon": "Cameroun",
    "Cape Verde" : "Cap Vert",
    "Central African Republic" : "République centrafricaine",
    "Chile" : "Chili",
    "Colombia" : "Colombie",
    "Croatia" : "Croatie",
    "Czech Republic" : "Tchéquie",
    "Denmark" : "Danemark",
    "DR Congo": "République démocratique du Congo",
    "Ecuador": "Équateur",
    "Egypt" : "Égypte",
    "Equatorial Guinea" : "Guinée équatoriale",
    "Estonia" : "Estonie",
    "Finland": "Finlande",
    "French Guiana" : "Guyane française",
    "Georgia" : "Georgie",
    "Greece" : "Grèce",
    "Guinea" : "Guinée",
    "Guinea-Bissau" : "Guinée-Bissau",
    "Hungary" : "Hongrie",
    "Iceland" : "Islande",
    "Indonesia" : "Indonesie",
    "Ireland" : "Irlande",
    "Jamaica" : "Jamaïque",
    "Japan" : "Japon",
    "Jordan" : "Jordanie",
    "Korea, South" : "Corée du Sud",
    "Libya" : "Libye",
    "Lithuania" : "Lituanie",
    "Malta" : "Malte",
    "Mexico" : "Mexique",
    "New Zealand" : "Nouvelle-Zélande",
    "North Macedonia" : "Macédoine du Nord",
    "Northern Ireland" : "Irlande du Nord",
    "Norway" : "Norvège",
    "Peru" : "Pérou",
    "Poland" : "Pologne",
    "Romania" : "Roumanie",
    "Russia" : "Russie",
    "Scotland" : "Écosse",
    "Serbia" : "Serbie",
    "Slovakia" : "Slovaquie",
    "Slovenia" : "Slovénie",
    "Sweden" : "Suède",
    "Syria" : "Syrie",
    "The Gambia" : "Gambie",
    "Tunisia" : "Tunisie",
    "Türkiye" : "Turquie",
    "United States" : "États-Unis",
    "Uzbekistan" : "Ouzbékistan",
    "Wales" : "Pays de Galles",
    "Zambia" : "Zambie"

}

#  Catégorie des postes pour le radar / Position category for the radar plot
position_category = {
    "Goalkeeper": "Gardiens de but",
    "Centre-Back": "Défenseurs centraux",
    "Right-Back": "Défenseurs latéraux",
    "Left-Back": "Défenseurs latéraux",
    "Left Midfield": "Milieux de terrain",
    "Right Midfield": "Milieux de terrain",
    "Central Midfield": "Milieux de terrain",
    "Defensive Midfield": "Milieux de terrain",
    "Attacking Midfield": "Milieux offensifs / Ailiers",
    "Right Winger": "Milieux offensifs / Ailiers",
    "Left Winger": "Milieux offensifs / Ailiers",
    "Second Stricker": "Attaquants",
    "Centre-Forward": "Attaquants"
}

# Statistiques par catégorie pour le radar / Statistics by categorie for the radar plot
category_stats = {
    "Gardiens de but": ['GA_per90', 'Saves_per90', 'Save%', '/90', 'PSxG+/-', 'Err_per90', 'Cmp%', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%'],
    "Défenseurs centraux": [ 'Won%', 'Tkl+Int_per90', 'Tkl%', 'Clr_per90', 'Err_per90', 'Touches_per90', 'Cmp%', 'Sw_per90', 'PrgP_per90', 'PrgC_per90', 'Fls_per90', 'CrdY_per90'],
    "Défenseurs latéraux": ['Gls_per90', 'xG_per90', 'Ast_per90', 'xA_per90', 'PrgC_per90', 'PrgP_per90', 'PrgR_per90', 'Touches_per90', 'Crs_per90', 'Cmp%', 'Tkl+Int_per90', 'Tkl%', 'Err_per90', 'Clr_per90', 'Fls_per90', 'CrdY_per90'],
    "Milieux de terrain": ['Gls_per90', 'xG_per90', 'Ast_per90', 'xA_per90', 'PrgC_per90', 'PrgP_per90', 'PrgR_per90', 'Touches_per90', 'Cmp%', 'Won%', 'Tkl+Int_per90', 'Tkl%', 'Err_per90', 'CrdY_per90'],
    "Milieux offensifs / Ailiers": ['Gls_per90', 'xG_per90', 'Ast_per90', 'xA_per90', 'G/Sh', 'PrgC_per90', 'PrgP_per90', 'PrgR_per90', 'Touches_per90', 'Cmp%', '1/3_per90', 'Succ_per90', 'Succ%', 'Dis_per90', 'Fld_per90', 'Tkl+Int_per90'],
    "Attaquants": ['Gls_per90', 'xG_per90', 'Ast_per90', 'xA_per90', 'Sh_per90', 'G/Sh', 'Dist', 'PrgC_per90', 'PrgP_per90', 'PrgR_per90', 'Touches_per90' , 'Cmp%', '1/3_per90', 'Fld_per90', 'Tkl+Int_per90']
}

# Fonction pour trouver les joueurs similaires / Function to find similar players / 
def find_similar_players(selected_player_name, df, filter_type=None, top_n=5):
    # Informations du joueur sélectionné / Selected player information
    try:
        selected_player_row = df[df['name'] == selected_player_name].iloc[0]
    except IndexError:
        return pd.DataFrame()

    sub_position = selected_player_row['sub_position']
    age = selected_player_row['Age']
    competition = selected_player_row['current_club_domestic_competition_id']
    country = selected_player_row['country_of_citizenship']

    candidates_df = df[df['sub_position'] == sub_position].copy() # Candidats = tous les joueurs du même poste / Candidates = all players in the same position

    candidates_df = candidates_df[candidates_df['name'] != selected_player_name] # Retirer le joueur lui-même du calcul / Remove the player himself from the calculation

    # Colonnes de stats à comparer (sauf les informations de base) / Columns of statistics to compare (except base informations) 
    stats_cols = df.columns[14:]
    stats_df = candidates_df[stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Ajouter le joueur sélectionné au début pour calculer les similarités
    # Add the player selected at the beginning to calculate similarities

    selected_stats = df[df['name'] == selected_player_name][stats_cols].apply(pd.to_numeric, errors='coerce').fillna(0)
    full_stats = pd.concat([selected_stats, stats_df], ignore_index=True)

    # Normalisation / Standardisation
    scaler = StandardScaler()
    stats_scaled = scaler.fit_transform(full_stats)

    similarities = cosine_similarity(stats_scaled)[0][1:] # Calcul de similarité / Similarity calculation

    # Ajouter les scores à candidates_df / Add scores to candidates_df
    candidates_df = candidates_df.reset_index(drop=True)
    candidates_df['percentage_similarity'] = [round(s * 100, 2) for s in similarities]

    # Appliquer un filtre si spécifié / Apply a filter if specified
    if filter_type == "championnat":
        candidates_df = candidates_df[
            candidates_df['current_club_domestic_competition_id'] == competition
        ]
    elif filter_type == "pays":
        candidates_df = candidates_df[
            candidates_df['country_of_citizenship'] == country
        ]
    elif filter_type == "tranche_age":
        if pd.isna(age):
            pass
        elif age < 23:
            candidates_df = candidates_df[candidates_df['Age'] < 23]
        elif 24 <= age <= 29:
            candidates_df = candidates_df[candidates_df['Age'].between(24, 29)]
        else:
            candidates_df = candidates_df[candidates_df['Age'] >= 30]

    candidates_df = candidates_df.sort_values(by='percentage_similarity', ascending=False) # Trier par similarité / Sort by similarity
    
    candidates_df['market_value_in_eur'] = candidates_df['market_value_in_eur'].apply(format_market_value) # Formater la colonne de valeur marchande / Formatting market value column

    # Colonnes à afficher / Columns to display
    final_cols = [
        'name', 'percentage_similarity', 'Age', 'country_of_citizenship',  'current_club_name', 'market_value_in_eur', 'contract_expiration_date'
         
        
    ]
    # Traduction du pays du joueur / Translation of the player's country
    if lang == "Français":
        candidates_df['country_of_citizenship'] = candidates_df['country_of_citizenship'].apply(
            lambda x: country_translation.get(x, x)
        )

    return candidates_df[final_cols].head(top_n)

## Fonctions pour les différentes pages de ce projet / Functions for the different pages from this project

# Page d'accueil / Home page
def home():
    if lang == "Français":
        # Titre de la page
        st.markdown(
            "<h3 style='text-align: center;'>Projet de visualisation des performances des joueurs sur la saison 24/25 par Romain Traboul</h3>", 
            unsafe_allow_html=True)

        st.image("image/logo_1.jpg") # Utilisation de la 1er bannière en image

        # Sous-titre
        st.markdown(
            "<h4 style='text-align: center;'>Présentation du projet</h4>", 
            unsafe_allow_html=True)

        # Description du projet
        st.markdown(
            """
            <p style="text-align: justify;">
            L'objectif de ce projet est de <strong>visualiser les performances des joueurs sur la saison 24/25</strong>.
            Issus du travail de la communauté Kaggle, les données proviennent de :
            <ul>
                <li><a href="https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025" target="_blank">Fbref (Kaggle)</a></li>
                <li><a href="https://www.kaggle.com/datasets/davidcariboo/player-scores" target="_blank">Transfermarkt (Kaggle)</a></li>
            </ul>
            </p>

            <p style="text-align: justify;">
            Ainsi, l'analyse portera sur la saison 24/25 pour les compétitions suivantes :
            <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
            </p>

            <br>

            <ul>
                <li><strong>📊 Analyse d'un Joueur</strong> : Analyse du joueur de votre choix à travers plusieurs statistiques</li>
                <li><strong>🥊 Comparaison entre Joueurs</strong> : Analyse comparative entre deux joueurs du même poste</li>
                <li><strong>🏆 Classement des joueurs</strong> : Classement des joueurs par performance selon une statistique choisie</li>
            </ul>

            <br>

            Pour plus de détails sur ce projet, vous avez à votre disposition :
            <ul>
                <li><em>La documentation du projet</em></li>
                <li><a href="https://github.com/Twiist33/Data_Viz_France" target="_blank">Le code associé à l'application</a></li>
                <li><em>Et enfin mon CV</em></li>
            </ul>
            """,
            unsafe_allow_html=True
        )

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1]) # Utilisation de st.columns pour afficher les 2 boutons côte à côte et centrés

        # Utilisation du 1er bouton pour télécharger la documentation du projet
        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.download_button(
                label="Documentation",
                data=doc,
                file_name="Documentation_Player_Performance_France.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Utilisation du 2ème bouton pour télécharger le CV en français
        with col3:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.download_button(
                label="Mon CV en français",
                data=cv_data_fr,
                file_name="CV_FR_Romain_Traboul.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)


    else:
        # Page title
        st.markdown(
            "<h3 style='text-align: center;'>Romain Traboul's project to visualize player performance over the 24/25 season</h3>", 
            unsafe_allow_html=True)

        st.image("image/logo_1.jpg") # Using the 1st image banner

        # Subtitle
        st.markdown(
            "<h4 style='text-align: center;'>Project presentation</h4>", 
            unsafe_allow_html=True)

        # Project description
        st.markdown(
            """
            <p style="text-align: justify;">
            The goal of this project is to <strong>visualize player performances during the 24/25 season</strong>.
            Originally contributed by Kaggle users, the data comes from:
            <ul>
                <li><a href="https://www.kaggle.com/datasets/hubertsidorowicz/football-players-stats-2024-2025" target="_blank">Fbref dataset on Kaggle</a></li>
                <li><a href="https://www.kaggle.com/datasets/davidcariboo/player-scores" target="_blank">Transfermarkt dataset on Kaggle</a></li>
            </ul>
            </p>
            <p style="text-align: justify;">
            The analysis will cover the 24/25 season for the following competitions:
            <strong>Ligue 1, Bundesliga, Premier League, La Liga, Serie A</strong>.
            </p>

            <br>

            <ul>
                <li><strong>📊 Player Analysis</strong>: Analyze the player of your choice through various statistics</li>
                <li><strong>🥊 Player Comparison</strong>: Compare two players who play in the same position</li>
                <li><strong>🏆 Player Ranking</strong>: Rank players based on a chosen statistic</li>
            </ul>

            <br>

            For more details about this project, you can refer to:
            <ul>
                <li><em>The project documentation</em></li>
                <li><a href="https://github.com/Twiist33/Data_Viz_France" target="_blank">The code used to build the application</a></li>
                <li><em>My resume</em></li>
            </ul>
            """, unsafe_allow_html=True
        )

        col1, col2, col3, col4= st.columns([1, 1, 1, 1]) # Use st.columns to display the 2 buttons side by side and centered

        # Use 1st button to download documentation
        with col2:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.download_button(
                label="Documentation",
                data=doc_eng,
                file_name="Documentation_Player_Performance_English.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)

        # Use the 2nd button to download the English CV
        with col3:
            st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
            st.download_button(
                label="My CV in english",
                data=cv_data_eng,
                file_name="CV_ENG_Romain_Traboul.pdf",
                mime="application/pdf"
            )
            st.markdown("</div>", unsafe_allow_html=True)

# Page de l'analyse d'un joueur / Player analysis page
def player_analysis():
    if lang == "Français":
        # Afficher le titre
        st.markdown(
            "<h4 style='text-align: center;'>📊 Analyse d'un joueur</h4>", 
            unsafe_allow_html=True)

        image_path = os.path.join(os.path.dirname(__file__), "image", "player_analysis.jpg") # Construction du chemin d'accès à l'image

        df = pd.read_csv('data/database_player.csv') # Charger les données

        player_names = [''] + sorted(df['name'].dropna().unique().tolist()) # Extraire la liste des joueurs

        selected_player = st.sidebar.selectbox("Choisissez un joueur :", player_names) # Sélection de joueur

        # Si un joueur est sélectionnée, on cache l’image   
        if not selected_player:
            # Aucun joueur sélectionné → afficher l'image d'intro
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
        else:
            player_data = df[df['name'] == selected_player].iloc[0] # Filtrer le DataFrame pour le joueur sélectionné

            # Profil du joueur (image à gauche, infos à droite)
            st.markdown(
                f"<h4 style='text-align: center;'>Profil du joueur</h4>",
                unsafe_allow_html=True
            )
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                if pd.notna(player_data['image_url']):
                    st.image(player_data['image_url'], width=200)

            with col2:
                st.markdown(f"**Nom :** {player_data['name']}")
                st.markdown(f"**Âge :** {int(player_data['Age'])}" if pd.notna(player_data['Age']) else "**Âge :** -")
                # Traduction du pays en français
                pays = country_translation.get(player_data['country_of_citizenship'], player_data['country_of_citizenship'])
                st.markdown(f"**Pays :** {pays}")
                st.markdown(f"**Club :** {player_data['current_club_name']}")
                # Traduction du poste en français
                poste = position_translation.get(player_data['sub_position'], player_data['sub_position'])
                st.markdown(f"**Poste :** {poste}")
            
            with col3:  
                st.markdown(f"**Taille :** {int(player_data['height_in_cm'])} cm" if pd.notna(player_data['height_in_cm']) else "**Taille :** -")
                st.markdown(f"**Valeur marchande :** {format_market_value(player_data['market_value_in_eur'])}")
                st.markdown(f"**Fin de contrat :** {player_data['contract_expiration_date']}" if pd.notna(player_data['contract_expiration_date']) else "**Fin de contrat :** -")
                st.markdown(f"**Matches joués :** {int(player_data['MP'])}" if pd.notna(player_data['MP']) else "**Matches joués :** -")
                st.markdown(f"**Minutes joués :** {int(player_data['Min'])}" if pd.notna(player_data['Min']) else "**Minutes joués :** -")

            # Filtre unique pour radar + similarité
            comparison_filter = st.radio(
                "Comparer à son poste avec :",
                options=[
                    "Aucun filtre",
                    "Même championnat",
                    "Même tranche d’âge",
                    "Même pays"
                ],
                index=0,
                horizontal=True
            )

            filter_arg = {
                "Aucun filtre": None,
                "Même championnat": "championnat",
                "Même tranche d’âge": "tranche_age",
                "Même pays": "pays"
            }[comparison_filter]

            poste_cat = position_category.get(player_data['sub_position'], None)

            # Glossaire des statistiques associées
            with st.expander(" Glossaire des statistiques"):
                if poste_cat:

                    if poste_cat == "Gardiens de but":
                        st.markdown("""
                        - **GA_per90** : Buts encaissés par 90 minutes  
                        - **Saves_per_90** : Arrêts réalisés par 90 minutes  
                        - **Save%** : Pourcentage d’arrêts effectués  
                        - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes  
                        - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                        - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **AvgLen** : Longueur moyenne des passes (en yards)  
                        - **Launch%** : Pourcentage de passes longues  
                        - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                        - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                        - **CS%** : Pourcentage de matchs sans but encaissé
                        """)

                    elif poste_cat == "Défenseurs centraux":
                        st.markdown("""
                        - **Won%** : Pourcentage de duels aériens gagnés  
                        - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                        - **Tkl%** : Pourcentage de dribbleurs taclés  
                        - **Clr_per90** : Dégagements par 90 minutes  
                        - **Err_per90** : Erreurs menant à un tir adverse  
                        - **Touches_per90** : Touches de balle par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **Sw_per90** : Changements d’aile par 90 minutes  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **Fls_per90** : Fautes commises par 90 minutes  
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        """)

                    elif poste_cat == "Défenseurs latéraux":
                        st.markdown("""
                        - **Gls_per90** : Buts marqués par 90 minutes  
                        - **xG_per90** : Expected Goals par 90 minutes  
                        - **Ast_per90** : Passes décisives par 90 minutes  
                        - **xA_per90** : Expected Assists par 90 minutes  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                        - **Touches_per90** : Touches de balle par 90 minutes  
                        - **Crs_per90** : Centres par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                        - **Tkl%** : Pourcentage de dribbleurs taclés  
                        - **Err_per90** : Erreurs menant à un tir adverse  
                        - **Clr_per90** : Dégagements par 90 minutes  
                        - **Fls_per90** : Fautes commises par 90 minutes  
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        """)

                    elif poste_cat == "Milieux de terrain":
                        st.markdown("""
                        - **Gls_per90** : Buts marqués par 90 minutes  
                        - **xG_per90** : Expected Goals par 90 minutes  
                        - **Ast_per90** : Passes décisives par 90 minutes  
                        - **xA_per90** : Expected Assists par 90 minutes  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                        - **Touches_per90** : Touches de balle par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **Won%** : Pourcentage de duels aériens gagnés  
                        - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                        - **Tkl%** : Pourcentage de dribbleurs taclés  
                        - **Err_per90** : Erreurs menant à un tir adverse  
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        """)

                    elif poste_cat == "Milieux offensifs / Ailiers":
                        st.markdown("""
                        - **Gls_per90** : Buts marqués par 90 minutes  
                        - **xG_per90** : Expected Goals par 90 minutes  
                        - **Ast_per90** : Passes décisives par 90 minutes  
                        - **xA_per90** : Expected Assists par 90 minutes  
                        - **G/Sh** : Buts par tir  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                        - **Touches_per90** : Touches de balle par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
                        - **Succ_per_90** : Dribbles réussis par 90 minutes  
                        - **Succ%** : Pourcentage de dribbles réussis  
                        - **Dis_per90** : Ballons perdus par 90 minutes  
                        - **Fld** : Fautes subies  
                        - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes
                        """)

                    elif poste_cat == "Attaquants":
                        st.markdown("""
                        - **Gls_per90** : Buts marqués par 90 minutes  
                        - **xG_per90** : Expected Goals par 90 minutes  
                        - **Ast_per90** : Passes décisives par 90 minutes  
                        - **xA_per90** : Expected Assists par 90 minutes  
                        - **G/Sh** : Buts par tir  
                        - **Dist** : Distance moyenne des tirs  
                        - **SoT_per90** : Tirs cadrés par 90 minutes  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                        - **Touches_per90** : Touches de balle par 90 minutes  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
                        - **Fld** : Fautes subies  
                        - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes
                        """)

            if poste_cat and poste_cat in category_stats:
                stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]

                # Groupe filtré selon le filtre sélectionné par l'utilisateur
                if filter_arg is None:
                    group_df = df[df['sub_position'].map(position_category.get) == poste_cat]
                elif filter_arg == "championnat":
                    group_df = df[
                        (df['sub_position'] == player_data['sub_position']) &
                        (df['current_club_domestic_competition_id'] == player_data['current_club_domestic_competition_id'])
                    ]
                elif filter_arg == "pays":
                    group_df = df[
                        (df['sub_position'] == player_data['sub_position']) &
                        (df['country_of_citizenship'] == player_data['country_of_citizenship'])
                    ]
                elif filter_arg == "tranche_age":
                    age = player_data['Age']
                    if pd.isna(age):
                        group_df = df[df['sub_position'].map(position_category.get) == poste_cat]
                    elif age < 23:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'] < 23)]
                    elif 24 <= age <= 29:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'].between(24, 29))]
                    else:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'] >= 30)]

                nb_players = len(group_df) # Calculer le nombre de joueur dans le groupe filtré

                # Si il y a moins de 5 joueurs, on n'affiche pas de radar pour le groupe associé
                if nb_players >= 5:
                    radar_df = group_df[['name'] + stats_cols].dropna(subset=stats_cols).copy()
                    radar_df = radar_df.set_index('name')

                    if player_data['name'] not in radar_df.index:
                        radar_df.loc[player_data['name']] = player_data[stats_cols]

                    stats_min = radar_df[stats_cols].min()
                    stats_max = radar_df[stats_cols].max()
                    radar_df_normalized = (radar_df[stats_cols] - stats_min) / (stats_max - stats_min) # Normalisation du radar

                    player_norm = radar_df_normalized.loc[player_data['name']].reindex(stats_cols).fillna(0) # Normalisation des données
                    group_median = radar_df_normalized.drop(index=player_data['name'], errors='ignore').median().reindex(stats_cols).fillna(0) # Calcul de la médiane

                    # Affichage du titre
                    st.markdown(
                        f"<h4 style='text-align: center;'>Radar de performance de {player_data['name']} vs {nb_players} joueurs dans sa catégorie</h4>",
                        unsafe_allow_html=True
                    )

                    # On affiche les deux radars (celui du joueur en bleu, et de la médiane de groupe en rouge)
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player_data['name'],
                        line=dict(color='blue'),
                        marker=dict(color='blue'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in group_median],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name='Médiane comparaison',
                        line=dict(color='red'),
                        marker=dict(color='red'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1]),
                            angularaxis=dict(rotation=90, direction="clockwise")
                        ),
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas assez de joueurs dans ce groupe pour générer un radar (minimum requis : 5).")

            similar_df = find_similar_players(selected_player, df, filter_type=filter_arg) # Recherche des joueurs similaires avec le même filtre utilisé
            if not similar_df.empty:
                # Affichage du titre
                st.markdown(
                    f"<h4 style='text-align: center;'>Joueurs similaires à {player_data['name']}</h4>",
                    unsafe_allow_html=True
                )
                st.dataframe(similar_df)
            else:
                st.info("Aucun joueur similaire trouvé avec les critères sélectionnés.")


    else:
        # Display the title
        st.markdown(
            "<h4 style='text-align: center;'>📊 Player analysis</h4>", 
            unsafe_allow_html=True)

        image_path = os.path.join(os.path.dirname(__file__), "image", "player_analysis.jpg") # Building the path for the image

        df = pd.read_csv('data/database_player.csv') # Collect the data

        player_names = [''] + sorted(df['name'].dropna().unique().tolist()) # Extract the list of players

        selected_player = st.sidebar.selectbox("Select a player :", player_names) # Select a player

        # If a player is selected, the image is hidden.   
        if not selected_player:
            # No player selected → show intro image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
        else:
            player_data = df[df['name'] == selected_player].iloc[0] # Filter the DataFrame for the selected player

            # Player profile (image on left, info on right)
            st.markdown(
                f"<h4 style='text-align: center;'>Player profile</h4>",
                unsafe_allow_html=True
            )
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                if pd.notna(player_data['image_url']):
                    st.image(player_data['image_url'], width=200)

            with col2:
                st.markdown(f"**Name :** {player_data['name']}")
                st.markdown(f"**Age :** {int(player_data['Age'])}" if pd.notna(player_data['Age']) else "**age :** -")
                st.markdown(f"**Country :** {player_data['country_of_citizenship']}")
                st.markdown(f"**Club :** {player_data['current_club_name']}")
                st.markdown(f"**Position :** {player_data['sub_position']}")

            with col3:  
                st.markdown(f"**Height :** {int(player_data['height_in_cm'])} cm" if pd.notna(player_data['height_in_cm']) else "**Heigth :** -")
                st.markdown(f"**Market Value :** {format_market_value(player_data['market_value_in_eur'])}")
                st.markdown(f"**Contract :** {player_data['contract_expiration_date']}" if pd.notna(player_data['contract_expiration_date']) else "**Contract :** -")
                st.markdown(f"**Matches played :** {int(player_data['MP'])}" if pd.notna(player_data['MP']) else "**Matches played :** -")
                st.markdown(f"**Minutes played :** {int(player_data['Min'])}" if pd.notna(player_data['Min']) else "**Minutes played :** -")

            # Single filter for radar + similarity
            comparison_filter = st.radio(
                "Compare his position with :",
                options=[
                    "No filter",
                    "Same championship",
                    "Same age group",
                    "Same country"
                ],
                index=0,
                horizontal=True
            )

            filter_arg = {
                "No filter": None,
                "Same championship": "championnat",
                "Same age group": "tranche_age",
                "Same country": "pays"
            }[comparison_filter]

            poste_cat = position_category.get(player_data['sub_position'], None)

            # Glossary of Statistics associated
            with st.expander("Glossary of Statistics"):
                if poste_cat:
                    if poste_cat == "Gardiens de but":
                        st.markdown("""
                        - **GA_per90**: Goals conceded per 90 minutes  
                        - **Saves_per_90**: Saves made per 90 minutes  
                        - **Save%**: Save percentage  
                        - **/90 (PSxG-GA/90)**: Post-Shot xG minus Goals Against per 90 minutes  
                        - **PSxG+/-**: Post-Shot xG minus Goals Against  
                        - **Err_per90**: Errors leading to shots per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **AvgLen**: Average pass length in yards  
                        - **Launch%**: Percentage of long passes  
                        - **Stp%**: Percentage of crosses stopped  
                        - **#OPA_per90**: Defensive actions outside penalty area per 90 minutes  
                        - **CS%**: Clean sheet percentage
                        """)

                    elif poste_cat == "Défenseurs centraux":
                        st.markdown("""
                        - **Won%**: Aerial duels won percentage  
                        - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                        - **Tkl%**: Percentage of dribblers tackled  
                        - **Clr_per90**: Clearances per 90 minutes  
                        - **Err_per90**: Errors leading to shots  
                        - **Touches_per90**: Ball touches per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **Sw_per90**: Switches (long diagonal passes) per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Fls_per90**: Fouls committed per 90 minutes  
                        - **CrdY_per90**: Yellow cards per 90 minutes
                        """)

                    elif poste_cat == "Défenseurs latéraux":
                        st.markdown("""
                        - **Gls_per90**: Goals per 90 minutes  
                        - **xG_per90**: Expected Goals per 90 minutes  
                        - **Ast_per90**: Assists per 90 minutes  
                        - **xA_per90**: Expected Assists per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Touches_per90**: Ball touches per 90 minutes  
                        - **Crs_per90**: Crosses per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                        - **Tkl%**: Percentage of dribblers tackled  
                        - **Err_per90**: Errors leading to shots  
                        - **Clr_per90**: Clearances per 90 minutes  
                        - **Fls_per90**: Fouls committed per 90 minutes  
                        - **CrdY_per90**: Yellow cards per 90 minutes
                        """)

                    elif poste_cat == "Milieux de terrain":
                        st.markdown("""
                        - **Gls_per90**: Goals per 90 minutes  
                        - **xG_per90**: Expected Goals per 90 minutes  
                        - **Ast_per90**: Assists per 90 minutes  
                        - **xA_per90**: Expected Assists per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Touches_per90**: Ball touches per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **Won%**: Aerial duels won percentage  
                        - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                        - **Tkl%**: Percentage of dribblers tackled  
                        - **Err_per90**: Errors leading to shots  
                        - **CrdY_per90**: Yellow cards per 90 minutes
                        """)

                    elif poste_cat == "Milieux offensifs / Ailiers":
                        st.markdown("""
                        - **Gls_per90**: Goals per 90 minutes  
                        - **xG_per90**: Expected Goals per 90 minutes  
                        - **Ast_per90**: Assists per 90 minutes  
                        - **xA_per90**: Expected Assists per 90 minutes  
                        - **G/Sh**: Goals per shot  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Touches_per90**: Ball touches per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **1/3_per90**: Passes into final third per 90 minutes  
                        - **Succ_per_90**: Successful take-ons per 90 minutes  
                        - **Succ%**: Take-on success rate  
                        - **Dis_per90**: Times dispossessed per 90 minutes  
                        - **Fld**: Fouls drawn  
                        - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes
                        """)

                    elif poste_cat == "Attaquants":
                        st.markdown("""
                        - **Gls_per90**: Goals per 90 minutes  
                        - **xG_per90**: Expected Goals per 90 minutes  
                        - **Ast_per90**: Assists per 90 minutes  
                        - **xA_per90**: Expected Assists per 90 minutes  
                        - **G/Sh**: Goals per shot  
                        - **Dist**: Average shot distance (in yards)  
                        - **SoT_per90**: Shots on target per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Touches_per90**: Ball touches per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **1/3_per90**: Passes into final third per 90 minutes  
                        - **Fld**: Fouls drawn  
                        - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes
                        """)

            if poste_cat and poste_cat in category_stats:
                stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]

                # Group filtered according to the selected filter by the user
                if filter_arg is None:
                    group_df = df[df['sub_position'].map(position_category.get) == poste_cat]
                elif filter_arg == "championnat":
                    group_df = df[
                        (df['sub_position'] == player_data['sub_position']) &
                        (df['current_club_domestic_competition_id'] == player_data['current_club_domestic_competition_id'])
                    ]
                elif filter_arg == "pays":
                    group_df = df[
                        (df['sub_position'] == player_data['sub_position']) &
                        (df['country_of_citizenship'] == player_data['country_of_citizenship'])
                    ]
                elif filter_arg == "tranche_age":
                    age = player_data['Age']
                    if pd.isna(age):
                        group_df = df[df['sub_position'].map(position_category.get) == poste_cat]
                    elif age < 23:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'] < 23)]
                    elif 24 <= age <= 29:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'].between(24, 29))]
                    else:
                        group_df = df[(df['sub_position'] == player_data['sub_position']) & (df['Age'] >= 30)]

                nb_players = len(group_df) # Calculation of the length of the group

                # If the group is less than 5, we don't build the radar
                if nb_players >= 5:
                    radar_df = group_df[['name'] + stats_cols].dropna(subset=stats_cols).copy()
                    radar_df = radar_df.set_index('name')

                    if player_data['name'] not in radar_df.index:
                        radar_df.loc[player_data['name']] = player_data[stats_cols]

                    stats_min = radar_df[stats_cols].min()
                    stats_max = radar_df[stats_cols].max()
                    radar_df_normalized = (radar_df[stats_cols] - stats_min) / (stats_max - stats_min) # Normalize

                    player_norm = radar_df_normalized.loc[player_data['name']].reindex(stats_cols).fillna(0) # Normalize
                    group_median = radar_df_normalized.drop(index=player_data['name'], errors='ignore').median().reindex(stats_cols).fillna(0) # Median

                    # Display the title
                    st.markdown(
                        f"<h4 style='text-align: center;'>Performance radar from {player_data['name']} vs {nb_players} players in his category</h4>",
                        unsafe_allow_html=True
                    )
                    # Display the radar (in blue for the player, and in red for the median group)
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player_data['name'],
                        line=dict(color='blue'),
                        marker=dict(color='blue'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in group_median],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name='Median comparison',
                        line=dict(color='red'),
                        marker=dict(color='red'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1]),
                            angularaxis=dict(rotation=90, direction="clockwise")
                        ),
                        showlegend=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough players in this group to generate a radar (minimum requirement: 5).")

            similar_df = find_similar_players(selected_player, df, filter_type=filter_arg) # Search for similar players using the same filter
            if not similar_df.empty:
                # Display the title
                st.markdown(
                    f"<h4 style='text-align: center;'>Players similar to {player_data['name']}</h4>",
                    unsafe_allow_html=True
                )
                st.dataframe(similar_df)
            else:
                st.info("Not enough players in this group to generate a radar (minimum requirement: 5).")

# Page de la comparaison entre 2 joueurs / 2 player comparison page
def player_comparison():
    if lang == "Français":
        st.markdown(
            "<h4 style='text-align: center;'>🥊 Comparaison de deux joueurs</h4>", 
            unsafe_allow_html=True)
        
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_comparison.jpg") # Construction du chemin menant à l'image

        df = pd.read_csv("data/database_player.csv") # Récupérer les données
        player_names = sorted(df['name'].dropna().unique().tolist()) # Ordonner par le nom du joueur

        st.sidebar.markdown("### Sélection des joueurs") # Sélection dans la sidebar

        player1 = st.sidebar.selectbox("Premier joueur :", [''] + player_names, key="player1") # Sélection du 1er joueur
        
        if not player1:
            # Aucun joueur sélectionné → afficher l'image d'intro
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)

        if player1:
            # Nous stockons les informations du 1er joueur
            player1_data = df[df['name'] == player1].iloc[0]
            sub_position = player1_data['sub_position']
            poste_cat = position_category.get(sub_position, None)

            same_position_players = df[df['sub_position'] == sub_position]
            player2_names = sorted(same_position_players['name'].dropna().unique().tolist())
            player2_names = [p for p in player2_names if p != player1]

            player2 = st.sidebar.selectbox("Second joueur (même poste) :", [''] + player2_names, key="player2") # Sélection du 2nd joueur
            
            if not player2:
                # Aucun joueur sélectionné → afficher l'image d'intro
                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)

            if player2:
                player2_data = df[df['name'] == player2].iloc[0] # Récupération du nom du 2nd joueur
                
                st.markdown("<h4 style='text-align: center;'>Profils des joueurs</h4>", unsafe_allow_html=True) # Affichage les profils côte à côte
                for pdata in [player1_data, player2_data]:
                    col1, col2, col3 = st.columns([1, 2, 2])

                    with col1:
                        if pd.notna(pdata['image_url']):
                            st.image(pdata['image_url'], width=200)

                    with col2:
                        st.markdown(f"**Nom :** {pdata['name']}")
                        st.markdown(f"**Âge :** {int(pdata['Age'])}" if pd.notna(pdata['Age']) else "**Âge :** -")
                        # Traduction du pays
                        pays = country_translation.get(pdata['country_of_citizenship'], pdata['country_of_citizenship'])
                        st.markdown(f"**Pays :** {pays}")
                        st.markdown(f"**Club :** {pdata['current_club_name']}")


                    with col3:
                        # Traduction du poste
                        poste = position_translation.get(pdata['sub_position'], pdata['sub_position'])
                        st.markdown(f"**Poste :** {poste}")
                        st.markdown(f"**Taille :** {int(pdata['height_in_cm'])} cm" if pd.notna(pdata['height_in_cm']) else "**Taille :** -")
                        st.markdown(f"**Valeur marchande :** {format_market_value(pdata['market_value_in_eur'])}")
                        st.markdown(f"**Fin de contrat :** {pdata['contract_expiration_date']}" if pd.notna(pdata['contract_expiration_date']) else "**Fin de contrat :** -")

                # Glossaire des statistiques associées
                with st.expander(" Glossaire des statistiques"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90** : Buts encaissés par 90 minutes  
                            - **Saves_per_90** : Arrêts réalisés par 90 minutes  
                            - **Save%** : Pourcentage d’arrêts effectués  
                            - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes  
                            - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                            - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **AvgLen** : Longueur moyenne des passes (en yards)  
                            - **Launch%** : Pourcentage de passes longues  
                            - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                            - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                            - **CS%** : Pourcentage de matchs sans but encaissé
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **Won%** : Pourcentage de duels aériens gagnés  
                            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                            - **Tkl%** : Pourcentage de dribbleurs taclés  
                            - **Clr_per90** : Dégagements par 90 minutes  
                            - **Err_per90** : Erreurs menant à un tir adverse  
                            - **Touches_per90** : Touches de balle par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **Sw_per90** : Changements d’aile par 90 minutes  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **Fls_per90** : Fautes commises par 90 minutes  
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **Gls_per90** : Buts marqués par 90 minutes  
                            - **xG_per90** : Expected Goals par 90 minutes  
                            - **Ast_per90** : Passes décisives par 90 minutes  
                            - **xA_per90** : Expected Assists par 90 minutes  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                            - **Touches_per90** : Touches de balle par 90 minutes  
                            - **Crs_per90** : Centres par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                            - **Tkl%** : Pourcentage de dribbleurs taclés  
                            - **Err_per90** : Erreurs menant à un tir adverse  
                            - **Clr_per90** : Dégagements par 90 minutes  
                            - **Fls_per90** : Fautes commises par 90 minutes  
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **Gls_per90** : Buts marqués par 90 minutes  
                            - **xG_per90** : Expected Goals par 90 minutes  
                            - **Ast_per90** : Passes décisives par 90 minutes  
                            - **xA_per90** : Expected Assists par 90 minutes  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                            - **Touches_per90** : Touches de balle par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **Won%** : Pourcentage de duels aériens gagnés  
                            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
                            - **Tkl%** : Pourcentage de dribbleurs taclés  
                            - **Err_per90** : Erreurs menant à un tir adverse  
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **Gls_per90** : Buts marqués par 90 minutes  
                            - **xG_per90** : Expected Goals par 90 minutes  
                            - **Ast_per90** : Passes décisives par 90 minutes  
                            - **xA_per90** : Expected Assists par 90 minutes  
                            - **G/Sh** : Buts par tir  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                            - **Touches_per90** : Touches de balle par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
                            - **Succ_per_90** : Dribbles réussis par 90 minutes  
                            - **Succ%** : Pourcentage de dribbles réussis  
                            - **Dis_per90** : Ballons perdus par 90 minutes  
                            - **Fld** : Fautes subies  
                            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                                st.markdown("""
                            - **Gls_per90** : Buts marqués par 90 minutes  
                            - **xG_per90** : Expected Goals par 90 minutes  
                            - **Ast_per90** : Passes décisives par 90 minutes  
                            - **xA_per90** : Expected Assists par 90 minutes  
                            - **G/Sh** : Buts par tir  
                            - **Dist** : Distance moyenne des tirs  
                            - **SoT_per90** : Tirs cadrés par 90 minutes  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
                            - **Touches_per90** : Touches de balle par 90 minutes  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
                            - **Fld** : Fautes subies  
                            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes
                            """)

                # Génération du radar
                if poste_cat and poste_cat in category_stats:
                    stats_cols = [col for col in category_stats[poste_cat] if col in df.columns] # Récupération des catégories des positions de joueurs

                    radar_df = df[df['sub_position'] == sub_position][['name'] + stats_cols].dropna(subset=stats_cols).copy()
                    radar_df = radar_df.set_index('name')

                    for p, pdata in [(player1, player1_data), (player2, player2_data)]:
                        if p not in radar_df.index:
                            radar_df.loc[p] = pdata[stats_cols]

                    stats_min = radar_df[stats_cols].min()
                    stats_max = radar_df[stats_cols].max()
                    radar_df_normalized = (radar_df[stats_cols] - stats_min) / (stats_max - stats_min) # Normalisation

                    player1_norm = radar_df_normalized.loc[player1].reindex(stats_cols).fillna(0) # Normalisation
                    player2_norm = radar_df_normalized.loc[player2].reindex(stats_cols).fillna(0) # Normalisation

                    # Affichage du titre et du radar
                    st.markdown(
                        f"<h4 style='text-align: center;'>Radar comparatif : {player1} vs {player2}</h4>",
                        unsafe_allow_html=True
                    )

                    fig = go.Figure()

                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player1_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player1,
                        line=dict(color='blue'),
                        marker=dict(color='blue'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))

                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player2_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player2,
                        line=dict(color='red'),
                        marker=dict(color='red'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1]),
                            angularaxis=dict(rotation=90, direction="clockwise")
                        ),
                        showlegend=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

    else:
        # Display the title
        st.markdown(
            "<h4 style='text-align: center;'>🥊 Player Comparison</h4>", 
            unsafe_allow_html=True)

        image_path = os.path.join(os.path.dirname(__file__), "image", "player_comparison.jpg") # Building the path for the image

        df = pd.read_csv("data/database_player.csv") # Recover the data
        player_names = sorted(df['name'].dropna().unique().tolist()) # Order by data 

        st.sidebar.markdown("### Player selection") # Selection in the sidebar

        player1 = st.sidebar.selectbox("First player :", [''] + player_names, key="player1") # Select the first player
        
        if not player1:
            # If the player is selected, we hide the image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)

        if player1:
            # Collecting the data for the players
            player1_data = df[df['name'] == player1].iloc[0]
            sub_position = player1_data['sub_position']
            poste_cat = position_category.get(sub_position, None)

            same_position_players = df[df['sub_position'] == sub_position]
            player2_names = sorted(same_position_players['name'].dropna().unique().tolist())
            player2_names = [p for p in player2_names if p != player1]

            player2 = st.sidebar.selectbox("Second player (same position) :", [''] + player2_names, key="player2") # Select the 2nd player
            
            if not player2:
                # If the player is selected, we hide the image
                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)

            if player2:
                player2_data = df[df['name'] == player2].iloc[0] # Collecting the name of the player 2
                
                st.markdown("<h4 style='text-align: center;'>Players profile</h4>", unsafe_allow_html=True) # Display complete profiles side by side

                for pdata in [player1_data, player2_data]:
                    col1, col2, col3 = st.columns([1, 2, 2])

                    with col1:
                        if pd.notna(pdata['image_url']):
                            st.image(pdata['image_url'], width=200)

                    with col2:
                        st.markdown(f"**Name :** {pdata['name']}")
                        st.markdown(f"**Age :** {int(pdata['Age'])}" if pd.notna(pdata['Age']) else "**Age :** -")
                        st.markdown(f"**Country :** {pdata['country_of_citizenship']}")
                        st.markdown(f"**Club :** {pdata['current_club_name']}")


                    with col3:
                        st.markdown(f"**Position :** {pdata['sub_position']}")
                        st.markdown(f"**Height :** {int(pdata['height_in_cm'])} cm" if pd.notna(pdata['height_in_cm']) else "**Taille :** -")
                        st.markdown(f"**Market Value :** {format_market_value(pdata['market_value_in_eur'])}")
                        st.markdown(f"**Contract :** {pdata['contract_expiration_date']}" if pd.notna(pdata['contract_expiration_date']) else "**Fin de contrat :** -")

                # Glossary of Statistics associated
                with st.expander("Glossary of Statistics"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90**: Goals conceded per 90 minutes  
                            - **Saves_per_90**: Saves made per 90 minutes  
                            - **Save%**: Save percentage  
                            - **/90 (PSxG-GA/90)**: Post-Shot xG minus Goals Against per 90 minutes  
                            - **PSxG+/-**: Post-Shot xG minus Goals Against  
                            - **Err_per90**: Errors leading to shots per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **AvgLen**: Average pass length in yards  
                            - **Launch%**: Percentage of long passes  
                            - **Stp%**: Percentage of crosses stopped  
                            - **#OPA_per90**: Defensive actions outside penalty area per 90 minutes  
                            - **CS%**: Clean sheet percentage
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **Won%**: Aerial duels won percentage  
                            - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                            - **Tkl%**: Percentage of dribblers tackled  
                            - **Clr_per90**: Clearances per 90 minutes  
                            - **Err_per90**: Errors leading to shots  
                            - **Touches_per90**: Ball touches per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **Sw_per90**: Switches (long diagonal passes) per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Fls_per90**: Fouls committed per 90 minutes  
                            - **CrdY_per90**: Yellow cards per 90 minutes
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **Gls_per90**: Goals per 90 minutes  
                            - **xG_per90**: Expected Goals per 90 minutes  
                            - **Ast_per90**: Assists per 90 minutes  
                            - **xA_per90**: Expected Assists per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Touches_per90**: Ball touches per 90 minutes  
                            - **Crs_per90**: Crosses per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                            - **Tkl%**: Percentage of dribblers tackled  
                            - **Err_per90**: Errors leading to shots  
                            - **Clr_per90**: Clearances per 90 minutes  
                            - **Fls_per90**: Fouls committed per 90 minutes  
                            - **CrdY_per90**: Yellow cards per 90 minutes
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **Gls_per90**: Goals per 90 minutes  
                            - **xG_per90**: Expected Goals per 90 minutes  
                            - **Ast_per90**: Assists per 90 minutes  
                            - **xA_per90**: Expected Assists per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Touches_per90**: Ball touches per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **Won%**: Aerial duels won percentage  
                            - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                            - **Tkl%**: Percentage of dribblers tackled  
                            - **Err_per90**: Errors leading to shots  
                            - **CrdY_per90**: Yellow cards per 90 minutes
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **Gls_per90**: Goals per 90 minutes  
                            - **xG_per90**: Expected Goals per 90 minutes  
                            - **Ast_per90**: Assists per 90 minutes  
                            - **xA_per90**: Expected Assists per 90 minutes  
                            - **G/Sh**: Goals per shot  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Touches_per90**: Ball touches per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **1/3_per90**: Passes into final third per 90 minutes  
                            - **Succ_per_90**: Successful take-ons per 90 minutes  
                            - **Succ%**: Take-on success rate  
                            - **Dis_per90**: Times dispossessed per 90 minutes  
                            - **Fld**: Fouls drawn  
                            - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **Gls_per90**: Goals per 90 minutes  
                            - **xG_per90**: Expected Goals per 90 minutes  
                            - **Ast_per90**: Assists per 90 minutes  
                            - **xA_per90**: Expected Assists per 90 minutes  
                            - **G/Sh**: Goals per shot  
                            - **Dist**: Average shot distance (in yards)  
                            - **SoT_per90**: Shots on target per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Touches_per90**: Ball touches per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **1/3_per90**: Passes into final third per 90 minutes  
                            - **Fld**: Fouls drawn  
                            - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes
                            """)

                # Radar generation
                if poste_cat and poste_cat in category_stats:
                    stats_cols = [col for col in category_stats[poste_cat] if col in df.columns] # Access to the category by position

                    radar_df = df[df['sub_position'] == sub_position][['name'] + stats_cols].dropna(subset=stats_cols).copy()
                    radar_df = radar_df.set_index('name')

                    for p, pdata in [(player1, player1_data), (player2, player2_data)]:
                        if p not in radar_df.index:
                            radar_df.loc[p] = pdata[stats_cols]

                    stats_min = radar_df[stats_cols].min()
                    stats_max = radar_df[stats_cols].max()
                    radar_df_normalized = (radar_df[stats_cols] - stats_min) / (stats_max - stats_min) # Normalize

                    player1_norm = radar_df_normalized.loc[player1].reindex(stats_cols).fillna(0) # Normalize
                    player2_norm = radar_df_normalized.loc[player2].reindex(stats_cols).fillna(0) # Normalize

                    # Displaying radar and his title
                    st.markdown(
                        f"<h4 style='text-align: center;'>Comparative radar : {player1} vs {player2}</h4>",
                        unsafe_allow_html=True
                    )

                    fig = go.Figure()

                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player1_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player1,
                        line=dict(color='blue'),
                        marker=dict(color='blue'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))

                    fig.add_trace(go.Scatterpolar(
                        r=[round(v, 2) for v in player2_norm],
                        theta=stats_cols,
                        mode='lines+markers',
                        fill='toself',
                        name=player2,
                        line=dict(color='red'),
                        marker=dict(color='red'),
                        hovertemplate='%{theta}: %{r:.2f}'
                    ))

                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 1]),
                            angularaxis=dict(rotation=90, direction="clockwise")
                        ),
                        showlegend=True
                    )

                    st.plotly_chart(fig, use_container_width=True)

# Page du classement des joueurs / Player ranking page
def ranking():
    # Page en frabçais
    if lang == "Français":
        st.markdown("<h4 style='text-align: center;'>🏆 Classement des joueurs</h4>", unsafe_allow_html=True) # Affichage du titre de la page
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking.jpg") # Construction du chemin pour l'image
        df = pd.read_csv("data/database_player.csv") # Récupération des données

        all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # Liste des statistiques disponibles

        selected_stat = st.sidebar.selectbox("Choisissez une statistique :", [""] + all_stats) # Choix de la statistique dans la sidebar
        
        if not selected_stat:
            # Si la métrique est selectionné, nous cachons l'image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                
        if selected_stat:
            # Début de la sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filtres")

                # Étape 1 : filtre selon la statistique sélectionnée
                df_with_stat = df.dropna(subset=[selected_stat])
                if selected_stat in ['Saves_per90', '#OPA_per90']:
                    df_with_stat = df_with_stat[df_with_stat[selected_stat] != 0]

                filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                # Étape 2 : filtre Poste
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options_fr = [""] + [position_translation.get(p, p) for p in poste_options_raw]
                poste_fr = st.selectbox("Poste", poste_options_fr)

                if poste_fr:
                    poste_en = {v: k for k, v in position_translation.items()}.get(poste_fr, poste_fr)
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_en]

                # Étape 3 : filtre Championnat
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("Championnat", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Étape 4 : filtre Club
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Étape 5 : filtre Pays
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options_fr = [""] + [country_translation.get(p, p) for p in pays_options_raw]
                pays_fr = st.selectbox("Pays", pays_options_fr)

                if pays_fr:
                    pays_en = {v: k for k, v in country_translation.items()}.get(pays_fr, pays_fr)
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_en]

                # Étape 6 : filtre Tranche d’âge
                # Créer dynamiquement les tranches d'âge disponibles
                tranche_options = [""]

                ages = filtered_df["Age"].dropna()

                if any(ages < 23):
                    tranche_options.append("< 23 ans")
                if any((ages >= 24) & (ages <= 29)):
                    tranche_options.append("24-29 ans")
                if any(ages >= 30):
                    tranche_options.append("30 ans et +")

                # Sélecteur
                age_group = st.selectbox("Tranche d'âge", tranche_options)

                # Appliquer le filtre si sélectionné
                if age_group:
                    if age_group == "< 23 ans":
                        filtered_df = filtered_df[filtered_df["Age"] < 23]
                    elif age_group == "24-29 ans":
                        filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                    elif age_group == "30 ans et +":
                        filtered_df = filtered_df[filtered_df["Age"] >= 30]

                # Étape 7 : filtre Valeur marchande
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_min = st.slider(
                    "Valeur marchande min (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_min_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Valeur minimale sélectionnée : **{format_market_value(valeur_min)}**")
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] >= valeur_min]

            # Placement du glossaire en sidebar
            with st.sidebar.expander("Glossaire des statistiques"):
                st.markdown("""
            ### Gardien de but :
            - **GA_per90** : Buts encaissés par 90 minutes  
            - **Saves_per_90** : Arrêts réalisés par 90 minutes  
            - **Save%** : Pourcentage d’arrêts  
            - **/90 (PSxG-GA/90)** : Post-Shot xG moins buts encaissés par 90 minutes  
            - **PSxG+/-** : Post-Shot xG moins buts encaissés  
            - **Err_per90** : Erreurs menant à un tir adverse par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **AvgLen** : Longueur moyenne des passes (en yards)  
            - **Launch%** : Pourcentage de passes longues  
            - **Stp%** : Pourcentage de centres arrêtés  
            - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
            - **CS%** : Pourcentage de clean sheets (matches sans but encaissé)

            ### Défenseurs centraux :
            - **Won%** : Pourcentage de duels aériens gagnés  
            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
            - **Tkl%** : Pourcentage de dribbleurs taclés  
            - **Clr_per90** : Dégagements par 90 minutes  
            - **Err_per90** : Erreurs menant à un tir adverse  
            - **Touches_per90** : Touches de balle par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **Sw_per90** : Changements de jeu (passes longues transversales) par 90 minutes  
            - **PrgP_per90** : Passes progressives par 90 minutes  
            - **PrgC_per90** : Conduites progressives par 90 minutes  
            - **Fls_per90** : Fautes commises par 90 minutes  
            - **CrdY_per90** : Cartons jaunes par 90 minutes

            ### Défenseurs latéraux :
            - **Gls_per90** : Buts marqués par 90 minutes  
            - **xG_per90** : Expected Goals par 90 minutes  
            - **Ast_per90** : Passes décisives par 90 minutes  
            - **xA_per90** : Expected Assists par 90 minutes  
            - **PrgP_per90** : Passes progressives par 90 minutes  
            - **PrgC_per90** : Conduites progressives par 90 minutes  
            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
            - **Touches_per90** : Touches de balle par 90 minutes  
            - **Crs_per90** : Centres par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
            - **Tkl%** : Pourcentage de dribbleurs taclés  
            - **Err_per90** : Erreurs menant à un tir adverse  
            - **Clr_per90** : Dégagements par 90 minutes  
            - **Fls_per90** : Fautes commises par 90 minutes  
            - **CrdY_per90** : Cartons jaunes par 90 minutes

            ### 🎯 Milieux de terrain :
            - **Gls_per90** : Buts marqués par 90 minutes  
            - **xG_per90** : Expected Goals par 90 minutes  
            - **Ast_per90** : Passes décisives par 90 minutes  
            - **xA_per90** : Expected Assists par 90 minutes  
            - **PrgP_per90** : Passes progressives par 90 minutes  
            - **PrgC_per90** : Conduites progressives par 90 minutes  
            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
            - **Touches_per90** : Touches de balle par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **Won%** : Pourcentage de duels aériens gagnés  
            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes  
            - **Tkl%** : Pourcentage de dribbleurs taclés  
            - **Err_per90** : Erreurs menant à un tir adverse  
            - **CrdY_per90** : Cartons jaunes par 90 minutes

            ### Milieux offensifs / Ailiers :
            - **Gls_per90** : Buts marqués par 90 minutes  
            - **xG_per90** : Expected Goals par 90 minutes  
            - **Ast_per90** : Passes décisives par 90 minutes  
            - **xA_per90** : Expected Assists par 90 minutes  
            - **G/Sh** : Buts par tir  
            - **PrgP_per90** : Passes progressives par 90 minutes  
            - **PrgC_per90** : Conduites progressives par 90 minutes  
            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
            - **Touches_per90** : Touches de balle par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
            - **Succ_per_90** : Dribbles réussis par 90 minutes  
            - **Succ%** : Pourcentage de dribbles réussis  
            - **Dis_per90** : Ballons perdus (tacles adverses) par 90 minutes  
            - **Fld** : Fautes subies  
            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes

            ### Attaquants :
            - **Gls_per90** : Buts marqués par 90 minutes  
            - **xG_per90** : Expected Goals par 90 minutes  
            - **Ast_per90** : Passes décisives par 90 minutes  
            - **xA_per90** : Expected Assists par 90 minutes  
            - **G/Sh** : Buts par tir  
            - **Dist** : Distance moyenne de tir (en yards)  
            - **SoT_per90** : Tirs cadrés par 90 minutes  
            - **PrgP_per90** : Passes progressives par 90 minutes  
            - **PrgC_per90** : Conduites progressives par 90 minutes  
            - **PrgR_per90** : Passes progressives reçues par 90 minutes  
            - **Touches_per90** : Touches de balle par 90 minutes  
            - **Cmp%** : Pourcentage de passes réussies  
            - **1/3_per90** : Passes dans le dernier tiers par 90 minutes  
            - **Fld** : Fautes subies  
            - **Tkl+Int_per90** : Tacles + interceptions par 90 minutes
                """)

            # Liste de colonnes
            df_stat = filtered_df[
                ['name', 'image_url', 'Age', 'country_of_citizenship', 'current_club_name',
                'current_club_domestic_competition_id', 'market_value_in_eur','contract_expiration_date',
                'sub_position', selected_stat]
            ].dropna(subset=[selected_stat])

            # Traduction du pays du joueur dans la table
            df_stat['country_of_citizenship'] = df_stat['country_of_citizenship'].apply(
                lambda x: country_translation.get(x, x)
            )
            # Utilisation du format de market_value
            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value)

            # Filtrage spécial si la statistique sélectionnée est GA_per90
            if selected_stat == 'GA_per90':
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
                df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
            else:
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

            # Cas particuliers : exclusion des gardiens pour certaines statistiques
            if selected_stat in ['Won%', 'Tkl%']:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

            col1, col2, col3 = st.columns([1, 1, 1])
            podium_order = [1, 0, 2]  # 2e, 1er, 3e
            medals = ["🥈", "🥇", "🥉"]

            columns = [col1, col2, col3]

            # Limiter aux joueurs disponibles dans la tables
            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    with columns[display_index]:
                        st.markdown(f"{medals[display_index]} **{top3.loc[i, 'name']}**")
                        if pd.notna(top3.loc[i, 'image_url']):
                            st.image(top3.loc[i, 'image_url'], width=150)
                        st.markdown(f"**{selected_stat} :** {round(top3.loc[i, selected_stat], 2)}")

            # Choix des colonnes dans la table
            final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
            final_df = final_df[[
                'name', 'Statistique', 'Age', 'country_of_citizenship', 'current_club_name', 'market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)


    else:
        # Display the title
        st.markdown("<h4 style='text-align: center;'>🏆 Player ranking</h4>", unsafe_allow_html=True)
        
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking.jpg") # Bulding the path for the image

        df = pd.read_csv("data/database_player.csv") # Recovering data

        all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # List of available statistics

        selected_stat = st.sidebar.selectbox("Choose a metric :", [""] + all_stats) # Choice of statistics in the sidebar
        
        if not selected_stat:
            # If the metric is selected, we hide the image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                
        if selected_stat:
            # Top of the sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filters")

                # Step 1: filter by selected statistic
                df_with_stat = df.dropna(subset=[selected_stat])
                if selected_stat in ['Saves_per90', '#OPA_per90']:
                    df_with_stat = df_with_stat[df_with_stat[selected_stat] != 0]

                filtered_df = df_with_stat.copy()  # Starting point for filters

                # Step 2: Position filter
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options = st.selectbox("Position", [""] + poste_options_raw )

                if poste_options:
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_options]

                # Step 3: League filter
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("League", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Step 4: Club filter
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Step 5: Country filter
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options = st.selectbox("Country", [""] + pays_options_raw )

                if pays_options:
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_options]

                # Step 6: Age group filter
                # Dynamically create the age ranges available
                tranche_options = [""]

                ages = filtered_df["Age"].dropna()

                if any(ages < 23):
                    tranche_options.append("< 23 yrs")
                if any((ages >= 24) & (ages <= 29)):
                    tranche_options.append("24-29 yrs")
                if any(ages >= 30):
                    tranche_options.append("30 yrs and +")

                age_group = st.selectbox("Age group", tranche_options) # Selector

                # Apply filter if selected
                if age_group:
                    if age_group == "< 23 yrs":
                        filtered_df = filtered_df[filtered_df["Age"] < 23]
                    elif age_group == "24-29 yrs":
                        filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                    elif age_group == "30 yrs abd +":
                        filtered_df = filtered_df[filtered_df["Age"] >= 30]

                # Step 7: Market value filter
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_min = st.slider(
                    "Minimum market value (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_min_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Minimum value selected : **{format_market_value(valeur_min)}**")
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] >= valeur_min]

            # Statistics glossary in the sidebar
            with st.sidebar.expander("Statistics glossary"):
                st.markdown("""
                ### Goalkeeper :
                - **GA_per90**: Goals conceded per 90 minutes  
                - **Saves_per_90**: Saves made per 90 minutes  
                - **Save%**: Save percentage  
                - **/90 (PSxG-GA/90)**: Post-Shot xG minus Goals Against per 90 minutes  
                - **PSxG+/-**: Post-Shot xG minus Goals Against  
                - **Err_per90**: Errors leading to shots per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **AvgLen**: Average pass length in yards  
                - **Launch%**: Percentage of long passes  
                - **Stp%**: Percentage of crosses stopped  
                - **#OPA_per90**: Defensive actions outside penalty area per 90 minutes  
                - **CS%**: Clean sheet percentage

                ### Center Back :
                - **Won%**: Aerial duels won percentage  
                - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                - **Tkl%**: Percentage of dribblers tackled  
                - **Clr_per90**: Clearances per 90 minutes  
                - **Err_per90**: Errors leading to shots  
                - **Touches_per90**: Ball touches per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **Sw_per90**: Switches (long diagonal passes) per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Fls_per90**: Fouls committed per 90 minutes  
                - **CrdY_per90**: Yellow cards per 90 minutes

                ### Full-backs :
                - **Gls_per90**: Goals per 90 minutes  
                - **xG_per90**: Expected Goals per 90 minutes  
                - **Ast_per90**: Assists per 90 minutes  
                - **xA_per90**: Expected Assists per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Touches_per90**: Ball touches per 90 minutes  
                - **Crs_per90**: Crosses per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                - **Tkl%**: Percentage of dribblers tackled  
                - **Err_per90**: Errors leading to shots  
                - **Clr_per90**: Clearances per 90 minutes  
                - **Fls_per90**: Fouls committed per 90 minutes  
                - **CrdY_per90**: Yellow cards per 90 minutes

                ### Midfielders :
                - **Gls_per90**: Goals per 90 minutes  
                - **xG_per90**: Expected Goals per 90 minutes  
                - **Ast_per90**: Assists per 90 minutes  
                - **xA_per90**: Expected Assists per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Touches_per90**: Ball touches per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **Won%**: Aerial duels won percentage  
                - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes  
                - **Tkl%**: Percentage of dribblers tackled  
                - **Err_per90**: Errors leading to shots  
                - **CrdY_per90**: Yellow cards per 90 minutes

                ### Attacking midfielders / Wingers :
                - **Gls_per90**: Goals per 90 minutes  
                - **xG_per90**: Expected Goals per 90 minutes  
                - **Ast_per90**: Assists per 90 minutes  
                - **xA_per90**: Expected Assists per 90 minutes  
                - **G/Sh**: Goals per shot  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Touches_per90**: Ball touches per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **1/3_per90**: Passes into final third per 90 minutes  
                - **Succ_per_90**: Successful take-ons per 90 minutes  
                - **Succ%**: Take-on success rate  
                - **Dis_per90**: Times dispossessed per 90 minutes  
                - **Fld**: Fouls drawn  
                - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes

                ### Forwards :
                - **Gls_per90**: Goals per 90 minutes  
                - **xG_per90**: Expected Goals per 90 minutes  
                - **Ast_per90**: Assists per 90 minutes  
                - **xA_per90**: Expected Assists per 90 minutes  
                - **G/Sh**: Goals per shot  
                - **Dist**: Average shot distance (in yards)  
                - **SoT_per90**: Shots on target per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Touches_per90**: Ball touches per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **1/3_per90**: Passes into final third per 90 minutes  
                - **Fld**: Fouls drawn  
                - **Tkl+Int_per90**: Tackles + interceptions per 90 minutes
                """)

            # Selecting columns
            df_stat = filtered_df[
                ['name', 'image_url', 'Age', 'country_of_citizenship', 'current_club_name',
                'current_club_domestic_competition_id', 'market_value_in_eur','contract_expiration_date',
                'sub_position', selected_stat]
            ].dropna(subset=[selected_stat])

            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value) # Format market value

            # Special filtering if the selected statistic is GA_per90
            if selected_stat == 'GA_per90':
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
                df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
            else:
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

            # Special cases: exclusion of goalkeepers for certain statistics
            if selected_stat in ['Won%', 'Tkl%']:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            top3 = df_stat.head(3).reset_index(drop=True) # Displaying podium

            col1, col2, col3 = st.columns([1, 1, 1])
            podium_order = [1, 0, 2]  # 2nd, 1st, 3rd
            medals = ["🥈", "🥇", "🥉"]

            columns = [col1, col2, col3]

            # Limit to available players
            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    with columns[display_index]:
                        st.markdown(f"{medals[display_index]} **{top3.loc[i, 'name']}**")
                        if pd.notna(top3.loc[i, 'image_url']):
                            st.image(top3.loc[i, 'image_url'], width=150)
                        st.markdown(f"**{selected_stat} :** {round(top3.loc[i, selected_stat], 2)}")

            # We display the table with the columns desired
            final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
            final_df = final_df[[
                'name', 'Statistic', 'Age', 'country_of_citizenship', 'current_club_name', 'market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)

# Appel de la fonction associé à la demande de l'utilisateur / Call of the function associated with the user request / 
if menu in ["Accueil", "Home"]:
    home()
elif menu in ["Joueur", "Player"]:
    player_analysis()
elif menu in ["Duel", "F2F"]:
    player_comparison()
elif menu in ["Classement", "Ranking"]:
    ranking()