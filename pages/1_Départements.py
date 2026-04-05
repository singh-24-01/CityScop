import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import plotly.express as px
import plotly.graph_objects as go


# Chargement des données
df1 = pd.read_excel('data/data_departement.xlsx')
df1[['Latitude', 'Longitude']] = df1['Geo Point'].str.split(', ', expand=True)
df1.dropna(subset=['Latitude'], inplace=True)
df1.dropna(subset=['Longitude'], inplace=True)
df1 = df1[df1['Population'] >= 20000]

df_meteo = pd.read_excel('data/meteo.xlsx')
for col in df_meteo.columns:
    df_meteo = df_meteo[df_meteo[col] != 0]

df = pd.merge(df1, df_meteo, left_on='Code', right_on='department (code)', how='left')
data_geo = json.load(open('data/departements.geojson', encoding='utf-8'))

st.set_page_config(layout="wide", page_title="Départements", page_icon="🗺️")


def France(dataframe):
    center = [46.603354, 2.668561]
    zoom = 6
    ville_data = dataframe
    rad = 10
    return center, zoom, ville_data, rad


def Ville(dataframe, ville):
    ville_data = dataframe[dataframe['Département'] == ville]
    center = [ville_data['Latitude'].mean(), ville_data['Longitude'].mean()]
    zoom = 9
    rad = 50
    return center, zoom, ville_data, rad


def display_kpi_metrics2(ville_data, indicateur):
    taux_indicateurs = []
    other_indicateurs = []

    for indicator in indicateur:
        if any(k in indicator for k in ["Taux", "Part", "Température", "Précipitations", "Loyer", "vent", "Proportion"]):
            taux_indicateurs.append(indicator)
        else:
            other_indicateurs.append(indicator)

    taux_kpi = ville_data[taux_indicateurs].mean()
    taux_kpi = {col: round(value, 2) for col, value in taux_kpi.items()}

    for col, value in taux_kpi.items():
        if 'Taux' in col or "Part" in col or "Proportion" in col:
            taux_kpi[col] = str(value) + '%'
        elif 'Température' in col:
            taux_kpi[col] = str(value) + ' °C'
        elif 'Précipitations' in col:
            taux_kpi[col] = str(value) + ' mm'
        elif 'vent' in col:
            taux_kpi[col] = str(value) + ' m/s'
        elif 'Loyer' in col:
            taux_kpi[col] = str(value) + ' €'
    taux_kpi = list(taux_kpi.values())

    other_kpi = ville_data[other_indicateurs].sum().tolist()
    other_kpi = [int(value) for value in other_kpi]
    kpi = taux_kpi + other_kpi
    kpi_name = taux_indicateurs + other_indicateurs

    num_kpis = len(kpi_name)
    num_rows = (num_kpis + 1) // 2
    columns = st.columns(2)

    for i in range(num_rows):
        columns[0].metric(kpi_name[2*i], kpi[2*i])
        if 2*i + 1 < num_kpis:
            columns[1].metric(kpi_name[2*i + 1], kpi[2*i + 1])


def display_kpi_metrics3(ville_data, indicateur):
    taux_indicateurs = []
    other_indicateurs = []

    for indicator in indicateur:
        if any(k in indicator for k in ["Taux", "Part", "Température", "Précipitations", "Loyer", "vent", "Proportion"]):
            taux_indicateurs.append(indicator)
        else:
            other_indicateurs.append(indicator)

    taux_kpi = ville_data[taux_indicateurs].mean()
    taux_kpi = {col: round(value, 2) for col, value in taux_kpi.items()}

    for col, value in taux_kpi.items():
        if 'Taux' in col or "Part" in col or "Proportion" in col:
            taux_kpi[col] = str(value) + '%'
        elif 'Température' in col:
            taux_kpi[col] = str(value) + ' °C'
        elif 'Précipitations' in col:
            taux_kpi[col] = str(value) + ' mm'
        elif 'vent' in col:
            taux_kpi[col] = str(value) + ' m/s'
        elif 'Loyer' in col:
            taux_kpi[col] = str(value) + ' €'
    taux_kpi = list(taux_kpi.values())

    other_kpi = ville_data[other_indicateurs].sum().tolist()
    other_kpi = [int(value) for value in other_kpi]
    kpi = taux_kpi + other_kpi
    kpi_name = taux_indicateurs + other_indicateurs

    num_kpis = len(kpi_name)
    num_rows = (num_kpis + 2) // 3
    columns = st.columns(3)

    for i in range(num_rows):
        columns[0].metric(kpi_name[3*i], kpi[3*i])
        if 3*i + 1 < num_kpis:
            columns[1].metric(kpi_name[3*i + 1], kpi[3*i + 1])
        if 3*i + 2 < num_kpis:
            columns[2].metric(kpi_name[3*i + 2], kpi[3*i + 2])


def show_analyse_departement(data_all, selected_indicateur, selected_departement):
    st.divider()
    st.subheader("📊 Analyse de l'indicateur")

    col_info, col_rank = st.columns([2, 1])

    # Top 10 et Bottom 10
    data_sorted = data_all[['Département', selected_indicateur]].dropna().sort_values(selected_indicateur, ascending=False)

    with col_info:
        tab1, tab2 = st.tabs(["🏆 Top 10 départements", "📉 Les 10 derniers"])
        with tab1:
            top10 = data_sorted.head(10).reset_index(drop=True)
            top10.index += 1
            fig_top = px.bar(
                top10,
                x=selected_indicateur,
                y='Département',
                orientation='h',
                color=selected_indicateur,
                color_continuous_scale='Blues',
                title=f"Top 10 : {selected_indicateur}"
            )
            fig_top.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_top, use_container_width=True)

        with tab2:
            bot10 = data_sorted.tail(10).reset_index(drop=True)
            fig_bot = px.bar(
                bot10,
                x=selected_indicateur,
                y='Département',
                orientation='h',
                color=selected_indicateur,
                color_continuous_scale='Reds',
                title=f"10 derniers : {selected_indicateur}"
            )
            fig_bot.update_layout(yaxis={'categoryorder': 'total descending'}, showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig_bot, use_container_width=True)

    with col_rank:
        if selected_departement != "France":
            val = data_all.loc[data_all['Département'] == selected_departement, selected_indicateur]
            if not val.empty:
                valeur = val.values[0]
                rang = data_sorted['Département'].tolist().index(selected_departement) + 1
                total = len(data_sorted)
                st.metric(f"Valeur : {selected_departement}", f"{round(valeur, 1)}")
                st.metric("Classement national", f"{rang} / {total}")
                percentile = round((1 - rang / total) * 100)
                if percentile >= 75:
                    st.success(f"Ce département est dans le **top {100 - percentile}%** national.")
                elif percentile <= 25:
                    st.warning(f"Ce département est dans le **dernier quart** national.")
                else:
                    st.info(f"Ce département se situe dans la **moyenne nationale**.")

        st.markdown("**Statistiques nationales**")
        col_s = data_all[selected_indicateur].dropna()
        st.write(f"- Moyenne : **{round(col_s.mean(), 1)}**")
        st.write(f"- Médiane : **{round(col_s.median(), 1)}**")
        st.write(f"- Min : **{round(col_s.min(), 1)}**")
        st.write(f"- Max : **{round(col_s.max(), 1)}**")

    # Distribution
    st.subheader("📈 Distribution nationale")
    fig_hist = px.histogram(
        data_all.dropna(subset=[selected_indicateur]),
        x=selected_indicateur,
        nbins=30,
        color_discrete_sequence=['#0496C7'],
        title=f"Répartition des valeurs : {selected_indicateur}"
    )
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)


def main():
    st.markdown("<h1 style='text-align: center;'>🗺️ Carte des Départements</h1>", unsafe_allow_html=True)
    st.write("Explorez les données par département en choisissant un domaine et un indicateur dans le menu à gauche.")

    versus = st.sidebar.toggle('⚔️ Mode Versus')
    marker = st.sidebar.checkbox('📍 Afficher les marqueurs')

    departements = sorted(df['Département'].tolist())
    departements.insert(0, "France")

    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)

    domaine = ["Démographie", "Economie", "Emploi", "Education", "Mobilité", "Logement", "Services", "Météo"]
    selected_domaine = st.sidebar.selectbox('🔍 Choisir un domaine', domaine)
    data1 = df

    if selected_domaine == "Démographie":
        indicateur = ['Population']
    elif selected_domaine == "Economie":
        indicateur = [
            "Nombre d'entreprises",
            "Nombre d'entreprises (Industrie)",
            "Nombre d'entreprises (Construction)",
            "Nombre d'entreprises (Commerce, transp., héberg. et restauration)",
            "Nombre d'entreprises (Information et communication)",
            "Nombre d'entreprises (Act. financières et assurance)",
            "Nombre d'entreprises (Act. Immobilières)",
            "Nombre d'entreprises (Act. scient. & techn., act. de serv. admi.)",
            "Nombre d'entreprises (Adm. publ, enseign, santé, action sociale)",
            "Nombre d'entreprises (Autres act. de services)"
        ]
    elif selected_domaine == "Emploi":
        indicateur = [
            "Nombre d'actifs",
            "Nombre d'inactifs",
            "Nombre de chômeurs",
            "Taux d'activité des 15-64 ans",
            "Taux de chômage des 15-64 ans"
        ]
    elif selected_domaine == "Revenu":
        indicateur = [
            "Taux d'épargne brute",
            "Montant d'épargne brute",
            "Médiane du revenu disponible",
            "Part des revenus d'activité",
            "Taux de pauvreté"
        ]
    elif selected_domaine == "Education":
        indicateur = [
            "Nombre d'écoles maternelles",
            "Nombre d'écoles élémentaires",
            "Nombre de collèges",
            "Nombre de lycées (général, technologique et/ou professionnel)",
            "Part des titulaires d'un diplôme de l'enseignement supérieur"
        ]
    elif selected_domaine == "Mobilité":
        indicateur = [
            "Part des déplacements en voiture",
            "Part des déplacements en transports en commun",
            "Part des déplacements en deux roues"
        ]
    elif selected_domaine == "Logement":
        indicateur = [
            "Nombre de logements",
            "Nombre de logements vacants",
            "Part des logements vacants",
            "Nombre de logements sociaux",
            "Nombre d'établissements d'hébergement pour personnes âgées"
        ]
    elif selected_domaine == "Services":
        indicateur = [
            "Nombre de licenciés sportifs",
            "Nombre de cinémas",
            "Part de la surface couverte en 4G",
            "Nombre d'équipements sportifs et culturels (gamme de proximité)",
            "Nombre d'équipements sportifs et culturels (gamme intermédiaire)",
            "Nombre d'équipements sportifs et culturels (gamme supérieure)",
            "Nombre de structures France Services",
            "Nombre de lieux délivrant des services Pôle Emploi"
        ]
    elif selected_domaine == "Météo":
        indicateur = [
            'Température',
            "Taux d'humidité",
            'Précipitations',
            'Vitesse du vent moyen'
        ]

    selected_indicateur = st.sidebar.selectbox('📌 Choisir un indicateur', indicateur)
    data = data1[[selected_indicateur, 'Latitude', 'Longitude', 'Département', 'Geo Shape']].copy()

    if selected_indicateur == "Nombre de structures France Services":
        data['Catégorie'], bins = pd.qcut(data[selected_indicateur].rank(method='first'), 3, retbins=True, labels=False)
    else:
        data['Catégorie'], bins = pd.qcut(data[selected_indicateur], 3, labels=False, retbins=True)

    quantile_ranges = []
    for start, end in zip(bins[:-1], bins[1:]):
        formatted_range = f"{int(start)} à {int(end)}"
        quantile_ranges.append(formatted_range)

    data["Catégorie"] = data["Catégorie"].astype(str)

    categ = st.sidebar.radio('📊 Répartition', ('Tous', quantile_ranges[0], quantile_ranges[1], quantile_ranges[2]))

    if versus:
        col1, col2 = st.columns(2)

        with col1:
            ville1 = st.selectbox("Choisissez un département", departements, key='ville1')
            if ville1 == "France":
                center1, zoom1, ville_data1, rad1 = France(df)
                zoom1 = 5
            else:
                center1, zoom1, ville_data1, rad1 = Ville(df, ville1)
            map1 = folium.Map(location=center1, zoom_start=zoom1, control_scale=True)

        with col2:
            ville2 = st.selectbox("Choisissez un département", departements, key='ville2')
            if ville2 == "France":
                center2, zoom2, ville_data2, rad2 = France(df)
                zoom2 = 5
            else:
                center2, zoom2, ville_data2, rad2 = Ville(df, ville2)
            map2 = folium.Map(location=center2, zoom_start=zoom2, control_scale=True)

    else:
        ville = st.selectbox("Choisissez un département", departements, key='ville')
        if ville == "France":
            center, zoom, ville_data, rad = France(df)
        else:
            center, zoom, ville_data, rad = Ville(df, ville)
        map = folium.Map(location=center, zoom_start=zoom, control_scale=True)

    if versus:
        with col1:
            display_kpi_metrics2(ville_data1, indicateur)
        with col2:
            display_kpi_metrics2(ville_data2, indicateur)
    else:
        display_kpi_metrics3(ville_data, indicateur)

    data2 = data.copy()
    if categ == quantile_ranges[0]:
        data2 = data2[data2['Catégorie'] == '0']
    elif categ == quantile_ranges[1]:
        data2 = data2[data2['Catégorie'] == '1']
    elif categ == quantile_ranges[2]:
        data2 = data2[data2['Catégorie'] == '2']

    if versus:
        with col1:
            for i, row in data2.iterrows():
                content = f'Département : {str(row["Département"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
                iframe = folium.IFrame(content, width=400, height=55)
                popup = folium.Popup(iframe, min_width=400, max_width=500)
                if marker:
                    folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup).add_to(map1)
            folium.Choropleth(
                geo_data=data_geo, name="choropleth", data=data2,
                columns=["Département", selected_indicateur],
                key_on="feature.properties.nom",
                fill_color="YlGnBu", fill_opacity=0.7, line_opacity=0.2,
                legend_name=selected_indicateur,
            ).add_to(map1)

        with col2:
            for i, row in data2.iterrows():
                content = f'Département : {str(row["Département"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
                iframe = folium.IFrame(content, width=400, height=55)
                popup = folium.Popup(iframe, min_width=400, max_width=500)
                if marker:
                    folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup).add_to(map2)
            folium.Choropleth(
                geo_data=data_geo, name="choropleth", data=data2,
                columns=["Département", selected_indicateur],
                key_on="feature.properties.nom",
                fill_color="YlGnBu", fill_opacity=0.7, line_opacity=0.2,
                legend_name=selected_indicateur,
            ).add_to(map2)

    else:
        for i, row in data2.iterrows():
            content = f'Département : {str(row["Département"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
            iframe = folium.IFrame(content, width=400, height=55)
            popup = folium.Popup(iframe, min_width=400, max_width=500)
            if marker:
                folium.Marker(location=[row['Latitude'], row['Longitude']], popup=popup).add_to(map)
        folium.Choropleth(
            geo_data=data_geo, name="choropleth", data=data2,
            columns=["Département", selected_indicateur],
            key_on="feature.properties.nom",
            fill_color="YlGnBu", fill_opacity=0.7, line_opacity=0.2,
            legend_name=selected_indicateur,
        ).add_to(map)

    if versus:
        with col1:
            st_folium(map1, height=500, width=500, key='map1')
        with col2:
            st_folium(map2, height=500, width=500, key='map2')
    else:
        st_folium(map, height=650, width=1050, key='map')

    # Section analyse
    if not versus:
        show_analyse_departement(data1, selected_indicateur, ville)
    else:
        st.divider()
        st.subheader("📊 Comparaison directe")
        if ville1 != "France" and ville2 != "France":
            vals = data1[data1['Département'].isin([ville1, ville2])][['Département', selected_indicateur]].dropna()
            if not vals.empty:
                fig_comp = px.bar(
                    vals, x='Département', y=selected_indicateur,
                    color='Département',
                    color_discrete_sequence=['#0496C7', '#02367B'],
                    title=f"{ville1} vs {ville2} : {selected_indicateur}"
                )
                st.plotly_chart(fig_comp, use_container_width=True)


if __name__ == "__main__":
    main()
