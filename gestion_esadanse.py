import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from PIL import Image

FILENAME = "inscriptions_esadanse.csv"

COLUMNS = [
    "ID", "Nom", "Prénom", "Date de naissance", "Code postal", "Ville", "Danse", "Email", "Tél", 
    "Nom responsable légal", "Prénom responsable légal", "Email responsable légal", "Tél responsable légal", "Date d'inscription", "Mode de paiement"
]

def init_csv():
    if not os.path.exists(FILENAME):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(FILENAME, index=False)

def load_data():
    df = pd.read_csv(FILENAME)
    df["Date de naissance"] = pd.to_datetime(df["Date de naissance"], errors="coerce")
    df["Date d'inscription"] = pd.to_datetime(df["Date d'inscription"], errors="coerce")
    return df

def save_data(df):
    df["Date de naissance"] = pd.to_datetime(df["Date de naissance"], errors="coerce").dt.date
    df["Date d'inscription"] = pd.to_datetime(df["Date d'inscription"], errors="coerce").dt.date
    df.to_csv(FILENAME, index=False)

def generate_id(df):
    return 1 if df.empty else int(df["ID"].max()) + 1

def reindex_ids(df):
    # Réindexe les IDs de manière séquentielle
    df["ID"] = range(1, len(df) + 1)
    return df

init_csv()
df = load_data()

today = date.today()
min_birth_date = today.replace(year=today.year - 99)
max_birth_date = today.replace(year=today.year - 3)

logo = Image.open("logo_esadanse.jpeg")

col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo, width=120)
with col2:
    st.markdown("<h1 style='margin-top: 15px;'>📋 Gestion des Inscriptions – ESA Danse</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📂 Menu")
    menu = st.radio(
        "",
        [
            "📝 Ajouter une inscription",
            "📄 Afficher les inscriptions",
            "✏️ Modifier une inscription",
            "🗑️ Supprimer une inscription"
        ],
        label_visibility="collapsed",
        index=0
    )

if "Ajouter" in menu:
    st.subheader("📝 Ajouter une nouvelle inscription")

    with st.form("form_add"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        datenaissance = st.date_input("Date de naissance", min_value=min_birth_date, max_value=max_birth_date)
        codepostal = st.text_input("Code postal")
        ville = st.text_input("Ville")
        danse = st.selectbox("Choix de danse", ["Modern'jazz enfant/ado", "Modern'jazz adulte", "Pilates", "Gym douce", "Salsa"])
        email = st.text_input("Email")
        tel = st.text_input("Téléphone")
        nom_rl = st.text_input("Nom responsable légal")
        prenom_rl = st.text_input("Prénom responsable légal")
        email_rl = st.text_input("Email responsable légal")
        tel_rl = st.text_input("Téléphone responsable légal")
        dateinscription = st.date_input("Date d'inscription", max_value=today)
        modepaiement = st.selectbox("Mode de paiement", ["Espèces", "Chèque", "Virement", "Carte bancaire", "Pass Sport", "Chèques vacances", "Autre"])
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            if nom and prenom and email:
                new_id = generate_id(df)
                new_row = pd.DataFrame([[
                    new_id, nom, prenom, datenaissance, codepostal, ville, danse, email, tel,
                    nom_rl, prenom_rl, email_rl, tel_rl, dateinscription, modepaiement
                ]], columns=COLUMNS)
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.success("Inscription ajoutée")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires")

elif "Afficher" in menu:
    st.subheader("📄 Liste des inscriptions")

    danse_filter = st.multiselect("Filtrer par type de danse", options=df["Danse"].dropna().unique(), default=df["Danse"].dropna().unique())
    filtered_df = df[df["Danse"].isin(danse_filter)]

    st.dataframe(filtered_df)

    st.subheader("📊 Statistiques")
    col1, col2 = st.columns(2)
    col1.metric("👥 Total inscrits", len(filtered_df))
    col2.metric("🕺 Cours", filtered_df["Danse"].nunique())

    st.subheader("📈 Répartition par cours")
    st.bar_chart(filtered_df["Danse"].value_counts())

elif "Modifier" in menu:
    st.subheader("✏️ Modifier une inscription existante")

    if not df.empty:
        # Crée une nouvelle colonne avec 'Nom' et 'Prénom' concaténés
        df['Nom et Prénom'] = df["Nom"] + " " + df["Prénom"]
        
        # Affiche le nom et prénom dans le selectbox pour choisir la personne à modifier
        selected_person = st.selectbox("Choisir la personne à modifier", df['Nom et Prénom'])

        # Récupère la ligne correspondante à la personne sélectionnée
        row = df[df["Nom et Prénom"] == selected_person].iloc[0]

        with st.form("form_edit"):
            nom = st.text_input("Nom", value=row["Nom"])
            prenom = st.text_input("Prénom", value=row["Prénom"])
            datenaissance = st.date_input("Date de naissance", value=pd.to_datetime(row["Date de naissance"]), min_value=min_birth_date, max_value=max_birth_date)
            codepostal = st.text_input("Code postal", value=row["Code postal"])
            ville = st.text_input("Ville", value=row["Ville"])
            danse = st.selectbox("Danse", ["Modern'jazz enfant/ado", "Modern'jazz adulte", "Pilates", "Gym douce", "Salsa"], index=["Modern'jazz enfant/ado", "Modern'jazz adulte", "Pilates", "Gym douce", "Salsa"].index(row["Danse"]))
            email = st.text_input("Email", value=row["Email"])
            tel = st.text_input("Téléphone", value=row["Tél"])
            nom_rl = st.text_input("Nom responsable légal", value=row["Nom responsable légal"])
            prenom_rl = st.text_input("Prénom responsable légal", value=row["Prénom responsable légal"])
            email_rl = st.text_input("Email responsable légal", value=row["Email responsable légal"])
            tel_rl = st.text_input("Téléphone responsable légal", value=row["Tél responsable légal"])
            dateinscription = st.date_input("Date d'inscription", value=pd.to_datetime(row["Date d'inscription"]), max_value=today)
            modepaiement = st.selectbox("Mode de paiement", ["Espèces", "Chèque", "Virement", "Carte bancaire", "Pass Sport", "Chèques vacances", "Autre"])
            submitted = st.form_submit_button("Mettre à jour")


            if submitted:
                # Met à jour la ligne avec les nouvelles données sans la colonne 'Cours'
                df.loc[df["Nom et Prénom"] == selected_person, ["Nom", "Prénom", "Date de naissance", "Code postal", "Ville", "Danse", "Email", "Tél", "Nom responsable légal", "Prénom responsable légal", "Email responsable légal", "Tél responsable légal", "Date d'inscription", "Mode de paiement"]] = [
                    nom, prenom, datenaissance, codepostal, ville, danse, email, tel, nom_rl, prenom_rl, email_rl, tel_rl, dateinscription, modepaiement
                ]
                save_data(df)
                st.success("Inscription mise à jour avec succès.")

                
elif "Supprimer" in menu:
    st.subheader("🗑️ Supprimer une inscription")

    if not df.empty:
        # Créer la colonne 'Nom et Prénom' si elle n'existe pas
        df['Nom et Prénom'] = df["Nom"] + " " + df["Prénom"]

        # Sélectionner la personne à supprimer
        selected_person = st.selectbox("Choisir la personne à supprimer", df["Nom et Prénom"])

        # Obtenir la ligne de la personne sélectionnée
        row = df[df["Nom et Prénom"] == selected_person].iloc[0]
        selected_id = row["ID"]

        # Afficher les informations avant confirmation
        st.write("Voulez-vous vraiment supprimer cette inscription ?")
        st.write(row.drop("Nom et Prénom"))  # Affiche les infos sauf la colonne concaténée

        # Bouton de confirmation
        if st.button("Confirmer la suppression"):
            # Supprimer la ligne par ID
            df = df[df["ID"] != selected_id]
            df = reindex_ids(df)
            save_data(df)
            st.success("Inscription supprimée.")
