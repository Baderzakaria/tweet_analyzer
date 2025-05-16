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

    data = pd.DataFrame({
        "Sentiment": ["Positif", "Négatif", "Neutre"],
        "Reddit":    [reddit["positive"], reddit["negative"], reddit["neutral"]],
        "Avis locaux": [local["positive"], local["negative"], local["neutral"]],
    })

    fig = px.bar(
        data.melt(id_vars="Sentiment", var_name="Source", value_name="Nombre"),
        x="Sentiment", y="Nombre", color="Source", barmode="group", text_auto=True,
        title="Répartition des sentiments"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Comparaison terminée !")
