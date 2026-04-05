import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px


# Chargement des données
df = pd.read_excel('data/data_ville.xlsx')
df.dropna(subset=['Latitude'], inplace=True)
df.dropna(subset=['Longitude'], inplace=True)
df = df[df['Population'] >= 20000]

st.set_page_config(layout="wide", page_title="Villes", page_icon="🏙️")


def France(dataframe):
    center = [46.603354, 2.668561]
    zoom = 6
    ville_data = dataframe
    rad = 10
    return center, zoom, ville_data, rad


def Ville(dataframe, ville):
    ville_data = dataframe[dataframe['Ville'] == ville]
    center = [ville_data['Latitude'].mean(), ville_data['Longitude'].mean()]
    zoom = 13
    rad = 50
    return center, zoom, ville_data, rad


def circle_marker(map, row, rad, icon_color, popup):
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        stroke=False, radius=rad, color=icon_color,
        fill=True, fill_color=icon_color, fill_opacity=0.7,
        popup=popup, icon=folium.Icon(color=icon_color, icon='')
    ).add_to(map)


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


def show_analyse_ville(data_all, selected_indicateur, selected_ville):
    st.divider()
    st.subheader("📊 Analyse de l'indicateur")

    col_charts, col_stats = st.columns([2, 1])

    data_sorted = data_all[['Ville', selected_indicateur]].dropna().sort_values(selected_indicateur, ascending=False)

    with col_charts:
        tab1, tab2 = st.tabs(["🏆 Top 10 villes", "📉 Les 10 dernières"])
        with tab1:
            top10 = data_sorted.head(10).reset_index(drop=True)
            fig_top = px.bar(
                top10, x=selected_indicateur, y='Ville', orientation='h',
                color=selected_indicateur, color_continuous_scale='Blues',
                title=f"Top 10 : {selected_indicateur}"
            )
            fig_top.update_layout(yaxis={'categoryorder': 'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_top, use_container_width=True)

        with tab2:
            bot10 = data_sorted.tail(10).reset_index(drop=True)
            fig_bot = px.bar(
                bot10, x=selected_indicateur, y='Ville', orientation='h',
                color=selected_indicateur, color_continuous_scale='Reds',
                title=f"10 dernières : {selected_indicateur}"
            )
            fig_bot.update_layout(yaxis={'categoryorder': 'total descending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_bot, use_container_width=True)

    with col_stats:
        if selected_ville != "France":
            val = data_all.loc[data_all['Ville'] == selected_ville, selected_indicateur]
            if not val.empty:
                valeur = val.values[0]
                rang = data_sorted['Ville'].tolist().index(selected_ville) + 1
                total = len(data_sorted)
                st.metric(f"Valeur : {selected_ville}", f"{round(valeur, 1)}")
                st.metric("Classement national", f"{rang} / {total}")
                percentile = round((1 - rang / total) * 100)
                if percentile >= 75:
                    st.success(f"Cette ville est dans le **top {100 - percentile}%** national.")
                elif percentile <= 25:
                    st.warning(f"Cette ville est dans le **dernier quart** national.")
                else:
                    st.info(f"Cette ville se situe dans la **moyenne nationale**.")

        st.markdown("**Statistiques nationales**")
        col_s = data_all[selected_indicateur].dropna()
        st.write(f"- Moyenne : **{round(col_s.mean(), 1)}**")
        st.write(f"- Médiane : **{round(col_s.median(), 1)}**")
        st.write(f"- Min : **{round(col_s.min(), 1)}**")
        st.write(f"- Max : **{round(col_s.max(), 1)}**")

    st.subheader("📈 Distribution nationale")
    fig_hist = px.histogram(
        data_all.dropna(subset=[selected_indicateur]),
        x=selected_indicateur, nbins=40,
        color_discrete_sequence=['#0496C7'],
        title=f"Répartition des valeurs : {selected_indicateur}"
    )
    fig_hist.update_layout(bargap=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)


def main():
    st.markdown("<h1 style='text-align: center;'>🏙️ Carte des Villes</h1>", unsafe_allow_html=True)
    st.write("Comparez les villes françaises de plus de 20 000 habitants sur une multitude d'indicateurs.")

    versus = st.sidebar.toggle('⚔️ Mode Versus')

    villes = sorted(df['Ville'].tolist())
    villes.insert(0, "France")

    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)

    domaine = ["Démographie", "Economie", "Emploi", "Education", "Mobilité", "Logement", "Services"]
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
            "Nombre d'actifs occupés de 15-64 ans",
            "Nombre de chômeurs",
            "Taux d'activité des 15-64 ans",
            "Taux d'emploi des 15-64 ans",
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
            "Effectif des établissements d'enseignement supérieur",
            "Part des titulaires d'un diplôme de l'enseignement supérieur"
        ]
    elif selected_domaine == "Mobilité":
        indicateur = [
            "Part des déplacements en voiture",
            "Part des déplacements en transports en commun",
            "Part des déplacements en deux roues",
            "Proportion d'actifs occupés résidant à 30 minutes ou plus de leur lieu de travail"
        ]
    elif selected_domaine == "Logement":
        indicateur = [
            "Nombre de logements",
            "Nombre de logements vacants",
            "Part des logements vacants",
            "Loyer d'annonce par m² pour un appartement",
            "Loyer d'annonce par m² pour une maison"
        ]
    elif selected_domaine == "Services":
        indicateur = [
            "Nombre de licenciés sportifs",
            "Nombre de cinémas",
            "Nombre de structures France Services"
        ]

    selected_indicateur = st.sidebar.selectbox('📌 Choisir un indicateur', indicateur)
    data = data1[[selected_indicateur, 'Latitude', 'Longitude', 'Ville']].copy()

    if selected_indicateur in ["Nombre de cinémas", "Nombre de structures France Services"]:
        data['Catégorie'], bins = pd.qcut(data[selected_indicateur].rank(method='first'), 3, retbins=True, labels=False)
    else:
        data['Catégorie'], bins = pd.qcut(data[selected_indicateur], 3, labels=False, retbins=True)

    quantile_ranges = []
    for start, end in zip(bins[:-1], bins[1:]):
        formatted_range = f"{int(start)} à {int(end)}"
        quantile_ranges.append(formatted_range)

    data["Catégorie"] = data["Catégorie"].astype(str)

    purpose_colour = {'0': '#55E2E9', '1': '#0496C7', '2': '#02367B'}

    categ = st.sidebar.radio('📊 Répartition', ('Tous', quantile_ranges[0], quantile_ranges[1], quantile_ranges[2]))

    if versus:
        col1, col2 = st.columns(2)

        with col1:
            ville1 = st.selectbox("Choisissez une ville", villes, key='ville1')
            if ville1 == "France":
                center1, zoom1, ville_data1, rad1 = France(df)
                zoom1 = 5
            else:
                center1, zoom1, ville_data1, rad1 = Ville(df, ville1)
            map1 = folium.Map(location=center1, zoom_start=zoom1, control_scale=True)

        with col2:
            ville2 = st.selectbox("Choisissez une ville", villes, key='ville2')
            if ville2 == "France":
                center2, zoom2, ville_data2, rad2 = France(df)
                zoom2 = 5
            else:
                center2, zoom2, ville_data2, rad2 = Ville(df, ville2)
            map2 = folium.Map(location=center2, zoom_start=zoom2, control_scale=True)

    else:
        ville = st.selectbox("Choisissez une ville", villes, key='ville')
        if ville == "France":
            center, zoom, ville_data, rad = France(df)
        else:
            center, zoom, ville_data, rad = Ville(df, ville)
        map = folium.Map(location=center, zoom_start=zoom, control_scale=True)

    if versus:
        with col1:
            display_kpi_metrics2(ville_data1, indicateur)
            st.subheader(selected_indicateur)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.color_picker(quantile_ranges[0], '#55E2E9', key='c1a')
            with c2:
                st.color_picker(quantile_ranges[1], '#0496C7', key='c2a')
            with c3:
                st.color_picker(quantile_ranges[2], '#02367B', key='c3a')
        with col2:
            display_kpi_metrics2(ville_data2, indicateur)
            st.subheader(selected_indicateur)
            c1, c2, c3 = st.columns(3)
            with c1:
                st.color_picker(quantile_ranges[0], '#55E2E9', key='c1b')
            with c2:
                st.color_picker(quantile_ranges[1], '#0496C7', key='c2b')
            with c3:
                st.color_picker(quantile_ranges[2], '#02367B', key='c3b')
    else:
        display_kpi_metrics3(ville_data, indicateur)
        st.subheader(selected_indicateur)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.color_picker(quantile_ranges[0], '#55E2E9', key='c1')
        with c2:
            st.color_picker(quantile_ranges[1], '#0496C7', key='c2')
        with c3:
            st.color_picker(quantile_ranges[2], '#02367B', key='c3')

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
                content = f'Ville : {str(row["Ville"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
                iframe = folium.IFrame(content, width=400, height=55)
                popup = folium.Popup(iframe, min_width=400, max_width=500)
                try:
                    icon_color = purpose_colour[row['Catégorie']]
                except:
                    icon_color = 'gray'
                circle_marker(map1, row, rad1, icon_color, popup)

        with col2:
            for i, row in data2.iterrows():
                content = f'Ville : {str(row["Ville"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
                iframe = folium.IFrame(content, width=400, height=55)
                popup = folium.Popup(iframe, min_width=400, max_width=500)
                try:
                    icon_color = purpose_colour[row['Catégorie']]
                except:
                    icon_color = 'gray'
                circle_marker(map2, row, rad2, icon_color, popup)
    else:
        for i, row in data2.iterrows():
            content = f'Ville : {str(row["Ville"])}<br>{selected_indicateur} : {str(row[selected_indicateur])}'
            iframe = folium.IFrame(content, width=400, height=55)
            popup = folium.Popup(iframe, min_width=400, max_width=500)
            try:
                icon_color = purpose_colour[row['Catégorie']]
            except:
                icon_color = 'gray'
            circle_marker(map, row, rad, icon_color, popup)

    if versus:
        with col1:
            st_folium(map1, height=500, width=500, key='map1')
        with col2:
            st_folium(map2, height=500, width=500, key='map2')
    else:
        st_folium(map, height=650, width=1050, key='map')

    # Section analyse
    if not versus:
        show_analyse_ville(data1, selected_indicateur, ville)
    else:
        st.divider()
        st.subheader("📊 Comparaison directe")
        if ville1 != "France" and ville2 != "France":
            vals = data1[data1['Ville'].isin([ville1, ville2])][['Ville', selected_indicateur]].dropna()
            if not vals.empty:
                fig_comp = px.bar(
                    vals, x='Ville', y=selected_indicateur,
                    color='Ville',
                    color_discrete_sequence=['#0496C7', '#02367B'],
                    title=f"{ville1} vs {ville2} : {selected_indicateur}"
                )
                st.plotly_chart(fig_comp, use_container_width=True)


if __name__ == "__main__":
    main()
