import streamlit as st
from supabase import create_client

# Configurações de acesso ao Supabase
SUPABASE_URL = "https://oqmvwomjbvfdjgvyleb.supabase.co".strip()
SUPABASE_KEY = "sb_publishable_9WcBzPoBvuy-pjnKL7yMgQ_Cs4kPcNI"

# Inicializa o cliente do Supabase com tratamento de cache
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

st.title("☀️ SolarX - Gestão de Orçamentos")

# Formulário de cadastro de orçamentos
with st.form("form_orcamento", clear_on_submit=True):
    st.subheader("1. Dados do Cliente")
    cliente = st.text_input("Nome do Cliente:")
    localizacao = st.text_input("Localização / Região:")
    tipo_instalacao = st.selectbox("Tipo de Instalação:", ["On-Grid (Rede)", "Off-Grid (Isolado)", "Híbrido"])

    st.subheader("2. Equipamentos e Potência")
    num_paineis = st.number_input("Quantidade de Painéis Solares:", min_value=1, value=6)
    potencia_painel = st.number_input("Potência do Painel (Wp):", min_value=100, value=550, step=5)

    potencia_total_kwp = (num_paineis * potencia_painel) / 1000
    st.markdown(f"### Potência Total Gerada: **{potencia_total_kwp:.2f} kWp**")

    enviar = st.form_submit_button("💾 Salvar Orçamento no Banco")

    if enviar:
        if not cliente.strip():
            st.error("Por favor, preencha o nome do cliente.")
        else:
            try:
                payload = {
                    "cliente": cliente,
                    "localizacao": localizacao,
                    "tipo_instalacao": tipo_instalacao,
                    "num_paineis": int(num_paineis),
                    "potencia_painel": int(potencia_painel),
                    "potencia_total_kwp": float(potencia_total_kwp)
                }
                
                # Executa a inserção no banco de dados
                resposta = supabase.table("orcamentos").insert(payload).execute()
                st.success(f"Orçamento salvo com sucesso para {cliente}!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar no banco de dados: {e}")

# Exibição dos dados salvos na nuvem
st.divider()
st.subheader("📋 Orçamentos Armazenados na Nuvem")

try:
    resultado = supabase.table("orcamentos").select("*").order("created_at", desc=True).execute()
    dados = resultado.data

    if dados and len(dados) > 0:
        st.dataframe(dados, use_container_width=True)
    else:
        st.info("Nenhum orçamento cadastrado ainda no banco de dados.")
except Exception as e:
    st.warning("Aguardando conexão ou dados na tabela.")