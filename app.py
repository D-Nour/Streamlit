import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# Définissez l'URL de la base de données directement ici
db_url = "sqlite:///pets.db"

# Créez une connexion à la base de données
conn = sqlite3.connect("pets.db", check_same_thread=False)
cursor = conn.cursor()

# Vérifiez si la table existe, sinon, créez-la
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        age INTEGER,
        sex TEXT,
        login_date TEXT
    )
''')
conn.commit()

# Fonction pour obtenir le nombre de connexions pour chaque personne
def get_login_counts():
    cursor.execute('''
        SELECT first_name, last_name, COUNT(*) AS login_count
        FROM users
        GROUP BY first_name, last_name
    ''')
    data = cursor.fetchall()
    return data

# Fonction pour supprimer les données en fonction de l'identifiant
def delete_data_by_id(user_id):
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()

# Fonction pour actualiser la base de données et rafraîchir l'application
def refresh_data():
    st.experimental_rerun()

# Votre application Streamlit
def main():
    st.title("Application Streamlit")

    # Formulaire pour saisir les informations
    st.header("Saisissez vos informations:")
    first_name = st.text_input("Prénom")
    last_name = st.text_input("Nom de famille")
    email = st.text_input("E-mail")
    age = st.number_input("Âge", min_value=0, step=1)
    sex = st.radio("Sexe", ["Masculin", "Féminin"])

    # Bouton pour soumettre le formulaire
    if st.button("Enregistrer"):
        # Ajoutez les informations dans la base de données avec la date actuelle
        login_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, age, sex, login_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, age, sex, login_date))
        conn.commit()

        # Affichez un message de confirmation
        st.success("Informations enregistrées avec succès!")

    # Query and display the data from the database
    cursor.execute('SELECT id, first_name, last_name, email, age, sex, login_date FROM users')
    data = cursor.fetchall()

    if data:
        # Renommer les colonnes
        columns = ["Identifiant", "Prénom", "Nom de famille", "E-mail", "Âge", "Sexe", "Date de connexion"]
        data_df = pd.DataFrame(data, columns=columns)

        # Obtenir le nombre de connexions pour chaque personne
        login_counts = get_login_counts()
        login_counts_df = pd.DataFrame(login_counts, columns=["Prénom", "Nom de famille", "Nombre de connexions"])

        # Fusionner les DataFrames sur les colonnes "Prénom" et "Nom de famille"
        merged_df = pd.merge(data_df, login_counts_df, on=["Prénom", "Nom de famille"], how="left")

        st.header("Données enregistrées:")
        st.dataframe(merged_df)

        # Section pour supprimer les données par identifiant
        st.header("Supprimer des données par identifiant")
        delete_id = st.text_input("Entrez l'identifiant à supprimer:")
        if st.button("Supprimer"):
            try:
                delete_id = int(delete_id)
                delete_data_by_id(delete_id)
                st.success(f"Données avec l'identifiant {delete_id} supprimées avec succès!")
            except ValueError:
                st.error("Veuillez entrer un identifiant numérique valide.")

        # Bouton pour actualiser la base de données
        if st.button("Actualiser la base"):
            refresh_data()

    else:
        st.warning("Aucune donnée enregistrée pour le moment.")

# Exécutez l'application
if __name__ == "__main__":
    main()
