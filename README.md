# 🏙️ CityScope : Comparer les villes françaises

## La question de départ

*Où est-ce qu'on devrait s'installer ?*

C'est une question qui paraît simple, mais dès qu'on commence à creuser, elle en génère des dizaines d'autres :

- Quelle ville a le plus d'opportunités d'emploi ?
- Où les loyers sont encore raisonnables ?
- Et le climat, ça ressemble à quoi là-bas ?
- Est-ce qu'il y a des écoles, des transports, des services ?
- Paris ou Lyon ? Bordeaux ou Nantes ? Et pourquoi pas une ville moyenne ?
- Comment comparer objectivement deux endroits sans passer des semaines à compiler des données ?

On s'est retrouvé face à un trop-plein d'informations dispersées, des données sur des dizaines de sites différents, et aucun outil pour tout mettre côte à côte et trancher.

---

## La réponse : un tableau de bord interactif

Pour répondre à toutes ces questions d'un seul coup, j'ai construit **CityScope** : une application web qui centralise les données publiques sur les villes et départements français et les rend comparables en quelques clics.

L'idée centrale : **ne plus chercher l'information, la visualiser directement.**

---

## Ce que l'application permet de faire

### 🗺️ Explorer la carte de France
Visualisez n'importe quel indicateur (emploi, logement, climat, services...) directement sur une carte interactive, à l'échelle des **villes** ou des **départements**. Filtrez par catégorie, activez les marqueurs, zoomez sur une zone.

### ⚔️ Mode Versus
Comparez deux territoires côte à côte : deux cartes, deux colonnes de métriques, un graphique de comparaison directe. Idéal pour trancher entre deux options.

### 📊 Analyses approfondies
La page Analyse va plus loin que la simple carte :

| Onglet | Ce qu'il fait |
|--------|---------------|
| 📋 Fiche territoire | Toutes les données d'une ville avec l'écart vs la moyenne nationale |
| 🏆 Classements | Top et flop des territoires sur n'importe quel indicateur |
| 🆚 Comparaison | Radar normalisé et barres groupées pour plusieurs villes |
| 🎯 Score personnalisé | Créez votre propre classement en pondérant vos critères |
| 🔗 Corrélations | Matrice de corrélation entre indicateurs |
| 📈 Scatter | Croisez deux indicateurs, détection automatique des outliers |
| 🔍 Trouve ta ville | Filtrez les villes par seuils (loyer, chômage, température...) avec carte |
| 👥 Démographie | Treemap, scatter emploi/chômage, diplômes vs pauvreté |
| 🌡️ Cadre de vie | Climat, loyers, mobilité et comparaison vs moyenne nationale |

---

## Les données utilisées

Toutes les sources sont publiques et vérifiées :

| Source | Contenu |
|--------|---------|
| **INSEE** | Population, emploi, éducation, logement, mobilité, revenus |
| **data.gouv.fr** | Transactions immobilières (DVF), établissements scolaires |
| **Météo-France** | Températures, précipitations, humidité, vent |

Les données couvrent les **villes de plus de 20 000 habitants** et l'ensemble des **départements français**.

---

## Stack technique

| Brique | Rôle |
|--------|------|
| `Python 3.14` | Langage principal |
| `Streamlit` | Interface web |
| `Pandas` | Manipulation des données |
| `Folium / streamlit-folium` | Cartes interactives |
| `Plotly Express` | Graphiques interactifs |
| `Scipy` | Statistiques et détection d'outliers |

---

## Lancer l'application

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer
streamlit run Accueil.py
```

L'app s'ouvre sur **http://localhost:8501**

---

## Structure du projet

```
CityScope-main/
├── Accueil.py                  # Page d'accueil
├── pages/
│   ├── 1_Départements.py       # Carte + analyse par département
│   ├── 2_Villes.py             # Carte + analyse par ville
│   ├── 3_Immobilier.py         # Données DVF (transactions foncières)
│   ├── 4_Ressources.py         # Données brutes
│   └── 5_Analyse.py            # Tableaux de bord analytiques
├── data/
│   ├── data_departement.xlsx
│   ├── data_ville.xlsx
│   ├── meteo.xlsx
│   ├── data_immobilier.xlsx
│   └── departements.geojson
├── image/
│   └── map.png
└── requirements.txt
```
