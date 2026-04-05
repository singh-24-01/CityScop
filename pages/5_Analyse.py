import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(layout="wide", page_title="Analyse", page_icon="📊")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] { gap: 3px; flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"] { padding: 5px 12px; font-size: 13px; border-radius: 6px 6px 0 0; }
    .stTabs [aria-selected="true"] { background-color: #0F2044; }
    .group-label { font-size: 11px; color: #4FC3F7; text-transform: uppercase;
                   letter-spacing: 1px; margin: 8px 0 2px 0; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_ville = pd.read_excel('data/data_ville.xlsx')
    df_ville.dropna(subset=['Latitude','Longitude'], inplace=True)
    df_ville = df_ville[df_ville['Population'] >= 20000]

    df_dep = pd.read_excel('data/data_departement.xlsx')
    df_dep[['Latitude','Longitude']] = df_dep['Geo Point'].str.split(', ', expand=True)
    df_dep.dropna(subset=['Latitude','Longitude'], inplace=True)
    df_dep = df_dep[df_dep['Population'] >= 20000]

    df_meteo = pd.read_excel('data/meteo.xlsx')
    for col in df_meteo.columns:
        df_meteo = df_meteo[df_meteo[col] != 0]

    df_dep = pd.merge(df_dep, df_meteo, left_on='Code', right_on='department (code)', how='left')
    return df_ville, df_dep

df_ville, df_dep = load_data()

COLS_VILLE = [c for c in df_ville.select_dtypes(include='number').columns if c not in ['Latitude','Longitude','Code']]
COLS_DEP   = [c for c in df_dep.select_dtypes(include='number').columns   if c not in ['Latitude','Longitude','Code','department (code)']]

COLORS = ['#4FC3F7','#02367B','#55E2E9','#F4A261','#E76F51','#2A9D8F','#E9C46A','#264653']

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("<h1 style='text-align:center;'>📊 Analyse approfondie</h1>", unsafe_allow_html=True)
st.write("On croise les données, on cherche des tendances, et on met en évidence ce qui distingue vraiment les territoires.")
st.divider()

niveau  = st.radio("Niveau d'analyse", ["Villes","Départements"], horizontal=True)
df      = df_ville if niveau=="Villes" else df_dep
col_nom = "Ville"  if niveau=="Villes" else "Département"
cols_num = COLS_VILLE if niveau=="Villes" else COLS_DEP

# ─── Groupes sémantiques d'indicateurs ───────────────────────────────────────
def cols_groupe(cols, keys): return [c for c in cols if any(k in c for k in keys)]

G = {
    "Emploi":    cols_groupe(cols_num, ["actif","emploi","chômage","activité","inactif"]),
    "Logement":  cols_groupe(cols_num, ["logement","Loyer","vacant","hébergement"]),
    "Education": cols_groupe(cols_num, ["école","collège","lycée","diplôme","supérieur","enseignement"]),
    "Services":  cols_groupe(cols_num, ["cinéma","sportif","licencié","France Services","culturels","4G","Pôle Emploi"]),
    "Mobilité":  cols_groupe(cols_num, ["déplacement","résidant","voiture","commun","deux roues"]),
    "Economie":  cols_groupe(cols_num, ["entreprises"]),
    "Météo":     cols_groupe(cols_num, ["Température","humidité","Précipitations","vent"]),
}

# ─── Labels des onglets regroupés par catégorie ───────────────────────────────
#  EXPLORER            COMPARER              ANALYSER              NOUVEAU
(t_fiche, t_rank,    t_versus, t_score,    t_corr, t_scatter,    t_filtre, t_demo, t_loyer) = st.tabs([
    "📋 Fiche",  "🏆 Classements",
    "🆚 Comparaison",  "🎯 Score",
    "🔗 Corrélations",  "📈 Scatter",
    "🔍 Trouve ta ville",  "👥 Démographie",  "🌡️ Cadre de vie",
])


# ══════════════════════════════════════════════════════════════════════════════
# 📋 FICHE TERRITOIRE
# ══════════════════════════════════════════════════════════════════════════════
with t_fiche:
    st.subheader("Fiche complète d'un territoire")
    st.write("Toutes les données disponibles, avec l'écart par rapport à la moyenne nationale pour chaque indicateur.")

    terr_fiche = st.selectbox(f"Territoire", sorted(df[col_nom].dropna().tolist()), key='fiche_terr')
    row = df[df[col_nom]==terr_fiche].iloc[0] if terr_fiche in df[col_nom].values else None

    if row is not None:
        st.markdown(f"## {terr_fiche}")
        st.divider()
        groupes_fiche = {
            "👥 Démographie":  cols_groupe(cols_num, ["Population"]),
            "💼 Emploi":       G["Emploi"],
            "🏠 Logement":     G["Logement"],
            "🎓 Education":    G["Education"],
            "🚗 Mobilité":     G["Mobilité"],
            "🎭 Services":     G["Services"],
            "🏭 Economie":     G["Economie"],
            "🌤️ Météo":       G["Météo"],
        }
        for gnom, gcols in groupes_fiche.items():
            valid = [c for c in gcols if c in df.columns and pd.notna(row.get(c))]
            if not valid: continue
            st.markdown(f"### {gnom}")
            ncols = min(4, len(valid))
            display_cols = st.columns(ncols)
            for i, c in enumerate(valid):
                val   = row[c]
                moy   = df[c].mean()
                delta = round(val - moy, 1)
                display_cols[i % ncols].metric(
                    label=c[:40], value=round(val,1),
                    delta=f"{'+' if delta>0 else ''}{delta} vs moy."
                )
            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 🏆 CLASSEMENTS
# ══════════════════════════════════════════════════════════════════════════════
with t_rank:
    st.subheader("Qui est en tête, qui est à la traîne ?")

    c1, c2 = st.columns([3,1])
    with c1: ind_rank = st.selectbox("Indicateur", cols_num, key='rank_ind')
    with c2: n_top    = st.slider("Nombre", 5, 30, 10, key='rank_n')

    data_rank = df[[col_nom, ind_rank]].dropna().sort_values(ind_rank, ascending=False).reset_index(drop=True)

    col_top, col_bot = st.columns(2)
    with col_top:
        st.markdown(f"#### 🏆 Top {n_top}")
        fig = px.bar(data_rank.head(n_top), x=ind_rank, y=col_nom, orientation='h',
                     color=ind_rank, color_continuous_scale='Blues')
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False, margin=dict(l=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_bot:
        st.markdown(f"#### 📉 Dernier {n_top}")
        fig = px.bar(data_rank.tail(n_top).iloc[::-1], x=ind_rank, y=col_nom, orientation='h',
                     color=ind_rank, color_continuous_scale='Reds')
        fig.update_layout(yaxis={'categoryorder':'total descending'}, coloraxis_showscale=False, margin=dict(l=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    c_box, c_stats = st.columns([2,1])
    with c_box:
        fig_box = px.box(data_rank, y=ind_rank, points="all", color_discrete_sequence=['#4FC3F7'],
                         title=f"Distribution : {ind_rank}")
        fig_box.update_traces(marker_size=3)
        st.plotly_chart(fig_box, use_container_width=True)
    with c_stats:
        st.markdown("#### Statistiques nationales")
        s = data_rank[ind_rank]
        st.metric("Moyenne",  round(s.mean(),1))
        st.metric("Médiane",  round(s.median(),1))
        st.metric("Minimum",  round(s.min(),1))
        st.metric("Maximum",  round(s.max(),1))
        st.metric("Écart-type", round(s.std(),1))


# ══════════════════════════════════════════════════════════════════════════════
# 🆚 COMPARAISON MULTI-VILLES
# ══════════════════════════════════════════════════════════════════════════════
with t_versus:
    st.subheader("Comparer plusieurs territoires sur plusieurs indicateurs")

    all_terr = sorted(df[col_nom].dropna().tolist())
    sel_terr = st.multiselect(f"{niveau}", all_terr, default=all_terr[:4], max_selections=8, key='mt')
    sel_inds = st.multiselect("Indicateurs", cols_num, default=cols_num[:5], max_selections=10, key='mi')

    if sel_terr and sel_inds:
        comp = df[df[col_nom].isin(sel_terr)][[col_nom]+sel_inds].set_index(col_nom)

        st.subheader("Tableau comparatif")
        st.dataframe(comp.T.style.background_gradient(axis=1, cmap='Blues'), use_container_width=True)

        if len(sel_inds) >= 3:
            st.subheader("Radar comparatif (normalisé 0–100)")
            norm = comp.copy()
            for c in sel_inds:
                mn, mx = norm[c].min(), norm[c].max()
                norm[c] = (norm[c]-mn)/(mx-mn)*100 if mx!=mn else 50
            fig_r = go.Figure()
            for idx, t in enumerate(sel_terr):
                if t in norm.index:
                    v = norm.loc[t, sel_inds].tolist()
                    fig_r.add_trace(go.Scatterpolar(
                        r=v+[v[0]], theta=sel_inds+[sel_inds[0]],
                        fill='toself', name=t, opacity=0.6, line_color=COLORS[idx%len(COLORS)]))
            fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                                showlegend=True, height=500)
            st.plotly_chart(fig_r, use_container_width=True)

        ind_bar = st.selectbox("Indicateur (barres)", sel_inds, key='bi')
        fig_bar = px.bar(comp[[ind_bar]].reset_index(), x=col_nom, y=ind_bar, color=col_nom,
                         color_discrete_sequence=px.colors.qualitative.Set2, title=ind_bar)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sélectionnez au moins un territoire et un indicateur.")


# ══════════════════════════════════════════════════════════════════════════════
# 🎯 SCORE PERSONNALISÉ
# ══════════════════════════════════════════════════════════════════════════════
with t_score:
    st.subheader("Créez votre propre classement")
    st.write("Ajustez les curseurs selon vos priorités. Le score classe les territoires en fonction de ce qui compte pour vous.")

    groupes_score = {k: v for k, v in G.items() if v and k != "Météo"}
    st.markdown("#### Poids par critère (0 = ignoré, 5 = très important)")
    poids = {}
    wcols = st.columns(len(groupes_score))
    icones = {"Emploi":"💼","Logement":"🏠","Education":"🎓","Services":"🎭","Mobilité":"🚗","Economie":"🏭"}
    for idx, (gnom, _) in enumerate(groupes_score.items()):
        with wcols[idx]:
            poids[gnom] = st.slider(f"{icones.get(gnom,'')} {gnom}", 0, 5, 3, key=f'w_{gnom}')

    score_df = df[[col_nom]].copy().dropna()
    total_w  = 0
    for gnom, gcols in groupes_score.items():
        w = poids[gnom]
        if w == 0: continue
        valid = [c for c in gcols if c in df.columns]
        if not valid: continue
        sub = df[valid].copy()
        for c in valid:
            mn, mx = sub[c].min(), sub[c].max()
            sub[c] = (sub[c]-mn)/(mx-mn)*100 if mx!=mn else 50
            if any(k in c for k in ["chômage","chômeurs","vacant","inactifs","pauvreté"]):
                sub[c] = 100 - sub[c]
        score_df[gnom] = sub.mean(axis=1).values * w
        total_w += w

    if total_w > 0:
        scols = [g for g in groupes_score if poids[g]>0 and g in score_df.columns]
        score_df['Score'] = score_df[scols].sum(axis=1) / total_w
        score_df = score_df.dropna(subset=['Score']).sort_values('Score', ascending=False).reset_index(drop=True)
        score_df.index += 1
        score_df['Score'] = score_df['Score'].round(1)

        c_pod, c_chart = st.columns([1,2])
        with c_pod:
            st.markdown("#### 🥇 Top 15")
            st.dataframe(score_df[[col_nom,'Score']].head(15), use_container_width=True)
        with c_chart:
            fig_sc = px.bar(score_df.head(25), x='Score', y=col_nom, orientation='h',
                            color='Score', color_continuous_scale='Teal', title="Top 25 : Score personnalisé")
            fig_sc.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_sc, use_container_width=True)

        st.divider()
        terr_s = st.selectbox("Chercher un territoire", [":"]+df[col_nom].dropna().sort_values().tolist(), key='ss')
        if terr_s != ":" and terr_s in score_df[col_nom].values:
            rang = score_df[score_df[col_nom]==terr_s].index[0]
            sc   = score_df.loc[rang,'Score']
            st.metric(f"Classement de {terr_s}", f"{rang} / {len(score_df)}", delta=f"Score : {sc}/100")
    else:
        st.warning("Mettez au moins un curseur à 1 pour calculer le score.")


# ══════════════════════════════════════════════════════════════════════════════
# 🔗 CORRÉLATIONS
# ══════════════════════════════════════════════════════════════════════════════
with t_corr:
    st.subheader("Quels indicateurs évoluent ensemble ?")
    st.write("**+1** → ils augmentent ensemble  |  **−1** → ils vont en sens inverse  |  **0** → aucun lien.")

    dom_corr = {
        "Emploi":        G["Emploi"],
        "Logement":      G["Logement"],
        "Education":     G["Education"],
        "Services":      G["Services"],
        "Tous (top 15)": cols_num[:15],
    }
    dom_sel  = st.selectbox("Groupe", list(dom_corr.keys()), key='corr_dom')
    sel_cols = [c for c in dom_corr[dom_sel] if c in df.columns]

    if len(sel_cols) >= 2:
        corr_m = df[sel_cols].dropna().corr().round(2)
        fig_c  = px.imshow(corr_m, text_auto=True, color_continuous_scale='RdBu',
                           zmin=-1, zmax=1, aspect="auto", title="Matrice de corrélation")
        fig_c.update_layout(height=500)
        st.plotly_chart(fig_c, use_container_width=True)

        st.subheader("Top 10 des paires les plus corrélées")
        pairs = [{'Indicateur A': corr_m.columns[i], 'Indicateur B': corr_m.columns[j],
                  'Corrélation': round(corr_m.iloc[i,j],3)}
                 for i in range(len(corr_m.columns)) for j in range(i+1,len(corr_m.columns))]
        pairs_df = pd.DataFrame(pairs).sort_values('Corrélation', key=abs, ascending=False).head(10)
        st.dataframe(pairs_df.reset_index(drop=True), use_container_width=True)
    else:
        st.info("Pas assez d'indicateurs dans ce groupe. Essayez 'Tous (top 15)'.")


# ══════════════════════════════════════════════════════════════════════════════
# 📈 SCATTER
# ══════════════════════════════════════════════════════════════════════════════
with t_scatter:
    st.subheader("Croiser deux indicateurs")
    st.write("Repérez des groupes, des valeurs atypiques ou des tendances en positionnant les territoires sur deux axes.")

    c_x, c_y, c_sz = st.columns(3)
    with c_x:  x_ind = st.selectbox("Axe X", cols_num, index=0, key='sx')
    with c_y:  y_ind = st.selectbox("Axe Y", cols_num, index=min(1,len(cols_num)-1), key='sy')
    with c_sz: sz_ind = st.selectbox("Taille bulles (optionnel)", ["Aucun"]+cols_num, key='ss2')

    sdata = df[[col_nom,x_ind,y_ind]+([sz_ind] if sz_ind!="Aucun" else [])].dropna()
    if len(sdata) > 0:
        kw = dict(data_frame=sdata, x=x_ind, y=y_ind, hover_name=col_nom,
                  color_discrete_sequence=['#4FC3F7'], title=f"{x_ind}  ×  {y_ind}", trendline="ols")
        if sz_ind != "Aucun": kw['size']=sz_ind; kw['size_max']=30
        fig_s = px.scatter(**kw)
        fig_s.update_layout(height=550)
        st.plotly_chart(fig_s, use_container_width=True)

        z_x = stats.zscore(sdata[x_ind].fillna(sdata[x_ind].mean()))
        z_y = stats.zscore(sdata[y_ind].fillna(sdata[y_ind].mean()))
        out = sdata[(abs(z_x)>2)|(abs(z_y)>2)].copy()
        if not out.empty:
            st.subheader(f"⚠️ {len(out)} valeurs atypiques")
            st.dataframe(out[[col_nom,x_ind,y_ind]].reset_index(drop=True), use_container_width=True)
        else:
            st.success("Aucune valeur vraiment atypique sur ces deux indicateurs.")
    else:
        st.warning("Pas assez de données.")


# ══════════════════════════════════════════════════════════════════════════════
# 🔍 TROUVE TA VILLE  (NOUVEAU)
# ══════════════════════════════════════════════════════════════════════════════
with t_filtre:
    st.subheader("🔍 Trouve ta ville idéale")
    st.write(
        "Fixez des seuils minimum et maximum sur les indicateurs qui comptent pour vous. "
        "L'outil vous renvoie la liste des territoires qui correspondent à tous vos critères."
    )

    # Choix des filtres
    filtres_disponibles = {
        "💼 Taux d'emploi":        next((c for c in cols_num if "Taux d'emploi" in c), None),
        "📉 Taux de chômage":      next((c for c in cols_num if "Taux de chômage" in c), None),
        "🏠 Loyer appartement":    next((c for c in cols_num if "Loyer" in c and "appartement" in c), None),
        "🏡 Loyer maison":         next((c for c in cols_num if "Loyer" in c and "maison" in c), None),
        "🌡️ Température":         next((c for c in cols_num if "Température" in c), None),
        "👥 Population":           next((c for c in cols_num if c == "Population"), None),
        "🎓 Diplômés sup.":        next((c for c in cols_num if "diplôme" in c and "supérieur" in c), None),
        "🚇 Transports en commun": next((c for c in cols_num if "transports en commun" in c), None),
    }
    filtres_disponibles = {k: v for k, v in filtres_disponibles.items() if v}

    actifs = st.multiselect("Critères à filtrer", list(filtres_disponibles.keys()),
                            default=list(filtres_disponibles.keys())[:3], key='filtre_choix')

    masque = pd.Series([True]*len(df), index=df.index)
    for label in actifs:
        col_f = filtres_disponibles[label]
        col_min = df[col_f].min()
        col_max = df[col_f].max()
        fmin, fmax = st.slider(
            label, float(col_min), float(col_max),
            (float(col_min), float(col_max)),
            key=f'fslider_{col_f}'
        )
        masque = masque & (df[col_f] >= fmin) & (df[col_f] <= fmax)

    resultats = df[masque][[col_nom] + [filtres_disponibles[l] for l in actifs]].dropna().reset_index(drop=True)
    resultats.index += 1

    st.divider()
    st.markdown(f"### {len(resultats)} territoire(s) correspondent à vos critères")

    if not resultats.empty:
        st.dataframe(resultats, use_container_width=True)

        # Visualiser sur une carte simple
        if len(resultats) <= 100:
            map_data = df[masque][['Latitude','Longitude',col_nom]].dropna().copy()
            map_data['Latitude']  = map_data['Latitude'].astype(float)
            map_data['Longitude'] = map_data['Longitude'].astype(float)
            fig_map = px.scatter_mapbox(
                map_data, lat='Latitude', lon='Longitude', hover_name=col_nom,
                zoom=5, center={"lat":46.6,"lon":2.3},
                mapbox_style="carto-darkmatter",
                color_discrete_sequence=['#4FC3F7'],
                title="Localisation des territoires sélectionnés"
            )
            fig_map.update_traces(marker_size=10)
            fig_map.update_layout(height=500, margin=dict(l=0,r=0,t=30,b=0))
            st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("Aucun territoire ne correspond à tous vos critères. Essayez d'élargir les plages.")


# ══════════════════════════════════════════════════════════════════════════════
# 👥 DÉMOGRAPHIE  (NOUVEAU)
# ══════════════════════════════════════════════════════════════════════════════
with t_demo:
    st.subheader("👥 Analyse démographique")
    st.write("Un regard sur la taille, la répartition et les profils de population des territoires.")

    col_pop = next((c for c in cols_num if c == "Population"), None)
    col_act = next((c for c in cols_num if "Taux d'activité" in c), None)
    col_cho = next((c for c in cols_num if "Taux de chômage" in c), None)
    col_pau = next((c for c in cols_num if "pauvreté" in c), None)
    col_dip = next((c for c in cols_num if "diplôme" in c and "supérieur" in c), None)

    if col_pop:
        st.markdown("### Répartition de la population")
        pop_data = df[[col_nom, col_pop]].dropna().sort_values(col_pop, ascending=False)

        c_treemap, c_hist = st.columns(2)
        with c_treemap:
            fig_t = px.treemap(pop_data.head(40), path=[col_nom], values=col_pop,
                               color=col_pop, color_continuous_scale='Blues',
                               title="Top 40 : Poids démographique")
            fig_t.update_layout(coloraxis_showscale=False, height=400)
            st.plotly_chart(fig_t, use_container_width=True)
        with c_hist:
            fig_h = px.histogram(pop_data, x=col_pop, nbins=40,
                                 color_discrete_sequence=['#4FC3F7'],
                                 title="Distribution des populations")
            fig_h.update_layout(height=400)
            st.plotly_chart(fig_h, use_container_width=True)

    if col_act and col_cho:
        st.markdown("### Emploi & chômage")
        emp_data = df[[col_nom, col_act, col_cho]].dropna()
        fig_emp = px.scatter(emp_data, x=col_act, y=col_cho, hover_name=col_nom,
                             color=col_cho, color_continuous_scale='RdYlGn_r',
                             title=f"Activité vs Chômage : chaque point = un {niveau[:-1].lower()}",
                             trendline="ols")
        fig_emp.update_layout(height=450, coloraxis_showscale=True)
        st.plotly_chart(fig_emp, use_container_width=True)

    if col_dip and col_pau:
        st.markdown("### Niveau de diplôme vs Pauvreté")
        dp_data = df[[col_nom, col_dip, col_pau]].dropna()
        if col_pop and col_pop in dp_data.columns:
            dp_data = dp_data.merge(df[[col_nom, col_pop]], on=col_nom, how='left')
            fig_dp = px.scatter(dp_data, x=col_dip, y=col_pau, hover_name=col_nom,
                                size=col_pop, size_max=40,
                                color=col_pau, color_continuous_scale='RdYlGn_r',
                                title="Plus de diplômés = moins de pauvreté ?", trendline="ols")
        else:
            fig_dp = px.scatter(dp_data, x=col_dip, y=col_pau, hover_name=col_nom,
                                color=col_pau, color_continuous_scale='RdYlGn_r',
                                title="Plus de diplômés = moins de pauvreté ?", trendline="ols")
        fig_dp.update_layout(height=450)
        st.plotly_chart(fig_dp, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# 🌡️ CADRE DE VIE  (NOUVEAU : remplace et enrichit l'ancien onglet Météo)
# ══════════════════════════════════════════════════════════════════════════════
with t_loyer:
    st.subheader("🌡️ Cadre de vie : climat, logement & mobilité")

    # : Météo :
    if G["Météo"]:
        st.markdown("### 🌤️ Classement climatique")
        ind_m = st.selectbox("Indicateur météo", G["Météo"], key='m_ind')
        dm = df[[col_nom, ind_m]].dropna().sort_values(ind_m, ascending=False)
        fig_m = px.bar(dm.head(25), x=col_nom, y=ind_m, color=ind_m,
                       color_continuous_scale='RdYlBu_r', title=f"Top 25 : {ind_m}")
        fig_m.update_layout(coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_m, use_container_width=True)

    # : Logement :
    cols_loyer = [c for c in G["Logement"] if "Loyer" in c]
    if len(cols_loyer) >= 2:
        st.markdown("### 🏠 Loyers : appartement vs maison")
        loyer_data = df[[col_nom]+cols_loyer].dropna().sort_values(cols_loyer[0], ascending=False)
        fig_l = px.scatter(loyer_data, x=cols_loyer[0], y=cols_loyer[1], hover_name=col_nom,
                           color=cols_loyer[0], color_continuous_scale='Oranges',
                           title="Loyer appartement vs maison (€/m²)", trendline="ols")
        fig_l.update_layout(height=450)
        st.plotly_chart(fig_l, use_container_width=True)

        st.markdown("#### Villes les plus chères vs les plus abordables")
        ind_l = st.selectbox("Loyer à classer", cols_loyer, key='loyer_cls')
        ld = df[[col_nom, ind_l]].dropna().sort_values(ind_l, ascending=False)
        cl, cr = st.columns(2)
        with cl:
            fig_exp = px.bar(ld.head(15), x=ind_l, y=col_nom, orientation='h',
                             color=ind_l, color_continuous_scale='Reds', title="🔴 Les plus chères")
            fig_exp.update_layout(yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_exp, use_container_width=True)
        with cr:
            fig_chp = px.bar(ld.tail(15).iloc[::-1], x=ind_l, y=col_nom, orientation='h',
                             color=ind_l, color_continuous_scale='Greens', title="🟢 Les plus abordables")
            fig_chp.update_layout(yaxis={'categoryorder':'total descending'}, coloraxis_showscale=False)
            st.plotly_chart(fig_chp, use_container_width=True)

    # : Mobilité :
    cols_mob = G["Mobilité"]
    if cols_mob:
        st.markdown("### 🚗 Modes de déplacement")
        moy_mob = df[cols_mob].mean().reset_index()
        moy_mob.columns = ['Mode','Part (%)']
        moy_mob['Mode'] = moy_mob['Mode'].str.replace("Part des déplacements en ","").str.replace("Proportion d'actifs occupés résidant à 30 minutes ou plus de leur lieu de travail","Navetteurs +30 min")
        fig_pie = px.pie(moy_mob, names='Mode', values='Part (%)',
                         title="Répartition moyenne nationale des modes de transport",
                         color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig_pie, use_container_width=True)

        terr_mob = st.selectbox("Comparer avec", ["Moyenne nationale"]+sorted(df[col_nom].dropna().tolist()), key='mob_t')
        if terr_mob != "Moyenne nationale":
            row_mob = df[df[col_nom]==terr_mob]
            if not row_mob.empty:
                vals_t = row_mob[cols_mob].values[0]
                vals_n = df[cols_mob].mean().values
                modes  = moy_mob['Mode'].tolist()
                fig_mob = go.Figure()
                fig_mob.add_trace(go.Bar(name=terr_mob, x=modes, y=vals_t, marker_color='#4FC3F7'))
                fig_mob.add_trace(go.Bar(name="Moyenne nationale", x=modes, y=vals_n, marker_color='#0F2044'))
                fig_mob.update_layout(barmode='group', title=f"Déplacements : {terr_mob} vs moyenne nationale",
                                      xaxis_tickangle=-30)
                st.plotly_chart(fig_mob, use_container_width=True)
