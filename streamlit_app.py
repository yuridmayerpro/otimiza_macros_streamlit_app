import streamlit as st
import gdown
import pandas as pd
import numpy as np
from calcula_macros import calcula_tmb, calcula_metas_macronutrientes1, calcula_metas_macronutrientes2, calcula_metas_macronutrientes3
from otimizador import objective, early_stopping_callback, otimiza
import optuna

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

# Extrair o FILE_ID e criar a URL de download
file_id = drive_url.split("/d/")[1].split("/edit")[0]
download_url = f"https://drive.google.com/uc?id={file_id}"

# Carrega a tabela TACO
df_taco = load_data_from_drive(download_url)

####################### CÁLCULO DOS MACROS #######################
# Inicializa o session_state se não existir
if 'peso' not in st.session_state:
    st.session_state['peso'] = 80
if 'idade' not in st.session_state:
    st.session_state['idade'] = 30
if 'sexo' not in st.session_state:
    st.session_state['sexo'] = 'm'
if 'objetivo' not in st.session_state:
    st.session_state['objetivo'] = 'hipertrofia'

# Input fields
st.session_state['peso'] = st.number_input("Peso (kg)", min_value=1, value=st.session_state['peso'], step=1)
st.session_state['idade'] = st.number_input("Idade", min_value=0, value=st.session_state['idade'], step=1)
st.session_state['sexo'] = st.selectbox("Sexo", options=['m', 'f'], index=['m', 'f'].index(st.session_state['sexo']))
st.session_state['objetivo'] = st.selectbox("Objetivo", options=['hipertrofia'], index=['hipertrofia'].index(st.session_state['objetivo']))

# Botão para calcular os macronutrientes
if st.button("Calcular Macros"):
    # Calcula os macros
    calorias_alvo1, gramas_proteina1, gramas_carboidrato1, gramas_gordura1 = calcula_metas_macronutrientes1(
        st.session_state['peso'], 
        st.session_state['idade'], 
        st.session_state['sexo'], 
        st.session_state['objetivo']
    )
    calorias_alvo2, gramas_proteina2, gramas_carboidrato2, gramas_gordura2 = calcula_metas_macronutrientes2(
        st.session_state['peso'], 
        st.session_state['idade'], 
        st.session_state['objetivo']
    )
    calorias_alvo3, gramas_proteina3, gramas_carboidrato3, gramas_gordura3 = calcula_metas_macronutrientes3(
        st.session_state['peso'], 
        st.session_state['idade'], 
        st.session_state['sexo'], 
        st.session_state['objetivo']
    )
    
    st.session_state['calorias_alvo'] = int(round(np.average([calorias_alvo1, calorias_alvo2, calorias_alvo3]), 0))
    st.session_state['proteina_alvo'] = int(round(np.average([gramas_proteina1, gramas_proteina2, gramas_proteina3]), 0))
    st.session_state['carboidrato_alvo'] = int(round(np.average([gramas_carboidrato1, gramas_carboidrato2, gramas_carboidrato3]), 0))
    
    st.write(f"Calorias alvo: {st.session_state['calorias_alvo']} kcal")
    st.write(f"Proteínas alvo: {st.session_state['proteina_alvo']} g")
    st.write(f"Carboidratos alvo: {st.session_state['carboidrato_alvo']} g")

####################### SELEÇÃO DOS ALIMENTOS PELO USUÁRIO #######################
# Inicializa o dicionário na sessão, se ainda não existir
if 'alimentos' not in st.session_state:
    st.session_state['alimentos'] = {}

# Função para adicionar alimento ao dicionário
def adicionar_alimento():
    alimento = st.session_state['alimento']
    limite_inferior = st.session_state['limite_inferior']
    limite_superior = st.session_state['limite_superior']
    if alimento and limite_inferior is not None and limite_superior is not None:
        st.session_state['alimentos'][alimento] = (limite_inferior, limite_superior)
        # Resetando os campos de entrada após a adição
        st.session_state['alimento'] = df_taco['Alimento'].tolist()[0] if not df_taco['Alimento'].empty else ''
        st.session_state['limite_inferior'] = 0
        st.session_state['limite_superior'] = 0

# Interface do usuário
st.title('Adicionar Alimentos e Definir Limites')

# Dropdown para selecionar o alimento
selected_alimento = st.selectbox(
    'Selecione o Alimento',
    options=df_taco['Alimento'].tolist(),
    key='alimento'
)

# Widgets para limites inferiores e superiores
st.number_input('Limite Inferior', key='limite_inferior', step=1)
st.number_input('Limite Superior', key='limite_superior', step=1)

# Botão para adicionar alimento
st.button('Adicionar Alimento', on_click=adicionar_alimento)

# Exibir o dicionário de alimentos e limites em formato de tabela
if st.session_state['alimentos']:
    st.subheader('Alimentos Selecionados:')
    # Cria um DataFrame para exibir em formato de tabela
    alimentos_df = pd.DataFrame(
        list(st.session_state['alimentos'].items()),
        columns=['Alimento', 'Limites']
    )
    alimentos_df['Limite Inferior (g)'] = alimentos_df['Limites'].apply(lambda x: x[0])
    alimentos_df['Limite Superior (g)'] = alimentos_df['Limites'].apply(lambda x: x[1])
    alimentos_df = alimentos_df.drop(columns=['Limites'])
    
    st.dataframe(alimentos_df, use_container_width=True, hide_index=True)

####################### EXECUTA A OTIMIZAÇÃO #######################
# Função para executar a otimização e exibir os resultados
def run_optimization(calorias_alvo, proteina_alvo, carboidrato_alvo, alimentos, peso, idade, sexo, objetivo, calorias_add, proteina_add, carboidrato_add, n_trials):
    global resultados
    resultados = {}
    resultados['study'], resultados['best_params'], resultados['best_validity'], resultados['calorias_alvo'], \
        resultados['gramas_proteina'], resultados['gramas_carboidrato'], resultados['df_final'] = \
        otimiza(calorias_alvo, proteina_alvo, carboidrato_alvo, alimentos, peso, idade, sexo, objetivo, calorias_add, proteina_add, carboidrato_add, n_trials, df_taco)
        
    # Exibir resultados
    st.subheader('Resultado Final')
    st.dataframe(resultados['df_final'].style.format({'massa': '{:.1f}', 'calorias': '{:.1f}', 'proteinas': '{:.1f}', 'carboidratos': '{:.1f}'}))

    # Verificando os valores finais
    st.subheader('Resumo')
    calorias_totais = resultados['df_final'].calorias.sum()
    proteinas_totais = resultados['df_final'].proteinas.sum()
    carboidratos_totais = resultados['df_final'].carboidratos.sum()

    st.write('Resultado:')
    st.write(f'Calorias: {calorias_totais:.1f}')
    st.write(f'Proteínas: {proteinas_totais:.1f}')
    st.write(f'Carboidratos: {carboidratos_totais:.1f}')

    st.write('\nMetas:')
    st.write(f'Calorias: {resultados["calorias_alvo"]}')
    st.write(f'Proteínas: {resultados["gramas_proteina"]}')
    st.write(f'Carboidratos: {resultados["gramas_carboidrato"]}')

    st.write('\nDesvios:')
    st.write(f'Calorias: {calorias_totais - resultados["calorias_alvo"]:.1f}')
    st.write(f'Proteínas: {proteinas_totais - resultados["gramas_proteina"]:.1f}')
    st.write(f'Carboidratos: {carboidratos_totais - resultados["gramas_carboidrato"]:.1f}')

# Interface do usuário no Streamlit
st.title('Otimização de Nutrição')

# Widgets para entrada de dados do usuário
calorias_add = st.number_input('Calorias Adicionais', value=0)
proteina_add = st.number_input('Proteína Adicional (g)', value=0)
carboidrato_add = st.number_input('Carboidrato Adicional (g)', value=0)
n_trials = st.number_input('Número de Trials', value=100)

if st.button('Executar Otimização'):
    with st.spinner('Executando otimização...'):
        run_optimization(st.session_state['calorias_alvo'],
                         st.session_state['proteina_alvo'],
                         st.session_state['carboidrato_alvo'],
                         st.session_state['alimentos'],
                         st.session_state['peso'], 
                         st.session_state['idade'], 
                         st.session_state['sexo'], 
                         st.session_state['objetivo'], 
                         calorias_add, 
                         proteina_add, 
                         carboidrato_add, 
                         n_trials)
        st.success('Otimização concluída!')
