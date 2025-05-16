# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

from aws_utils   import save_comment_to_dynamodb
from reddit_utils import get_reddit_comments
from ml_agri_page import show_ml_page     # ta page ML

st.set_page_config(page_title="Sentiment Suite", page_icon="🚀", layout="wide")
# app.py  ───────────────────────────────────────────────
page = st.sidebar.radio(
    "Choisis ta vue :",
    ["🔍 Analyse Reddit", "📊 ML Agri", "📈 Comparaison"]
)

# ----------------------------------------------------------------------
# 1️⃣  PAGE REDDIT  -----------------------------------------------------
# ----------------------------------------------------------------------
if page == "🔍 Analyse Reddit":

    # --- CSS (facultatif : déplace-le dans un helper si tu veux) ---
    css_file = os.path.join("templates", "styles.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # --- UI Reddit ----------------------------------------------------
    st.title("🔍 Reddit Comment Analyzer")
    st.header("Analyse de Sentiments des Commentaires Reddit")

    keyword        = st.text_input("Entrez un mot-clé pour rechercher des commentaires Reddit")
    comment_limit  = st.slider("Nombre de commentaires à analyser", 1, 100, 10)
    sentiment_filter = st.selectbox("Type de commentaires à générer",
                                    ["Tous", "Positifs", "Négatifs", "Neutres"])

    if st.button("Rechercher et Analyser") and keyword:
        comments = get_reddit_comments(keyword, limit=comment_limit)

        # -- filtrage par sentiment -----------------------------------
        if sentiment_filter != "Tous":
            mapping = {"Positifs": "positive", "Négatifs": "negative", "Neutres": "neutral"}
            wanted  = mapping[sentiment_filter]
            comments = [c for c in comments if c["Sentiment"] == wanted]

        if not comments:
            st.error("Aucun commentaire trouvé.")
            st.stop()

        # -- DataFrame ------------------------------------------------
        df = pd.DataFrame(comments)
        reddit_counts = df["Sentiment"].value_counts().to_dict()
        reddit_counts = {k.lower(): reddit_counts.get(k, 0) for k in ["positive", "negative", "neutral"]}
        st.session_state["reddit_counts"] = reddit_counts

        st.dataframe(df)

        # -- Pie chart Sentiments -------------------------------------
        st.subheader("📊 Répartition des Sentiments")
        pie = (df["Sentiment"].value_counts()
                     .rename_axis("Sentiment").reset_index(name="Count"))
        fig = px.pie(pie, names="Sentiment", values="Count",
                     color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)

        # -- Bubble Langues ------------------------------------------
        st.subheader("🗂️ Répartition des Langues")
        lang = (df["Language"].value_counts()
                        .rename_axis("Language").reset_index(name="Count"))
        fig2 = px.scatter(lang, x="Language", y="Count", size="Count",
                          color="Language", color_discrete_sequence=px.colors.qualitative.Bold)
        st.plotly_chart(fig2)

        # -- Liste des commentaires ----------------------------------
        st.subheader("📝 Commentaires analysés")
        for _, row in df.iterrows():
            st.markdown(f"**🗣️ {row.Language} | {row.Sentiment}**")
            st.write(row.OriginalText)
            st.markdown("---")

        st.success(f"✅ {len(df)} commentaires sauvegardés !")

        # -- Sauvegarde DynamoDB -------------------------------------
        for _, c in df.iterrows():
            table = {"positive": "PositiveTweets",
                     "negative": "NegativeTweets",
                     "neutral":  "NeutralTweets"}[c.Sentiment]
            save_comment_to_dynamodb(table, c.Translation, c.Sentiment)

# ----------------------------------------------------------------------
# 2️⃣  PAGE MACHINE LEARNING  ------------------------------------------
# ----------------------------------------------------------------------
elif page == "📊 ML Agri":
    show_ml_page()
elif page == "📈 Comparaison":
    from compare import show_compare_page   # ← voir point 3
    show_compare_page()
