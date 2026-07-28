import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Dashboard Concurso Docentes",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Dashboard - Concurso de Docentes")
st.markdown("Consulte, filtre e ordene a lista de candidatos por Grupo de Recrutamento, Graduação e Prioridades.")

# Carregamento dos dados
@st.cache_data
def load_data():
    df = pd.read_excel("Concurso_Docentes.xlsx")
    # Limpeza/conversão de dados se necessário
    if "Graduação" in df.columns:
        df["Graduação"] = pd.to_numeric(df["Graduação"], errors="coerce")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar o ficheiro 'Concurso_Docentes.xlsx': {e}")
    st.stop()

# --- PAINEL LATERAL (FILTROS) ---
st.sidebar.header("🔍 Filtros & Ordenação")

# 1. Grupo de Recrutamento
grupos = sorted(df["Grupo Recrutamento"].dropna().unique())
grupo_selecionado = st.sidebar.selectbox("Selecione o Grupo de Recrutamento:", grupos)

# Filtrar por Grupo
df_filtrado = df[df["Grupo Recrutamento"] == grupo_selecionado]

# 2. Seleção / Exclusão de Prioridades
prioridades_disponiveis = sorted(df_filtrado["Prioridade"].dropna().unique())
prioridades_selecionadas = st.sidebar.multiselect(
    "Prioridades a INCLUIR na lista:",
    options=prioridades_disponiveis,
    default=prioridades_disponiveis,
    help="Desmarque as prioridades que pretende retirar da visualização."
)

df_filtrado = df_filtrado[df_filtrado["Prioridade"].isin(prioridades_selecionadas)]

# 3. Ordenação por Graduação
ordem_graduacao = st.sidebar.radio(
    "Ordenar Graduação:",
    options=["Descendente (Maior para Menor)", "Ascendente (Menor para Maior)"],
    index=0
)

ascending_flag = True if ordem_graduacao.startswith("Ascendente") else False
df_filtrado = df_filtrado.sort_values(by="Graduação", ascending=ascending_flag)

# --- INDICADORES (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Candidatos", len(df_filtrado))
col2.metric("Graduação Máxima", f"{df_filtrado['Graduação'].max():.3f}" if not df_filtrado.empty else "N/A")
col3.metric("Graduação Mínima", f"{df_filtrado['Graduação'].min():.3f}" if not df_filtrado.empty else "N/A")
if "Situação" in df_filtrado.columns:
    colocados = len(df_filtrado[df_filtrado["Situação"] == "Colocado"])
    col4.metric("Colocados", colocados)

st.markdown("---")

# --- TABELA INTERATIVA ---
st.subheader(f"Lista de Candidatos — {grupo_selecionado}")

# Colunas principais a exibir (pode personalizar conforme o necessário)
colunas_exibir = [
    "N.º Ordem", "N.º Utilizador", "Nome do/a Candidato/a", 
    "Prioridade", "Graduação", "Situação", "Novo Provimento / Motivo Exclusão"
]
colunas_presentes = [col for col in colunas_exibir if col in df_filtrado.columns]

st.dataframe(
    df_filtrado[colunas_presentes],
    use_container_width=True,
    height=500
)

# --- BOTÃO DE DOWNLOAD ---
csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Exportar Lista Filtrada (CSV)",
    data=csv_data,
    file_name=f"candidatos_{grupo_selecionado.split('-')[0].strip()}.csv",
    mime="text/csv"
)