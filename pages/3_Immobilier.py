import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import statistics
import matplotlib.pyplot as plt
import plotly.express as px
import requests
from io import StringIO
import os


df = pd.read_excel('data/data_immobilier.xlsx')
df.dropna(subset=['Latitude'], inplace=True)
df.dropna(subset=['Longitude'], inplace=True)
df = df[df['Population'] >= 20000]


st.set_page_config(layout="wide")


def France(dataframe):
    center = [46.603354, 2.668561]
    zoom = 6
    ville_data = dataframe
    rad = 10
    return center, zoom, ville_data, rad


def Ville(dataframe, ville):
    ville_data = dataframe[dataframe['ville_code'] == ville]
    center = [ville_data['Latitude'].mean(), ville_data['Longitude'].mean()]
    zoom = 14
    rad = 8
    return center, zoom, ville_data, rad


def circle_marker(map, row, rad, icon_color, popup):
    folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
                        stroke=False,
                        radius=rad,
                        color=icon_color,
                        fill=True,
                        fill_color=icon_color,
                        fill_opacity=0.7,
                        popup=popup,
                        icon=folium.Icon(color=icon_color, icon='')).add_to(map)


def main():
    purpose_colour = {
        '0': '#55E2E9',
        '1': '#0496C7',
        '2': '#02367B'
    }

    st.markdown("<h1 style='text-align: center;'>Analyse Immobilière</h1>", unsafe_allow_html=True)

    versus = st.sidebar.toggle('Versus')
    indicateur = ["Valeur foncière","Surface réelle bâtie","Prix au m2"]
    selected_indicateur = st.sidebar.selectbox('Choisir un indicateur', indicateur)
    type = ["Tous les types de locaux","Maison","Appartement"]
    selected_type = st.sidebar.selectbox('Choisir un type de local', type)

    villes = df['ville_code'].tolist()
    villes = sorted(villes)
    villes.insert(0, "France")

    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)


    if versus:
        col1, col2 = st.columns(2)

        with col1:
            ville1 = st.selectbox("Choisissez une ville", villes, key='ville1')
            if ville1=="France":
                center1, zoom1, ville_data1, rad1 = France(df)
                zoom1=5
                map1 = folium.Map(location=center1, zoom_start=zoom1, control_scale=True)
            else:
                code=ville1[-6:-4]
                vil=ville1[-6:-1]
                csv_filename = f'data/immobilier/dvf_departement_{code}.csv'

                if os.path.exists(csv_filename):
                    print('existe deja')
                else:
                    # URL de base pour le téléchargement des fichiers CSV
                    url_base = "https://dvf-api.data.gouv.fr/dvf/csv/?dep="


                    url = f"{url_base}{code}"
                    response = requests.get(url)
                    if response.ok and response.content:
                        try:
                            # Création d'un DataFrame à partir des données téléchargées
                            data = pd.read_csv(StringIO(response.content.decode('utf-8')))
                            # Sauvegarde du DataFrame en CSV
                            csv_filename = f'data/immobilier/dvf_departement_{code}.csv'
                            data.to_csv(csv_filename, index=False)
                            print(f"Téléchargé et sauvegardé : {csv_filename}")
                        except pd.errors.EmptyDataError:
                            print(f"Aucune donnée à lire pour le département {code}")
                    else:
                        print(f"Erreur lors du téléchargement pour le département {code}")

                
                center1, zoom1, ville_data1, rad1 = Ville(df, ville1)
                
                dfbis = pd.read_csv(csv_filename, sep=',')
                dfbis = dfbis[dfbis['id_mutation'] != 'id_mutation']
                dfbis = dfbis[dfbis['type_local'].isin(['Maison', 'Appartement'])]
                dfbis['adresse_suffixe'].fillna('', inplace=True)
                dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
                dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: x[:5])
                dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
                dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: x[:5])
                dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 2 else str(x))
                dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: x[:2])

                dfbis['adresse'] = (
                    dfbis['adresse_numero'].astype(str).str.replace('.0', '') + " " +
                    dfbis['adresse_suffixe'].astype(str) + " " +
                    dfbis['adresse_nom_voie'].astype(str) + " " +
                    dfbis['code_postal'].astype(str) + " " +
                    dfbis['nom_commune'].astype(str)
                )
                dfbis['Adresse'] = dfbis['adresse'].str.replace('  ', ' ')
                dfbis['Latitude'] = dfbis['latitude'].astype(float)
                dfbis['Longitude'] = dfbis['longitude'].astype(float)
                dfbis['Valeur foncière'] = dfbis['valeur_fonciere'].astype(float)
                dfbis['Surface réelle bâtie'] = dfbis['surface_reelle_bati'].astype(float)
                dfbis.dropna(subset=['Valeur foncière'], inplace=True)
                dfbis.dropna(subset=['Surface réelle bâtie'], inplace=True)
                dfbis = dfbis.rename(columns={'type_local': 'Type local'})

                cols_to_keep = ['id_mutation','date_mutation','Valeur foncière','Adresse','code_commune','code_departement','Type local','Surface réelle bâtie','Longitude','Latitude']
                dfbis = dfbis[cols_to_keep]
                dfbis.drop_duplicates(subset=['id_mutation'], inplace=True)
                dfbis.dropna(subset=['Latitude'], inplace=True)
                dfbis.dropna(subset=['Longitude'], inplace=True)
                dfbis['Prix au m2']=dfbis['Valeur foncière']/dfbis['Surface réelle bâtie']

                df2001 = dfbis
                if ville1 == "Paris (75056)":
                    df2001['code_commune']="75056"
                df2001 = df2001[df2001['code_commune'] == str(vil)]
                df2022 = df2001.groupby('Adresse').last().reset_index()
                row_count = df2022.shape[0]
                df2022 = df2022[-int(5/100*row_count):]

                
                map1 = folium.Map(location=center1, zoom_start=zoom1, control_scale=True)

                data_type=df2022
                if selected_type == "Maison":
                    data1=data_type[data_type['Type local'] == 'Maison']
                elif selected_type == "Appartement":
                    data1=data_type[data_type['Type local'] == 'Appartement']
                else:
                    data1=data_type

                data = data1[[selected_indicateur,'Latitude','Longitude','Adresse','Type local']]

                data['Catégorie'], bins =  pd.qcut(data[selected_indicateur], 3, retbins=True, labels=False)

                quantile_ranges = []
                for start, end in zip(bins[:-1], bins[1:]):
                    start, end = int(start), int(end)
                    formatted_range = f"{start} à {end}"
                    quantile_ranges.append(formatted_range)

                data["Catégorie"] = data["Catégorie"].astype(str)

                categ = st.radio('Répartition',('Tous',quantile_ranges[0],quantile_ranges[1],quantile_ranges[2]), key='categ1')

                data2=data
                if categ == quantile_ranges[0]:
                    data2=data2[(data2['Catégorie']== '0')]
                elif categ == quantile_ranges[1]:
                    data2=data2[(data2['Catégorie']== '1')]
                elif categ == quantile_ranges[2]:
                    data2=data2[(data2['Catégorie']== '2')]
                else:
                    data2=data
                dataville1=data2
            
                col11,col21,col31 = st.columns(3)
                col11.metric('Valeur foncière',str(round(data1['Valeur foncière'].mean(),2)) + '€')
                col21.metric('Surface réelle bâtie',str(round(data1['Surface réelle bâtie'].mean(),2)) + 'm2')
                col31.metric('Prix au m2',str(round(data1['Prix au m2'].mean(),2)) + '€')

                st.subheader(selected_indicateur)
                color1,color2,color3=st.columns(3)
                with color1:
                    st.color_picker(quantile_ranges[0],'#55E2E9',key=color1)
                with color2:
                    st.color_picker(quantile_ranges[1],'#0496C7',key=color2)
                with color3:
                    st.color_picker(quantile_ranges[2],'#02367B',key=color3)


                if ville1=="France":
                    center, zoom, ville_data, rad = France(df)

                for i,row in dataville1.iterrows():
                    content = f'Adresse : {str(row["Adresse"])}<br>' f'{selected_indicateur} : {str(row[selected_indicateur])}'
                    iframe = folium.IFrame(content, width=400, height=55)
                    popup = folium.Popup(iframe, min_width=400, max_width=500)
                                                
                    try:
                        icon_color = purpose_colour[row['Catégorie']]
                    except:
                        icon_color = 'gray'
                    circle_marker(map1, row, rad1, icon_color, popup)
    

        with col2:
            ville2 = st.selectbox("Choisissez une ville", villes, key='ville2')
            if ville2=="France":
                center2, zoom2, ville_data2, rad2 = France(df)
                zoom2=5
                map2 = folium.Map(location=center2, zoom_start=zoom2, control_scale=True)
            else:
                code=ville2[-6:-4]
                vil=ville2[-6:-1]
                csv_filename = f'data/immobilier/dvf_departement_{code}.csv'

                if os.path.exists(csv_filename):
                    print('existe deja')
                else:
                    # URL de base pour le téléchargement des fichiers CSV
                    url_base = "https://dvf-api.data.gouv.fr/dvf/csv/?dep="


                    url = f"{url_base}{code}"
                    response = requests.get(url)
                    if response.ok and response.content:
                        try:
                            # Création d'un DataFrame à partir des données téléchargées
                            data = pd.read_csv(StringIO(response.content.decode('utf-8')))
                            # Sauvegarde du DataFrame en CSV
                            csv_filename = f'data/immobilier/dvf_departement_{code}.csv'
                            data.to_csv(csv_filename, index=False)
                            print(f"Téléchargé et sauvegardé : {csv_filename}")
                        except pd.errors.EmptyDataError:
                            print(f"Aucune donnée à lire pour le département {code}")
                    else:
                        print(f"Erreur lors du téléchargement pour le département {code}")

                center2, zoom2, ville_data2, rad2 = Ville(df, ville2)
                
                dfbis = pd.read_csv(csv_filename, sep=',')
                dfbis = dfbis[dfbis['id_mutation'] != 'id_mutation']
                dfbis = dfbis[dfbis['type_local'].isin(['Maison', 'Appartement'])]
                dfbis['adresse_suffixe'].fillna('', inplace=True)
                dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
                dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: x[:5])
                dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
                dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: x[:5])
                dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 2 else str(x))
                dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: x[:2])

                dfbis['adresse'] = (
                    dfbis['adresse_numero'].astype(str).str.replace('.0', '') + " " +
                    dfbis['adresse_suffixe'].astype(str) + " " +
                    dfbis['adresse_nom_voie'].astype(str) + " " +
                    dfbis['code_postal'].astype(str) + " " +
                    dfbis['nom_commune'].astype(str)
                )
                dfbis['Adresse'] = dfbis['adresse'].str.replace('  ', ' ')
                dfbis['Latitude'] = dfbis['latitude'].astype(float)
                dfbis['Longitude'] = dfbis['longitude'].astype(float)
                dfbis['Valeur foncière'] = dfbis['valeur_fonciere'].astype(float)
                dfbis['Surface réelle bâtie'] = dfbis['surface_reelle_bati'].astype(float)
                dfbis.dropna(subset=['Valeur foncière'], inplace=True)
                dfbis.dropna(subset=['Surface réelle bâtie'], inplace=True)
                dfbis = dfbis.rename(columns={'type_local': 'Type local'})

                cols_to_keep = ['id_mutation','date_mutation','Valeur foncière','Adresse','code_commune','code_departement','Type local','Surface réelle bâtie','Longitude','Latitude']
                dfbis = dfbis[cols_to_keep]
                dfbis.drop_duplicates(subset=['id_mutation'], inplace=True)
                dfbis.dropna(subset=['Latitude'], inplace=True)
                dfbis.dropna(subset=['Longitude'], inplace=True)
                dfbis['Prix au m2']=dfbis['Valeur foncière']/dfbis['Surface réelle bâtie']

                df2002 = dfbis
                if ville2 == "Paris (75056)":
                    df2002['code_commune']="75056"
                df2002 = df2002[df2002['code_commune'] == str(vil)]
                df2022 = df2002.groupby('Adresse').last().reset_index()
                row_count = df2022.shape[0]
                df2022 = df2022[-int(5/100*row_count):]

                
                map2 = folium.Map(location=center2, zoom_start=zoom2, control_scale=True)
                indicateur = ["Valeur foncière","Surface réelle bâtie"]

                data_type=df2022
                if selected_type == "Maison":
                    data1=data_type[data_type['Type local'] == 'Maison']
                elif selected_type == "Appartement":
                    data1=data_type[data_type['Type local'] == 'Appartement']
                else:
                    data1=data_type

                data = data1[[selected_indicateur,'Latitude','Longitude','Adresse','Type local']]

                data['Catégorie'], bins =  pd.qcut(data[selected_indicateur], 3, retbins=True, labels=False)

                quantile_ranges = []
                for start, end in zip(bins[:-1], bins[1:]):
                    start, end = int(start), int(end)
                    formatted_range = f"{start} à {end}"
                    quantile_ranges.append(formatted_range)

                data["Catégorie"] = data["Catégorie"].astype(str)

                categ = st.radio('Répartition',('Tous',quantile_ranges[0],quantile_ranges[1],quantile_ranges[2]), key='categ2')

                data2=data
                if categ == quantile_ranges[0]:
                    data2=data2[(data2['Catégorie']== '0')]
                elif categ == quantile_ranges[1]:
                    data2=data2[(data2['Catégorie']== '1')]
                elif categ == quantile_ranges[2]:
                    data2=data2[(data2['Catégorie']== '2')]
                else:
                    data2=data
                dataville2=data2

                col12,col22,col32 = st.columns(3)
                col12.metric('Valeur foncière',str(round(data1['Valeur foncière'].mean(),2)) + '€')
                col22.metric('Surface réelle bâtie',str(round(data1['Surface réelle bâtie'].mean(),2)) + 'm2')
                col32.metric('Prix au m2',str(round(data1['Prix au m2'].mean(),2)) + '€')

                st.subheader(selected_indicateur)
                color1,color2,color3=st.columns(3)
                with color1:
                    st.color_picker(quantile_ranges[0],'#55E2E9',key=color1)
                with color2:
                    st.color_picker(quantile_ranges[1],'#0496C7',key=color2)
                with color3:
                    st.color_picker(quantile_ranges[2],'#02367B',key=color3)

                if ville2=="France":
                    center, zoom, ville_data, rad = France(df)

                for i,row in dataville2.iterrows():
                    content = f'Adresse : {str(row["Adresse"])}<br>' f'{selected_indicateur} : {str(row[selected_indicateur])}'
                    iframe = folium.IFrame(content, width=400, height=55)
                    popup = folium.Popup(iframe, min_width=400, max_width=500)
                                                
                    try:
                        icon_color = purpose_colour[row['Catégorie']]
                    except:
                        icon_color = 'gray'
                    circle_marker(map2, row, rad2, icon_color, popup)


    else:
        ville = st.selectbox("Choisissez une ville", villes, key='ville')
        if ville=="France":
            center, zoom, ville_data, rad = France(df)
            map = folium.Map(location=center, zoom_start=zoom, control_scale=True)

        else:
            code=ville[-6:-4]
            vil=ville[-6:-1]
            csv_filename = f'data/immobilier/dvf_departement_{code}.csv'

            if os.path.exists(csv_filename):
                print('existe deja')
            else:
                # URL de base pour le téléchargement des fichiers CSV
                url_base = "https://dvf-api.data.gouv.fr/dvf/csv/?dep="


                url = f"{url_base}{code}"
                response = requests.get(url)
                if response.ok and response.content:
                    try:
                        # Création d'un DataFrame à partir des données téléchargées
                        data = pd.read_csv(StringIO(response.content.decode('utf-8')))
                        # Sauvegarde du DataFrame en CSV
                        csv_filename = f'data/immobilier/dvf_departement_{code}.csv'
                        data.to_csv(csv_filename, index=False)
                        print(f"Téléchargé et sauvegardé : {csv_filename}")
                    except pd.errors.EmptyDataError:
                        print(f"Aucune donnée à lire pour le département {code}")
                else:
                    print(f"Erreur lors du téléchargement pour le département {code}")

            center, zoom, ville_data, rad = Ville(df, ville)
            
            dfbis = pd.read_csv(csv_filename, sep=',')
            dfbis = dfbis[dfbis['id_mutation'] != 'id_mutation']
            dfbis = dfbis[dfbis['type_local'].isin(['Maison', 'Appartement'])]
            dfbis['adresse_suffixe'].fillna('', inplace=True)
            dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
            dfbis['code_postal'] = dfbis['code_postal'].astype(str).apply(lambda x: x[:5])
            dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 5 else str(x))
            dfbis['code_commune'] = dfbis['code_commune'].astype(str).apply(lambda x: x[:5])
            dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: '0' + x if len(str(x)) != 2 else str(x))
            dfbis['code_departement'] = dfbis['code_departement'].astype(str).apply(lambda x: x[:2])

            dfbis['adresse'] = (
                dfbis['adresse_numero'].astype(str).str.replace('.0', '') + " " +
                dfbis['adresse_suffixe'].astype(str) + " " +
                dfbis['adresse_nom_voie'].astype(str) + " " +
                dfbis['code_postal'].astype(str) + " " +
                dfbis['nom_commune'].astype(str)
            )
            dfbis['Adresse'] = dfbis['adresse'].str.replace('  ', ' ')
            dfbis['Latitude'] = dfbis['latitude'].astype(float)
            dfbis['Longitude'] = dfbis['longitude'].astype(float)
            dfbis['Valeur foncière'] = dfbis['valeur_fonciere'].astype(float)
            dfbis['Surface réelle bâtie'] = dfbis['surface_reelle_bati'].astype(float)
            dfbis.dropna(subset=['Valeur foncière'], inplace=True)
            dfbis.dropna(subset=['Surface réelle bâtie'], inplace=True)
            dfbis = dfbis.rename(columns={'type_local': 'Type local'})

            cols_to_keep = ['id_mutation','date_mutation','Valeur foncière','Adresse','code_commune','code_departement','Type local','Surface réelle bâtie','Longitude','Latitude']
            dfbis = dfbis[cols_to_keep]
            dfbis.drop_duplicates(subset=['id_mutation'], inplace=True)
            dfbis.dropna(subset=['Latitude'], inplace=True)
            dfbis.dropna(subset=['Longitude'], inplace=True)
            dfbis['Prix au m2']=dfbis['Valeur foncière']/dfbis['Surface réelle bâtie']

            df2000 = dfbis
            if ville == "Paris (75056)":
                df2000['code_commune']="75056"
            df2000 = df2000[df2000['code_commune'] == str(vil)]
            df2022 = df2000.groupby('Adresse').last().reset_index()
            row_count = df2022.shape[0]
            df2022 = df2022[-int(5/100*row_count):]

            
            map = folium.Map(location=center, zoom_start=zoom, control_scale=True)
            data_type=df2022
            if selected_type == "Maison":
                data1=data_type[data_type['Type local'] == 'Maison']
            elif selected_type == "Appartement":
                data1=data_type[data_type['Type local'] == 'Appartement']
            else:
                data1=data_type

            data = data1[[selected_indicateur,'Latitude','Longitude','Adresse','Type local']]

            data['Catégorie'], bins =  pd.qcut(data[selected_indicateur], 3, retbins=True, labels=False)

            quantile_ranges = []
            for start, end in zip(bins[:-1], bins[1:]):
                start, end = int(start), int(end)
                formatted_range = f"{start} à {end}"
                quantile_ranges.append(formatted_range)

            data["Catégorie"] = data["Catégorie"].astype(str)

            categ = st.sidebar.radio('Répartition',('Tous',quantile_ranges[0],quantile_ranges[1],quantile_ranges[2]))

            data2=data
            if categ == quantile_ranges[0]:
                data2=data2[(data2['Catégorie']== '0')]
            elif categ == quantile_ranges[1]:
                data2=data2[(data2['Catégorie']== '1')]
            elif categ == quantile_ranges[2]:
                data2=data2[(data2['Catégorie']== '2')]
            else:
                data2=data

            col13,col23,col33 = st.columns(3)
            col13.metric('Valeur foncière',str(round(data1['Valeur foncière'].mean(),2)) + '€')
            col23.metric('Surface réelle bâtie',str(round(data1['Surface réelle bâtie'].mean(),2)) + 'm2')
            col33.metric('Prix au m2',str(round(data1['Prix au m2'].mean(),2)) + '€')

            st.subheader(selected_indicateur)
            color1,color2,color3=st.columns(3)
            with color1:
                st.color_picker(quantile_ranges[0],'#55E2E9',key=color1)
            with color2:
                st.color_picker(quantile_ranges[1],'#0496C7',key=color2)
            with color3:
                st.color_picker(quantile_ranges[2],'#02367B',key=color3)

            if ville=="France":
                center, zoom, ville_data, rad = France(df)

            for i,row in data2.iterrows():
                content = f'Adresse : {str(row["Adresse"])}<br>' f'{selected_indicateur} : {str(row[selected_indicateur])}'
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

    if versus:
        st.divider()
        with col1:
            if ville1!="France":
                col111, col222 = st.columns(2)
                col111.metric('Nombre total de ventes',str(df2001.shape[0]))
                col222.metric('Prix de vente médian au m2',str(int(statistics.median(df2001['Prix au m2']))) + '€')

                df_show=df2001
                df_show = df_show.groupby('Type local')['Prix au m2'].agg(['count', 'median']).reset_index()
                df_show = df_show.rename(columns={'count':'Nombre de ventes', 'median':'Prix médian au m2'})
                df_show['Prix médian au m2'] = df_show['Prix médian au m2'].astype(int).astype(str) + '€'
                st.header("Données par type de local")
                st.dataframe(df_show, use_container_width=True, hide_index=True)

                data_type=df2001
                if selected_type == "Maison":
                    df_date=data_type[data_type['Type local'] == 'Maison']
                elif selected_type == "Appartement":
                    df_date=data_type[data_type['Type local'] == 'Appartement']
                else:
                    df_date=data_type

                df_date['Year_Month'] = df_date['date_mutation'].str[:7]
                df_date=df_date[['Year_Month','Prix au m2']]
                df_date['Year_Month'] = pd.to_datetime(df_date['Year_Month'])
                df_date = df_date.groupby('Year_Month')['Prix au m2'].median().reset_index()

                fig1 = px.line(
                    df_date, 
                    x ='Year_Month',   
                    y ='Prix au m2', 
                    markers = True, 
                    labels = {'Year_Month' : 'Date de vente',
                              'Prix au m2' :'Prix médian au m2'}, 
                    title = 'Evolution du prix de vente médian au m2' )
                fig1.update_layout(xaxis_tickangle=-45)
                fig1.update_layout(width = 500, height =600)
                col1.plotly_chart(fig1)

                max_value = df_date['Prix au m2'].max()
                num_bins = 10
                bin_edges = range(0, int(max_value) + int(max_value) // num_bins + 1, int(max_value) // num_bins)

                
                plt.figure(figsize=(10, 6))
                plt.hist(df2022['Prix au m2'], bins=bin_edges, edgecolor='black')
                plt.title('Distribution des prix de vente')
                plt.xlabel('Prix médian au m2')
                plt.ylabel('Nombre de ventes')
                plt.tight_layout()
                st.pyplot()


        with col2:
            if ville2!="France":
                col333, col444 = st.columns(2)
                col333.metric('Nombre total de ventes',str(df2002.shape[0]))
                col444.metric('Prix de vente médian au m2',str(int(statistics.median(df2002['Prix au m2']))) + '€')

                df_show2=df2002
                df_show2 = df_show2.groupby('Type local')['Prix au m2'].agg(['count', 'median']).reset_index()
                df_show2 = df_show2.rename(columns={'count':'Nombre de ventes', 'median':'Prix médian au m2'})
                df_show2['Prix médian au m2'] = df_show2['Prix médian au m2'].astype(int).astype(str) + '€'
                st.header("Données par type de local")
                st.dataframe(df_show, use_container_width=True, hide_index=True)

                data_type2=df2002
                if selected_type == "Maison":
                    df_date2=data_type2[data_type2['Type local'] == 'Maison']
                elif selected_type == "Appartement":
                    df_date2=data_type2[data_type2['Type local'] == 'Appartement']
                else:
                    df_date2=data_type2

                df_date2['Year_Month'] = df_date2['date_mutation'].str[:7]
                df_date2=df_date2[['Year_Month','Prix au m2']]
                df_date2['Year_Month'] = pd.to_datetime(df_date2['Year_Month'])
                df_date2 = df_date2.groupby('Year_Month')['Prix au m2'].median().reset_index()

                fig = px.line(
                    df_date2, 
                    x ='Year_Month',   
                    y ='Prix au m2', 
                    markers = True, 
                    labels = {'Year_Month' : 'Date de vente',
                              'Prix au m2' :'Prix médian au m2'}, 
                    title = 'Evolution du prix de vente médian au m2' )
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_layout(width = 500, height =600)
                col2.plotly_chart(fig)

                max_value2 = df_date2['Prix au m2'].max()
                num_bins2 = 10
                bin_edges2 = range(0, int(max_value2) + int(max_value2) // num_bins2 + 1, int(max_value2) // num_bins2)

                plt.figure(figsize=(10, 6))
                plt.hist(df2002['Prix au m2'], bins=bin_edges, edgecolor='black')
                plt.title('Distribution des prix de vente')
                plt.xlabel('Prix médian au m2')
                plt.ylabel('Nombre de ventes')
                plt.tight_layout()
                st.pyplot()


    else:
        if ville!="France":
            st.divider()
            col1, col2 = st.columns(2)
            col1.metric('Nombre total de ventes',str(df2000.shape[0]))
            col2.metric('Prix de vente médian au m2',str(int(statistics.median(df2000['Prix au m2']))) + '€')

            df_show=df2000
            df_show = df_show.groupby('Type local')['Prix au m2'].agg(['count', 'median']).reset_index()
            df_show = df_show.rename(columns={'count':'Nombre de ventes', 'median':'Prix médian au m2'})
            df_show['Prix médian au m2'] = df_show['Prix médian au m2'].astype(int).astype(str) + '€'
            st.header("Données par type de local")
            st.dataframe(df_show, use_container_width=True, hide_index=True)

            data_type=df2000
            if selected_type == "Maison":
                df_date=data_type[data_type['Type local'] == 'Maison']
            elif selected_type == "Appartement":
                df_date=data_type[data_type['Type local'] == 'Appartement']
            else:
                df_date=data_type

            colgrap1, colgrap2 = st.columns(2)

            with colgrap1:
                df_date['Year_Month'] = df_date['date_mutation'].str[:7]
                df_date=df_date[['Year_Month','Prix au m2']]
                df_date['Year_Month'] = pd.to_datetime(df_date['Year_Month'])
                df_date = df_date.groupby('Year_Month')['Prix au m2'].median().reset_index()

                fig = px.line(
                    df_date, 
                    x ='Year_Month',   
                    y ='Prix au m2', 
                    markers = True, 
                    labels = {'Year_Month' : 'Date de vente',
                              'Prix au m2' :'Prix médian au m2'}, 
                    title = 'Evolution du prix de vente médian au m2' )
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_layout(width = 500)
                st.plotly_chart(fig)

            
            with colgrap2:
                max_value = df_date['Prix au m2'].max()
                num_bins = 10
                bin_edges = range(0, int(max_value) + int(max_value) // num_bins + 1, int(max_value) // num_bins)

                plt.figure(figsize=(10, 6))
                plt.hist(df2022['Prix au m2'], bins=bin_edges, edgecolor='black')
                plt.title('Distribution des prix de vente')
                plt.xlabel('Prix médian au m2')
                plt.ylabel('Nombre de ventes')
                plt.tight_layout()
                st.pyplot()


if __name__ == "__main__":
    main()
