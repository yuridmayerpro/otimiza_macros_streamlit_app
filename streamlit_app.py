import streamlit as st
import gdown
import pandas as pd

# Function to load DataFrame from Google Drive
@st.cache_data
def load_data_from_drive(url):
    output = 'df_taco.xlsx'
    gdown.download(url, output, quiet=False)
    df = pd.read_excel(output)
    return df

st.title("Calculadora de Macronutrientes")

# URL to the Google Drive file containing the df_taco dataset
drive_url = st.text_input("URL do arquivo no Google Drive")

if drive_url:
    df_taco = load_data_from_drive(drive_url)
    st.write("Exemplo de dados carregados:")
    #st.write(df_taco.head())
    st.dataframe(df_taco)
