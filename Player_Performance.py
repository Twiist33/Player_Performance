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
from mplsoccer import PyPizza, FontManager
from matplotlib.patches import Patch
import base64

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
    options=["Menu", "Joueur", "Duel","Stats", "Stats +", "Scout"] if lang == "Français" else
            ["Home", "Player", "F2F","Stats", "Stats +","Scout"],
    icons=["house", "person", "crosshair","trophy", "list-ol","binoculars"],
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
    "Second Striker": "Attaquants",
    "Centre-Forward": "Attaquants"
}

# Traduction des catégories statistiques de base en français / Translating basic statistical categories into French
base_stat_translation = {
    "goal_scoring_created": "Création de buts",
    "goal_scoring_conceded": "Occasions concédées",
    "efficiency": "Efficacité",
    "error_fouls": "Erreurs et fautes",
    "short_clearance": "Relance courte",
    "long_clearance": "Relance longue",
    "positioning": "Positionnement",
    "aerial_defense": "Jeu aérien défensif",
    "finish": "Finition",
    "building": "Construction du jeu",
    "creation": "Création d'occasions",
    "dribble": "Dribbles",
    "projection": "Projection",
    "defensive_actions": "Actions défensives",
    "waste": "Pertes de balle",
    "faults_committed": "Fautes commises",
    "provoked_fouls": "Fautes provoquées",
    "aerial": "Jeu aérien"
}

# Statistiques par catégorie pour le radar / Statistics by categorie for the radar plot
category_stats = {
    "Gardiens de but": ["GA_per90", "PSxG_per90", "/90", "Save%", "PSxG+/-", "Err_per90","Launch%", "AvgLen", "Cmp%", "AvgDist", "#OPA_per90", "Stp%"],
    "Défenseurs centraux": ["G-PK_per90", "PrgP_per90","Cmp%","xAG_per90","PrgC_per90","Err_per90","Tkl%","Int_per90","Tkl_per90","CrdY_per90","Won_per90","Won%" ],
    "Défenseurs latéraux": ["G-PK_per90", "PrgP_per90", "Cmp%", "xAG_per90", "Succ_per90", "PrgC_per90", "Err_per90", "Tkl%", "Int_per90", "Tkl_per90", "CrdY_per90", "Won%"],
    "Milieux de terrain": ["G-PK_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "PrgC_per90", "Fld_per90", "Err_per90", "Tkl%", "Int_per90", "CrdY_per90", "Won%"],
    "Milieux offensifs / Ailiers": ["npxG_per90","G-PK_per90", "G-xG_per90", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90", "Succ_per90", "Succ%", "PrgC_per90", "Fld_per90", "Dis_per90"],
    "Attaquants": ["npxG_per90","Sh_per90", "G-PK_per90", "G-xG_per90", "G/Sh", "PrgP_per90", "PrgR_per90", "Cmp%", "xAG_per90","Succ_per90", "PrgC_per90", "Dis_per90"    ]
}

# Fonction pour renommer les noms des catégories / Function for renaming category names
def format_stat_name(stat):
    if stat.startswith("score_"):
        return stat.replace("score_", "").replace("_", " ").capitalize()
    return stat.capitalize() if stat == "rating" else stat

# Fonction pour effectuer un radar plot avec les données / Radar plot function with data
def plot_pizza_radar(labels, player_values, median_values, title="Radar",legend_labels=("Joueur", "Médiane")):
    # Paramètres de la pizza plot / Parameters of the pizza plot
    pizza = PyPizza(
        params=labels,
        background_color="#EFF0D1",
        straight_line_color="#000000",
        straight_line_lw=1,
        last_circle_lw=1,
        last_circle_color="#000000",
        other_circle_ls="--",
        other_circle_color="#000000",
        other_circle_lw=0.5
    )
    
    # Mise des couleurs et valeurs sur la pizza plot / Dislay colors and values on the pizza plot
    fig, ax = pizza.make_pizza(
        values=[round(v) for v in player_values],
        compare_values=[round(v) for v in median_values],
        figsize=(8, 8),
        kwargs_slices=dict(
            facecolor="#7FBFFF", edgecolor="#000000", zorder=2, linewidth=1
        ),
        kwargs_compare=dict(
            facecolor="#e63946", edgecolor="#000000", zorder=1, linewidth=1
        ),
        kwargs_params=dict(
            color="#000000", fontsize=11, va="center"
        ),
        kwargs_values=dict(
            color="#000000", fontsize=11, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#7FBFFF", boxstyle="round,pad=0.2", lw=1)
        ),
        kwargs_compare_values=dict(
            color="#000000", fontsize=11, zorder=3,
            bbox=dict(edgecolor="#000000", facecolor="#f08080", boxstyle="round,pad=0.2", lw=1)
        )
    )

    # Ajustement si valeurs proches / Adjustment if values are close
    threshold = 10
    params_offset = [
        abs(p - m) < threshold for p, m in zip(player_values, median_values)
    ]
    pizza.adjust_texts(params_offset, offset=-0.17, adj_comp_values=True)

    # Titre du radar / Radar title
    fig.text(
        0.5, 1.00, title,
        ha="center", fontsize=14, fontweight="bold", color="#000000"
    )

    # Légende personnalisée / Custom legend
    legend_elements = [
        Patch(facecolor="#7FBFFF", edgecolor='black', label=legend_labels[0]),
        Patch(facecolor="#e63946", edgecolor='black', label=legend_labels[1])
    ]
    ax.legend(
        handles=legend_elements,
        loc='lower center', bbox_to_anchor=(0.5, -0.15),
        ncol=2, fontsize=10, frameon=False
    )

    return fig

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
                <li><strong>🏆 Classement des joueurs (Stats de Base) </strong> : Classement des joueurs par performance selon une statistique de base choisie</li>
                <li><strong>🥇 Classement des joueurs (Stats Avancées) </strong> : Classement des joueurs par performance selon une statistique avancée choisie</li>
                <li><strong>🔎 Scouting </strong> : Établissement d'une liste de joueurs collant aux critères choisis</li>
            </ul>

            <br>

            Pour plus de détails sur ce projet, vous avez à votre disposition :
            <ul>
                <li><em>La documentation du projet</em></li>
                <li><a href="https://player-performance-big-5-24-25-romain-traboul.streamlit.app/" target="_blank">Le code associé à l'application</a></li>
                <li><em>Et enfin mon CV</em></li>
            </ul>
            """,
            unsafe_allow_html=True
        )

        # Encodage base64 des fichiers PDF
        doc_base64 = base64.b64encode(doc).decode()
        cv_base64 = base64.b64encode(cv_data_fr).decode()

        # HTML pour les boutons centrés, responsive
        st.markdown(
            f"""
            <div style='
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 2rem;
                margin-bottom: 1.5rem;
            '>
                <div style="text-align: center;">
                    <a href="data:application/pdf;base64,{doc_base64}" download="Documentation_Player_Performance_France.pdf">
                        <button style="padding: 0.5rem 1.2rem; font-size: 1rem;">Documentation</button>
                    </a>
                </div>
                <div style="text-align: center;">
                    <a href="data:application/pdf;base64,{cv_base64}" download="CV_FR_Romain_Traboul.pdf">
                        <button style="padding: 0.5rem 1.2rem; font-size: 1rem;">Mon CV en français</button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )




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
                <li><strong>🏆 Player Ranking (Advanced Statistics) </strong>: Rank players based on a chosen advanced statistic</li>
                <li><strong>🥇 Player Ranking (Basis Statistics) </strong>: Rank players based on a chosen basis statistic</li>
                <li><strong>🔎 Scouting </strong> : Drawing up a list of players matching the chosen criteria</li>
            </ul>

            <br>

            For more details about this project, you can refer to:
            <ul>
                <li><em>The project documentation</em></li>
                <li><a href="https://player-performance-big-5-24-25-romain-traboul.streamlit.app/" target="_blank">The code used to build the application</a></li>
                <li><em>My resume</em></li>
            </ul>
            """, unsafe_allow_html=True
        )

        # Encodage base64 des fichiers PDF
        doc_base64 = base64.b64encode(doc_eng).decode()
        cv_base64 = base64.b64encode(cv_data_eng).decode()

        # HTML pour les boutons centrés, responsive
        st.markdown(
            f"""
            <div style='
                display: flex;
                justify-content: center;
                flex-wrap: wrap;
                gap: 2rem;
                margin-bottom: 1.5rem;
            '>
                <div style="text-align: center;">
                    <a href="data:application/pdf;base64,{doc_base64}" download="Documentation_Player_Performance_France.pdf">
                        <button style="padding: 0.5rem 1.2rem; font-size: 1rem;">Documentation</button>
                    </a>
                </div>
                <div style="text-align: center;">
                    <a href="data:application/pdf;base64,{cv_base64}" download="CV_ENG_Romain_Traboul.pdf">
                        <button style="padding: 0.5rem 1.2rem; font-size: 1rem;">My CV in english</button>
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


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
                st.info("Dérouler la barre latérale pour choisir la langue et le joueur à analyser")
        else:
            player_data = df[df['name'] == selected_player].iloc[0] # Filtrer le DataFrame pour le joueur sélectionné

            # Récupération des traductions
            pays = country_translation.get(player_data['country_of_citizenship'], player_data['country_of_citizenship'])
            poste = position_translation.get(player_data['sub_position'], player_data['sub_position'])

            # Profil du joueur (image à gauche, infos à droite)
            st.markdown("<h4 style='text-align: center;'>Profil du joueur</h4>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

            <div style="flex: 1; text-align: center; min-width: 180px;">
                <img src="{player_data['image_url']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
            </div>

            <div style="flex: 2; min-width: 280px;">
                <p><strong>Nom :</strong> {player_data['name']}</p>
                <p><strong>Âge :</strong> {int(player_data['Age']) if pd.notna(player_data['Age']) else "-"}</p>
                <p><strong>Pays :</strong> {pays}</p>
                <p><strong>Club :</strong> {player_data['current_club_name']}</p>
                <p><strong>Poste :</strong> {poste}</p>
            </div>

            <div style="flex: 2; min-width: 280px;">
                <p><strong>Taille :</strong> {int(player_data['height_in_cm']) if pd.notna(player_data['height_in_cm']) else "-" } cm</p>
                <p><strong>Valeur marchande :</strong> {format_market_value(player_data['market_value_in_eur'])}</p>
                <p><strong>Fin de contrat :</strong> {player_data['contract_expiration_date'] if pd.notna(player_data['contract_expiration_date']) else "-"}</p>
                <p><strong>Matches joués :</strong> {int(player_data['MP']) if pd.notna(player_data['MP']) else "-"}</p>
                <p><strong>Minutes jouées :</strong> {int(player_data['Min']) if pd.notna(player_data['Min']) else "-"}</p>
            </div>

            </div>
            """, unsafe_allow_html=True)

            # Filtre unique pour radar + similarité
            comparison_filter = st.radio(
                "En comparaison à son poste : ",
                options=[
                    "Vue globale",
                    "Championnat",
                    "Tranche d’âge",
                    "Pays"
                ],
                index=0,
                horizontal=True
            )

            filter_arg = {
                "Vue globale": None,
                "Championnat": "championnat",
                "Tranche d’âge": "tranche_age",
                "Pays": "pays"
            }[comparison_filter]

            poste_cat = position_category.get(player_data['sub_position'], None)

            # Glossaire des statistiques associées
            with st.expander(" Glossaire des statistiques"):
                if poste_cat:

                    if poste_cat == "Gardiens de but":
                        st.markdown("""
                        - **GA_per90** : Buts encaissés par 90 minutes 
                        - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                        - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                        - **Save%** : Pourcentage d’arrêts effectués  
                        - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                        - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                        - **Launch%** : Pourcentage de passes longues  
                        - **AvgLen** : Longueur moyenne des passes (en yards)  
                        - **Cmp%** : Pourcentage de passes réussies  
                        - **AvgDist** : Distance moyenne des passes (en yards)  
                        - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                        - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                        """)

                    elif poste_cat == "Défenseurs centraux":
                        st.markdown("""
                        - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                        - **PrgP_per90** : Passes progressives par 90 minutes
                        - **Cmp%** : Pourcentage de passes réussies
                        - **xAG_per90** : Expected Assisted Goals par 90 minutes
                        - **PrgC_per90** : Conduites progressives par 90 minutes
                        - **Err_per90** : Erreurs menant à un tir adverse
                        - **Tkl%** : Pourcentage de tacles effectués
                        - **Int_per90** : Interceptions par 90 minutes
                        - **Tkl_per90** : Tacles par 90 minutes
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        - **Won_per90** : Duels aériens gagnés par 90 minutes
                        - **Won%** : Pourcentage de duels aériens gagnés
                        """)

                    elif poste_cat == "Défenseurs latéraux":
                        st.markdown("""
                        - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                        - **PrgP_per90** : Passes progressives par 90 minutes
                        - **Cmp%** : Pourcentage de passes réussies
                        - **xAG_per90** : Expected Assisted Goals par 90 minutes
                        - **PrgC_per90** : Conduites progressives par 90 minutes
                        - **Err_per90** : Erreurs menant à un tir adverse
                        - **Tkl%** : Pourcentage de tacles effectués 
                        - **Int_per90** : Interceptions par 90 minutes
                        - **Tkl_per90** : Tacles par 90 minutes
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        - **Won_per90** : Duels aériens gagnés par 90 minutes
                        - **Won%** : Pourcentage de duels aériens gagnés 
                        """)

                    elif poste_cat == "Milieux de terrain":
                        st.markdown("""
                        - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                        - **PrgP_per90** : Passes progressives par 90 minutes
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes
                        - **Cmp%** : Pourcentage de passes réussies
                        - **xAG_per90** : Expected Assisted Goals par 90 minutes
                        - **PrgC_per90** : Conduites progressives par 90 minutes
                        - **Fld_per90** : Fautes subies par 90 minutes
                        - **Err_per90** : Erreurs menant à un tir adverse
                        - **Tkl%** : Pourcentage de tacles effectués 
                        - **Int_per90** : Interceptions par 90 minutes
                        - **CrdY_per90** : Cartons jaunes par 90 minutes
                        - **Won%** : Pourcentage de duels aériens gagnés 
                        """)

                    elif poste_cat == "Milieux offensifs / Ailiers":
                        st.markdown("""
                        - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                        - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                        - **G-xG_per90** : Expected Goals par 90 minutes
                        - **PrgP_per90** : Passes progressives par 90 minutes
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes
                        - **Cmp%** : Pourcentage de passes réussies
                        - **xAG_per90** : Expected Assisted Goals par 90 minutes
                        - **Succ_per90** : Dribbles réussis par 90 minutes
                        - **Succ%** : Pourcentage de dribbles réussis
                        - **PrgC_per90** : Conduites progressives par 90 minutes
                        - **Fld_per90** : Fautes subies par 90 minutes
                        - **Dis_per90** : Ballons perdus par 90 minutes
                        """)

                    elif poste_cat == "Attaquants":
                        st.markdown("""
                        - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                        - **Sh_per90** : Tirs tentés par 90 minutes
                        - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                        - **G-xG_per90** : Expected Goals par 90 minutes
                        - **G/Sh** : Buts par tir  
                        - **PrgP_per90** : Passes progressives par 90 minutes  
                        - **PrgR_per90** : Passes progressives reçues par 90 minutes
                        - **Cmp%** : Pourcentage de passes réussies
                        - **xAG_per90** : Expected Assisted Goals par 90 minutes
                        - **Succ_per_90** : Dribbles réussis par 90 minutes  
                        - **PrgC_per90** : Conduites progressives par 90 minutes  
                        - **Dis_per90** : Ballons perdus par 90 minutes  
                        """)

            if poste_cat and poste_cat in category_stats:
                stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]
                player_rating = player_data.get("rating", None)

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

                    # Calcul de la note si elle existe
                    rating_text = f" - Note : {round(player_rating, 2)}" if player_rating is not None else ""

                    # Affichage du titre avec note
                    st.markdown(
                        f"<h4 style='text-align: center;'>Radar de performance de {player_data['name']} vs {nb_players} joueurs dans sa catégorie {rating_text}</h4>",
                        unsafe_allow_html=True
                    )

                    # Construction de la pizza plot (joueur-médiane à son poste) pour les statistiques avancées
                    fig_pizza_stat_adv = plot_pizza_radar(
                        labels=stats_cols,
                        player_values=player_norm * 100,
                        median_values=group_median * 100,
                        title=f"Statistiques avancées de {player_data['name']} de vs Médiane à son poste",
                        legend_labels=(player_data['name'], "Médiane poste")
                    )

                    # Liste des colonnes à afficher selon le poste
                    if poste_cat == "Gardiens de but":
                        pizza_cols = [
                            "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                            "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                        ]
                    else:
                        pizza_cols = [
                            "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                            "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                            "score_faults_committed", "score_provoked_fouls", "score_aerial"
                        ]

                    # On garde uniquement les colonnes présentes
                    pizza_cols = [col for col in pizza_cols if col in df.columns]
                    pizza_labels = [base_stat_translation.get(col.replace("score_", ""), col) for col in pizza_cols]

                    # Vérifie que toutes les colonnes existent pour le joueur
                    if all(col in player_data for col in pizza_cols):

                        player_values = [player_data[col] for col in pizza_cols]

                        # Calcul des valeurs médianes sur le groupe filtré
                        group_df_scores = group_df[pizza_cols].dropna()
                        if len(group_df_scores) >= 5:
                            group_median = group_df_scores.median().tolist()

                            player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                            median_scaled = [round(v) for v in group_median]

                            # Construction de la pizza plot (joueur-médiane) pour les statistiques de base
                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,
                                player_values=player_scaled,
                                median_values=median_scaled,
                                title=f"Statistiques de base de {player_data['name']} vs Médiane à son poste",
                                legend_labels=(player_data['name'], "Médiane poste")
                            )

                            # Affichage dans Streamlit
                            col1, col2 = st.columns(2)
                            with col1:
                                st.pyplot(fig_pizza_stat_basis)
                            with col2:
                                st.pyplot(fig_pizza_stat_adv)

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
                st.info("Scroll down the sidebar to select the language and the player you wish to analyze")
        else:
            player_data = df[df['name'] == selected_player].iloc[0] # Filter the DataFrame for the selected player

            # Player profile (image on left, info on right)
            st.markdown(
                f"<h4 style='text-align: center;'>Player profile</h4>",
                unsafe_allow_html=True
            )

            st.markdown(f"""
            <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto;">

            <div style="flex: 1; text-align: center; min-width: 180px;">
                <img src="{player_data['image_url']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
            </div>

            <div style="flex: 2; min-width: 280px;">
                <p><strong>Name :</strong> {player_data['name']}</p>
                <p><strong>Age :</strong> {int(player_data['Age']) if pd.notna(player_data['Age']) else "-"}</p>
                <p><strong>Country :</strong> {player_data['country_of_citizenship']}</p>
                <p><strong>Club :</strong> {player_data['current_club_name']}</p>
                <p><strong>Position :</strong> {player_data['sub_position']}</p>
            </div>

            <div style="flex: 2; min-width: 280px;">
                <p><strong>Height :</strong> {int(player_data['height_in_cm']) if pd.notna(player_data['height_in_cm']) else "-" } cm</p>
                <p><strong>Market Value :</strong> {format_market_value(player_data['market_value_in_eur'])}</p>
                <p><strong>Contract :</strong> {player_data['contract_expiration_date'] if pd.notna(player_data['contract_expiration_date']) else "-"}</p>
                <p><strong>Matches Played :</strong> {int(player_data['MP']) if pd.notna(player_data['MP']) else "-"}</p>
                <p><strong>Minutes Played :</strong> {int(player_data['Min']) if pd.notna(player_data['Min']) else "-"}</p>
            </div>

            </div>
            """, unsafe_allow_html=True)

            # Single filter for radar + similarity
            comparison_filter = st.radio(
                "Compared to his position :",
                options=[
                    "Overview",
                    "Championship",
                    "Age group",
                    "Country"
                ],
                index=0,
                horizontal=True
            )

            filter_arg = {
                "Overview": None,
                "Championship": "championnat",
                "Age group": "tranche_age",
                "Country": "pays"
            }[comparison_filter]

            poste_cat = position_category.get(player_data['sub_position'], None)

            # Glossary of Statistics associated
            with st.expander("Glossary of Statistics"):
                if poste_cat:
                    if poste_cat == "Gardiens de but":
                        st.markdown("""
                        - **GA_per90**: Goals conceded per 90 minutes  
                        - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                        - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                        - **Save%**: Save percentage  
                        - **PSxG+/-**: Difference between PSxG and goals conceded  
                        - **Err_per90**: Errors leading to a shot per 90 minutes  
                        - **Launch%**: Percentage of long passes  
                        - **AvgLen**: Average pass length (in yards)  
                        - **Cmp%**: Pass completion percentage  
                        - **AvgDist**: Average pass distance (in yards)  
                        - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                        - **Stp%**: Percentage of crosses stopped inside the box 
                        """)

                    elif poste_cat == "Défenseurs centraux":
                        st.markdown("""
                        - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Err_per90**: Errors leading to a shot  
                        - **Tkl%**: Tackle success rate  
                        - **Int_per90**: Interceptions per 90 minutes  
                        - **Tkl_per90**: Tackles per 90 minutes  
                        - **CrdY_per90**: Yellow cards per 90 minutes  
                        - **Won_per90**: Aerial duels won per 90 minutes  
                        - **Won%**: Aerial duel success rate  
                        """)

                    elif poste_cat == "Défenseurs latéraux":
                        st.markdown("""
                        - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Err_per90**: Errors leading to a shot  
                        - **Tkl%**: Tackle success rate  
                        - **Int_per90**: Interceptions per 90 minutes  
                        - **Tkl_per90**: Tackles per 90 minutes  
                        - **CrdY_per90**: Yellow cards per 90 minutes  
                        - **Won_per90**: Aerial duels won per 90 minutes  
                        - **Won%**: Aerial duel success rate  
                        """)

                    elif poste_cat == "Milieux de terrain":
                        st.markdown("""
                        - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Fld_per90**: Fouls drawn per 90 minutes  
                        - **Err_per90**: Errors leading to a shot  
                        - **Tkl%**: Tackle success rate  
                        - **Int_per90**: Interceptions per 90 minutes  
                        - **CrdY_per90**: Yellow cards per 90 minutes  
                        - **Won%**: Aerial duel success rate 
                        """)

                    elif poste_cat == "Milieux offensifs / Ailiers":
                        st.markdown("""
                        - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                        - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                        - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                        - **Succ_per90**: Successful dribbles per 90 minutes  
                        - **Succ%**: Dribble success rate  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Fld_per90**: Fouls drawn per 90 minutes  
                        - **Dis_per90**: Dispossessions per 90 minutes
                        """)

                    elif poste_cat == "Attaquants":
                        st.markdown("""
                        - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                        - **Sh_per90**: Shots attempted per 90 minutes  
                        - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                        - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                        - **G/Sh**: Goals per shot  
                        - **PrgP_per90**: Progressive passes per 90 minutes  
                        - **PrgR_per90**: Progressive passes received per 90 minutes  
                        - **Cmp%**: Pass completion percentage  
                        - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                        - **Succ_per_90**: Successful dribbles per 90 minutes  
                        - **PrgC_per90**: Progressive carries per 90 minutes  
                        - **Dis_per90**: Dispossessions per 90 minutes 
                        """)

            if poste_cat and poste_cat in category_stats:
                stats_cols = [col for col in category_stats[poste_cat] if col in df.columns]
                player_rating = player_data.get("rating", None)

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

                    # Rating calculation if available
                    rating_text = f" - Rating : {round(player_rating, 2)}" if player_rating is not None else ""

                    # Title display with note
                    st.markdown(
                        f"<h4 style='text-align: center;'>Performance radar from {player_data['name']} vs {nb_players} players in his category {rating_text}</h4>",
                        unsafe_allow_html=True
                    )
                    
                    # Bulding the pizza plot (player-median) for the advanced statistics
                    fig_pizza_stat_adv = plot_pizza_radar(
                        labels=stats_cols,
                        player_values=player_norm * 100,
                        median_values=group_median * 100,
                        title=f"Advanced statistics of {player_data['name']} vs. median at the same position",
                        legend_labels=(player_data['name'], "Median position")
                    )

                    # List of columns to be displayed by position
                    if poste_cat == "Gardiens de but":
                        pizza_cols = [
                            "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                            "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                        ]
                    else:
                        pizza_cols = [
                            "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                            "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                            "score_faults_committed", "score_provoked_fouls", "score_aeria"
                        ]

                    # We keep only the columns present
                    pizza_cols = [col for col in pizza_cols if col in df.columns]
                    pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                    # Checks that all columns exist for the player
                    if all(col in player_data for col in pizza_cols):

                        player_values = [player_data[col] for col in pizza_cols]

                        # Calculation of median values on the filtered group
                        group_df_scores = group_df[pizza_cols].dropna()
                        if len(group_df_scores) >= 5:
                            group_median = group_df_scores.median().tolist()

                            player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                            median_scaled = [round(v) for v in group_median]

                            # Bulding the pizza plot (player-median) for the basic statistics
                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,
                                player_values=player_scaled,
                                median_values=median_scaled,
                                title=f"Basic statistics of {player_data['name']} vs. median at the same position",
                                legend_labels=(player_data['name'], "Median position")
                            )

                    # List of columns to be displayed by position
                    if poste_cat == "Gardiens de but":
                        pizza_cols = [
                            "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                            "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                        ]
                    else:
                        pizza_cols = [
                            "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                            "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                            "score_faults_committed", "score_provoked_fouls", "score_aeria"
                        ]

                    # We keep only the columns present
                    pizza_cols = [col for col in pizza_cols if col in df.columns]
                    pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                    # Checks that all columns exist for the player
                    if all(col in player_data for col in pizza_cols):

                        player_values = [player_data[col] for col in pizza_cols]

                        # Calculation of median values on the filtered group
                        group_df_scores = group_df[pizza_cols].dropna()
                        if len(group_df_scores) >= 5:
                            group_median = group_df_scores.median().tolist()

                            player_scaled = [v if pd.notna(v) else 0 for v in player_values]
                            median_scaled = [round(v) for v in group_median]


                            fig_pizza_stat_basis = plot_pizza_radar(
                                labels=pizza_labels,
                                player_values=player_scaled,
                                median_values=median_scaled,
                                title="Basic statistics vs. median at the same position",
                                legend_labels=(player_data['name'], "Median position")
                            )

                            # Display in Streamlit
                            col1, col2 = st.columns(2)
                            with col1:
                                st.pyplot(fig_pizza_stat_basis)
                            with col2:
                                st.pyplot(fig_pizza_stat_adv)

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
                st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")

        if player1:
            # Nous stockons les informations du 1er joueur
            player1_data = df[df['name'] == player1].iloc[0]
            sub_position = player1_data['sub_position']
            poste_cat = position_category.get(sub_position, None)

            # Tous les sub_position de la même catégorie
            sub_positions_same_cat = [
                pos for pos, cat in position_category.items() if cat == poste_cat
            ]

            # On filtre tous les joueurs ayant un poste dans cette catégorie
            same_category_players = df[df['sub_position'].isin(sub_positions_same_cat)]
            player2_names = sorted(same_category_players['name'].dropna().unique().tolist())
            player2_names = [p for p in player2_names if p != player1]


            player2 = st.sidebar.selectbox("Second joueur (même poste) :", [''] + player2_names, key="player2") # Sélection du 2nd joueur
            
            if not player2:
                # Aucun joueur sélectionné → afficher l'image d'intro
                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
                    st.info("Dérouler la barre latérale pour choisir la langue et les joueurs à analyser")


            if player2:
                player2_data = df[df['name'] == player2].iloc[0] # Récupération du nom du 2nd joueur
                
                # On affiche le profil des joueurs
                st.markdown("<h4 style='text-align: center;'>Profils des joueurs</h4>", unsafe_allow_html=True)

                for pdata in [player1_data, player2_data]:
                    # Traductions
                    pays = country_translation.get(pdata['country_of_citizenship'], pdata['country_of_citizenship'])
                    poste = position_translation.get(pdata['sub_position'], pdata['sub_position'])

                    st.markdown(f"""
                    <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                    <div style="flex: 1; text-align: center; min-width: 180px;">
                        <img src="{pdata['image_url']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                    </div>

                    <div style="flex: 2; min-width: 280px;">
                        <p><strong>Nom :</strong> {pdata['name']}</p>
                        <p><strong>Âge :</strong> {int(pdata['Age']) if pd.notna(pdata['Age']) else "-"}</p>
                        <p><strong>Pays :</strong> {pays}</p>
                        <p><strong>Club :</strong> {pdata['current_club_name']}</p>
                    </div>

                    <div style="flex: 2; min-width: 280px;">
                        <p><strong>Poste :</strong> {poste}</p>
                        <p><strong>Taille :</strong> {int(pdata['height_in_cm']) if pd.notna(pdata['height_in_cm']) else "-" } cm</p>
                        <p><strong>Valeur marchande :</strong> {format_market_value(pdata['market_value_in_eur'])}</p>
                        <p><strong>Fin de contrat :</strong> {pdata['contract_expiration_date'] if pd.notna(pdata['contract_expiration_date']) else "-"}</p>
                    </div>

                    </div>
                    """, unsafe_allow_html=True)

                # Glossaire des statistiques associées
                with st.expander(" Glossaire des statistiques"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90** : Buts encaissés par 90 minutes 
                            - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                            - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                            - **Save%** : Pourcentage d’arrêts effectués  
                            - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                            - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                            - **Launch%** : Pourcentage de passes longues  
                            - **AvgLen** : Longueur moyenne des passes (en yards)  
                            - **Cmp%** : Pourcentage de passes réussies  
                            - **AvgDist** : Distance moyenne des passes (en yards)  
                            - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                            - **Stp%** : Pourcentage de centres arrêtés dans la surface  
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués
                            - **Int_per90** : Interceptions par 90 minutes
                            - **Tkl_per90** : Tacles par 90 minutes
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won_per90** : Duels aériens gagnés par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués 
                            - **Int_per90** : Interceptions par 90 minutes
                            - **Tkl_per90** : Tacles par 90 minutes
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won_per90** : Duels aériens gagnés par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés 
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Fld_per90** : Fautes subies par 90 minutes
                            - **Err_per90** : Erreurs menant à un tir adverse
                            - **Tkl%** : Pourcentage de tacles effectués 
                            - **Int_per90** : Interceptions par 90 minutes
                            - **CrdY_per90** : Cartons jaunes par 90 minutes
                            - **Won%** : Pourcentage de duels aériens gagnés 
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **G-xG_per90** : Expected Goals par 90 minutes
                            - **PrgP_per90** : Passes progressives par 90 minutes
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **Succ_per90** : Dribbles réussis par 90 minutes
                            - **Succ%** : Pourcentage de dribbles réussis
                            - **PrgC_per90** : Conduites progressives par 90 minutes
                            - **Fld_per90** : Fautes subies par 90 minutes
                            - **Dis_per90** : Ballons perdus par 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                            - **Sh_per90** : Tirs tentés par 90 minutes
                            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                            - **G-xG_per90** : Expected Goals par 90 minutes
                            - **G/Sh** : Buts par tir  
                            - **PrgP_per90** : Passes progressives par 90 minutes  
                            - **PrgR_per90** : Passes progressives reçues par 90 minutes
                            - **Cmp%** : Pourcentage de passes réussies
                            - **xAG_per90** : Expected Assisted Goals par 90 minutes
                            - **Succ_per_90** : Dribbles réussis par 90 minutes  
                            - **PrgC_per90** : Conduites progressives par 90 minutes  
                            - **Dis_per90** : Ballons perdus par 90 minutes  
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
                    
                    player1_rating = player1_data.get("rating", None)
                    player2_rating = player2_data.get("rating", None)

                    # Calcul de la note si elle existe
                    rating1_text = f"Note : {round(player1_rating)}" if player1_rating is not None else ""
                    rating2_text = f"Note : {round(player2_rating)}" if player2_rating is not None else ""
                    
                    # Affichage du titre et du radar
                    st.markdown(
                        f"<h4 style='text-align: center;'>Radar comparatif : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",
                        unsafe_allow_html=True
                    )
                    
                    # Création de la la pizza plot des statistiques avancées
                    fig_pizza_stat_adv = plot_pizza_radar(
                        labels=stats_cols,
                        player_values=player1_norm * 100,
                        median_values=player2_norm * 100,
                        title=f"Statistiques avancées de {player1} vs {player2}",
                        legend_labels=(player1, player2)
                    )

                    # Liste de colonnes de score par poste
                    if poste_cat == "Gardiens de but":
                        pizza_cols = [
                            "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                            "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                        ]
                    else:
                        pizza_cols = [
                            "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                            "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                            "score_faults_committed", "score_provoked_fouls", "score_aeria"
                        ]

                    # Nous ne gardons uniquement les colonnes d'interêt pour le poste
                    pizza_cols = [col for col in pizza_cols if col in df.columns]
                    pizza_labels = [base_stat_translation.get(col.replace("score_", ""), col) for col in pizza_cols]

                    # Vérification si ces colonnes existent pour les deux joueurs
                    if all((col in player1_data) and (col in player2_data) for col in pizza_cols):

                        player1_values = [player1_data[col] for col in pizza_cols]
                        player2_values = [player2_data[col] for col in pizza_cols]

                        # Vérifie que les données sont valides pour les deux joueurs
                        player1_scaled = [v if pd.notna(v) else 0 for v in player1_values]
                        player2_scaled = [v if pd.notna(v) else 0 for v in player2_values]

                        # Création du radar comparatif (pizza plot) pour les statistiques de base
                        fig_pizza_stat_basis = plot_pizza_radar(
                            labels=pizza_labels,
                            player_values=player1_scaled,
                            median_values=player2_scaled,
                            title=f"Statistiques de base de {player1} vs {player2}",
                            legend_labels=(player1, player2)
                        )

                    # Affichage dans Streamlit
                    col1, col2 = st.columns(2)
                    with col1:
                        st.pyplot(fig_pizza_stat_basis)
                    with col2:
                        st.pyplot(fig_pizza_stat_adv)

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
                st.info("Scroll down the sidebar to select the language and players for analysis")

        if player1:
            # Collecting the data for the players
            player1_data = df[df['name'] == player1].iloc[0]
            sub_position = player1_data['sub_position']
            poste_cat = position_category.get(sub_position, None)

            # All sub_positions in the same category
            sub_positions_same_cat = [
                pos for pos, cat in position_category.items() if cat == poste_cat
            ]

            # We filter all players with a position in this category
            same_category_players = df[df['sub_position'].isin(sub_positions_same_cat)]
            player2_names = sorted(same_category_players['name'].dropna().unique().tolist())
            player2_names = [p for p in player2_names if p != player1]

            player2 = st.sidebar.selectbox("Second player (same position) :", [''] + player2_names, key="player2") # Select the 2nd player
            
            if not player2:
                # If the player is selected, we hide the image
                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
                    st.info("Scroll down the sidebar to select the language and players for analysis")
                    

            if player2:
                player2_data = df[df['name'] == player2].iloc[0] # Collecting the name of the player 2
                
                # We display players profiles
                st.markdown("<h4 style='text-align: center;'>Players profile</h4>", unsafe_allow_html=True)

                for pdata in [player1_data, player2_data]:
                    st.markdown(f"""
                    <div style="display: flex; flex-direction: row; justify-content: space-between; gap: 2rem; flex-wrap: nowrap; align-items: center; overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;">

                    <div style="flex: 1; text-align: center; min-width: 180px;">
                        <img src="{pdata['image_url']}" style="width: 100%; max-width: 150px; border-radius: 10px;">
                    </div>

                    <div style="flex: 2; min-width: 280px;">
                        <p><strong>Name:</strong> {pdata['name']}</p>
                        <p><strong>Age:</strong> {int(pdata['Age']) if pd.notna(pdata['Age']) else "-"}</p>
                        <p><strong>Country:</strong> {pdata['country_of_citizenship']}</p>
                        <p><strong>Club:</strong> {pdata['current_club_name']}</p>
                    </div>

                    <div style="flex: 2; min-width: 280px;">
                        <p><strong>Position:</strong> {pdata['sub_position']}</p>
                        <p><strong>Height:</strong> {int(pdata['height_in_cm']) if pd.notna(pdata['height_in_cm']) else "-"} cm</p>
                        <p><strong>Market Value:</strong> {format_market_value(pdata['market_value_in_eur'])}</p>
                        <p><strong>Contract:</strong> {pdata['contract_expiration_date'] if pd.notna(pdata['contract_expiration_date']) else "-"}</p>
                    </div>

                    </div>
                    """, unsafe_allow_html=True)

                # Glossary of Statistics associated
                with st.expander("Glossary of Statistics"):
                    if poste_cat:

                        if poste_cat == "Gardiens de but":
                            st.markdown("""
                            - **GA_per90**: Goals conceded per 90 minutes  
                            - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                            - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                            - **Save%**: Save percentage  
                            - **PSxG+/-**: Difference between PSxG and goals conceded  
                            - **Err_per90**: Errors leading to a shot per 90 minutes  
                            - **Launch%**: Percentage of long passes  
                            - **AvgLen**: Average pass length (in yards)  
                            - **Cmp%**: Pass completion percentage  
                            - **AvgDist**: Average pass distance (in yards)  
                            - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                            - **Stp%**: Percentage of crosses stopped inside the box 
                            """)

                        elif poste_cat == "Défenseurs centraux":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90**: Interceptions per 90 minutes  
                            - **Tkl_per90**: Tackles per 90 minutes  
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won_per90**: Aerial duels won per 90 minutes  
                            - **Won%**: Aerial duel success rate  
                            """)

                        elif poste_cat == "Défenseurs latéraux":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90**: Interceptions per 90 minutes  
                            - **Tkl_per90**: Tackles per 90 minutes  
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won_per90**: Aerial duels won per 90 minutes  
                            - **Won%**: Aerial duel success rate  
                            """)

                        elif poste_cat == "Milieux de terrain":
                            st.markdown("""
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Fld_per90**: Fouls drawn per 90 minutes  
                            - **Err_per90**: Errors leading to a shot  
                            - **Tkl%**: Tackle success rate  
                            - **Int_per90**: Interceptions per 90 minutes  
                            - **CrdY_per90**: Yellow cards per 90 minutes  
                            - **Won%**: Aerial duel success rate
                            """)

                        elif poste_cat == "Milieux offensifs / Ailiers":
                            st.markdown("""
                            - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **Succ_per90**: Successful dribbles per 90 minutes  
                            - **Succ%**: Dribble success rate  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Fld_per90**: Fouls drawn per 90 minutes  
                            - **Dis_per90**: Dispossessions per 90 minutes
                            """)

                        elif poste_cat == "Attaquants":
                            st.markdown("""
                            - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                            - **Sh_per90**: Shots attempted per 90 minutes  
                            - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                            - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                            - **G/Sh**: Goals per shot  
                            - **PrgP_per90**: Progressive passes per 90 minutes  
                            - **PrgR_per90**: Progressive passes received per 90 minutes  
                            - **Cmp%**: Pass completion percentage  
                            - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                            - **Succ_per_90**: Successful dribbles per 90 minutes  
                            - **PrgC_per90**: Progressive carries per 90 minutes  
                            - **Dis_per90**: Dispossessions per 90 minutes 
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

                    player1_rating = player1_data.get("rating", None)
                    player2_rating = player2_data.get("rating", None)

                    # Rating calculation if available
                    rating1_text = f"Rating : {round(player1_rating)}" if player1_rating is not None else ""
                    rating2_text = f"Rating : {round(player2_rating)}" if player2_rating is not None else ""
                    
                    # Title and radar display
                    st.markdown(
                        f"<h4 style='text-align: center;'>Radar comparison : {player1} ({rating1_text}) vs {player2} ({rating2_text})</h4>",
                        unsafe_allow_html=True
                    )
                    
                    # Creating the advanced statistics pizza plot
                    fig_pizza_stat_adv = plot_pizza_radar(
                        labels=stats_cols,
                        player_values=player1_norm * 100,
                        median_values=player2_norm * 100,
                        title=f"Advanced statistics of {player1} vs {player2}",
                        legend_labels=(player1, player2)
                    )

                    # List of score columns by position
                    if poste_cat == "Gardiens de but":
                        pizza_cols = [
                            "score_goal_scoring_conceded", "score_efficiency", "score_error_fouls",
                            "score_short_clearance", "score_long_clearance", "score_positioning", "score_aerial_defense"
                        ]
                    else:
                        pizza_cols = [
                            "score_goal_scoring_created", "score_finish", "score_building", "score_creation",
                            "score_dribble", "score_projection", "score_defensive_actions", "score_waste",
                            "score_faults_committed", "score_provoked_fouls", "score_aeria"
                        ]

                    # We keep only the columns of interest for the post
                    pizza_cols = [col for col in pizza_cols if col in df.columns]
                    pizza_labels = [col.replace("score_", "").replace("_", " ").capitalize() for col in pizza_cols]

                    # Check if these columns exist for both players
                    if all((col in player1_data) and (col in player2_data) for col in pizza_cols):

                        player1_values = [player1_data[col] for col in pizza_cols]
                        player2_values = [player2_data[col] for col in pizza_cols]

                        # Checks that data is valid for both players
                        player1_scaled = [v if pd.notna(v) else 0 for v in player1_values]
                        player2_scaled = [v if pd.notna(v) else 0 for v in player2_values]

                        # Creation of comparative radar (pizza plot) for the basic statistics
                        fig_pizza_stat_basis = plot_pizza_radar(
                            labels=pizza_labels,
                            player_values=player1_scaled,
                            median_values=player2_scaled,
                            title=f"Basic statistics of {player1} vs {player2}",
                            legend_labels=(player1, player2)
                        )

                    # Display in Streamlit
                    col1, col2 = st.columns(2)
                    with col1:
                        st.pyplot(fig_pizza_stat_basis)
                    with col2:
                        st.pyplot(fig_pizza_stat_adv)

# Page du classement des joueurs pour les statistiques de base / Player ranking page by basis statistics
def ranking_basis():
    # Page en français
    if lang == "Français":
        st.markdown("<h4 style='text-align: center;'>🏅 Classement des joueurs (0-100) pour les statistiques de base selon leur position</h4>", unsafe_allow_html=True) # Affichage du titre de la page
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking_basis.jpg") # Construction du chemin pour l'image
        df = pd.read_csv("data/database_player.csv") # Récupération des données
        
        # Récupération des colonnes "score_" + "rating"
        all_stats_raw = [col for col in df.columns if col.startswith("score_")]
        if "rating" in df.columns:
            all_stats_raw.append("rating")

        # Traduction pour l'affichage
        translated_stats = [
            base_stat_translation.get(col.replace("score_", ""), "Note") if col == "rating"
            else base_stat_translation.get(col.replace("score_", ""), col)
            for col in all_stats_raw
        ]
        stat_name_mapping = dict(zip(translated_stats, all_stats_raw))
        
        selected_stat_display = st.sidebar.selectbox("Choisissez une statistique :", [""] + translated_stats) # Demande à l'utilisateur du choix de statistique
        
        selected_stat = stat_name_mapping.get(selected_stat_display, None)

        if not selected_stat:
            # Si la métrique est selectionné, nous cachons l'image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")

                
        if selected_stat:
            # Début de la sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filtres")
                
                df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                # Filtre Poste
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options_fr = [""] + [position_translation.get(p, p) for p in poste_options_raw]
                poste_fr = st.selectbox("Poste", poste_options_fr)

                if poste_fr:
                    poste_en = {v: k for k, v in position_translation.items()}.get(poste_fr, poste_fr)
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_en]

                # Filtre Championnat
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("Championnat", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Filtre Club
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Filtre Pays
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options_fr = [""] + [country_translation.get(p, p) for p in pays_options_raw]
                pays_fr = st.selectbox("Pays", pays_options_fr)

                if pays_fr:
                    pays_en = {v: k for k, v in country_translation.items()}.get(pays_fr, pays_fr)
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_en]

                # Filtre Tranche d’âge (création dynamiquement des tranches d'âge disponibles)
                tranche_options = [""]

                ages = filtered_df["Age"].dropna()

                if any(ages < 23):
                    tranche_options.append("< 23 ans")
                if any((ages >= 24) & (ages <= 29)):
                    tranche_options.append("24-29 ans")
                if any(ages >= 30):
                    tranche_options.append("30 ans et +")

                age_group = st.selectbox("Tranche d'âge", tranche_options) # Sélecteur de la trancge d'âge

                # Appliquer le filtre si sélectionné
                if age_group:
                    if age_group == "< 23 ans":
                        filtered_df = filtered_df[filtered_df["Age"] < 23]
                    elif age_group == "24-29 ans":
                        filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                    elif age_group == "30 ans et +":
                        filtered_df = filtered_df[filtered_df["Age"] >= 30]

                # Filtre de valeur marchande
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_max = st.slider(
                    "Valeur marchande maximum (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_max_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Valeur maximum sélectionné : **{format_market_value(valeur_max)}**") # Affichage du choix de l'utilisateur
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] <= valeur_max]

            # Définir les statistiques spécifiques aux gardiens
            goalkeeper_stats = [
                "goal_scoring_conceded", "efficiency", "error_fouls",
                "short_clearance", "long_clearance", "positioning", "aerial_defense"
            ]

            # Liste de colonnes
            df_stat = filtered_df[
                ['name', 'image_url', 'Age', 'country_of_citizenship', 'current_club_name',
                'current_club_domestic_competition_id', 'market_value_in_eur','contract_expiration_date',
                'sub_position', selected_stat]
            ].dropna(subset=[selected_stat])

            # Filtrage conditionnel selon la statistique sélectionnée
            if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
            else:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            df_stat['sub_position'] = df_stat['sub_position'].apply(
                lambda x: position_translation.get(x, x)
            )

            # Traduction du pays du joueur dans la table
            df_stat['country_of_citizenship'] = df_stat['country_of_citizenship'].apply(
                lambda x: country_translation.get(x, x)
            )
            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value) # Utilisation du format de market_value
            
            df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Ordonner les données du plus grand au plus petit

            top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

            # Ordre podium et médailles
            podium_order = [0, 1, 2]
            medals = ["🥇","🥈", "🥉"]

            podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    player = top3.loc[i]
                    name = player['name']
                    stat = round(player[selected_stat]) if pd.notna(player[selected_stat]) else "-"
                    image_url = player['image_url']
                    image_html = f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>" if pd.notna(image_url) else ""

                    player_html = (
                        "<div style='min-width: 200px; text-align: center;'>"
                        f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                        f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                        f"{image_html}"
                        f"<div style='font-size: 16px;'><strong>{selected_stat_display}:</strong> {stat}</div>"
                        "</div>"
                    )
                    podium_html += player_html

            podium_html += "</div>"

            st.markdown(podium_html, unsafe_allow_html=True)

            # Choix des colonnes dans la table
            final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
            final_df = final_df[[
                'name', 'Statistique', 'Age', 'country_of_citizenship', 'current_club_name', 'sub_position','market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)

    else:

        st.markdown("<h4 style='text-align: center;'>🏅 Player rankings (0-100) for basic statistics according to their position</h4>", unsafe_allow_html=True) # Display title
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking_basis.jpg") # Path of the image
        df = pd.read_csv("data/database_player.csv") # Collect the data
        
        # Retrieve “score_” + “rating” columns
        all_stats_raw = [col for col in df.columns if col.startswith("score_")]
        if "rating" in df.columns:
            all_stats_raw.append("rating")

        translated_stats = [format_stat_name(col) for col in all_stats_raw] # Apply format to names for display

        stat_name_mapping = dict(zip(translated_stats, all_stats_raw)) # Create display mapping → real name

        selected_stat_display = st.sidebar.selectbox("Select a statistic :", [""] + translated_stats) # Selector in the sidebar

        selected_stat = stat_name_mapping.get(selected_stat_display, None) # Recover the real name of the column

        if not selected_stat:
            # If the metric is selected, we hide the image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                st.info("Scroll down the sidebar to select the language, metric and filters of your choice")
                
                
        if selected_stat:
            # Top of the sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filters")

                df_with_stat = df.dropna(subset=[selected_stat]) # Filter by selected statistic

                filtered_df = df_with_stat.copy()  # Starting point for filters

                # Position filter
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options = st.selectbox("Position", [""] + poste_options_raw )

                if poste_options:
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_options]

                # League filter
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("League", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Club filter
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Country filter
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options = st.selectbox("Country", [""] + pays_options_raw )

                if pays_options:
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_options]

                # Age group filter (dynamically create the age ranges available)
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

                # Market value filter
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_max = st.slider(
                    "Maximum market value (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_max_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Maximum value selected: **{format_market_value(valeur_max)}**") # Display the choice of the user
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] <= valeur_max]
        

            # Define statistics specific to goalkeepers
            goalkeeper_stats = [
                "goal_scoring_conceded", "efficiency", "error_fouls",
                "short_clearance", "long_clearance", "positioning", "aerial_defense"
            ]
            # Selecting columns
            df_stat = filtered_df[
                ['name', 'image_url', 'Age', 'country_of_citizenship', 'current_club_name','sub_position',
                'current_club_domestic_competition_id', 'market_value_in_eur','contract_expiration_date', selected_stat]
            ].dropna(subset=[selected_stat])

            # Conditional filtering by selected statistic
            if selected_stat in [f"score_{stat}" for stat in goalkeeper_stats]:
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
            else:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value) # Format market value
                
            df_stat = df_stat.sort_values(by=selected_stat, ascending=False) # Order data from largest to smallest

            top3 = df_stat.head(3).reset_index(drop=True) # Displaying podium

            podium_order = [0, 1, 2]  # 1st, 2nd, 3rd
            medals = ["🥇", "🥈", "🥉"]

            # Start of scrollable container
            podium_html = "<div style='display: flex; overflow-x: auto; gap: 2rem; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;'>"

            # Creating player blocks
            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    player = top3.loc[i]
                    name = player['name']
                    image_url = player['image_url']
                    stat_val = round(player[selected_stat]) if pd.notna(player[selected_stat]) else "-"
                    stat_label = format_stat_name(selected_stat)

                    image_html = (
                        f"<img src='{image_url}' style='width: 100%; max-width: 120px; border-radius: 10px; margin-bottom: 0.5rem;'>"
                        if pd.notna(image_url) else ""
                    )

                    player_html = (
                        "<div style='min-width: 200px; text-align: center;'>"
                        f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                        f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                        f"{image_html}"
                        f"<div style='font-size: 16px;'><strong>{stat_label}:</strong> {stat_val}</div>"
                        "</div>"
                    )

                    podium_html += player_html

            # Closing the container
            podium_html += "</div>"

            # Final display
            st.markdown(podium_html, unsafe_allow_html=True)

            # We display the table with the columns desired
            final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
            final_df = final_df[[
                'name', 'Statistic', 'Age', 'country_of_citizenship', 'current_club_name', 'sub_position', 'market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)

# Page du classement des joueurs pour les statistiques avancées / Player ranking page by advanced statistics
def ranking():
    # Page en français
    if lang == "Français":
        st.markdown("<h4 style='text-align: center;'>🏆 Classement des joueurs pour les statistiques avancées</h4>", unsafe_allow_html=True) # Affichage du titre de la page
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking.jpg") # Construction du chemin pour l'image
        df = pd.read_csv("data/database_player.csv") # Récupération des données

        all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # Liste des statistiques disponibles

        selected_stat = st.sidebar.selectbox("Choisissez une statistique :", [""] + all_stats) # Choix de la statistique dans la sidebar
        
        if not selected_stat:
            # Si la métrique est selectionné, nous cachons l'image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                st.info("Dérouler la barre latérale pour sélectionner la langue, la métrique et les filtres de votre choix")
                
        if selected_stat:
            # Début de la sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filtres")

                df_with_stat = df.dropna(subset=[selected_stat]) # Filtre selon la statistique sélectionnée

                filtered_df = df_with_stat.copy()  # Point de départ pour les filtres

                # Filtre Poste
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options_fr = [""] + [position_translation.get(p, p) for p in poste_options_raw]
                poste_fr = st.selectbox("Poste", poste_options_fr)

                if poste_fr:
                    poste_en = {v: k for k, v in position_translation.items()}.get(poste_fr, poste_fr)
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_en]

                # Filtre Championnat
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("Championnat", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Filtre Club
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Filtre Pays
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options_fr = [""] + [country_translation.get(p, p) for p in pays_options_raw]
                pays_fr = st.selectbox("Pays", pays_options_fr)

                if pays_fr:
                    pays_en = {v: k for k, v in country_translation.items()}.get(pays_fr, pays_fr)
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_en]

                # Filtre Tranche d’âge (créer dynamiquement les tranches d'âge disponibles)
                tranche_options = [""]
                ages = filtered_df["Age"].dropna()

                if any(ages < 23):
                    tranche_options.append("< 23 ans")
                if any((ages >= 24) & (ages <= 29)):
                    tranche_options.append("24-29 ans")
                if any(ages >= 30):
                    tranche_options.append("30 ans et +")

                age_group = st.selectbox("Tranche d'âge", tranche_options) # Sélecteur

                # Appliquer le filtre si sélectionné
                if age_group:
                    if age_group == "< 23 ans":
                        filtered_df = filtered_df[filtered_df["Age"] < 23]
                    elif age_group == "24-29 ans":
                        filtered_df = filtered_df[(filtered_df["Age"] >= 24) & (filtered_df["Age"] <= 29)]
                    elif age_group == "30 ans et +":
                        filtered_df = filtered_df[filtered_df["Age"] >= 30]

                # Filtre de valeur marchande
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_max = st.slider(
                    "Valeur marchande maximum (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_max_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Valeur maximum sélectionné : **{format_market_value(valeur_max)}**") # Affichage du choix de l'utilisateur
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] <= valeur_max]

            # Placement du glossaire en sidebar
            with st.sidebar.expander("Glossaire des statistiques"):
                st.markdown("""
                ### Gardien de but :
                - **GA_per90** : Buts encaissés par 90 minutes 
                - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
                - **/90 (PSxG-GA/90)** : Différence entre PSxG et buts encaissés par 90 minutes
                - **Save%** : Pourcentage d’arrêts effectués  
                - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés  
                - **Err_per90** : Erreurs conduisant à un tir adverse par 90 minutes
                - **Launch%** : Pourcentage de passes longues  
                - **AvgLen** : Longueur moyenne des passes (en yards)  
                - **Cmp%** : Pourcentage de passes réussies  
                - **AvgDist** : Distance moyenne des passes (en yards)  
                - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  
                - **Stp%** : Pourcentage de centres arrêtés dans la surface  

                ### Défenseurs centraux :
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **PrgP_per90** : Passes progressives par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **PrgC_per90** : Conduites progressives par 90 minutes
                - **Err_per90** : Erreurs menant à un tir adverse
                - **Tkl%** : Pourcentage de tacles effectués
                - **Int_per90** : Interceptions par 90 minutes
                - **Tkl_per90** : Tacles par 90 minutes
                - **CrdY_per90** : Cartons jaunes par 90 minutes
                - **Won_per90** : Duels aériens gagnés par 90 minutes
                - **Won%** : Pourcentage de duels aériens gagnés

                ### Défenseurs latéraux :
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **PrgP_per90** : Passes progressives par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **PrgC_per90** : Conduites progressives par 90 minutes
                - **Err_per90** : Erreurs menant à un tir adverse
                - **Tkl%** : Pourcentage de tacles effectués 
                - **Int_per90** : Interceptions par 90 minutes
                - **Tkl_per90** : Tacles par 90 minutes
                - **CrdY_per90** : Cartons jaunes par 90 minutes
                - **Won_per90** : Duels aériens gagnés par 90 minutes
                - **Won%** : Pourcentage de duels aériens gagnés 

                ### Milieux de terrain :
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **PrgP_per90** : Passes progressives par 90 minutes
                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **PrgC_per90** : Conduites progressives par 90 minutes
                - **Fld_per90** : Fautes subies par 90 minutes
                - **Err_per90** : Erreurs menant à un tir adverse
                - **Tkl%** : Pourcentage de tacles effectués 
                - **Int_per90** : Interceptions par 90 minutes
                - **CrdY_per90** : Cartons jaunes par 90 minutes
                - **Won%** : Pourcentage de duels aériens gagnés 

                ### Milieux offensifs / Ailiers :
                - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **G-xG_per90** : Expected Goals par 90 minutes
                - **PrgP_per90** : Passes progressives par 90 minutes
                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **Succ_per90** : Dribbles réussis par 90 minutes
                - **Succ%** : Pourcentage de dribbles réussis
                - **PrgC_per90** : Conduites progressives par 90 minutes
                - **Fld_per90** : Fautes subies par 90 minutes
                - **Dis_per90** : Ballons perdus par 90 minutes

                ### Attaquants :
                - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
                - **Sh_per90** : Tirs tentés par 90 minutes
                - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
                - **G-xG_per90** : Expected Goals par 90 minutes
                - **G/Sh** : Buts par tir  
                - **PrgP_per90** : Passes progressives par 90 minutes  
                - **PrgR_per90** : Passes progressives reçues par 90 minutes
                - **Cmp%** : Pourcentage de passes réussies
                - **xAG_per90** : Expected Assisted Goals par 90 minutes
                - **Succ_per_90** : Dribbles réussis par 90 minutes  
                - **PrgC_per90** : Conduites progressives par 90 minutes  
                - **Dis_per90** : Ballons perdus par 90 minutes  
                """)

            # Appliquer des conditions minimales sur les métriques spécifiques
            thresholds = {
                'Cmp%': ('Cmp', 250),
                'Tkl%': ('Tkl', 40),
                'Won%': ('Won', 30),
                'Succ%': ('Succ', 30)
            }

            if selected_stat in thresholds:
                col, min_value = thresholds[selected_stat]
                
                # S'assurer que la colonne existe et que les valeurs sont numériques
                if col in filtered_df.columns:
                    filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                    st.markdown(f"<small><strong>Filtre : {col} > {min_value}</strong></small>", unsafe_allow_html=True)

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
            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value) # Utilisation du format de market_value

            # Filtrage spécial si la statistique sélectionnée est reservée aux gardiens
            if selected_stat in ['Saves_per90', 'Save%', '/90', 'PSxG+/-','AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%']:
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
    
            # Filtrage spécial si la statistique sélectionnée est GA_per90
            if selected_stat == 'GA_per90':
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
                df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
            else:
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

            # Cas particuliers : exclusion des gardiens pour certaines statistiques
            if selected_stat in ['Won%', 'Tkl%','Succ%']:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            df_stat['sub_position'] = df_stat['sub_position'].apply(
                lambda x: position_translation.get(x, x)
            )
            top3 = df_stat.head(3).reset_index(drop=True) # Affichage du podium

            podium_order = [0, 1, 2]
            medals = ["🥇", "🥈", "🥉"]

            podium_html = (
                "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
            )

            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    player = top3.loc[i]
                    name = player['name']
                    image_url = player['image_url']
                    stat_val = round(player[selected_stat], 2) if pd.notna(player[selected_stat]) else "-"

                    image_html = (
                        f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                        "border-radius: 10px; margin-bottom: 0.5rem;'>"
                        if pd.notna(image_url) else ""
                    )

                    player_html = (
                        "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                        f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                        f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                        f"{image_html}"
                        f"<div style='font-size: 16px;'><strong>{selected_stat}:</strong> {stat_val}</div>"
                        "</div>"
                    )

                    podium_html += player_html

            podium_html += "</div></div>"

            st.markdown(podium_html, unsafe_allow_html=True)

            # Choix des colonnes dans la table
            final_df = df_stat.rename(columns={selected_stat: 'Statistique'})
            final_df = final_df[[
                'name', 'Statistique', 'Age', 'country_of_citizenship', 'current_club_name', 'sub_position','market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)

    else:
        st.markdown("<h4 style='text-align: center;'>🏆 Player ranking for advanced statistics</h4>", unsafe_allow_html=True) # Display the title
        
        image_path = os.path.join(os.path.dirname(__file__), "image", "player_ranking.jpg") # Bulding the path for the image

        df = pd.read_csv("data/database_player.csv") # Recovering data

        all_stats = sorted(set(stat for stats in category_stats.values() for stat in stats if stat in df.columns)) # List of available statistics

        selected_stat = st.sidebar.selectbox("Choose a metric :", [""] + all_stats) # Choice of statistics in the sidebar
        
        if not selected_stat:
            # If the metric is selected, we hide the image
            if os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
                st.info("Scroll down the sidebar to select the language, metric and filters of your choice")
                
        if selected_stat:
            # Top of the sidebar
            with st.sidebar:
                st.markdown("### 🎯 Filters")

                df_with_stat = df.dropna(subset=[selected_stat]) # Filter by selected statistic

                filtered_df = df_with_stat.copy()  # Starting point for filters

                # Position filter
                poste_options_raw = sorted(filtered_df["sub_position"].dropna().unique())
                poste_options = st.selectbox("Position", [""] + poste_options_raw )

                if poste_options:
                    filtered_df = filtered_df[filtered_df["sub_position"] == poste_options]

                # League filter
                championnat_options = sorted(filtered_df["current_club_domestic_competition_id"].dropna().unique())
                championnat = st.selectbox("League", [""] + championnat_options)

                if championnat:
                    filtered_df = filtered_df[filtered_df["current_club_domestic_competition_id"] == championnat]

                # Club filter
                club_options = sorted(filtered_df["current_club_name"].dropna().unique())
                club = st.selectbox("Club", [""] + club_options)

                if club:
                    filtered_df = filtered_df[filtered_df["current_club_name"] == club]

                # Country filter
                pays_options_raw = sorted(filtered_df["country_of_citizenship"].dropna().unique())
                pays_options = st.selectbox("Country", [""] + pays_options_raw )

                if pays_options:
                    filtered_df = filtered_df[filtered_df["country_of_citizenship"] == pays_options]

                # Age group filter (dynamically create the age ranges available)
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

                # Market value filter
                valeur_min_possible = 0
                valeur_max_possible = int(filtered_df["market_value_in_eur"].max()) if not filtered_df["market_value_in_eur"].isnull().all() else 10_000_000

                valeur_max = st.slider(
                    "Maximum market value (€)",
                    valeur_min_possible,
                    valeur_max_possible,
                    valeur_max_possible,
                    step=100000,
                    format="%d"
                )

                st.markdown(f"Maximum value selected: **{format_market_value(valeur_max)}**") # Display the choice of the user
                filtered_df = filtered_df[filtered_df["market_value_in_eur"] <= valeur_max]

            # Statistics glossary in the sidebar
            with st.sidebar.expander("Statistics glossary"):
                st.markdown("""
                ### Goalkeeper :
                - **GA_per90**: Goals conceded per 90 minutes  
                - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
                - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes  
                - **Save%**: Save percentage  
                - **PSxG+/-**: Difference between PSxG and goals conceded  
                - **Err_per90**: Errors leading to a shot per 90 minutes  
                - **Launch%**: Percentage of long passes  
                - **AvgLen**: Average pass length (in yards)  
                - **Cmp%**: Pass completion percentage  
                - **AvgDist**: Average pass distance (in yards)  
                - **#OPA_per90**: Defensive actions outside the penalty area per 90 minutes  
                - **Stp%**: Percentage of crosses stopped inside the box 

                ### Center Back :
                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Err_per90**: Errors leading to a shot  
                - **Tkl%**: Tackle success rate  
                - **Int_per90**: Interceptions per 90 minutes  
                - **Tkl_per90**: Tackles per 90 minutes  
                - **CrdY_per90**: Yellow cards per 90 minutes  
                - **Won_per90**: Aerial duels won per 90 minutes  
                - **Won%**: Aerial duel success rate  

                ### Full-backs :
                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Err_per90**: Errors leading to a shot  
                - **Tkl%**: Tackle success rate  
                - **Int_per90**: Interceptions per 90 minutes  
                - **Tkl_per90**: Tackles per 90 minutes  
                - **CrdY_per90**: Yellow cards per 90 minutes  
                - **Won_per90**: Aerial duels won per 90 minutes  
                - **Won%**: Aerial duel success rate  

                ### Midfielders :
                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Fld_per90**: Fouls drawn per 90 minutes  
                - **Err_per90**: Errors leading to a shot  
                - **Tkl%**: Tackle success rate  
                - **Int_per90**: Interceptions per 90 minutes  
                - **CrdY_per90**: Yellow cards per 90 minutes  
                - **Won%**: Aerial duel success rate

                ### Attacking midfielders / Wingers :
                - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                - **Succ_per90**: Successful dribbles per 90 minutes  
                - **Succ%**: Dribble success rate  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Fld_per90**: Fouls drawn per 90 minutes  
                - **Dis_per90**: Dispossessions per 90 minutes

                ### Forwards :
                - **npxG_per90**: Non-penalty Expected Goals per 90 minutes  
                - **Sh_per90**: Shots attempted per 90 minutes  
                - **G-PK_per90**: Goals scored minus penalties per 90 minutes  
                - **G-xG_per90**: Difference between goals and Expected Goals per 90 minutes  
                - **G/Sh**: Goals per shot  
                - **PrgP_per90**: Progressive passes per 90 minutes  
                - **PrgR_per90**: Progressive passes received per 90 minutes  
                - **Cmp%**: Pass completion percentage  
                - **xAG_per90**: Expected Assisted Goals per 90 minutes  
                - **Succ_per_90**: Successful dribbles per 90 minutes  
                - **PrgC_per90**: Progressive carries per 90 minutes  
                - **Dis_per90**: Dispossessions per 90 minutes 
                """)

            # Apply minimum conditions to specific metrics
            thresholds = {
                'Cmp%': ('Cmp', 250),
                'Tkl%': ('Tkl', 40),
                'Won%': ('Won', 30),
                'Succ%': ('Succ', 30)
            }

            if selected_stat in thresholds:
                col, min_value = thresholds[selected_stat]
                
                # Check that the column exists and that the values are numeric
                if col in filtered_df.columns:
                    filtered_df = filtered_df[pd.to_numeric(filtered_df[col], errors='coerce') > min_value]
                    st.markdown(f"<small><strong>Filter : {col} > {min_value}</strong></small>", unsafe_allow_html=True)

            # Selecting columns
            df_stat = filtered_df[
                ['name', 'image_url', 'Age', 'country_of_citizenship', 'current_club_name',
                'current_club_domestic_competition_id', 'market_value_in_eur','contract_expiration_date',
                'sub_position', selected_stat]
            ].dropna(subset=[selected_stat])

            df_stat['market_value_in_eur'] = df_stat['market_value_in_eur'].apply(format_market_value) # Format market value

            # Special filtering if the selected statistic is reserved for goalkeepers
            if selected_stat in ['Saves_per90', 'Save%', '/90', 'PSxG+/-','AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%']:
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
                
            # Special filtering if the selected statistic is GA_per90
            if selected_stat == 'GA_per90':
                df_stat = df_stat[df_stat['sub_position'] == 'Goalkeeper']
                df_stat = df_stat.sort_values(by=selected_stat, ascending=True)
            else:
                df_stat = df_stat.sort_values(by=selected_stat, ascending=False)

            # Special cases: exclusion of goalkeepers for certain statistics
            if selected_stat in ['Won%', 'Tkl%','Succ%']:
                df_stat = df_stat[df_stat['sub_position'] != 'Goalkeeper']

            top3 = df_stat.head(3).reset_index(drop=True) # Displaying podium

            # Display the podium
            podium_order = [0, 1, 2]
            medals = ["🥇", "🥈", "🥉"]

            podium_html = (
                "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
            )

            for display_index, i in enumerate(podium_order):
                if i < len(top3):
                    player = top3.loc[i]
                    name = player['name']
                    image_url = player['image_url']
                    stat_val = round(player[selected_stat], 2) if pd.notna(player[selected_stat]) else "-"

                    image_html = (
                        f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                        "border-radius: 10px; margin-bottom: 0.5rem;'>"
                        if pd.notna(image_url) else ""
                    )

                    player_html = (
                        "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                        f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                        f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                        f"{image_html}"
                        f"<div style='font-size: 16px;'><strong>{selected_stat}:</strong> {stat_val}</div>"
                        "</div>"
                    )

                    podium_html += player_html

            podium_html += "</div></div>"

            st.markdown(podium_html, unsafe_allow_html=True)

            # We display the table with the columns desired
            final_df = df_stat.rename(columns={selected_stat: 'Statistic'})
            final_df = final_df[[
                'name', 'Statistic', 'Age', 'country_of_citizenship', 'current_club_name', 'market_value_in_eur', 'contract_expiration_date'
            ]]

            st.dataframe(final_df, use_container_width=True)

# Page de recherche de joueur / Player search page
def scout():
    # Page en français
    if lang == "Français":
        st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True) # Affichage du titre de la page
        df = pd.read_csv("data/database_player.csv") # Récupération des données
        
        # Caractéristiques générales (avec traductions lorsque cela est nécéssaire)
        pays_options_raw = sorted(df["country_of_citizenship"].dropna().unique())
        pays_options_fr = [country_translation.get(p, p) for p in pays_options_raw]
        pays_fr = st.multiselect("Pays", pays_options_fr, placeholder="")
        reverse_country_map = {v: k for k, v in country_translation.items()}
        pays_en = [reverse_country_map.get(p, p) for p in pays_fr] if pays_fr else []

        age_min, age_max = st.slider("Âge", 17, 42, (17, 42))
        height_min, height_max = st.slider("Taille (cm)", 163, 206, (163, 206))

        poste_options_raw = sorted(df["sub_position"].dropna().unique())
        poste_options_fr = [position_translation.get(p, p) for p in poste_options_raw]
        poste_fr = st.multiselect("Poste", poste_options_fr, placeholder="")
        poste_en = [k for k, v in position_translation.items() if v in poste_fr] if poste_fr else []

        contract_years = sorted(df["contract_expiration_date"].dropna().apply(lambda x: str(x)[:4]).unique())
        contract_year = st.multiselect("Année de fin de contrat", contract_years, placeholder="")

        championnat = st.multiselect("Championnat", sorted(df["current_club_domestic_competition_id"].dropna().unique()), placeholder="")
        
        # Mise à jour dynamique des clubs en fonction des championnats
        if championnat:
            clubs_filtered = df[df["current_club_domestic_competition_id"].isin(championnat)]["current_club_name"].dropna().unique()
            club = st.multiselect("Club", sorted(clubs_filtered), placeholder="")
        else:
            club = st.multiselect("Club", sorted(df["current_club_name"].dropna().unique()), placeholder="")

        price_max = st.slider("Valeur marchande maximum (€)", 0, int(df["market_value_in_eur"].max()), 200000000, step=100000)

        # Statistiques de base avec traduction
        all_stats_raw = [col for col in df.columns if col.startswith("score_")]
        if "rating" in df.columns:
            all_stats_raw.append("rating")

        translated_stats = [
            base_stat_translation.get(col.replace("score_", ""), "Note") if col == "rating"
            else base_stat_translation.get(col.replace("score_", ""), col)
            for col in all_stats_raw
        ]
        stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

        selected_base_stats_display = st.multiselect("Statistiques de base", translated_stats, placeholder="")
        selected_base_stats = [stat_name_mapping[disp] for disp in selected_base_stats_display if disp in stat_name_mapping]
        base_stat_limits = {}
        for display_name in selected_base_stats_display:
            stat = stat_name_mapping[display_name]
            min_val, max_val = int(df[stat].min()), int(df[stat].max())
            base_stat_limits[stat] = st.slider(
                f"{display_name} (min / max)",
                min_val, max_val,
                (min_val, max_val),
                step=1
            )

        # Statistiques avancées (à partir de la 30e colonne)
        selected_adv_stats, adv_stat_limits = [], {}
        adv_columns = df.columns[30:]
        selected_adv_stats = st.multiselect("Statistiques avancées", list(adv_columns), placeholder="")
        for stat in selected_adv_stats:
            if stat in df.columns:
                min_val, max_val = float(df[stat].min()), float(df[stat].max())
                adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

        nb_players = st.slider("Nombre de joueurs à afficher", 3, 30, 10) # Choix de nombre de joueurs à afficher
        
        # Injecte du CSS pour centrer tous les boutons
        st.markdown(
            """
            <style>
            div.stButton > button {
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Et ici le vrai bouton fonctionnel
        recherche = st.button("🔍 Rechercher")

        # On s'assure qu'un minimum d'informations a été renseigné
        nb_filled = sum([
            bool(pays_fr), bool(poste_fr), bool(contract_year), bool(championnat),
            bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0
        ])

        if recherche:
            if nb_filled < 1:
                st.error("Veuillez remplir au moins 1 critères pour lancer la recherche.")
            else:
                # On récupère les données associées
                df_filtered = df.copy()
                if pays_en: df_filtered = df_filtered[df_filtered["country_of_citizenship"].isin(pays_en)]
                if poste_en: df_filtered = df_filtered[df_filtered["sub_position"].isin(poste_en)]
                if contract_year: df_filtered = df_filtered[df_filtered["contract_expiration_date"].str[:4].isin(contract_year)]
                if championnat: df_filtered = df_filtered[df_filtered["current_club_domestic_competition_id"].isin(championnat)]
                if club: df_filtered = df_filtered[df_filtered["current_club_name"].isin(club)]
                df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]
                df_filtered = df_filtered[(df_filtered["height_in_cm"] >= height_min) & (df_filtered["height_in_cm"] <= height_max)]
                df_filtered = df_filtered[df_filtered["market_value_in_eur"] <= price_max]

                for stat, (min_v, max_v) in base_stat_limits.items():
                    df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                for stat, (min_v, max_v) in adv_stat_limits.items():
                    if stat in df_filtered.columns:
                        df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                
                # Filtrage avancé spécial : seuils minimaux pour certaines stats
                thresholds = {
                    'Cmp%': ('Cmp', 250),
                    'Tkl%': ('Tkl', 40),
                    'Won%': ('Won', 30),
                    'Succ%': ('Succ', 30)
                }

                for stat in selected_adv_stats:
                    if stat in thresholds:
                        col, min_val = thresholds[stat]
                        if col in df_filtered.columns:
                            df_filtered = df_filtered[df_filtered[col] >= min_val]

                # Filtrage gardien / joueur selon les stats avancées
                goalkeeper_advanced_stats = ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%', 'GA_per90']

                if any(stat in selected_adv_stats for stat in goalkeeper_advanced_stats):
                    df_filtered = df_filtered[df_filtered["sub_position"] == "Goalkeeper"]

                # Exclusion des gardiens pour certaines stats
                if any(stat in ['Won%', 'Tkl%', 'Succ%'] for stat in selected_adv_stats):
                    df_filtered = df_filtered[df_filtered["sub_position"] != "Goalkeeper"]

                all_stats = selected_base_stats + selected_adv_stats
                display_columns = ["name", "image_url", "Age", "country_of_citizenship", "current_club_name",
                                   "sub_position", "market_value_in_eur", "contract_expiration_date", "rating"] + all_stats

                df_stat = df_filtered.dropna(subset=["rating"]).sort_values("rating", ascending=False)
                
                # Filtrage gardien / joueurs de champ selon la stat sélectionnée
                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]
                # Vérifie si une stat de base sélectionnée est spécifique aux gardiens
                selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                if selected_goalkeeper_stats:
                    df_stat = df_stat[df_stat["sub_position"] == "Goalkeeper"]
                elif selected_base_stats:
                    df_stat = df_stat[df_stat["sub_position"] != "Goalkeeper"]
                df_stat = df_stat[display_columns].head(nb_players).reset_index(drop=True)

                # Traductions de plusieurs catégories (postion, pays) et mise sous format des valeurs sur le marché des transferts
                df_stat["sub_position"] = df_stat["sub_position"].apply(lambda x: position_translation.get(x, x))
                df_stat["country_of_citizenship"] = df_stat["country_of_citizenship"].apply(lambda x: country_translation.get(x, x))
                df_stat["market_value_in_eur"] = df_stat["market_value_in_eur"].apply(format_market_value)

                # Construction du podium
                top3 = df_stat.head(3)
                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['name']
                        rating = round(player['rating'], 2) if pd.notna(player['rating']) else "-"
                        image_url = player['image_url']
                        
                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_block = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>Note :</strong> {rating}</div>"
                            "</div>"
                        )

                        podium_html += player_block

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                final_df = df_stat.drop(columns=["image_url"]) # Suppression de image_url pour la table finale
                st.dataframe(final_df, use_container_width=True)

        # Sidebar résumé
        with st.sidebar:
            st.markdown("### 🧾 Filtres sélectionnés")
            if pays_fr:
                st.markdown(f"- **Pays :** {', '.join(pays_fr)}")
            if poste_fr:
                st.markdown(f"- **Postes :** {', '.join(poste_fr)}")
            st.markdown(f"- **Âge :** {age_min} - {age_max} ans")
            st.markdown(f"- **Taille :** {height_min} - {height_max} cm")
            st.markdown(f"- **Valeur max :** {format_market_value(price_max)}")
            if contract_year:
                st.markdown(f"- **Contrat :** {', '.join(contract_year)}")
            if championnat:
                st.markdown(f"- **Championnat :** {', '.join(championnat)}")
            if club:
                st.markdown(f"- **Clubs :** {', '.join(club)}")

            if selected_base_stats_display:
                st.markdown("**Stats de base :**")
                for disp_label in selected_base_stats_display:
                    raw_stat = stat_name_mapping.get(disp_label)
                    if raw_stat in base_stat_limits:
                        st.markdown(f"- {disp_label} : {base_stat_limits[raw_stat]}")

            if selected_adv_stats:
                st.markdown("**Stats avancées :**")
                for stat in selected_adv_stats:
                    if stat in adv_stat_limits:
                        st.markdown(f"- {stat} : {adv_stat_limits[stat]}")

        # Placement du glossaire en sidebar
        with st.sidebar.expander("Glossaire des statistiques avancées"):
            st.markdown("""
            ### Statistiques générales
            - **MP** : Nombre de matches joués
            - **Starts** : Nombre de matches débutés en tant que titulaire
            - **Min** : Nombre de minutes joués
            - **90s** : Nombre de minutes joués divisé par 90

            ### Gardien de but :
            - **GA_per90** : Buts encaissés par 90 minutes
            - **SoTA_per90** : Nombre de tirs cadrés concédés par 90 minutes 
            - **Save_per90** : Nombre d’arrêts effectués par 90 minutes
            - **PSxG_per90** : Post-Shot Expected Goals par 90 minutes
            - **PSxG+/-** : Différence entre les PSxG (xG post-tir) et buts encaissés
            - **/90 /PSxG-GA/90** : Différence entre PSxG et buts encaissés par 90 minutes
            - **PKm_per90** : Nombre de pénaltys non arrêtés par le gardien par 90 minutes
            - **PKsv_per90** : Nombre de pénaltys arrêtés par le gardien par 90 minutes
            - **Thr_per90** : Nombre de dégagements effectués par le gardien par 90 minutes
            - **Stp_per90** : Nombre de centres arrêtés dans la surface par 90 minutes
            - **Save%** : Pourcentage d’arrêts effectués  
            - **CS%** : Pourcentage de clean sheat (matchs sans encaisser de but)
            - **AvgLen** : Longueur moyenne des passes (en yards)  
            - **Launch%** : Pourcentage de passes longues  
            - **Stp%** : Pourcentage de centres arrêtés dans la surface  
            - **#OPA_per90** : Actions défensives hors de la surface par 90 minutes  

            ### Joueurs de champs :
            - **Gls_per90** : Buts par 90 minutes
            - **Ast_per90** : Passe décisves par 90 minutes
            - **G+A_per90** : Buts + Passe décisives par 90 minutes  
            - **G-PK** : Buts marquées - pénaltys inscrits
            - **G-PK_per90** : Buts marquées - pénaltys inscrits par 90 minutes
            - **G-xG_per90** : Buts marquées - Expected Goals par 90 minutes
            - **PK_per90** : Penaltys par 90 minutes
            - **npxG** : Non-penalty Expected Goals
            - **npxG_per90** : Non-penalty Expected Goals par 90 minutes
            - **xAG_per90** : Expected Assisted Goals par 90 minutes
            - **PrgC_per90** : Conduites progressives par 90 minutes
            - **A-xAG** : Nombre de passe décisives - Expected Assisted Goals
            - **Sh_per90** : Tirs tentés par 90 minutes
            - **SoT_per90** : Tir cadrés par 90 minutes
            - **G/Sh** : Buts par tir
            - **SoT%** : Pourcentage de Tirs cadrés
            - **PrgP_per90** : Passes progressives par 90 minutes
            - **PrgR_per90** : Passes progressives reçues par 90 minutes
            - **Cmp** : Nombre de passes réussis
            - **Cmp_per90** : Nombre de passes réussis par 90 minutes
            - **Cmp%** : Pourcentage de passes réussies
            - **AvgDist**: Distance moyenne des passes (en yards)  
            - **1/3_per90** : Nombre de passes réussis dans le derniers tiers offensifs par 90 minutes
            - **PPA_per90** : Nombre de passes réussis dans la surface de réparation adverse par 90 minutes
            - **CrsPA_per90** : Nombre de centres réussis dans la surface de réparation adverse par 90 minutes
            - **Sw_per90** : Nombre de passes longues réussis par 90 minutes
            - **Crs_per90** : Nombre de centres réussis par 90 minutes
            - **Tkl** : Nombre de tacles effectués
            - **Tkl_per90** : Nombre de tacles effectués par 90 minutes
            - **Int_per90** : Nombre d'interceptions effectués par 90 minutes
            - **Clr_per90** : Nombre de dégagements effectués par 90 minutes
            - **Err_per90** : Erreurs menant à un tir adverse par 90 minutes
            - **Fld_per90** : Fautes subies par 90 minutes
            - **Touches_per90** : Nombre de touches du ballon par 90 minutes
            - **Succ_per90** : Dribbles réussis par 90 minutes
            - **Carries_per90** : Nombre de portage du ballon par 90 minutes
            - **Mis_per90** : Nombre de mauvais contrôle du ballon par 90 minutes
            - **Dis_per90** : Ballons perdus par 90 minutes
            - **Fls_per90** : Nombre de fautes provoquées par 90 minutes
            - **PKwon_per90** : Nombre de penaltys obtenus par 90 minutes
            - **PKcon_per90** : Nombre de penaltys concédés par 90 minutes
            - **Recov_per90** : Nombre de récupération du ballon par 90 minutes
            - **Tkl%** : Pourcentage de tacles effectués
            - **Succ%** : Pourcentage de dribbles réussis
            - **Won_per90** : Duels aériens gagnés par 90 minutes
            - **Won%** : Pourcentage de duels aériens gagnés
            - **CrdY_per90** : Cartons jaunes par 90 minutes
            - **CrdR_per90** : Cartons rouges par 90 minutes
            """)

    else :
        st.markdown("<h4 style='text-align: center;'> 🔎 Scouting </h4>", unsafe_allow_html=True) # Display the title
        df = pd.read_csv("data/database_player.csv") # Recover the data 

        # General Characteristics
        country_options = sorted(df["country_of_citizenship"].dropna().unique())
        country = st.multiselect("Country", country_options, placeholder="")

        age_min, age_max = st.slider("Age", 17, 42, (17, 42))
        height_min, height_max = st.slider("Height (cm)", 163, 206, (163, 206))

        position_options = sorted(df["sub_position"].dropna().unique())
        position = st.multiselect("Position", position_options, placeholder="")

        contract_years = sorted(df["contract_expiration_date"].dropna().apply(lambda x: str(x)[:4]).unique())
        contract_year = st.multiselect("Contract end year", contract_years, placeholder="")

        leagues = st.multiselect("League", sorted(df["current_club_domestic_competition_id"].dropna().unique()), placeholder="")

        if leagues:
            filtered_clubs = df[df["current_club_domestic_competition_id"].isin(leagues)]["current_club_name"].dropna().unique()
            club = st.multiselect("Club", sorted(filtered_clubs), placeholder="")
        else:
            club = st.multiselect("Club", sorted(df["current_club_name"].dropna().unique()), placeholder="")

        price_max = st.slider("Maximum market value (€)", 0, int(df["market_value_in_eur"].max()), 200000000, step=100000)

        # Base statistics
        all_stats_raw = [col for col in df.columns if col.startswith("score_")]
        if "rating" in df.columns:
            all_stats_raw.append("rating")

        # Apply formatting for display
        translated_stats = [format_stat_name(col) for col in all_stats_raw]
        stat_name_mapping = dict(zip(translated_stats, all_stats_raw))

        selected_base_stats_display = st.multiselect("Base statistics", translated_stats, placeholder="")
        selected_base_stats = [stat_name_mapping[disp] for disp in selected_base_stats_display if disp in stat_name_mapping]
        base_stat_limits = {}
        for display_name in selected_base_stats_display:
            stat = stat_name_mapping[display_name]
            min_val, max_val = int(df[stat].min()), int(df[stat].max())
            base_stat_limits[stat] = st.slider(f"{display_name} (min / max)", min_val, max_val, (min_val, max_val), step=1)

        # Advanced statistics (from column 30)
        selected_adv_stats, adv_stat_limits = [], {}
        adv_columns = df.columns[30:]
        selected_adv_stats = st.multiselect("Advanced statistics", list(adv_columns), placeholder="")
        for stat in selected_adv_stats:
            if stat in df.columns:
                min_val, max_val = float(df[stat].min()), float(df[stat].max())
                adv_stat_limits[stat] = st.slider(f"{stat} (min / max)", min_val, max_val, (min_val, max_val))

        nb_players = st.slider("Number of players to display", 3, 30, 10) # Choice of the number of players to display

        # Inject CSS to center all buttons
        st.markdown(
            """
            <style>
            div.stButton > button {
                display: block;
                margin-left: auto;
                margin-right: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # And here's the real functional button
        search = st.button("🔍 Search")


        # We want that 1 criterias to start the search
        nb_filled = sum([
            bool(country), bool(position), bool(contract_year), bool(leagues),
            bool(club), len(selected_base_stats) > 0, len(selected_adv_stats) > 0
        ])

        if search:
            if nb_filled < 1:
                st.error("Please fill at least 1 criteria to start the search.")
            else:
                # We recovering the data
                df_filtered = df.copy()
                if country: df_filtered = df_filtered[df_filtered["country_of_citizenship"].isin(country)]
                if position: df_filtered = df_filtered[df_filtered["sub_position"].isin(position)]
                if contract_year: df_filtered = df_filtered[df_filtered["contract_expiration_date"].str[:4].isin(contract_year)]
                if leagues: df_filtered = df_filtered[df_filtered["current_club_domestic_competition_id"].isin(leagues)]
                if club: df_filtered = df_filtered[df_filtered["current_club_name"].isin(club)]
                df_filtered = df_filtered[(df_filtered["Age"] >= age_min) & (df_filtered["Age"] <= age_max)]
                df_filtered = df_filtered[(df_filtered["height_in_cm"] >= height_min) & (df_filtered["height_in_cm"] <= height_max)]
                df_filtered = df_filtered[df_filtered["market_value_in_eur"] <= price_max]

                for stat, (min_v, max_v) in base_stat_limits.items():
                    df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]
                for stat, (min_v, max_v) in adv_stat_limits.items():
                    if stat in df_filtered.columns:
                        df_filtered = df_filtered[df_filtered[stat].between(min_v, max_v)]

                # Thresholds made to not over-reward a player which have a low number realised on a statistic but a high percentage
                thresholds = {
                    'Cmp%': ('Cmp', 250),
                    'Tkl%': ('Tkl', 40),
                    'Won%': ('Won', 30),
                    'Succ%': ('Succ', 30)
                }

                for stat in selected_adv_stats:
                    if stat in thresholds:
                        col, min_val = thresholds[stat]
                        if col in df_filtered.columns:
                            df_filtered = df_filtered[df_filtered[col] >= min_val]

                # Some specifics parameters for the goalkeepers
                goalkeeper_advanced_stats = ['Saves_per90', 'Save%', '/90', 'PSxG+/-', 'AvgLen', 'Launch%', 'Stp%', '#OPA_per90', 'CS%', 'GA_per90']
                if any(stat in selected_adv_stats for stat in goalkeeper_advanced_stats):
                    df_filtered = df_filtered[df_filtered["sub_position"] == "Goalkeeper"]
                if any(stat in ['Won%', 'Tkl%', 'Succ%'] for stat in selected_adv_stats):
                    df_filtered = df_filtered[df_filtered["sub_position"] != "Goalkeeper"]

                goalkeeper_stats = [
                    "goal_scoring_conceded", "efficiency", "error_fouls",
                    "short_clearance", "long_clearance", "positioning", "aerial_defense"
                ]
                selected_goalkeeper_stats = [stat for stat in selected_base_stats if stat in [f"score_{s}" for s in goalkeeper_stats]]
                
                if selected_goalkeeper_stats:
                    df_filtered = df_filtered[df_filtered["sub_position"] == "Goalkeeper"]
                elif selected_base_stats:
                    df_filtered = df_filtered[df_filtered["sub_position"] != "Goalkeeper"]

                all_stats = selected_base_stats + selected_adv_stats
                display_columns = ["name", "image_url", "Age", "country_of_citizenship", "current_club_name",
                                   "sub_position", "market_value_in_eur", "contract_expiration_date", "rating"] + all_stats # We choose the list of informations collected

                df_stat = df_filtered.dropna(subset=["rating"]).sort_values("rating", ascending=False)
                df_stat = df_stat[display_columns].head(nb_players).reset_index(drop=True)

                df_stat["market_value_in_eur"] = df_stat["market_value_in_eur"].apply(format_market_value) # Format market value

                # We display a podium
                top3 = df_stat.head(3)
                podium_order = [0, 1, 2]
                medals = ["🥇", "🥈", "🥉"]

                podium_html = (
                    "<div style='overflow-x: auto; margin-bottom: 2rem; padding-bottom: 1rem; "
                    "border-bottom: 1px solid #e0e0e0; width: 100%;'>"
                    "<div style='display: inline-flex; gap: 2rem; white-space: nowrap;'>"
                )

                for display_index, i in enumerate(podium_order):
                    if i < len(top3):
                        player = top3.loc[i]
                        name = player['name']
                        rating = round(player['rating'], 2) if pd.notna(player['rating']) else "-"
                        image_url = player['image_url']
                        
                        image_html = (
                            f"<img src='{image_url}' style='width: 100%; max-width: 120px; "
                            "border-radius: 10px; margin-bottom: 0.5rem;'>"
                            if pd.notna(image_url) else ""
                        )

                        player_block = (
                            "<div style='display: inline-block; min-width: 200px; max-width: 220px; text-align: center;'>"
                            f"<div style='font-size: 30px;'>{medals[display_index]}</div>"
                            f"<div style='font-weight: bold; font-size: 18px; margin: 0.5rem 0;'>{name}</div>"
                            f"{image_html}"
                            f"<div style='font-size: 16px;'><strong>Rating :</strong> {rating}</div>"
                            "</div>"
                        )

                        podium_html += player_block

                podium_html += "</div></div>"

                st.markdown(podium_html, unsafe_allow_html=True)

                final_df = df_stat.drop(columns=["image_url"])
                st.dataframe(final_df, use_container_width=True) # We didsplay the entire list of players asked

        # Sidebar summary
        with st.sidebar:
            st.markdown("### 🧾 Selected Filters")
            if country:
                st.markdown(f"- **Country:** {', '.join(country)}")
            if position:
                st.markdown(f"- **Positions:** {', '.join(position)}")
            st.markdown(f"- **Age:** {age_min} - {age_max} years")
            st.markdown(f"- **Height:** {height_min} - {height_max} cm")
            st.markdown(f"- **Max value:** {format_market_value(price_max)}")
            if contract_year:
                st.markdown(f"- **Contract:** {', '.join(contract_year)}")
            if leagues:
                st.markdown(f"- **League:** {', '.join(leagues)}")
            if club:
                st.markdown(f"- **Club:** {', '.join(club)}")

            if selected_base_stats_display:
                st.markdown("**Base Stats:**")
                for disp_label in selected_base_stats_display:
                    raw_stat = stat_name_mapping.get(disp_label)
                    if raw_stat in base_stat_limits:
                        st.markdown(f"- {disp_label}: {base_stat_limits[raw_stat]}")

            if selected_adv_stats:
                st.markdown("**Advanced Stats:**")
                for stat in selected_adv_stats:
                    if stat in adv_stat_limits:
                        st.markdown(f"- {stat}: {adv_stat_limits[stat]}")

        # Gloassary in the sidebar
        with st.sidebar.expander("Glossary of advanced statistics"):
            st.markdown("""
            ### General statistics
            - **MP** : Number of matches played
            - **Starts** : Number of matches played at starter
            - **Min** : Number of minutes played
            - **90s** : Number of minutes played divided by 90

            ### Goalkeeper :
            - **GA_per90** : Goals conceded per 90 minutes  
            - **SoTA_per90** : Number of shot on target conceded per 90 minutes 
            - **Save_per90** : Number of saves made per 90 minutes
            - **PSxG_per90**: Post-Shot Expected Goals per 90 minutes  
            - **PSxG+/-** : Difference between PSxG and goals conceded 
            - **/90 (PSxG-GA/90)**: Difference between PSxG and goals conceded per 90 minutes             
            - **PKm_per90** : Number of penaltys non-save by the keeper per 90 minutes
            - **PKsv_per90** : Number of penaltys save by the keeper per 90 minutes
            - **Thr_per90** : Number of throws made by the keeper per 90 minutes
            - **Stp_per90** : Number of cross stopped into penalty area by the keeper
            - **Save%** : Save percentage  
            - **CS%** : Percentage og clean sheat (matches without conceded a goal)
            - **AvgLen** :  Average pass length (in yards)   
            - **Launch%** : Percentage of long passes
            - **Stp%** : Percentage of crosses stopped inside the box  
            - **#OPA_per90** : Defensive actions outside the penalty area per 90 minutes

            ### Field player :
            - **Gls_per90** : Goals per 90 minutes
            - **Ast_per90** : Assists per 90 minutes
            - **G+A_per90** : Goals + Assists per 90 minutes  
            - **G-PK** : Goals - penaltys scored
            - **G-PK_per90** : Goals scored minus penalties per 90 minutes
            - **G-xG_per90** : Buts minus Expected Goals per 90 minutes
            - **PK_per90** : Penaltys per 90 minutes
            - **npxG** : Non-penalty Expected Goals
            - **npxG_per90** : Non-penalty Expected Goals per 90 minutes 
            - **xAG_per90** : Expected Assisted Goals per 90 minutes  
            - **PrgC_per90** : Progressive carries per 90 minutes 
            - **A-xAG** : Number of assists - Expected Assisted Goals
            - **Sh_per90** : Shots attempted per 90 minutes
            - **SoT_per90** : Shot on target per 90 minutes
            - **G/Sh** : Goals per shot  
            - **SoT%** : Percentage of Shot on target
            - **PrgP_per90** : Progressive passes per 90 minutes 
            - **PrgR_per90** : Progressive passes received per 90 minutes 
            - **Cmp** : Number of passes achieved
            - **Cmp_per90** : Number of passes achieved par 90 minutes
            - **Cmp%** : Pass completion percentage
            - **AvgDist**: Average pass distance (in yards)  
            - **1/3_per90** : Number of passes achieved into last third area per 90 minutes
            - **PPA_per90** : Number of passes achieved into penalty area par 90 minutes
            - **CrsPA_per90** : Number of crosses achieved into penalty area par 90 minutes
            - **Sw_per90** : Number of long passes completed per 90 minutes
            - **Crs_per90** : Number of crosses completed per 90 minutes
            - **Tkl** : Number of tackes made
            - **Tkl_per90** : Tackles per 90 minutes 
            - **Int_per90** : Interceptions per 90 minutes 
            - **Clr_per90** : Number of clearances made per 90 minutes
            - **Err_per90** : Errors leading to a shot per 90 minutes  
            - **Fld_per90** : Fouls drawn per 90 minutes 
            - **Touches_per90** : Number of touches of the ball per 90 minutes
            - **Succ_per90** : Successful dribbles per 90 minutes  
            - **Carries_per90** : Number of carries per 90 minutes
            - **Mis_per90** : Number of times a player failed when attempting to gain control of a ball
            - **Dis_per90** : Dispossessions per 90 minutes
            - **Fls_per90** : Number of faults provoked per 90 minutes
            - **PKwon_per90** : Number of penaltys obtained per 90 minutes
            - **PKcon_per90** : Number of penaltys conceded par 90 minutes
            - **Recov_per90** : Number of recovery made per 90 minutes
            - **Tkl%** : Tackle success rate 
            - **Succ%** : Dribble success rate  
            - **Won_per90** : Aerial duels won per 90 minutes  
            - **Won%** : Aerial duel success rate 
            - **CrdY_per90** : Yellow cards per 90 minutes  
            - **CrdR_per90** : Red cards per 90 minutes  
            """)

# Appel de la fonction associé à la demande de l'utilisateur / Call of the function associated with the user request / 
if menu in ["Menu", "Home"]:
    home()
elif menu in ["Joueur", "Player"]:
    player_analysis()
elif menu in ["Duel", "F2F"]:
    player_comparison()
elif menu in ["Stats"]:
    ranking_basis()
elif menu in ["Stats +"]:
    ranking()
elif menu in ["Scout"]:
    scout()