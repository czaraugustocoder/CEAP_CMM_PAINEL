import streamlit as st
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from PIL import Image
from io import BytesIO
import base64
from streamlit_gsheets import GSheetsConnection

current_working_directory = os.getcwd()

dados = os.path.join(current_working_directory, "CEAP_CMM_2024.xlsx")

path_logo = os.path.join(current_working_directory, "logo.png")

import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="TRANSPARÊNCIA - CMM",
                   layout="wide"
)

dados_dash = pd.read_excel(dados)

dados_dash['IMG_PATH'] = dados_dash['IMG'].apply(lambda x: os.path.join(current_working_directory, x))

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #F5F5F4;
#   }
</style>
""", unsafe_allow_html=True)

st.title("TRANSPARÊNCIA EM DASHBOARDS - CÂMARA MUNICIPAL DE MANAUS")

st.markdown(
    """
    <style>
    /* Muda a cor de fundo da sidebar */
    [data-testid="stSidebar"] {
        background-color: #ebebeb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.image(path_logo)

mes = st.sidebar.multiselect(
    "Selecione o Mês",
    options= dados_dash["MES_DESPESA"].unique()
)

if ((len(mes) != 0)):
    print(mes)
    dados_dash = dados_dash.query(
        "MES_DESPESA == @mes")
    
import locale

#função de conversão de float em moeda brasileira
def format_pt_br(value):
    # Converte o float para uma string formatada com duas casas decimais
    formatted_value = f"{value:,.2f}"
    
    # Troca o separador decimal de ponto para vírgula e o separador de milhar de vírgula para ponto
    formatted_value = formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")
    
    return formatted_value
    
tg_ceap = dados_dash['VALOR'].sum()
cota_mensal = 33085.85

# Formatar o valor como moeda brasileira
tg_ceap_br = format_pt_br(tg_ceap)
cota_mensal_br = format_pt_br(cota_mensal)

qt_ver = len(dados_dash['VEREADOR'].unique().tolist())

st.markdown("<hr>", unsafe_allow_html=True)
a1, a2, a3 = st.columns(3)
a1.metric(label="VALOR GASTO - CEAP (2024)",value=f"{tg_ceap_br}")
a2.metric(label="VALOR ATUAL DA COTA MENSAL (2024)", value=f"{cota_mensal_br}") 
a3.metric(label="QTD DE VEREADORES", value=f"{qt_ver}") 
st.markdown("<hr>", unsafe_allow_html=True)

dados_dash_donut = dados_dash.groupby(['VEREADOR', 'MES_DESPESA'])['VALOR'].sum().reset_index()
dados_dash_resumo = dados_dash.groupby(['VEREADOR', 'IMG_PATH'])['VALOR'].sum().reset_index()

# Criando o Treemap
fig_despesa = px.treemap(dados_dash, 
                 path=['ITEM_DESPESA'], 
                 values='VALOR',
                 title="GASTOS DA CEAP POR ITEM DE DESPESA (2024)")

# Dados de exemplo
labels = ['TOTAL GASTO', 'TOTAL ECONOMIZADO']
values = [tg_ceap, (len(dados_dash_donut) * cota_mensal)]

# Criando o gráfico de donut
fig_total = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4, marker=dict(colors=['#FF0000', '#0000e0']))])

# Personalizando o layout
fig_total.update_layout(
    title_text="TOTAL GASTO E ECONOMIZADO - CEAP (2024)",
    showlegend=False
)

col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig_total)
with col2:
    st.plotly_chart(fig_despesa)

# Função para converter imagem para HTML
def image_to_html(path, width=100):
    image = Image.open(path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    html_img = f'<img src="data:image/PNG;base64,{img_str}" width="{width}"/>'
    return html_img

dados_dash_resumo = dados_dash_resumo.sort_values(by='VALOR', ascending=False)

dados_dash_resumo = dados_dash_resumo.reset_index(drop=True)
dados_dash_resumo.index = dados_dash_resumo.index + 1

dados_dash_resumo['FOTO'] = dados_dash_resumo['IMG_PATH'].apply(lambda x: image_to_html(x))

dados_dash_resumo['VALOR TOTAL GASTO'] = dados_dash_resumo['VALOR'].apply(lambda x: format_pt_br(x))

dados_dash_resumo = dados_dash_resumo[['FOTO','VEREADOR',"VALOR TOTAL GASTO"]]

st.markdown("<hr>", unsafe_allow_html=True)

st.write("**RANKING DE GASTOS COM A CEAP - 2024**")

# Centralizar a tabela com CSS
st.markdown(
    """
    <style>
    .center-table {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Envolva a tabela em um div com a classe "center-table"
st.markdown(
    f"""
    <div class="center-table">
        {dados_dash_resumo.to_html(escape=False)}
    </div>
    """,
    unsafe_allow_html=True
)