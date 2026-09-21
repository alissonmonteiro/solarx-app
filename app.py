import os
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import streamlit as st
from supabase import create_client
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# Configuração da Página no Streamlit (Com Ícone Personalizado)
st.set_page_config(
    page_title="SolarX - Gestão de Orçamentos", 
    layout="wide", 
    page_icon="icon_png.png"
)

# CONEXÃO COM O SUPABASE
SUPABASE_URL = "https://oqmvvomjbvfdjjgvyleb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9xbXZ2b21qYnZmZGpqZ3Z5bGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk2NDE4OTgsImV4cCI6MjEwNTIxNzg5OH0.vlxe1shu0zgM0tXAnKS0aynIuoQsjXX32Ny_lbLBicc"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CONSTANTES DE NEGÓCIO
IVA = Decimal("0.23")
MARGEM_EQUIP = Decimal("0.15")
MARGEM_INSTALACAO = Decimal("0.20")
START_PROPOSAL = 145
START_CLIENT = 16

# FUNÇÕES AUXILIARES DE CÁLCULO
def money(v):
    d = Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{d:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def sale_price(cost, margin=MARGEM_EQUIP):
    cost_dec = Decimal(str(cost or 0))
    return (cost_dec * (Decimal("1") + margin)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

# DADOS SUPABASE
def get_clients():
    res = supabase.table("clients").select("*").order("number").execute()
    return res.data or []

def get_products():
    res = supabase.table("products").select("*").order("description").execute()
    return res.data or []

def get_next_proposal():
    res = supabase.table("quotes").select("proposal").order("proposal", desc=True).limit(1).execute()
    if res.data and res.data[0]["proposal"]:
        return max(START_PROPOSAL, int(res.data[0]["proposal"]) + 1)
    return START_PROPOSAL

def get_next_client_number():
    res = supabase.table("clients").select("number").order("number", desc=True).limit(1).execute()
    if res.data and res.data[0]["number"]:
        return max(START_CLIENT, int(res.data[0]["number"]) + 1)
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

# GERAÇÃO DE PDF
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

def generate_pdf_buffer(client, items, discount, installation_cost, notes, proposal):
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
    draw_text(c, *PDF_POS["prepared_by"], "Alisson Monteiro", 8, False)

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

    inst_sale = (installation_cost * (Decimal("1") + MARGEM_INSTALACAO)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    taxable_global = max(Decimal("0"), subtotal_items + inst_sale - discount)
    iva_global = (taxable_global * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total_global = taxable_global + iva_global

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

# --- EXIBIÇÃO DO BANNER DA MARCA NO TOPO DA APLICAÇÃO ---
base_dir = os.path.dirname(os.path.abspath(__file__))
banner_path = os.path.join(base_dir, "banner_solarx.png")
if os.path.exists(banner_path):
    st.image(banner_path, use_container_width=True)
else:
    st.title("☀️ SolarX - Gestão de Orçamentos")

if not os.path.exists(os.path.join(base_dir, "BASE_Orçamento_SOLARX_00_A.jpg")):
    st.warning("⚠️ Imagem de fundo do orçamento PDF não encontrada no repositório.")

tab_quote, tab_clients, tab_products, tab_history = st.tabs([
    "📋 Novo Orçamento", "👥 Clientes", "📦 Equipamentos", "📂 Histórico na Nuvem"
])

# TAB 1: NOVO ORÇAMENTO
with tab_quote:
    st.subheader("1. Dados Gerais")
    col1, col2 = st.columns([1, 3])
    
    clients_list = get_clients()
    client_options = {f"{c['number']:04d} - {c['name']}": c for c in clients_list}
    
    with col1:
        proposal_num = st.number_input("Proposta Nº", value=get_next_proposal(), step=1)
    with col2:
        selected_client_str = st.selectbox("Selecione o Cliente", options=[""] + list(client_options.keys()))
        selected_client = client_options.get(selected_client_str)

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
            st.markdown(f"<div style='padding: 8px; background-color: #1e293b; border-radius: 4px; border: 1px solid #334155; text-align: right; font-weight: bold; color: #4ade80;'>{money(total_line_dec)} €</div>", unsafe_allow_html=True)
            
        if prod and qty > 0 and price_dec > 0:
            items_data.append({
                "ref": prod.get("ref", ""),
                "description": prod["description"],
                "qty": qty_dec,
                "unit": prod.get("unit", "UN"),
                "unit_price": price_dec,
                "line_total": total_line_dec
            })

    st.subheader("3. Valores Finais e Observações")
    c_inst, c_disc, c_obs = st.columns([1.5, 1.5, 3])
    
    with c_inst:
        inst_cost_in = st.number_input("Instalação (€ Custo)", min_value=0.0, value=0.0, step=10.0)
    with c_disc:
        discount_in = st.number_input("Desconto €", min_value=0.0, value=0.0, step=5.0)
    with c_obs:
        notes_in = st.text_input("Observações", value="Instalação INCLUIDA")

    inst_cost_dec = Decimal(str(inst_cost_in))
    discount_dec = Decimal(str(discount_in))

    subtotal_items = sum((it["line_total"] for it in items_data), Decimal("0"))
    taxable_equip = max(Decimal("0"), subtotal_items - discount_dec)
    total_equip = taxable_equip + (taxable_equip * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    inst_sale = (inst_cost_dec * (Decimal("1") + MARGEM_INSTALACAO)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    taxable_global = max(Decimal("0"), subtotal_items + inst_sale - discount_dec)
    total_global = taxable_global + (taxable_global * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    st.markdown("---")
    st.markdown(f"### 💰 **Total Equipamentos (c/ IVA 23%):** `{money(total_equip)} €` | 🚀 **TOTAL GERAL PROPOSTA:** `{money(total_global)} €`")

    if st.button("💾 Salvar no Supabase e Gerar PDF", type="primary"):
        if not selected_client:
            st.error("Por favor, selecione um cliente.")
        elif not items_data:
            st.error("Selecione pelo menos 1 equipamento com quantidade e valor superiores a 0.")
        else:
            try:
                q_res = supabase.table("quotes").insert({
                    "proposal": int(proposal_num),
                    "client_id": selected_client["id"],
                    "created_at": datetime.now().isoformat(),
                    "discount": float(discount_dec),
                    "installation_cost": float(inst_cost_dec),
                    "notes": notes_in,
                    "total": float(total_global)
                }).execute()
                
                qid = q_res.data[0]["id"]

                items_payload = [{
                    "quote_id": qid,
                    "ref": it["ref"],
                    "description": it["description"],
                    "qty": float(it["qty"]),
                    "unit": it["unit"],
                    "unit_price": float(it["unit_price"]),
                    "line_total": float(it["line_total"])
                } for it in items_data]
                
                supabase.table("quote_items").insert(items_payload).execute()

                pdf_buf = generate_pdf_buffer(selected_client, items_data, discount_dec, inst_cost_dec, notes_in, proposal_num)
                
                st.success("Orçamento gravado com sucesso no Supabase!")
                st.download_button(
                    label="📄 Descarregar Proposta em PDF",
                    data=pdf_buf,
                    file_name=f"Orcamento_{proposal_num}_{selected_client['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Erro ao gravar orçamento: {e}")

# TAB 2: CLIENTES
with tab_clients:
    st.subheader("Gerenciar e Editar Clientes")
    clients_df = get_clients()
    if clients_df:
        edited_clients = st.data_editor(clients_df, key="clients_editor", use_container_width=True, num_rows="dynamic")
        if st.button("💾 Salvar Alterações de Clientes"):
            try:
                for row in edited_clients:
                    if "id" in row and row["id"] is not None:
                        supabase.table("clients").update({
                            "name": row.get("name"),
                            "contact": row.get("contact"),
                            "nif": row.get("nif"),
                            "address": row.get("address"),
                            "postal": row.get("postal"),
                            "phone": row.get("phone"),
                            "email": row.get("email")
                        }).eq("id", row["id"]).execute()
                    else:
                        if row.get("name"):
                            num = get_next_client_number()
                            supabase.table("clients").insert({
                                "number": num,
                                "name": row.get("name"),
                                "contact": row.get("contact"),
                                "nif": row.get("nif"),
                                "address": row.get("address"),
                                "postal": row.get("postal"),
                                "phone": row.get("phone"),
                                "email": row.get("email")
                            }).execute()
                st.success("Dados dos clientes atualizados com sucesso na nuvem!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar clientes: {e}")

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
with tab_products:
    st.subheader("Gerenciar e Editar Equipamentos")
    prods_df = get_products()
    if prods_df:
        edited_prods = st.data_editor(prods_df, key="prods_editor", use_container_width=True, num_rows="dynamic")
        if st.button("💾 Salvar Alterações de Equipamentos"):
            try:
                for row in edited_prods:
                    if "id" in row and row["id"] is not None:
                        supabase.table("products").update({
                            "ref": row.get("ref"),
                            "description": row.get("description"),
                            "cost": float(row.get("cost", 0)),
                            "margin": float(row.get("margin", 0.15)),
                            "unit": row.get("unit", "UN")
                        }).eq("id", row["id"]).execute()
                    else:
                        if row.get("description"):
                            supabase.table("products").insert({
                                "ref": row.get("ref"),
                                "description": row.get("description"),
                                "cost": float(row.get("cost", 0)),
                                "margin": float(row.get("margin", 0.15)),
                                "unit": row.get("unit", "UN")
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

            venda_sugerida = sale_price(p_cost, Decimal(str(p_margin)))
            st.info(f"💡 Preço de Venda Calculado (+{p_margin*100:.0f}%): **{money(venda_sugerida)} €**")

            if st.form_submit_button("Guardar Equipamento"):
                if not p_desc:
                    st.error("Descrição é obrigatória!")
                else:
                    supabase.table("products").insert({
                        "ref": p_ref,
                        "description": p_desc,
                        "cost": float(p_cost),
                        "margin": float(p_margin),
                        "unit": p_unit
                    }).execute()
                    st.success("Equipamento cadastrado com sucesso!")
                    st.rerun()

# TAB 4: HISTÓRICO
with tab_history:
    st.subheader("Orçamentos Salvos no Supabase")
    quotes_res = supabase.table("quotes").select("id, proposal, created_at, discount, installation_cost, notes, total, clients(name)").order("created_at", desc=True).execute()
    if quotes_res.data:
        st.dataframe(quotes_res.data, use_container_width=True)
