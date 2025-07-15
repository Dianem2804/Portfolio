import streamlit as st

# Titre de l'application
st.title("Bienvenue sur mon app Streamlit")

# Entrée utilisateur pour le nom
nom = st.text_input("Quel est votre nom ?")

# Entrée utilisateur pour l'âge
age = st.number_input("Quel est votre âge ?", min_value=0, max_value=120, step=1)

# Bouton pour valider
if st.button("Valider"):
    if nom:
        st.success(f"Bonjour {nom} ! Vous avez {age} ans.")
    else:
        st.warning("Veuillez entrer votre nom.")
