import os
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import streamlit as st
import pandas as pd
from supabase import create_client
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# Configuração da Página no Streamlit (Com Ícone Personalizado)
st.set_page_config(
    page_title="SolarX - Gestão de Orçamentos", 
    layout="wide", 
    page_icon="icon_png.png" if os.path.exists("icon_png.png") else "☀️"
)

# SOLARX ENERGY — Identidade premium (CSS de apresentação; sem alterar lógica)
st.markdown("""
<style>
:root{--energy-a:#ff852e;--energy-b:#ff276f;--sx-bg:#090d18;--sx-panel:#151a2b;--sx-edge:rgba(218,226,255,.12);}
html,body,[data-testid="stAppViewContainer"],.stApp{background:#090d18!important;color:#f7f7fb!important;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse 70% 50% at 90% -12%,rgba(255,69,110,.12),transparent 75%),radial-gradient(ellipse 48% 50% at -10% 100%,rgba(255,120,34,.07),transparent 70%),#090d18!important;}
[data-testid="stHeader"]{background:transparent!important;}
.block-container{max-width:1460px;padding-top:1.6rem;padding-bottom:3rem;}
[data-testid="stSidebar"]{background:linear-gradient(160deg,rgba(24,28,46,.98),rgba(11,14,26,.99))!important;border-right:1px solid var(--sx-edge)!important;}
[data-testid="stSidebar"] [data-testid="stImage"]{padding:.8rem 0 1rem;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.45rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{border:1px solid transparent;border-radius:12px;padding:9px 12px;background:transparent;transition:background .15s ease;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.06);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(100deg,#ff852e,#ff276f)!important;box-shadow:0 5px 18px rgba(255,48,107,.16);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{color:white!important;font-weight:650;}
[data-testid="stSidebar"] [role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:.93rem;}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"],div.stDownloadButton>button[kind="primary"]{background:linear-gradient(95deg,#ff862e,#ff276f)!important;border:0!important;color:#fff!important;font-weight:680!important;box-shadow:0 7px 22px rgba(255,42,102,.17)!important;}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:12px!important;min-height:42px;transition:transform .12s ease,box-shadow .12s ease;background:rgba(255,255,255,.045);border:1px solid var(--sx-edge);color:#f8f8fd;}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-1px);border-color:rgba(255,117,82,.43)!important;color:white!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div{background:rgba(26,31,49,.62)!important;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid var(--sx-edge)!important;border-radius:18px!important;}
[data-testid="stExpander"]{border:1px solid var(--sx-edge)!important;background:rgba(21,26,43,.72)!important;border-radius:15px!important;overflow:hidden;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--sx-edge)!important;border-radius:14px!important;overflow:hidden;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div{background:rgba(20,25,42,.87)!important;color:#f8f9ff!important;border-color:rgba(220,229,255,.13)!important;border-radius:11px!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus{border-color:#ff5680!important;}
[data-testid="stMetric"]{background:rgba(22,27,45,.76);padding:16px;border:1px solid var(--sx-edge);border-radius:16px;}
[data-testid="stMetricValue"]{color:white!important;}
[data-testid="stAlert"]{border-radius:13px!important;}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{line-height:1.55;}
h1,h2,h3{letter-spacing:-.027em!important;color:white!important;}
h1{font-size:2rem!important;}h2{font-size:1.42rem!important;}h3{font-size:1.14rem!important;}
hr{border-color:rgba(235,240,255,.09)!important;}
.sx-eyebrow{font-size:.71rem;text-transform:uppercase;letter-spacing:.16em;font-weight:700;color:#b4b8c8;margin-bottom:.28rem;}
.sx-heading{font-size:1.9rem;font-weight:750;letter-spacing:-.03em;color:#fff;margin:0 0 .25rem;}
.sx-subtitle{color:#a9afc2;font-size:.91rem;margin-bottom:1.6rem;}
.sx-topline{background:linear-gradient(90deg,#ff276f 0%,#ff7047 62%,#ffa820 100%);height:3px;border-radius:999px;margin-bottom:1.45rem;}
.sx-kpi{position:relative;min-height:149px;background:linear-gradient(145deg,rgba(31,38,60,.84),rgba(18,23,38,.87));border:1px solid rgba(215,226,255,.11);border-radius:18px;padding:18px 18px 14px;backdrop-filter:blur(16px);overflow:hidden;}
.sx-kpi::after{content:"";position:absolute;width:115px;height:115px;background:radial-gradient(circle,rgba(255,116,66,.055),transparent 70%);right:-25px;top:-30px;pointer-events:none;}
.sx-kpi-head{display:flex;justify-content:space-between;align-items:center;gap:.5rem;margin-bottom:20px;}
.sx-kpi-name{color:#c9cddb;font-size:.82rem;font-weight:600;}
.sx-kpi-icon{width:22px;height:22px;stroke:#e7e9f4;stroke-width:1.8;fill:none;stroke-linecap:round;stroke-linejoin:round;}
.sx-kpi-value{font-size:1.55rem;color:#fff;letter-spacing:-.03em;font-weight:740;white-space:nowrap;}
.sx-kpi-sub{font-size:.72rem;color:#8b94a8;margin-top:8px;}
.sx-tag{padding:4px 9px;border-radius:100px;font-size:.68rem;font-weight:650;background:rgba(61,204,138,.10);color:#4ddfa6;}
.sx-tag.warn{background:rgba(255,172,40,.12);color:#ffbd62;}.sx-tag.bad{background:rgba(249,66,100,.14);color:#ff758a;}
.sx-glow{color:#fff;background:linear-gradient(90deg,#ffac36,#ff477f);background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.sx-section{color:#f4f5fa;font-weight:680;font-size:1.05rem;margin:1.2rem 0 .9rem;letter-spacing:-.01em;}
.sx-mini-note{font-size:.78rem;color:#a8b0c1;}
@media(max-width:768px){.block-container{padding:1rem .75rem 3rem;}.sx-heading{font-size:1.5rem;}.sx-kpi{min-height:128px;padding:13px 12px;}.sx-kpi-value{font-size:1.18rem;}.sx-kpi-name{font-size:.73rem;}.sx-kpi-head{margin-bottom:12px;}[data-testid="stSidebar"]{width:250px!important;}}
[data-testid="stSidebar"] [role="radiogroup"] label{display:flex!important;align-items:center!important;gap:.55rem!important;}
[data-testid="stSidebar"] [role="radiogroup"] label::before{content:"";flex:0 0 19px;width:19px;height:19px;background-size:contain;background-position:center;background-repeat:no-repeat;opacity:.97;}

[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(1)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Im0zIDEwIDktNyA5IDd2MTBhMSAxIDAgMCAxLTEgMWgtNXYtN0g5djdINGExIDEgMCAwIDEtMS0xeiIvPjwvc3ZnPg==")}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(2)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik03IDJoOWw1IDV2MTRIN3oiLz48cGF0aCBkPSJNMTYgMnY2aDVNMTAgMTJoOE0xMCAxNmg4Ii8+PC9zdmc+")}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(3)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0xNiAyMXYtMmE0IDQgMCAwIDAtNC00SDZhNCA0IDAgMCAwLTQgNHYyIi8+PGNpcmNsZSBjeD0iOSIgY3k9IjciIHI9IjQiLz48cGF0aCBkPSJNMjIgMjF2LTJhNCA0IDAgMCAwLTMtMy44N00xNiAzLjEzYTQgNCAwIDAgMSAwIDcuNzUiLz48L3N2Zz4=")}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(4)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxyZWN0IHg9IjMiIHk9IjciIHdpZHRoPSIxOCIgaGVpZ2h0PSIxNCIgcng9IjIiLz48cGF0aCBkPSJtMyA3IDktNSA5IDVNMTIgMTJ2OSIvPjwvc3ZnPg==")}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(5)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxjaXJjbGUgY3g9IjEyIiBjeT0iNyIgcj0iNCIvPjxwYXRoIGQ9Ik01IDIxdi0zYTcgNyAwIDAgMSAxNCAwdjMiLz48L3N2Zz4=")}
[data-testid="stSidebar"] [role="radiogroup"] label:nth-of-type(6)::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43IiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIGQ9Ik0yMCAxNi42QTQuNyA0LjcgMCAwIDAgMTcgOGE2LjggNi44IDAgMCAwLTEzIDJBNC41IDQuNSAwIDAgMCA1IDE5aDEzYTMuNSAzLjUgMCAwIDAgMi0yLjR6Ii8+PC9zdmc+")}
</style>
""", unsafe_allow_html=True)

# CONEXÃO COM O SUPABASE
SUPABASE_URL = "https://oqmvvomjbvfdjjgvyleb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9xbXZ2b21qYnZmZGpqZ3Z5bGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk2NDE4OTgsImV4cCI6MjEwNTIxNzg5OH0.vlxe1shu0zgM0tXAnKS0aynIuoQsjXX32Ny_lbLBicc"
# Em produção, configure SUPABASE_SERVICE_ROLE_KEY nos Secrets do Streamlit.
# Nunca publique a chave de serviço: é usada apenas para a tabela de pagamentos.
# A ligação legada anon para as demais tabelas é mantida para compatibilidade.
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", SUPABASE_URL))
SERVER_KEY = st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", SUPABASE_KEY))
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Separar privilégios: a chave de serviço é usada APENAS para pagamentos.
payments_db = create_client(SUPABASE_URL, SERVER_KEY) if SERVER_KEY else supabase

# CONSTANTES DE NEGÓCIO
IVA = Decimal("0.23")
MARGEM_EQUIP = Decimal("0.15")
MARGEM_INSTALACAO = Decimal("0.20")
START_PROPOSAL = 145
START_CLIENT = 16

# --- SISTEMA DE SENHA DE ACESSO COM BOTÃO ENTER ---
def check_password():
    def password_entered():
        entered_pwd = st.session_state.get("password_input", "")
        if entered_pwd == st.secrets.get("app_password", "solarx123"):
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        st.subheader("🔒 Acesso Restrito - SolarX")
        with st.form("login_form"):
            col_pwd, col_btn = st.columns([3, 1])
            with col_pwd:
                st.text_input("Introduza a senha de acesso:", type="password", key="password_input", label_visibility="collapsed", placeholder="Introduza a senha...")
            with col_btn:
                submitted = st.form_submit_button("Enter")
            
            if submitted:
                password_entered()

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Senha incorreta. Tente novamente.")
        return False
    return True

if not check_password():
    st.stop()

# FUNÇÕES AUXILIARES DE CÁLCULO
def money(v):
    d = Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def sale_price(cost, margin=MARGEM_EQUIP):
    cost_dec = Decimal(str(cost or 0))
    return (cost_dec * (Decimal("1") + margin)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# ESTADOS COMERCIAIS E REGRAS FINANCEIRAS
STATUS_LABELS = {
    "em_analise": "Em análise", "aprovado": "Aprovado",
    "rejeitado": "Rejeitado", "instalado": "Instalado",
}
PAYMENT_LABELS = {"transferencia": "Transferência", "numerario": "Numerário", "outro": "Outro"}


def D(value):
    try:
        return Decimal(str(value if value is not None else "0"))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def cents(value):
    return D(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def money_eur(value):
    return money(value) + " €"


def dttm(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def report_month(date_value):
    parsed = dttm(date_value)
    return parsed.strftime("%Y-%m") if parsed else None


def month_range(months_back=6):
    now = datetime.now()
    idx = now.year * 12 + now.month - 1
    months = []
    for step in range(months_back - 1, -1, -1):
        n = idx - step
        months.append(f"{n // 12:04d}-{n % 12 + 1:02d}")
    return months


def fetch_all(table, columns="*", order_col="id", descending=False, client=None):
    """Paginação: evita truncamento implícito de 1.000 linhas no Supabase."""
    found, start, page_size = [], 0, 500
    api = client or supabase
    while True:
        query = api.table(table).select(columns)
        if order_col:
            query = query.order(order_col, desc=descending)
        data = query.range(start, start + page_size - 1).execute().data or []
        found.extend(data)
        if len(data) < page_size:
            return found
        start += page_size


def checked_solar_flag(row):
    val=row.get("is_solar_panel")
    return val is True or str(val).strip().lower() in ("true", "1", "sim")


def checked_panel_wp(row):
    if not checked_solar_flag(row):
        return None
    val=row.get("panel_wp")
    if val is None or str(val).strip().lower() in ("", "nan", "none"):
        return 600.0
    power=float(val)
    if power <= 0:
        raise ValueError("A potência do painel deve ser superior a zero")
    return power


def quote_totals(quote, items):
    """Equipamentos com IVA normal; instalação com taxa documentada."""
    gross_equipment = sum((cents(x.get("line_total")) for x in items), Decimal("0"))
    discount = cents(quote.get("discount"))
    equip_net = max(Decimal("0"), gross_equipment - discount)
    equip_iva = cents(equip_net * IVA)
    if quote.get("finance_version") == "legacy" and quote.get("installation_sale") is None:
        # Compatibilidade se uma versão antiga ainda gravar durante a migração.
        install_net = cents(D(quote.get("installation_cost")) * Decimal("1.20"))
    else:
        install_net = cents(quote.get("installation_sale"))
    tax_rate = D(quote.get("installation_iva_rate", "0.23"))
    install_iva = cents(install_net * tax_rate)
    net = equip_net + install_net
    total = net + equip_iva + install_iva
    if quote.get("finance_version") == "legacy":
        # Modelo anterior: desconto sobre o total global e IVA calculado uma
        # única vez sobre equipamentos + instalação (custo com acréscimo 20%).
        # Respeita orçamentos já emitidos, inclusive descontos elevados.
        net = max(Decimal("0"), gross_equipment + install_net - discount)
        full_tax = cents(net * IVA)
        total = net + full_tax
        install_iva = full_tax - equip_iva
    known_cost = bool(items) and all(it.get("cost_unit") is not None for it in items)
    direct_cost = sum((D(it.get("cost_unit")) * D(it.get("qty")) for it in items), Decimal("0"))
    direct_cost += cents(quote.get("installation_cost")) + cents(quote.get("extra_cost"))
    return {
        "equipment_net": equip_net, "equipment_iva": equip_iva,
        "install_net": install_net, "install_iva": install_iva,
        "net": net, "iva": (cents(net * IVA) if quote.get("finance_version") == "legacy" else equip_iva + install_iva), "total": total,
        "cost_known": known_cost, "cost": cents(direct_cost),
        "profit": cents(net - direct_cost) if known_cost else None,
        "kwp": sum((D(it.get("panel_wp")) * D(it.get("qty")) for it in items), Decimal("0")) / 1000,
    }


def get_all_items():
    return fetch_all("quote_items", "id,quote_id,qty,ref,description,unit,unit_price,line_total,cost_unit,panel_wp")


def quote_payments():
    try:
        return fetch_all("quote_payments", "id,quote_id,amount,received_at,method,note", "id", client=payments_db)
    except Exception:
        return None


def require_financial_schema():
    """Impede gravar orçamentos incompletos caso ainda falte executar o SQL."""
    try:
        supabase.table("quotes").select(
            "id,status,approved_at,installed_at,invoiced_at,invoice_number,"
            "installation_sale,installation_iva_rate,installation_tax_basis,extra_cost,finance_version"
        ).limit(1).execute()
        supabase.table("quote_items").select("id,cost_unit,panel_wp").limit(1).execute()
        supabase.table("products").select("id,is_solar_panel,panel_wp").limit(1).execute()
        supabase.table("clients").select("id,created_at").limit(1).execute()
        return True
    except Exception as exc:
        st.error("Atualização da base de dados pendente. Execute primeiro o SQL de migração SOLARX_PREMIUM_MIGRACAO.sql no Supabase, e só depois atualize o app.py. Detalhe: " + str(exc))
        return False

# DADOS SUPABASE
def get_clients():
    try:
        return fetch_all("clients", "*", "number")
    except Exception:
        return []

def get_products():
    try:
        return fetch_all("products", "*", "description")
    except Exception:
        return []

def get_users():
    """Obtém os utilizadores exclusivamente do Supabase.

    Não usa ficheiros locais como fonte de verdade: em alojamentos Streamlit
    o disco local pode ser temporário e perder os dados após reinícios/deploys.
    """
    try:
        res = supabase.table("users").select("id, name").order("id").execute()
        return res.data or []
    except Exception as exc:
        raise RuntimeError(
            "Não foi possível consultar a tabela 'public.users' no Supabase. "
            "Confirme se a tabela existe e se a política RLS permite SELECT. "
            f"Detalhe técnico: {exc}"
        ) from exc


def editor_rows(data):
    """Normaliza o retorno do st.data_editor para uma lista de dicionários."""
    if data is None:
        return []
    if hasattr(data, "to_dict"):
        try:
            return data.to_dict(orient="records")
        except TypeError:
            pass
    if isinstance(data, dict):
        return [data]
    return list(data)


def row_id(row):
    """Retorna um ID válido, ignorando valores vazios/NaN do editor."""
    value = row.get("id")
    if value is None:
        return None
    try:
        if value != value:  # NaN é o único valor que não é igual a si próprio.
            return None
    except Exception:
        pass
    if isinstance(value, str) and not value.strip():
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return value

def get_next_proposal():
    try:
        res = supabase.table("quotes").select("proposal").order("proposal", desc=True).limit(1).execute()
        if res.data and res.data[0]["proposal"]:
            return max(START_PROPOSAL, int(res.data[0]["proposal"]) + 1)
    except Exception:
        pass
    return START_PROPOSAL

def get_next_client_number():
    try:
        res = supabase.table("clients").select("number").order("number", desc=True).limit(1).execute()
        if res.data and res.data[0]["number"]:
            return max(START_CLIENT, int(res.data[0]["number"]) + 1)
    except Exception:
        pass
    return START_CLIENT

# CALLBACK PARA ATUALIZAR PREÇO UNITÁRIO
def update_product_row(row_idx, product_dict):
    selected_key = st.session_state.get(f"prod_{row_idx}")
    prod = product_dict.get(selected_key)
    if prod:
        cost = Decimal(str(prod.get("cost", 0)))
        margin = Decimal(str(prod.get("margin", 0.15)))
        price_sale = (cost * (Decimal("1") + margin)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        st.session_state[f"price_{row_idx}"] = float(price_sale)
        if st.session_state.get(f"qty_{row_idx}", 0.0) == 0.0:
            st.session_state[f"qty_{row_idx}"] = 1.0
    else:
        st.session_state[f"price_{row_idx}"] = 0.0
        st.session_state[f"qty_{row_idx}"] = 0.0

# GERAÇÃO DE PDF DE ORÇAMENTO
PDF_POS = {
    "proposal": (502.5, 802.0),
    "issue_date": (502.5, 791.6),
    "prepared_by": (122.4, 642.0),
    "client_name": (362.5, 722.0),
    "address1": (322.5, 692.0),
    "postal": (362.5, 672.0),
    "nif": (362.5, 642.0),
    "phone": (482.2, 632.0),
    "email": (342.5, 622.0),
    "client_no": (342.5, 632.0),
    "table_ref_x": 44.0,
    "table_desc_x": 93.0,
    "table_qty_right": 355.5,
    "table_unit_x": 363.5,
    "table_price_right": 457.5,
    "table_total_right": 573.5,
    "table_y": 472.0,
    "table_step": 10.02,
    "notes": (102.5, 231.7),
    "tot_equip_right": (176.0, 152.0),
    "tot_discount_right": (176.0, 142.0),
    "tot_iva_right": (176.0, 132.0),
    "tot_left_final_right": (197.0, 112.0),
    "tot_right_final_right": (557.0, 112.0)
}

def draw_text(c, x, y, text, size=8, bold=False, color=(0, 0, 0)):
    c.setFillColorRGB(*color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, str(text))

def generate_pdf_buffer(client, items, discount, installation_price, notes, proposal, prepared_by, installation_iva_rate=IVA):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_img = os.path.join(base_dir, "BASE_Orçamento_SOLARX_00_A.jpg")

    if os.path.exists(base_img):
        c.drawImage(ImageReader(base_img), 0, 0, width=w, height=h, preserveAspectRatio=False, mask="auto")

    date_str = datetime.now().strftime("%d-%m-%Y")
    draw_text(c, *PDF_POS["proposal"], str(proposal), 9, True, (1, 1, 1))
    draw_text(c, *PDF_POS["issue_date"], date_str, 8, True, (1, 1, 1))
    draw_text(c, *PDF_POS["prepared_by"], str(prepared_by), 8, False)

    draw_text(c, *PDF_POS["client_name"], client["name"][:38], 8, True)
    address = (client.get("address") or "").replace("\n", " | ")
    parts = [p.strip() for p in address.split("|") if p.strip()]
    if parts:
        draw_text(c, *PDF_POS["address1"], parts[0][:38], 8)
    if client.get("postal"):
        draw_text(c, *PDF_POS["postal"], client["postal"][:16], 8)

    draw_text(c, *PDF_POS["nif"], (client.get("nif") or "")[:18], 8)
    draw_text(c, *PDF_POS["client_no"], f"{int(client.get('number', 0)):04d}", 8, True)
    draw_text(c, *PDF_POS["phone"], (client.get("phone") or "")[:18], 8, True)
    draw_text(c, *PDF_POS["email"], (client.get("email") or "")[:42], 8)

    for i, it in enumerate(items[:14]):
        y = PDF_POS["table_y"] - i * PDF_POS["table_step"]
        draw_text(c, PDF_POS["table_ref_x"], y, str(it.get("ref", ""))[:8], 8)
        draw_text(c, PDF_POS["table_desc_x"], y, str(it["description"])[:48], 8)
        c.setFont("Helvetica", 8)
        c.drawRightString(PDF_POS["table_qty_right"], y, f"{it['qty']:g}")
        c.drawString(PDF_POS["table_unit_x"], y, str(it.get("unit", "UN"))[:5])
        c.drawRightString(PDF_POS["table_price_right"], y, money(it["unit_price"]))
        c.drawRightString(PDF_POS["table_total_right"], y, money(it["line_total"]))

    if notes.strip():
        draw_text(c, *PDF_POS["notes"], notes[:95], 8)

    subtotal_items = sum((it["line_total"] for it in items), Decimal("0"))
    taxable_equip = max(Decimal("0"), subtotal_items - discount)
    iva_equip = (taxable_equip * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_equip = taxable_equip + iva_equip

    # Preço de instalação é MANUAL e não recebe margem automática.
    # Forma de pagamento não altera a taxa de IVA.
    inst_sale = cents(installation_price)
    iva_install = cents(inst_sale * D(installation_iva_rate))
    total_global = total_equip + inst_sale + iva_install

    c.setFont("Helvetica", 8.5)
    c.drawRightString(*PDF_POS["tot_equip_right"], money(subtotal_items))
    c.drawRightString(*PDF_POS["tot_discount_right"], money(discount))
    c.drawRightString(*PDF_POS["tot_iva_right"], money(iva_equip))

    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(*PDF_POS["tot_left_final_right"], money(total_equip))

    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(*PDF_POS["tot_right_final_right"], money(total_global))

    c.save()
    buffer.seek(0)
    return buffer

# --- GERAÇÃO DE PDF DE REQUISIÇÃO DE MATERIAL ---
def generate_requisition_pdf_buffer(quote, items, prepared_by_name):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_img = os.path.join(base_dir, "BASE_Requisicao_SOLARX.jpg")

    if os.path.exists(base_img):
        c.drawImage(
            ImageReader(base_img), 0, 0,
            width=w, height=h,
            preserveAspectRatio=False,
            mask="auto"
        )

    # As coordenadas abaixo foram medidas nos retângulos vermelhos da
    # GRELHA_CALIBRACAO_03_REQUISICAO.pdf.
    # A origem do ReportLab fica no canto inferior esquerdo.
    # O deslocamento de 2 pt coloca a linha de base dentro de cada caixa.
    req_pos = {
        "prepared_by": (142.0, h - 192.1300 + 2.0, 76.0),
        "email_contact": (142.0, h - 211.8960 + 2.0, 136.0),
        "request_date": (421.9670, h - 151.5630 + 2.0, 76.0),
        "proposal": (421.9670, h - 192.1300 + 2.0, 76.0),
        "description_x": 62.0,
        "description_width": 336.0,
        "quantity_right": 456.3440,
        "unit_x": 464.2620,
        "unit_width": 71.9,
    }

    # Cada linha tem a sua coordenada Y individual, medida no retângulo
    # correspondente. Não usar um passo fixo: a grelha tem pequenas
    # diferenças verticais entre algumas linhas.
    row_bottoms_top = [
        321.2500, 351.6610, 381.5590, 411.9700, 441.4040,
        471.8160, 501.7130, 532.1240, 561.4040, 591.3720,
        621.8200, 652.1240, 682.4510,
    ]
    row_ys = [h - bottom + 2.0 for bottom in row_bottoms_top]

    def draw_fitted_text(x, y, value, max_width, font_size=8.0, min_font_size=6.0):
        """Escreve texto sem ultrapassar a largura do respetivo retângulo."""
        value = str(value or "").strip()
        if not value:
            return

        font_name = "Helvetica"
        size = font_size
        while size > min_font_size and c.stringWidth(value, font_name, size) > max_width:
            size = round(size - 0.25, 2)

        if c.stringWidth(value, font_name, size) > max_width:
            suffix = "..."
            while value and c.stringWidth(value + suffix, font_name, size) > max_width:
                value = value[:-1]
            value = value.rstrip() + suffix if value else suffix

        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_name, size)
        c.drawString(x, y, value)

    date_str = datetime.now().strftime("%d/%m/%Y")

    # 1. Dados do requerente
    draw_fitted_text(
        req_pos["prepared_by"][0],
        req_pos["prepared_by"][1],
        prepared_by_name,
        req_pos["prepared_by"][2]
    )

    # O NIF 322499895 já está impresso no próprio modelo-base da SOLARX.
    # O campo Email / Contacto recebe os dados do cliente da proposta.
    client_data = quote.get("clients") or {}
    client_email = str(client_data.get("email") or "").strip()
    client_phone = str(client_data.get("phone") or "").strip()
    contact_parts = [value for value in (client_email, client_phone) if value]
    email_contact = " | ".join(contact_parts)

    draw_fitted_text(
        req_pos["email_contact"][0],
        req_pos["email_contact"][1],
        email_contact,
        req_pos["email_contact"][2]
    )

    # 2. Detalhes da encomenda
    draw_fitted_text(
        req_pos["request_date"][0],
        req_pos["request_date"][1],
        date_str,
        req_pos["request_date"][2]
    )
    draw_fitted_text(
        req_pos["proposal"][0],
        req_pos["proposal"][1],
        quote.get("proposal", ""),
        req_pos["proposal"][2]
    )

    # 3. Tabela de artigos requisitados (13 linhas disponíveis)
    # Os números 01 a 13 já estão impressos no modelo-base; por isso,
    # apenas Descrição, Quantidade e Unidade são preenchidas pelo código.
    for i, it in enumerate(items[:13]):
        y = row_ys[i]

        draw_fitted_text(
            req_pos["description_x"],
            y,
            it.get("description", ""),
            req_pos["description_width"],
            font_size=8.0,
            min_font_size=6.0
        )

        qty_text = f"{float(it.get('qty', 0)):g}"
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 8)
        c.drawRightString(req_pos["quantity_right"], y, qty_text)

        draw_fitted_text(
            req_pos["unit_x"],
            y,
            it.get("unit", "UN"),
            req_pos["unit_width"],
            font_size=8.0,
            min_font_size=6.0
        )

    c.save()
    buffer.seek(0)
    return buffer

# DASHBOARD — dados reais, sem métricas simuladas de produção/bateria.
from html import escape as html_escape

ICON_SVG = {
    "approved": '<path d="M20 6 9 17l-5-5"/><path d="M12 22a10 10 0 1 0-10-10"/>',
    "clients": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "solar": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
    "sales": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M7 15h2"/>',
    "tax": '<path d="M4 3h16v18l-4-2-4 2-4-2-4 2V3z"/><path d="M8 8h8m-8 4h8"/>',
    "profit": '<path d="m3 17 6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
}


def kpi_card(label, value, detail, icon="sales", tone=""):
    svg = f'<svg viewBox="0 0 24 24" class="sx-kpi-icon" aria-hidden="true">{ICON_SVG.get(icon, ICON_SVG["sales"])}</svg>'
    tag = f'<span class="sx-tag {tone}">{html_escape(detail)}</span>' if detail.startswith(("+", "−", "-")) else f'<span class="sx-kpi-sub">{html_escape(detail)}</span>'
    st.markdown(f"""<div class="sx-kpi"><div class="sx-kpi-head"><span class="sx-kpi-name">{html_escape(label)}</span>{svg}</div><div class="sx-kpi-value">{html_escape(str(value))}</div>{tag}</div>""",unsafe_allow_html=True)


def render_dashboard():
    st.markdown('<div class="sx-heading">Visão Geral</div><div class="sx-subtitle">Indicadores comerciais e financeiros reais, atualizados a partir do Supabase.</div>',unsafe_allow_html=True)
    try:
        clients = fetch_all("clients", "id,created_at", "id")
        quotes = fetch_all("quotes", "*", "id")
        all_items = get_all_items()
        all_payments = quote_payments()
    except Exception as exc:
        st.error("Falha ao consultar os indicadores no Supabase: " + str(exc))
        return

    mapped_items = {}
    for it in all_items:
        mapped_items.setdefault(it.get("quote_id"), []).append(it)
    summaries = {q["id"]: quote_totals(q, mapped_items.get(q["id"],[])) for q in quotes}
    month_list = month_range(12)
    period = st.selectbox("Período dos indicadores", ["Este mês", "Últimos 6 meses", "Últimos 12 meses", "Todo o histórico"],index=1)
    if period=="Este mês":
        selected_months=set(month_list[-1:])
    elif period=="Últimos 6 meses":
        selected_months=set(month_list[-6:])
    elif period=="Últimos 12 meses":
        selected_months=set(month_list)
    else:
        selected_months=None

    in_period=lambda value: selected_months is None or report_month(value) in selected_months
    approved=[q for q in quotes if q.get("status") in ("aprovado","instalado") and q.get("approved_at") and in_period(q.get("approved_at"))]
    installed=[q for q in quotes if q.get("status")=="instalado" and q.get("installed_at") and in_period(q.get("installed_at"))]
    new_clients=[c for c in clients if c.get("created_at") and in_period(c.get("created_at"))]
    missing_client_dates=sum(1 for c in clients if not c.get("created_at"))
    # Crescimento comparado com o período imediatamente anterior, quando possível.
    if selected_months:
        count_months=len(selected_months)
        last_idx=datetime.now().year*12+datetime.now().month-1
        previous_months=set()
        for step in range(count_months, count_months*2):
            idx=last_idx-step
            previous_months.add(f"{idx//12:04d}-{idx%12+1:02d}")
        previous_clients=sum(report_month(c.get("created_at")) in previous_months for c in clients)
        variation=len(new_clients)-previous_clients
        client_detail=f"{len(new_clients)} novos · {variation:+d} vs período anterior"
    else:
        client_detail=f"{len(new_clients)} novos com data conhecida"
    sales_net=sum((summaries[q["id"]]["net"] for q in approved),Decimal("0"))
    iva=sum((summaries[q["id"]]["iva"] for q in approved),Decimal("0"))
    project_kwp=sum((summaries[q["id"]]["kwp"] for q in approved),Decimal("0"))
    installed_kwp=sum((summaries[q["id"]]["kwp"] for q in installed),Decimal("0"))
    profits=[summaries[q["id"]]["profit"] for q in approved if summaries[q["id"]]["cost_known"]]
    n_unknown=sum(not summaries[q["id"]]["cost_known"] for q in approved)
    profit=sum(profits,Decimal("0"))

    st.markdown('<div class="sx-section">Resumo comercial</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    with c1:kpi_card("Projetos aprovados",str(len(approved)),"Aprovados no período", "approved")
    with c2:kpi_card("Clientes cadastrados",str(len(clients)),client_detail,"clients")
    with c3:kpi_card("Potência fotovoltaica aprovada",f"{project_kwp:,.2f} kWp".replace(",","X").replace(".",",").replace("X","."),f"Instalados no período: {installed_kwp:.2f} kWp", "solar")
    c4,c5,c6=st.columns(3)
    with c4:kpi_card("Vendas aprovadas (sem IVA)",money_eur(sales_net),"Não são recebimentos", "sales")
    with c5:kpi_card("IVA das propostas aprovadas",money_eur(iva),"Estimativa; não é IVA a pagar", "tax")
    with c6:kpi_card("Lucro bruto estimado",money_eur(profit) if profits else "—",(f"{n_unknown} proposta(s) sem custos históricos" if n_unknown else "Custos diretos deduzidos"),"profit")

    st.markdown('<div class="sx-section">Evolução e distribuição</div>',unsafe_allow_html=True)
    if selected_months is None:
        months=sorted({report_month(q.get("approved_at")) for q in quotes if report_month(q.get("approved_at"))} | {report_month(c.get("created_at")) for c in clients if report_month(c.get("created_at"))})
        if not months:months=month_list
    else:months=[m for m in month_list if m in selected_months]
    revenue_by_month={m:0.0 for m in months}
    for q in quotes:
        m=report_month(q.get("approved_at"))
        if q.get("status") in ("aprovado","instalado") and m in revenue_by_month:
            revenue_by_month[m]+=float(summaries[q["id"]]["net"])
    c_left,c_right=st.columns([1.65,1])
    with c_left:
        with st.container(border=True):
            st.markdown("**Vendas aprovadas · sem IVA (€)**")
            if any(revenue_by_month.values()):
                st.bar_chart(pd.DataFrame({"Mês":list(revenue_by_month),"Vendas (€)":list(revenue_by_month.values())}).set_index("Mês"),height=270,x_label="Mês",y_label="€")
                st.caption("Meses representados na sequência: "+", ".join(months))
            else:st.info("Ainda não há orçamentos aprovados neste período.")
    with c_right:
        with st.container(border=True):
            st.markdown("**Estado dos projetos · total histórico**")
            state_counts={status:sum(q.get("status", "em_analise")==status for q in quotes) for status in STATUS_LABELS}
            st.bar_chart(pd.DataFrame({"Estado":[STATUS_LABELS[k] for k in state_counts],"Projetos":list(state_counts.values())}).set_index("Estado"),height=270)
            st.caption("Apenas os projetos marcados como aprovados contam como vendas.")

    st.markdown('<div class="sx-section">Fluxo de caixa e execução</div>',unsafe_allow_html=True)
    paid=Decimal("0")
    if all_payments is not None:
        paid=sum((cents(p.get("amount")) for p in all_payments if in_period(p.get("received_at"))),Decimal("0"))
    billed=sum((cents(q.get("total")) for q in quotes if q.get("invoiced_at") and in_period(q.get("invoiced_at"))),Decimal("0"))
    open_balance=sum((max(Decimal("0"),cents(q.get("total"))-sum((cents(p.get("amount")) for p in (all_payments or []) if p.get("quote_id")==q["id"]),Decimal("0"))) for q in quotes if q.get("status") in ("aprovado","instalado")),Decimal("0"))
    a,b,c=st.columns(3)
    with a:st.metric("Pagamentos registados no período",money_eur(paid) if all_payments is not None else "Indisponível")
    with b:st.metric("Orçamentos faturados no período",money_eur(billed))
    with c:st.metric("Saldo por receber (projetos ativos)",money_eur(open_balance) if all_payments is not None else "Indisponível")
    if all_payments is None:
        st.warning("A tabela quote_payments não está acessível. Configure SUPABASE_SERVICE_ROLE_KEY nos Secrets do Streamlit e confirme a migração SQL.")
    if n_unknown:
        st.info(f"{n_unknown} orçamento(s) aprovado(s) têm custos unitários históricos desconhecidos. Não entraram no lucro apresentado; podem ser completados no Histórico.")
    if missing_client_dates:
        st.caption(f"{missing_client_dates} cliente(s) existentes antes da migração não têm data de cadastro conhecida; não são considerados no indicador de novos clientes.")
    st.caption("IVA é estimado sobre propostas aprovadas. Vendas, faturação, recebimentos e lucro são indicadores diferentes. Não há dados telemétricos de inversores/baterias.")

# Navegação lateral — mobile utiliza o recolhimento nativo do Streamlit.
base_dir = os.path.dirname(os.path.abspath(__file__))
with st.sidebar:
    mark_path = next((os.path.join(base_dir, x) for x in
                     ["logo_solarx_mono.png", "HORIZ_Logo_SOLARX_COLOR.png"]
                     if os.path.isfile(os.path.join(base_dir, x))), None)
    if mark_path:
        st.image(mark_path, use_container_width=True)
    else:
        st.markdown("### SOLAR X")
    pages = ["Visão Geral", "Novo Orçamento", "Clientes", "Equipamentos", "Utilizadores", "Histórico e Requisições"]
    page = st.radio("Navegação", pages, label_visibility="collapsed", key="sx_page")
    st.divider()
    st.caption("SOLARX  •  Energy Business")
    if SERVER_KEY:
        st.caption("● Registo privado de pagamentos ativo")
    else:
        st.caption("● A usar chave pública legada")

st.markdown('<div class="sx-topline"></div>', unsafe_allow_html=True)
if not require_financial_schema():
    st.stop()
if not os.path.exists(os.path.join(base_dir, "BASE_Orçamento_SOLARX_00_A.jpg")):
    st.caption("ℹ O modelo de fundo do orçamento não foi encontrado. Mantenha BASE_Orçamento_SOLARX_00_A.jpg na pasta do app.py.")

if page == "Visão Geral":
    render_dashboard()

# TAB 1: NOVO ORÇAMENTO
if page == "Novo Orçamento":
    st.markdown('<div class="sx-heading">Novo Orçamento</div><div class="sx-subtitle">Prepare a proposta e calcule equipamentos, instalação e IVA.</div>',unsafe_allow_html=True)
    st.subheader("1. Dados Gerais")
    col1, col2, col3 = st.columns([1, 2, 2])
    
    clients_list = get_clients()
    client_options = {f"{c['number']:04d} - {c['name']}": c for c in clients_list}
    
    try:
        users_list = get_users()
    except Exception as users_error:
        users_list = []
        st.warning(
            "Não foi possível carregar os utilizadores do Supabase. "
            "A lista será apresentada com o nome padrão até a tabela public.users "
            f"ser configurada. Detalhe: {users_error}"
        )
    user_names = [u.get("name", "Alisson Monteiro") for u in users_list if u.get("name")]
    if not user_names:
        user_names = ["Alisson Monteiro"]
    
    with col1:
        proposal_num = st.number_input("Proposta Nº", value=get_next_proposal(), step=1)
    with col2:
        selected_client_str = st.selectbox("Selecione o Cliente", options=[""] + list(client_options.keys()))
        selected_client = client_options.get(selected_client_str)
    with col3:
        selected_user = st.selectbox("Elaborado Por", options=user_names)

    if selected_client:
        st.info(f"**NIF:** {selected_client.get('nif', '')} | **Telemóvel:** {selected_client.get('phone', '')} | **E-mail:** {selected_client.get('email', '')} | **Morada:** {selected_client.get('address', '')}")

    st.subheader("2. Equipamentos e Serviços (Margem Automática +15%)")
    products_list = get_products()
    product_options = {f"{p.get('ref') or ''} - {p['description']}": p for p in products_list}

    col_h1, col_h2, col_h3, col_h4 = st.columns([4, 1.2, 1.8, 1.8])
    col_h1.caption("**Equipamento / Descrição**")
    col_h2.caption("**Qtd**")
    col_h3.caption("**Preço Venda Unit. (€)**")
    col_h4.caption("**Total Linha (€)**")

    items_data = []
    
    for i in range(14):
        if f"price_{i}" not in st.session_state:
            st.session_state[f"price_{i}"] = 0.0
        if f"qty_{i}" not in st.session_state:
            st.session_state[f"qty_{i}"] = 0.0

        c_p, c_q, c_pr, c_tot = st.columns([4, 1.2, 1.8, 1.8])
        
        with c_p:
            p_sel = st.selectbox(
                f"Item {i+1}", 
                [""] + list(product_options.keys()), 
                key=f"prod_{i}", 
                on_change=update_product_row,
                args=(i, product_options),
                label_visibility="collapsed"
            )
            prod = product_options.get(p_sel)
        
        with c_q:
            qty = st.number_input(
                f"Qtd {i+1}", 
                min_value=0.0, 
                step=1.0, 
                key=f"qty_{i}", 
                label_visibility="collapsed"
            )
            
        with c_pr:
            unit_price = st.number_input(
                f"Venda € {i+1}", 
                min_value=0.0, 
                step=5.0, 
                format="%.2f",
                key=f"price_{i}", 
                label_visibility="collapsed"
            )
        
        qty_dec = Decimal(str(qty))
        price_dec = Decimal(str(unit_price))
        total_line_dec = (price_dec * qty_dec).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        with c_tot:
            line_str = money(total_line_dec)
            st.markdown(f"**{line_str} €**")
            
        if prod and qty > 0 and price_dec > 0:
            items_data.append({
                "ref": prod.get("ref", ""),
                "description": prod["description"],
                "qty": qty_dec,
                "unit": prod.get("unit", "UN"),
                "unit_price": price_dec,
                "line_total": total_line_dec,
                # Guardar snapshot de custo e potência, evitando distorções futuras.
                "cost_unit": cents(prod.get("cost")),
                "panel_wp": cents(prod.get("panel_wp") or 600) if prod.get("is_solar_panel") else None
            })

    st.subheader("3. Instalação, IVA e condições")
    st.caption("Escolha a regra comercial de instalação. Pode preservar o cálculo antigo (custo + 20%) ou definir um preço totalmente manual.")
    installation_mode = st.radio(
        "Como calcular a instalação?",
        options=("Cálculo anterior (+20% sobre custo)", "Preço manual (sem acréscimo)"),
        horizontal=True,
        key="sx_inst_mode",
        help="No cálculo anterior, 500 € de custo tornam-se 600 € de preço sem IVA e 738 € com IVA a 23%."
    )
    c1,c2,c3=st.columns([1,1,1])
    if installation_mode.startswith("Cálculo anterior"):
        with c1:
            inst_base_in=st.number_input(
                "Instalação — custo base (€)", min_value=0.0, value=0.0,
                step=25.0, key="sx_inst_base",
                help="É o antigo campo 'Instalação (€ Custo)'. Aplica 20% de acréscimo para calcular o preço de venda."
            )
        inst_cost_dec=cents(inst_base_in)
        inst_sale_dec=cents(inst_cost_dec*(Decimal("1")+MARGEM_INSTALACAO))
        with c2:
            st.metric("Preço de instalação sem IVA", money_eur(inst_sale_dec))
    else:
        with c1:
            inst_sale_in=st.number_input(
                "Preço instalação, sem IVA (€)", min_value=0.0, value=0.0,
                step=25.0, key="sx_inst_sale",
                help="Preço definido manualmente após a visita, sem qualquer acréscimo automático."
            )
        with c2:
            inst_cost_in=st.number_input(
                "Custo real de instalação (€)", min_value=0.0, value=0.0,
                step=25.0, key="sx_inst_cost",
                help="Mão de obra ou subcontratação efetivamente suportada pela SolarX. Não aparece no PDF."
            )
        inst_sale_dec=cents(inst_sale_in)
        inst_cost_dec=cents(inst_cost_in)
    with c3:
        extra_cost_in=st.number_input(
            "Outros custos diretos (€)",min_value=0.0,value=0.0,step=10.0,
            key="sx_extra_cost",help="Deslocações, consumíveis, etc. Não são cobrados automaticamente ao cliente."
        )
    extra_cost_dec=cents(extra_cost_in)
    c_disc,c_tax=st.columns([1,2])
    with c_disc:
        discount_in=st.number_input("Desconto equipamentos, sem IVA (€)",min_value=0.0,value=0.0,step=5.0,key="sx_discount")
    with c_tax:
        tax_selection=st.selectbox("IVA da instalação",["Taxa normal (23%)","Outro enquadramento fiscal (0%, sujeito a validação)"],key="sx_tax_mode")
    inst_tax_rate=IVA if tax_selection.startswith("Taxa normal") else Decimal("0")
    tax_basis=""
    if inst_tax_rate==0:
        tax_basis=st.text_input("Fundamento fiscal documentado (obrigatório)",key="sx_tax_basis",placeholder="Referência legal validada pelo contabilista")
        st.warning("Numerário não constitui motivo para dispensar IVA. Utilize 0% apenas com fundamento fiscal válido confirmado pelo contabilista.")
    notes_in=st.text_input("Observações",value="Instalação INCLUIDA",key="sx_quote_notes")

    subtotal_items=sum((it["line_total"] for it in items_data),Decimal("0"))
    discount_dec=cents(discount_in)
    # inst_sale_dec e inst_cost_dec já refletem o modo escolhido acima.
    # Modo anterior: custo + 20%; modo manual: preço indicado, sem acréscimo.
    equip_net=max(Decimal("0"),subtotal_items-discount_dec)
    equip_iva=cents(equip_net*IVA)
    installation_iva=cents(inst_sale_dec*inst_tax_rate)
    total_equip=equip_net+equip_iva
    total_global=total_equip+inst_sale_dec+installation_iva
    total_cost=sum((it["cost_unit"]*it["qty"] for it in items_data),Decimal("0"))+inst_cost_dec+extra_cost_dec
    gross_profit=cents(equip_net+inst_sale_dec-total_cost)

    with st.container(border=True):
        st.markdown("**Resumo da proposta**")
        a,b,c=st.columns(3)
        with a:st.metric("Equipamentos com IVA",money_eur(total_equip))
        with b:st.metric("Instalação com IVA aplicável",money_eur(inst_sale_dec+installation_iva))
        with c:st.metric("TOTAL DA PROPOSTA",money_eur(total_global))
        st.caption(f"Equipamentos sem IVA: {money_eur(equip_net)} · IVA equipamento: {money_eur(equip_iva)} · IVA instalação: {money_eur(installation_iva)} · Lucro bruto estimado interno: {money_eur(gross_profit)}")
        st.caption("A forma de pagamento será registada no Histórico após a aprovação. Não altera o IVA.")

    if st.button("Guardar no Supabase e gerar proposta PDF",type="primary",key="sx_save_quote"):
        if not selected_client:
            st.error("Selecione um cliente.")
        elif not items_data:
            st.error("Selecione pelo menos um equipamento com quantidade e valor superiores a zero.")
        elif discount_dec>subtotal_items:
            st.error("O desconto de equipamentos não pode superar o seu subtotal.")
        elif inst_tax_rate==0 and not tax_basis.strip():
            st.error("Indique o fundamento fiscal antes de usar um enquadramento sem IVA na instalação.")
        else:
            try:
                quote_payload={
                    "proposal":int(proposal_num),"client_id":selected_client["id"],
                    "created_at":datetime.now().isoformat(),
                    "discount":float(discount_dec),
                    "installation_sale":float(inst_sale_dec),
                    "installation_cost":float(inst_cost_dec),
                    "installation_iva_rate":float(inst_tax_rate),
                    "installation_tax_basis":tax_basis.strip() if inst_tax_rate==0 else None,
                    "extra_cost":float(extra_cost_dec),"notes":notes_in,
                    "status":"em_analise", "finance_version":"v2", "total":float(total_global),
                }
                items_payload=[{
                    "ref":it["ref"],"description":it["description"],
                    "qty":float(it["qty"]),"unit":it["unit"],
                    "unit_price":float(it["unit_price"]),
                    "line_total":float(it["line_total"]),
                    "cost_unit":float(it["cost_unit"]),
                    "panel_wp":float(it["panel_wp"]) if it["panel_wp"] is not None else None,
                } for it in items_data]
                # PDF gerado ANTES da gravação: evita orçamentos guardados sem PDF válido.
                pdf_buf=generate_pdf_buffer(selected_client,items_data,discount_dec,inst_sale_dec,
                                            notes_in,proposal_num,selected_user,inst_tax_rate)
                q_res=supabase.table("quotes").insert(quote_payload).execute()
                if not q_res.data:raise RuntimeError("Supabase não confirmou a inserção do orçamento")
                quote_id=q_res.data[0]["id"]
                try:
                    for it in items_payload:it["quote_id"]=quote_id
                    supabase.table("quote_items").insert(items_payload).execute()
                except Exception as e:
                    # Tentar rollback do cabeçalho, sem eliminar informação pré-existente.
                    try:supabase.table("quotes").delete().eq("id",quote_id).execute()
                    except Exception:pass
                    raise RuntimeError(f"Não foi possível guardar os artigos; verifique se a proposta {proposal_num} ficou registada. {e}")
                st.success("Orçamento e artigos gravados com sucesso no Supabase!")
                st.download_button("Descarregar proposta PDF",data=pdf_buf,
                    file_name=f"Orcamento_{proposal_num}_{selected_client['name'].replace(' ','_')}.pdf",
                    mime="application/pdf",key=f"sx_quote_download_{quote_id}",type="primary")
            except Exception as e:
                st.error("Erro ao gravar o orçamento: "+str(e))

# TAB 2: CLIENTES
if page == "Clientes":
    st.markdown('<div class="sx-heading">Clientes</div><div class="sx-subtitle">Gestão centralizada de contactos e histórico comercial.</div>',unsafe_allow_html=True)
    st.info(
        "Remova linhas e clique em Salvar. Para eliminar clientes e os seus "
        "orçamentos associados será exigida uma confirmação separada."
    )

    notice = st.session_state.pop("clients_save_notice", None)
    if notice:
        st.success(notice)

    # Uma eliminação pendente nunca é executada por um simples clique em Salvar.
    pending = st.session_state.get("clients_pending_delete") or []
    if pending:
        st.error(
            "⚠️ EXCLUSÃO DEFINITIVA: esta operação apagará os clientes abaixo, "
            "os respetivos orçamentos e todos os artigos desses orçamentos. "
            "Os documentos deixarão de estar disponíveis no histórico. "
            "A operação não pode ser desfeita pela aplicação."
        )
        for entry in pending:
            st.write(
                f"• **{entry['name']}** (ID {entry['id']}): "
                f"**{entry['quote_count']} orçamento(s)** e "
                f"**{entry['item_count']} artigo(s)** a eliminar"
            )
        st.warning(
            "Faça uma cópia de segurança no Supabase antes de confirmar. "
            "A exclusão usa pedidos separados à API e não é uma transação única: "
            "se ocorrer uma falha de rede, pode haver uma eliminação parcial."
        )
        confirmed = st.checkbox(
            "Compreendo que os clientes, orçamentos e artigos serão eliminados definitivamente.",
            key=f"clients_delete_ack_{st.session_state.get('clients_editor_version', 0)}"
        )
        confirmation = st.text_input(
            'Para confirmar, escreva exatamente ELIMINAR',
            key=f"clients_delete_phrase_{st.session_state.get('clients_editor_version', 0)}"
        )
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button(
                "CONFIRMAR EXCLUSÃO DEFINITIVA",
                type="primary",
                disabled=not (confirmed and confirmation == "ELIMINAR"),
                key="clients_delete_confirm_button"
            ):
                # Revalidar IDs, nome e contagens para evitar eliminar dados
                # diferentes daqueles que foram apresentados na confirmação.
                try:
                    for entry in pending:
                        cid = entry["id"]
                        current = (
                            supabase.table("clients").select("id,name")
                            .eq("id", cid).execute().data or []
                        )
                        if len(current) != 1 or current[0]["name"] != entry["name"]:
                            raise RuntimeError(
                                f"O cliente ID {cid} foi alterado ou removido. "
                                "Cancele e refaça a seleção."
                            )
                        quote_rows = (
                            supabase.table("quotes").select("id")
                            .eq("client_id", cid).execute().data or []
                        )
                        quote_ids = [q["id"] for q in quote_rows]
                        if len(quote_ids) != entry["quote_count"]:
                            raise RuntimeError(
                                f"O número de orçamentos do cliente {entry['name']} "
                                "mudou. Cancele e refaça a seleção."
                            )
                        item_count = 0
                        for qid in quote_ids:
                            item_count += len(
                                supabase.table("quote_items").select("id")
                                .eq("quote_id", qid).execute().data or []
                            )
                        if item_count != entry["item_count"]:
                            raise RuntimeError(
                                f"Os artigos associados a {entry['name']} "
                                "mudaram. Cancele e refaça a seleção."
                            )

                    deleted_clients = 0
                    deleted_quotes = 0
                    deleted_items = 0
                    for entry in pending:
                        cid = entry["id"]
                        quote_rows = (
                            supabase.table("quotes").select("id")
                            .eq("client_id", cid).execute().data or []
                        )
                        for q in quote_rows:
                            qid = q["id"]
                            # Ordem necessária para respeitar as foreign keys.
                            item_rows = (
                                supabase.table("quote_items").select("id")
                                .eq("quote_id", qid).execute().data or []
                            )
                            supabase.table("quote_items").delete().eq("quote_id", qid).execute()
                            if (supabase.table("quote_items").select("id")
                                    .eq("quote_id", qid).limit(1).execute().data):
                                raise RuntimeError(f"Artigos do orçamento ID {qid} não foram removidos.")
                            deleted_items += len(item_rows)
                            supabase.table("quotes").delete().eq("id", qid).execute()
                            if (supabase.table("quotes").select("id")
                                    .eq("id", qid).limit(1).execute().data):
                                raise RuntimeError(f"Orçamento ID {qid} não foi removido.")
                            deleted_quotes += 1
                        supabase.table("clients").delete().eq("id", cid).execute()
                        if (supabase.table("clients").select("id")
                                .eq("id", cid).limit(1).execute().data):
                            raise RuntimeError(f"Cliente ID {cid} não foi removido.")
                        deleted_clients += 1

                    st.session_state["clients_pending_delete"] = []
                    st.session_state["clients_save_notice"] = (
                        f"Exclusão confirmada: {deleted_clients} cliente(s), "
                        f"{deleted_quotes} orçamento(s) e {deleted_items} artigo(s) removidos."
                    )
                    st.session_state["clients_editor_version"] = (
                        st.session_state.get("clients_editor_version", 0) + 1
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(
                        "Não foi possível concluir a exclusão. Algumas operações podem "
                        f"já ter ocorrido. Verifique o Supabase antes de tentar novamente. Detalhe: {exc}"
                    )
        with col_cancel:
            if st.button("Cancelar exclusão", key="clients_delete_cancel_button"):
                st.session_state["clients_pending_delete"] = []
                st.session_state["clients_editor_version"] = (
                    st.session_state.get("clients_editor_version", 0) + 1
                )
                st.rerun()

    clients_df = get_clients()
    if clients_df is not None:
        if "clients_editor_version" not in st.session_state:
            st.session_state["clients_editor_version"] = 0
        clients_editor_key = f"clients_editor_{st.session_state['clients_editor_version']}"
        edited_clients = st.data_editor(
            clients_df,
            key=clients_editor_key,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["id", "number"]
        )

        if st.button("Salvar Alterações de Clientes", disabled=bool(pending)):
            try:
                original_rows = editor_rows(clients_df)
                edited_rows = editor_rows(edited_clients)
                original_by_id = {
                    row_id(row): row for row in original_rows if row_id(row) is not None
                }
                deleted_ids = set(original_by_id) - {
                    row_id(row) for row in edited_rows if row_id(row) is not None
                }

                # Guardar as edições normais sem apagar ainda nenhum cliente.
                for row in edited_rows:
                    current_id = row_id(row)
                    name = str(row.get("name") or "").strip()
                    if not name:
                        if current_id is not None:
                            raise ValueError(
                                f"O cliente ID {current_id} ficou sem nome. "
                                "Preencha o nome ou remova a linha inteira."
                            )
                        continue
                    client_payload = {
                        "name": name,
                        "contact": row.get("contact"),
                        "nif": row.get("nif"),
                        "address": row.get("address"),
                        "postal": row.get("postal"),
                        "phone": row.get("phone"),
                        "email": row.get("email")
                    }
                    if current_id is not None:
                        supabase.table("clients").update(client_payload).eq("id", current_id).execute()
                    else:
                        client_payload["number"] = get_next_client_number()
                        supabase.table("clients").insert(client_payload).execute()

                if deleted_ids:
                    pending_delete = []
                    for cid in sorted(deleted_ids):
                        quotes = (
                            supabase.table("quotes").select("id")
                            .eq("client_id", cid).execute().data or []
                        )
                        count_items = 0
                        for quote in quotes:
                            count_items += len(
                                supabase.table("quote_items").select("id")
                                .eq("quote_id", quote["id"]).execute().data or []
                            )
                        pending_delete.append({
                            "id": cid,
                            "name": str(original_by_id[cid].get("name") or f"ID {cid}"),
                            "quote_count": len(quotes),
                            "item_count": count_items
                        })
                    st.session_state["clients_pending_delete"] = pending_delete
                    st.session_state["clients_save_notice"] = (
                        "Alterações guardadas. A exclusão ainda NÃO foi executada: "
                        "confirme-a no painel acima."
                    )
                else:
                    st.session_state["clients_save_notice"] = (
                        "Dados dos clientes atualizados com sucesso."
                    )
                st.session_state["clients_editor_version"] += 1
                st.rerun()
            except Exception as exc:
                st.error(f"Erro ao atualizar clientes: {exc}")

    with st.expander("➕ Cadastrar Novo Cliente"):
        with st.form("form_client"):
            c1, c2 = st.columns(2)
            with c1:
                c_name = st.text_input("Nome *")
                c_contact = st.text_input("Pessoa de Contacto")
                c_nif = st.text_input("NIF")
                c_phone = st.text_input("Telemóvel")
            with c2:
                c_address = st.text_input("Morada")
                c_postal = st.text_input("Código Postal")
                c_email = st.text_input("E-mail")
            
            if st.form_submit_button("Guardar Cliente"):
                if not c_name:
                    st.error("Nome é obrigatório!")
                else:
                    num = get_next_client_number()
                    supabase.table("clients").insert({
                        "number": num,
                        "name": c_name,
                        "contact": c_contact,
                        "nif": c_nif,
                        "address": c_address,
                        "postal": c_postal,
                        "phone": c_phone,
                        "email": c_email
                    }).execute()
                    st.success("Cliente registado com sucesso!")
                    st.rerun()

# TAB 3: EQUIPAMENTOS
if page == "Equipamentos":
    st.markdown('<div class="sx-heading">Equipamentos</div><div class="sx-subtitle">Catálogo, preços e potência fotovoltaica por artigo.</div>',unsafe_allow_html=True)
    st.info("Marque a coluna is_solar_panel e informe panel_wp (600 por padrão) nos painéis, para contabilizar kWp corretamente no Dashboard.")
    prods_df = get_products()
    if prods_df is not None:
        edited_prods = st.data_editor(prods_df, key="prods_editor", use_container_width=True, num_rows="dynamic", disabled=["id"])
        if st.button("Salvar Alterações de Equipamentos"):
            try:
                original_ids = {item["id"] for item in prods_df if "id" in item}
                clean_product_rows = editor_rows(edited_prods)
                edited_ids = {row_id(row) for row in clean_product_rows if row_id(row) is not None}
                deleted_ids = original_ids - edited_ids
                for d_id in deleted_ids:
                    supabase.table("products").delete().eq("id", d_id).execute()

                for row in clean_product_rows:
                    if row_id(row) is not None:
                        supabase.table("products").update({
                            "ref": row.get("ref"),
                            "description": row.get("description"),
                            "cost": float(row.get("cost", 0)),
                            "margin": float(row.get("margin", 0.15)),
                            "unit": row.get("unit", "UN"),
                            "is_solar_panel": checked_solar_flag(row),
                            "panel_wp": checked_panel_wp(row)
                        }).eq("id", row["id"]).execute()
                    else:
                        if row.get("description"):
                            supabase.table("products").insert({
                                "ref": row.get("ref"),
                                "description": row.get("description"),
                                "cost": float(row.get("cost", 0)),
                                "margin": float(row.get("margin", 0.15)),
                                "unit": row.get("unit", "UN"),
                                "is_solar_panel": checked_solar_flag(row),
                                "panel_wp": checked_panel_wp(row)
                            }).execute()
                st.success("Catálogo de equipamentos atualizado com sucesso na nuvem!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar equipamentos: {e}")

    with st.expander("➕ Cadastrar Novo Equipamento"):
        with st.form("form_product"):
            p_ref = st.text_input("Referência")
            p_desc = st.text_input("Descrição *")
            p_cost = st.number_input("Custo (€) *", min_value=0.0, step=10.0)
            p_margin = st.number_input("Margem (ex: 0.15 para 15%)", value=0.15, step=0.01, format="%.2f")
            p_unit = st.text_input("Unidade", value="UN")
            p_is_panel = st.checkbox("Este equipamento é um painel fotovoltaico")
            p_wp = st.number_input("Potência do painel (Wp)", min_value=1.0, value=600.0, step=50.0, disabled=not p_is_panel)

            venda_sugerida = sale_price(p_cost, Decimal(str(p_margin)))
            st.info(f"Preço de Venda Calculado (+{p_margin*100:.0f}%): **{money(venda_sugerida)} €**")

            if st.form_submit_button("Guardar Equipamento"):
                if not p_desc:
                    st.error("Descrição é obrigatória!")
                else:
                    supabase.table("products").insert({
                        "ref": p_ref,
                        "description": p_desc,
                        "cost": float(p_cost),
                        "margin": float(p_margin),
                        "unit": p_unit,
                        "is_solar_panel":p_is_panel,
                        "panel_wp":float(p_wp) if p_is_panel else None
                    }).execute()
                    st.success("Equipamento cadastrado com sucesso!")
                    st.rerun()

# TAB 4: UTILIZADORES
if page == "Utilizadores":
    st.markdown('<div class="sx-heading">Utilizadores</div><div class="sx-subtitle">Pessoas autorizadas a elaborar documentos comerciais.</div>',unsafe_allow_html=True)
    st.info(
        "Os utilizadores são lidos e gravados diretamente no Supabase. "
        "Não é usado armazenamento local temporário."
    )

    users_notice = st.session_state.pop("users_save_notice", None)
    if users_notice:
        st.success(users_notice)

    users_load_error = None
    try:
        users_data = get_users()
    except Exception as e:
        users_data = []
        users_load_error = e
        st.error(
            "Não foi possível carregar os utilizadores do Supabase. "
            "Confirme a tabela public.users e as permissões RLS. "
            f"Detalhe: {e}"
        )

    if users_data:
        if "users_editor_version" not in st.session_state:
            st.session_state["users_editor_version"] = 0
        users_editor_key = f"users_editor_{st.session_state['users_editor_version']}"
        edited_users = st.data_editor(
            users_data,
            key=users_editor_key,
            use_container_width=True,
            num_rows="dynamic",
            disabled=["id"]
        )

        if st.button("Salvar Alterações de Utilizadores"):
            try:
                original_rows = editor_rows(users_data)
                edited_rows = editor_rows(edited_users)
                original_ids = {
                    row_id(row) for row in original_rows if row_id(row) is not None
                }
                edited_ids = {
                    row_id(row) for row in edited_rows if row_id(row) is not None
                }
                deleted_ids = original_ids - edited_ids

                # Valida os nomes antes de efetuar alterações na nuvem.
                clean_rows = []
                seen_names = set()
                for row in edited_rows:
                    name = str(row.get("name") or "").strip()
                    current_id = row_id(row)
                    if not name:
                        if current_id is not None:
                            raise ValueError(
                                f"O utilizador com ID {current_id} ficou sem nome. "
                                "Preencha o nome ou remova a linha inteira."
                            )
                        continue
                    normalized = name.casefold()
                    if normalized in seen_names:
                        raise ValueError(f"O utilizador '{name}' está repetido na lista.")
                    seen_names.add(normalized)
                    clean_rows.append((current_id, name))

                for user_id in deleted_ids:
                    supabase.table("users").delete().eq("id", user_id).execute()

                for user_id, name in clean_rows:
                    if user_id is not None:
                        supabase.table("users").update({"name": name}).eq("id", user_id).execute()
                    else:
                        supabase.table("users").insert({"name": name}).execute()

                st.session_state["users_save_notice"] = "Lista de utilizadores atualizada diretamente no Supabase."
                st.session_state["users_editor_version"] += 1
                st.rerun()
            except Exception as e:
                st.error(
                    "Não foi possível guardar todas as alterações dos utilizadores no Supabase. "
                    "Nenhuma gravação local temporária foi apresentada como permanente. "
                    f"Detalhe: {e}"
                )
    elif not users_load_error:
        st.info("Ainda não existem utilizadores registados. Cadastre o primeiro abaixo.")

    with st.expander("➕ Cadastrar Novo Utilizador", expanded=not bool(users_data)):
        with st.form("form_user"):
            u_name = st.text_input("Nome do Utilizador *")
            if st.form_submit_button("Guardar Utilizador"):
                clean_name = u_name.strip()
                if not clean_name:
                    st.error("O nome é obrigatório!")
                else:
                    try:
                        current_users = get_users()
                        duplicate = any(
                            str(user.get("name") or "").strip().casefold() == clean_name.casefold()
                            for user in current_users
                        )
                        if duplicate:
                            st.warning(f"O utilizador '{clean_name}' já está registado.")
                        else:
                            supabase.table("users").insert({"name": clean_name}).execute()
                            st.session_state["users_save_notice"] = (
                                f"Utilizador '{clean_name}' gravado com sucesso no Supabase."
                            )
                            st.rerun()
                    except Exception as err:
                        st.error(
                            "O utilizador NÃO foi gravado de forma persistente. "
                            "Confirme se a tabela public.users existe e se as políticas RLS "
                            "permitem SELECT e INSERT. Execute também o ficheiro SQL de "
                            f"configuração fornecido. Detalhe: {err}"
                        )

# TAB 5: HISTÓRICO + ACOMPANHAMENTO DOS PROJETOS
if page == "Histórico e Requisições":
    st.markdown('<div class="sx-heading">Histórico e Requisições</div><div class="sx-subtitle">Aprovação, instalação, faturação, pagamentos e requisições de material.</div>',unsafe_allow_html=True)
    st.caption("Orçamentos anteriores à atualização começam em 'Em análise' e necessitam de classificação manual. Valores de custos históricos desconhecidos não são estimados.")
    try:
        history_users=get_users()
    except Exception as users_error:
        history_users=[]
        st.warning("A lista de utilizadores não está disponível: "+str(users_error))
    try:
        quotes_list=fetch_all("quotes", "*,clients(id,name,address,postal,nif,phone,email)", "created_at", True)
    except Exception as e:
        st.error("Erro ao consultar histórico no Supabase: "+str(e))
        quotes_list=[]
    filter_cols=st.columns([2,1])
    with filter_cols[0]:
        hist_query=st.text_input("Pesquisar proposta / cliente",placeholder="Número ou nome",key="sx_hist_search")
    with filter_cols[1]:
        hist_status=st.selectbox("Filtrar estado",["Todos"]+list(STATUS_LABELS.values()),key="sx_hist_filter")
    shown=[]
    for q in quotes_list:
        client_data=q.get("clients") or {}
        qname=str(client_data.get("name") or "Cliente desconhecido")
        label=STATUS_LABELS.get(q.get("status"),"Em análise")
        if hist_status!="Todos" and label!=hist_status:continue
        if hist_query.strip() and hist_query.strip().casefold() not in (str(q.get("proposal"))+" "+qname).casefold():continue
        shown.append(q)
    st.caption(f"{len(shown)} proposta(s) encontradas")
    for q in shown:
        qid=q["id"]
        qstatus=q.get("status") or "em_analise"
        client_data=q.get("clients") or {}
        cname=str(client_data.get("name") or "Cliente desconhecido")
        proposal=q.get("proposal")
        label=STATUS_LABELS.get(qstatus,"Em análise")
        with st.expander(f"Proposta {proposal} · {cname} · {label} · {money_eur(q.get('total'))}"):
            pill_class = "sx-tag" if qstatus in ("aprovado", "instalado") else ("sx-tag bad" if qstatus=="rejeitado" else "sx-tag warn")
            st.markdown(f'<span class="{pill_class}">{html_escape(label)}</span>',unsafe_allow_html=True)
            st.write(f"**Cliente:** {cname}   |   **Criado:** {str(q.get('created_at') or '')[:10]}   |   **Estado:** {label}")
            if q.get("notes"):st.caption("Observações: "+str(q.get("notes")))
            try:
                quote_items=supabase.table("quote_items").select("*").eq("quote_id",qid).order("id").execute().data or []
            except Exception as exc:
                st.error(f"Não foi possível carregar os artigos da proposta {proposal}: {exc}")
                continue
            totals=quote_totals(q,quote_items)
            a,b,c=st.columns(3)
            with a:st.metric("Total da proposta",money_eur(q.get("total")))
            with b:st.metric("Potência registada",f"{totals['kwp']:.2f} kWp")
            with c:st.metric("Lucro bruto estimado",money_eur(totals['profit']) if totals['cost_known'] else "Por completar")
            st.divider()
            st.markdown("**1. Gestão comercial e execução**")
            with st.form(f"sx_status_form_{qid}"):
                new_status=st.selectbox("Estado do projeto",options=list(STATUS_LABELS),index=list(STATUS_LABELS).index(qstatus) if qstatus in STATUS_LABELS else 0,
                    format_func=lambda k:STATUS_LABELS[k],key=f"sx_status_input_{qid}")
                st.caption("Aprovar regista a data de aprovação; instalar regista a data de conclusão.")
                submit_status=st.form_submit_button("Guardar estado do projeto")
            if submit_status:
                try:
                    now=datetime.now().isoformat()
                    update={"status":new_status}
                    if new_status in ("aprovado","instalado") and (qstatus not in ("aprovado","instalado") or not q.get("approved_at")):
                        update["approved_at"]=now
                    if new_status=="instalado" and (qstatus!="instalado" or not q.get("installed_at")):
                        update["installed_at"]=now
                    if new_status not in ("aprovado","instalado"):
                        update["approved_at"]=None
                        update["installed_at"]=None
                    elif new_status=="aprovado":
                        update["installed_at"]=None
                    supabase.table("quotes").update(update).eq("id",qid).execute()
                    st.success("Estado atualizado no Supabase")
                    st.rerun()
                except Exception as exc:
                    st.error("Erro ao guardar estado: "+str(exc))

            st.markdown("**2. Faturação e custos**")
            with st.form(f"sx_invoice_form_{qid}"):
                inv_number=st.text_input("Número da fatura (se emitida)",value=q.get("invoice_number") or "",key=f"sx_invoice_nr_{qid}")
                inv_date=st.date_input("Data de faturação",value=(dttm(q.get("invoiced_at")).date() if dttm(q.get("invoiced_at")) else datetime.now().date()),key=f"sx_invoice_date_{qid}")
                was_invoiced=st.checkbox("Confirmo que a fatura foi efetivamente emitida",value=bool(q.get("invoiced_at")),key=f"sx_invoice_check_{qid}")
                invoice_submit=st.form_submit_button("Guardar faturação")
            if invoice_submit:
                if was_invoiced and not inv_number.strip():
                    st.error("Informe o número da fatura realmente emitida.")
                else:
                    try:
                        supabase.table("quotes").update({
                            "invoice_number":inv_number.strip() if was_invoiced else None,
                            "invoiced_at":inv_date.isoformat() if was_invoiced else None,
                        }).eq("id",qid).execute()
                        st.success("Dados de faturação atualizados")
                        st.rerun()
                    except Exception as exc:st.error("Erro ao guardar faturação: "+str(exc))

            with st.expander("Completar custos e potência de propostas antigas"):
                st.caption("Só altere custos se tiver os valores reais do orçamento original. O catálogo atual pode ter preços diferentes.")
                editor_input=[{
                    "id":it["id"],"Designação":it.get("description") or "",
                    "Quantidade":float(it.get("qty") or 0),
                    "Custo unitário histórico (€)":float(it["cost_unit"]) if it.get("cost_unit") is not None else None,
                    "Potência por painel (Wp)":float(it["panel_wp"]) if it.get("panel_wp") is not None else None,
                } for it in quote_items]
                edited_hist=st.data_editor(editor_input,key=f"sx_cost_editor_{qid}",num_rows="fixed",use_container_width=True,disabled=["id","Designação","Quantidade"])
                if st.button("Guardar custos / potência",key=f"sx_cost_save_{qid}"):
                    try:
                        for row in editor_rows(edited_hist):
                            def optional_amount(raw):
                                if raw is None or str(raw).strip().lower() in ("", "nan", "none"):
                                    return None
                                val=float(raw)
                                if val<0:raise ValueError("Custos e potência não podem ser negativos")
                                return val
                            supabase.table("quote_items").update({
                                "cost_unit":optional_amount(row.get("Custo unitário histórico (€)")),
                                "panel_wp":optional_amount(row.get("Potência por painel (Wp)"))
                            }).eq("id",row["id"]).eq("quote_id",qid).execute()
                        st.success("Custos e potência atualizados")
                        st.rerun()
                    except Exception as exc:st.error("Erro ao guardar valores históricos: "+str(exc))

            st.markdown("**3. Pagamentos recebidos**")
            try:
                pay_rows=payments_db.table("quote_payments").select("*").eq("quote_id",qid).order("received_at").execute().data or []
                pay_error=None
            except Exception as exc:
                pay_error=exc
                pay_rows=[]
            total_paid=sum((cents(x.get("amount")) for x in pay_rows),Decimal("0"))
            remaining=max(Decimal("0"),cents(q.get("total"))-total_paid)
            if pay_error:
                st.warning("Pagamentos indisponíveis. Configure a chave secreta de servidor no Streamlit e execute a migração. "+str(pay_error))
            else:
                u,v=st.columns(2)
                with u:st.metric("Recebido",money_eur(total_paid))
                with v:st.metric("Por receber",money_eur(remaining))
                for p in pay_rows:
                    st.caption(f"{str(p.get('received_at') or '')[:10]} · {PAYMENT_LABELS.get(p.get('method'),p.get('method'))} · {money_eur(p.get('amount'))} · {p.get('note') or ''}")
                if qstatus not in ("aprovado","instalado"):
                    st.caption("Para registar recebimentos, primeiro marque o projeto como Aprovado.")
                elif remaining>0:
                    with st.form(f"sx_pay_form_{qid}"):
                        pc1,pc2,pc3=st.columns([1,1,1])
                        with pc1:paid_date=st.date_input("Data do recebimento",value=datetime.now().date(),key=f"sx_pay_date_{qid}")
                        with pc2:paid_method=st.selectbox("Método de pagamento",list(PAYMENT_LABELS),format_func=lambda m:PAYMENT_LABELS[m],key=f"sx_pay_type_{qid}")
                        with pc3:paid_amount=st.number_input("Montante recebido (€)",min_value=0.01,value=float(remaining),step=10.0,key=f"sx_pay_amount_{qid}")
                        paid_note=st.text_input("Nota do pagamento (opcional)",key=f"sx_pay_note_{qid}")
                        paid_submit=st.form_submit_button("Registar recebimento")
                    if paid_submit:
                        if cents(paid_amount)>remaining:
                            st.error("O montante excede o saldo por receber.")
                        else:
                            try:
                                payments_db.table("quote_payments").insert({
                                    "quote_id":qid,"amount":float(cents(paid_amount)),
                                    "received_at":paid_date.isoformat(),"method":paid_method,
                                    "note":paid_note.strip() or None,
                                }).execute()
                                st.success("Recebimento registado")
                                st.rerun()
                            except Exception as exc:st.error("Erro ao registar pagamento: "+str(exc))

            st.divider()
            st.markdown("**4. Requisição de material**")
            selected_req=[]
            if quote_items:
                for idx,it in enumerate(quote_items):
                    if st.checkbox(f"{it.get('description')}  ·  {it.get('qty')} {it.get('unit') or 'UN'}",
                        value=(idx<13),key=f"sx_req_{qid}_{it['id']}"):
                        selected_req.append(it)
                if len(selected_req)>13:
                    st.warning("O modelo PDF da requisição comporta no máximo 13 linhas; desmarque os itens excedentes.")
            names=[u.get("name") for u in history_users if u.get("name")] or ["Alisson Monteiro"]
            req_user=st.selectbox("Elaborado por",names,key=f"sx_req_user_{qid}")
            if st.button("Gerar requisição PDF",key=f"sx_req_make_{qid}"):
                if not selected_req:st.warning("Selecione pelo menos um artigo.")
                elif len(selected_req)>13:st.error("É permitido um máximo de 13 artigos.")
                else:
                    try:
                        req_buf=generate_requisition_pdf_buffer(q,selected_req,req_user)
                        st.download_button("Descarregar requisição",data=req_buf,
                            file_name=f"Requisicao_Material_Proposta_{proposal}.pdf",mime="application/pdf",
                            key=f"sx_req_dl_{qid}",type="primary")
                    except Exception as exc:st.error("Falha ao gerar PDF: "+str(exc))
