import streamlit as st

st.set_page_config(layout="wide", page_title="CityScope", page_icon="🏙️")

st.title("🏙️ CityScope")

st.header("Bienvenue !")

st.image("image/map.png", width=250)

st.subheader("C'est quoi CityScope ?")

st.write(
    "Vous envisagez de déménager mais vous ne savez pas encore vers quelle ville vous tourner ? "
    "CityScope est là pour ça. On a rassemblé des données concrètes sur des dizaines de villes françaises "
    "pour vous aider à comparer ce qui compte vraiment : le marché de l'emploi, le coût du logement, "
    "la qualité de vie, le climat, les services disponibles... et bien d'autres choses encore."
)

st.subheader("Pourquoi ça peut vous aider ?")

st.write(
    "🗺️ **Une carte interactive** : Visualisez les indicateurs directement sur une carte de France, "
    "par ville ou par département, avec la possibilité de filtrer par catégorie."
)

st.write(
    "⚡ **Le mode Versus** : Comparez deux villes (ou deux départements) côte à côte en un seul coup d'œil. "
    "Parfait pour trancher entre deux options."
)

st.write(
    "📊 **Des analyses claires** : Classements, corrélations, tendances... On va au-delà des simples chiffres "
    "pour vous donner une vraie lecture de la situation."
)

st.write(
    "✅ **Des données fiables** : Toutes les données viennent de sources publiques et vérifiées : "
    "INSEE, data.gouv.fr, Météo-France... On ne fait pas dans l'approximation."
)

st.divider()

st.write(
    "Utilisez le menu à gauche pour explorer les cartes par **département**, par **ville**, "
    "analyser le marché **immobilier**, ou plonger dans la page **Analyse** pour des insights plus poussés."
)

st.info("💡 Astuce : activez le mode **Versus** dans la barre latérale pour comparer deux territoires en même temps.")
