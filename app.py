import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from aws_utils import save_comment_to_dynamodb
from reddit_utils import get_reddit_comments
from ml_agri_page import show_ml_page  

st.set_page_config(page_title="Sentiment Suite", page_icon="🚀", layout="wide")

page = st.sidebar.radio(
    "Choisis ta vue :",
    ["🔍 Analyse Reddit", "📊 ML Agri"]
)

# --- logiques de routage ultra-simples ---
if page == "🔍 Analyse Reddit":
    # 👉 ici ton code Reddit EXISTANT (copié tel quel ou refactorisé en fonction show_reddit())
    ...
elif page == "📊 ML Agri":
    show_ml_page()          
# Charger le CSS depuis templates
css_file = os.path.join("templates", "styles.css")
if os.path.exists(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Titre de l'application
st.title("🔍 Reddit Comment Analyzer")
st.header("Analyse de Sentiments des Commentaires Reddit")

# Saisie du mot-clé et du nombre de commentaires
keyword = st.text_input("Entrez un mot-clé pour rechercher des commentaires Reddit")
comment_limit = st.slider("Nombre de commentaires à analyser", min_value=1, max_value=100, value=10)

# Choix du type de commentaire
sentiment_filter = st.selectbox(
    "Type de commentaires à générer",
    ["Tous", "Positifs", "Négatifs", "Neutres"]
)

if st.button("Rechercher et Analyser"): 
    if keyword:
        # Récupération des commentaires
        comments = get_reddit_comments(keyword, limit=comment_limit)

        # Filtrage des commentaires selon le choix
        if sentiment_filter == "Positifs":
            comments = [c for c in comments if c["Sentiment"] == "positive"]
        elif sentiment_filter == "Négatifs":
            comments = [c for c in comments if c["Sentiment"] == "negative"]
        elif sentiment_filter == "Neutres":
            comments = [c for c in comments if c["Sentiment"] == "neutral"]

        if comments:
            # Préparation des données
            data = {"OriginalText": [], "Language": [], "Translation": [], "Sentiment": []}
            for comment in comments:
                data["OriginalText"].append(comment["OriginalText"])
                data["Language"].append(comment["Language"])
                data["Translation"].append(comment["Translation"])
                data["Sentiment"].append(comment["Sentiment"])

                # Enregistrement dans DynamoDB
                if comment["Sentiment"] == "positive":
                    save_comment_to_dynamodb("PositiveTweets", comment["Translation"], comment["Sentiment"])
                elif comment["Sentiment"] == "negative":
                    save_comment_to_dynamodb("NegativeTweets", comment["Translation"], comment["Sentiment"])
                else:
                    save_comment_to_dynamodb("NeutralTweets", comment["Translation"], comment["Sentiment"])

            # Affichage des statistiques
            df = pd.DataFrame(data)
            st.dataframe(df)

            # Graphique des sentiments (Pie Chart)
            st.subheader("📊 Répartition des Sentiments")
            sentiment_counts = df["Sentiment"].value_counts().reset_index()
            sentiment_counts.columns = ["Sentiment", "Count"]
            fig = px.pie(sentiment_counts, names="Sentiment", values="Count", 
                         title="Répartition des Sentiments", 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig)

            # Graphique des langues (Bubble Chart)
            st.subheader("🗂️ Répartition des Langues")
            language_counts = df["Language"].value_counts().reset_index()
            language_counts.columns = ["Language", "Count"]
            fig = px.scatter(language_counts, x="Language", y="Count", size="Count", 
                             color="Language", title="Distribution des langues", 
                             color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig)

            # Affichage des commentaires
            st.subheader("📝 Commentaires analysés")
            for i, row in df.iterrows():
                st.markdown(f"**🗣️ Langue : {row['Language']} | Sentiment : {row['Sentiment']}**")
                st.write(row['OriginalText'])
                st.markdown("---")

            st.success(f"✅ {len(comments)} commentaires analysés et sauvegardés avec succès !")
        else:
            st.error(f"Aucun commentaire {sentiment_filter.lower()} trouvé pour ce mot-clé.")
    else:
        st.error("Veuillez entrer un mot-clé.")

