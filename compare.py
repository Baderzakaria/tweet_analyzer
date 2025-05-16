# pages/compare.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_compare_page():
    st.title("📈 Comparaison Reddit vs Avis locaux")

    reddit = st.session_state.get("reddit_counts")
    local  = st.session_state.get("local_counts")

    if not reddit or not local:
        st.info(
            "➡️ Lance d’abord l’analyse Reddit **et** importe ton CSV dans "
            "« 📊 ML Agri » pour voir la comparaison."
        )
        return

    # ➕ Total pour calcul de pourcentage
    total_reddit = sum(reddit.values())
    total_local  = sum(local.values())

    data = pd.DataFrame({
        "Sentiment": ["Positif", "Négatif", "Neutre"],
        "Reddit (%)": [
            round(100 * reddit["positive"] / total_reddit, 1),
            round(100 * reddit["negative"] / total_reddit, 1),
            round(100 * reddit["neutral"]  / total_reddit, 1)
        ],
        "Avis locaux (%)": [
            round(100 * local["positive"] / total_local, 1),
            round(100 * local["negative"] / total_local, 1),
            round(100 * local["neutral"]  / total_local, 1)
        ]
    })

    # ➕ Tableau lisible
    st.subheader("📋 Répartition en pourcentage")
    st.dataframe(data.set_index("Sentiment"))

    # ➕ Graphique groupé
    fig = px.bar(
        data.melt(id_vars="Sentiment", var_name="Source", value_name="Pourcentage"),
        x="Sentiment", y="Pourcentage", color="Source", barmode="group", text_auto=True,
        title="Distribution des sentiments (en %)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Comparaison terminée !")
