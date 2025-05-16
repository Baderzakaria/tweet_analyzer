# ml_agri_page.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk, re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)   # silencieux

def show_ml_page():
    st.title("📊 Analyse de Sentiment (Machine Learning) sur Données Agri")

    # Upload du fichier CSV
    uploaded_file = st.file_uploader("📁 Importer un fichier CSV", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("🔍 Aperçu des données")
        st.write(df.head())

        # Colonnes fixes pour ton jeu de données
        texte_col = "commentaire"
        label_col = "sentiment"

        # Séparer en train/test
        X_train, X_test, y_train, y_test = train_test_split(
            df[texte_col], df[label_col], test_size=0.3, random_state=42
        )

        # Stopwords français
        french_stopwords = stopwords.words('french')

        # TF-IDF
        vect = TfidfVectorizer(stop_words=french_stopwords, max_features=500)
        X_train_vect = vect.fit_transform(X_train)
        X_test_vect  = vect.transform(X_test)

        # Modèle
        model = LogisticRegression(max_iter=200)
        model.fit(X_train_vect, y_train)

        # Rapport de classification
        y_pred = model.predict(X_test_vect)
        st.subheader("📋 Rapport de classification")
        report_df = pd.DataFrame(
            classification_report(y_test, y_pred, output_dict=True)
        ).transpose()
        st.write(report_df)

        # Matrice de confusion + heatmap
        st.subheader("🔢 Matrice de confusion")
        cm = confusion_matrix(y_test, y_pred, labels=model.classes_)
        cm_df = pd.DataFrame(cm, index=model.classes_, columns=model.classes_)
        st.write(cm_df)

        fig_cm, ax_cm = plt.subplots()
        sns.heatmap(cm_df, annot=True, fmt='d', cmap='Blues', ax=ax_cm)
        ax_cm.set_xlabel("Prédiction")
        ax_cm.set_ylabel("Vérité terrain")
        st.pyplot(fig_cm)

        # Prédire sur tout le dataset
        df["sentiment_prédit"] = model.predict(vect.transform(df[texte_col]))
        st.subheader("📘 Données avec prédiction")
        st.write(df[[texte_col, label_col, "sentiment_prédit"]])

        # Distribution
        st.subheader("📊 Distribution des sentiments prédits")
        fig1, ax1 = plt.subplots()
        sns.countplot(x="sentiment_prédit", data=df, palette="pastel", ax=ax1)
        st.pyplot(fig1)

        # Nuage de mots
        st.subheader("☁️ Nuage de mots")
        all_text = " ".join(df[texte_col].astype(str)).lower()
        clean_text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', all_text)
        tokens = [w for w in clean_text.split() if w not in french_stopwords]
        wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(tokens))

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.imshow(wordcloud, interpolation="bilinear")
        ax2.axis("off")
        st.pyplot(fig2)
