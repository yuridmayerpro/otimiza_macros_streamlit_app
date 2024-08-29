import streamlit as st
import gdown
import pandas as pd
import numpy as np
from calcula_macros import calcula_tmb, calcula_metas_macronutrientes1, calcula_metas_macronutrientes2, calcula_metas_macronutrientes3



####################### IMPORTAÇÃO DOS DADOS NECESSÁRIOS #######################
# Function to load DataFrame from Google Drive
@st.cache_data
def load_data_from_drive(url):
    output = 'df_taco.xlsx'
    gdown.download(url, output, quiet=True)
    df = pd.read_excel(output)
    return df

st.title("Calculadora de Macronutrientes")

# URL to the Google Drive file containing the df_taco dataset
drive_url = 'https://docs.google.com/spreadsheets/d/1rhFcWtHXq7e1G6UaoiRid09OeeiuVbW4/edit?usp=drive_link&ouid=114098703207826352607&rtpof=true&sd=true'
#drive_url = st.text_input("URL do arquivo no Google Drive", value=url)

# Extrair o FILE_ID e criar a URL de download
file_id = drive_url.split("/d/")[1].split("/edit")[0]
download_url = f"https://drive.google.com/uc?id={file_id}"

# Carrega a tabela TACO
df_taco = load_data_from_drive(download_url)
#if drive_url:
#    try:
#        # Load data
#        df_taco = load_data_from_drive(download_url)
#        st.success("Tabela carregada com sucesso!")
#    except Exception as e:
#        st.error(f"Erro ao carregar a tabela: {e}")



####################### CÁLCULO DOS MACROS #######################
# Input fields
peso = st.number_input("Peso (kg)", min_value=1, value=80, step=1)
idade = st.number_input("Idade", min_value=0, value=30, step=1)
sexo = st.selectbox("Sexo", options=['m', 'f'])
objetivo = st.selectbox("Objetivo", options=['hipertrofia'])

# Botão para calcular os macronutrientes
if st.button("Calcular Macros"):
    # Calcula os macros
    calorias_alvo1, gramas_proteina1, gramas_carboidrato1, gramas_gordura1 = calcula_metas_macronutrientes1(peso, idade, sexo, objetivo)
    calorias_alvo2, gramas_proteina2, gramas_carboidrato2, gramas_gordura2 = calcula_metas_macronutrientes2(peso, idade, objetivo)
    calorias_alvo3, gramas_proteina3, gramas_carboidrato3, gramas_gordura3 = calcula_metas_macronutrientes3(peso, idade, sexo, objetivo)

    calorias_alvo = int(round(np.average([calorias_alvo1, calorias_alvo2, calorias_alvo3]), 0))
    proteina_alvo = int(round(np.average([gramas_proteina1, gramas_proteina2, gramas_proteina3]), 0))
    carboidrato_alvo = int(round(np.average([gramas_carboidrato1, gramas_carboidrato2, gramas_carboidrato3]), 0))
    
    st.write(f"Calorias alvo: {calorias_alvo} kcal")
    st.write(f"Proteínas alvo: {proteina_alvo} g")
    st.write(f"Carboidratos alvo: {carboidrato_alvo} g")



####################### SELEÇÃO DOS ALIMENTOS PELO USUÁRIO #######################
# Inicializa o dicionário na sessão, se ainda não existir
if 'alimentos' not in st.session_state:
    st.session_state['alimentos'] = {}

# Função para adicionar alimento ao dicionário
def adicionar_alimento():
    alimento = st.session_state.alimento
    limite_inferior = st.session_state.limite_inferior
    limite_superior = st.session_state.limite_superior
    if alimento and limite_inferior is not None and limite_superior is not None:
        st.session_state['alimentos'][alimento] = (limite_inferior, limite_superior)
        st.session_state.alimento = ''
        st.session_state.limite_inferior = 0
        st.session_state.limite_superior = 0
        #st.success(f'Alimento adicionado: {alimento} com limites ({limite_inferior}, {limite_superior})')

# Interface do usuário
st.title('Adicionar Alimentos e Definir Limites')

# Verifique se df_taco tem valores
if not df_taco.empty:
    # Dropdown para selecionar o alimento
    st.selectbox(
        'Selecione o Alimento',
        options=df_taco['Alimento'].tolist(),
        key='alimento'
    )

    # Widgets para limites inferiores e superiores
    st.number_input('Limite Inferior', key='limite_inferior', step=1)
    st.number_input('Limite Superior', key='limite_superior', step=1)

    # Botão para adicionar alimento
    st.button('Adicionar Alimento', on_click=adicionar_alimento)

    # Exibir o dicionário de alimentos e limites
    if st.session_state['alimentos']:
        st.subheader('Alimentos Selecionados:')
        for alimento, limites in st.session_state['alimentos'].items():
            st.write(f'{alimento}: Limite Inferior = {limites[0]}, Limite Superior = {limites[1]}')
else:
    st.error('DataFrame df_taco está vazio. Verifique os dados de entrada.')
