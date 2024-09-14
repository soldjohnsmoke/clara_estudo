import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pdfplumber
from io import BytesIO
from streamlit_lottie import st_lottie


st.set_page_config(page_title="Inicio", page_icon="imagens/soccer-ball.png", layout="wide")

st.subheader('Tabela de Estudo do Trimestre', divider='rainbow')

repo_url = "https://api.github.com/repos/soldjohnsmoke/clara_estudo/contents/3_trimestre"


def get_repo_files(repo_url):
    headers = {"Authorization": st.secrets['chave_git']}
    response = requests.get(repo_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve files from GitHub repository")
        return []

files = get_repo_files(repo_url)

if files:
    file_list = [file['name'] for file in files if file['name'].endswith('.pdf')]
    pdf = st.selectbox('Selecione um arquivo', file_list)
else:
    st.write("No files found.")


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


col1, col2 = st.columns([2, 4])

with col1:
    lottie_url = "https://lottie.host/2cba7601-bdad-4004-9c7b-ae5d686942ac/kQgy2JbwnH.json"
    st_lottie(lottie_url, speed=1, reverse=True, loop=True, quality="high", width=400)

with col2:
    # Load the selected PDF file
    if pdf:
        pdf_url = f'https://raw.githubusercontent.com/soldjohnsmoke/clara_estudo/main/3_trimestre/{pdf}'
        response = requests.get(pdf_url)

        if response.status_code == 200:
            pdf_data = BytesIO(response.content)

            with pdfplumber.open(pdf_data) as pdf_reader:
                pagina = pdf_reader.pages[0]  # Assuming we want the first page

                # Extract tables from the PDF
                tabelas = pagina.extract_tables()

                if tabelas:
                    df = pd.DataFrame(tabelas[0])

                    # Find index of row with 'Assunto' and set that as header
                    idx_assunto = df.apply(lambda x: x.str.contains("Assunto", na=False)).any(axis=1)
                    idx_assunto = df.index[idx_assunto].tolist()

                    if idx_assunto:
                        header_idx = idx_assunto[0]
                        df.columns = df.iloc[header_idx]
                        df = df.drop(range(header_idx + 1)).reset_index(drop=True)

                        table = st.data_editor(df, use_container_width=True, hide_index=True)
                    else:
                        st.write("Linha com 'Assunto' não encontrada.")
                else:
                    st.write("Nenhuma tabela encontrada na página.")
        else:
            st.write("Erro ao carregar o PDF.")

palavras_excluir = ["AE", "Revisão", "Retap", "Ret Ap", "REVISÃO", "AE 3", 'Revisão', ]

def deve_excluir(item):
    return any(palavra in item for palavra in palavras_excluir)

# Filtrando o DataFrame
df_filtrado = df[~df['Assunto'].apply(deve_excluir)]
assuntos = df_filtrado['Assunto'].unique()
botoes_assunto = st.columns(len(assuntos))
for i, x in enumerate(botoes_assunto):
    if x.button(assuntos[i], key=f"league_{i}", use_container_width=True):
        st.write(assuntos[i])



