import os
import io
import base64
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

# SOLARX ENERGY — Revisão premium do design aprovado; não modifica Supabase ou PDFs.
st.markdown("""
<style>
/* SOLARX ENERGY PREMIUM • revisão visual 02 • CSS isolado da lógica */
:root{--energy-a:#ff8b31;--energy-b:#ff246a;--sx-bg:#090d18;--sx-panel:#151a2b;--sx-edge:rgba(215,227,255,.12);--sx-muted:#9ea7bb;}
html,body,[data-testid="stAppViewContainer"],.stApp{color:#f7f8fc!important;font-family:Inter,"SF Pro Display",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif!important;}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse 65% 52% at 100% -18%,rgba(255,80,120,.11),transparent 73%),radial-gradient(ellipse 55% 60% at -13% 105%,rgba(255,130,39,.06),transparent 72%),#090d18!important;}
[data-testid="stHeader"]{background:rgba(9,13,24,.82)!important;backdrop-filter:blur(15px);-webkit-backdrop-filter:blur(15px);border-bottom:1px solid rgba(255,255,255,.03);}
.block-container{max-width:1570px!important;padding-top:4.3rem!important;padding-bottom:5rem!important;padding-left:2.2rem!important;padding-right:2.2rem!important;}
/* Barra Energy abaixo dos controles hospedados pelo Streamlit */
.sx-topline{height:10px;border-radius:100px;margin:6px 0 2.35rem;background:linear-gradient(92deg,#ff286e 0%,#ff5c48 55%,#ffa51e 100%);box-shadow:0 5px 24px rgba(255,53,110,.20),0 1px 0 rgba(255,255,255,.18) inset;}
/* Navegação lateral refinada, sem duplicar os controles nativos do radio */
[data-testid="stSidebar"]{background:linear-gradient(163deg,#171b2e 0%,#121624 56%,#0c101d 100%)!important;border-right:1px solid rgba(223,231,255,.11)!important;}
[data-testid="stSidebar"]>div:first-child{padding:1.6rem 1.05rem 1rem!important;}
[data-testid="stSidebar"] [data-testid="stImage"]{max-width:100%;padding:1.05rem .25rem 1.1rem;}
[data-testid="stSidebar"] [role="radiogroup"]{gap:.40rem!important;}
[data-testid="stSidebar"] [role="radiogroup"] label{position:relative;display:flex!important;align-items:center!important;gap:.8rem!important;min-height:47px;padding:10px 13px!important;background:transparent!important;border:1px solid transparent!important;border-radius:13px!important;cursor:pointer;transition:background .16s,border-color .16s,transform .16s;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:rgba(255,255,255,.055)!important;transform:translateX(2px);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked),[data-testid="stSidebar"] [role="radiogroup"] label:has([aria-checked="true"]){background:linear-gradient(102deg,#ff9230,#ff246a)!important;border-color:rgba(255,208,192,.28)!important;box-shadow:0 7px 21px rgba(255,48,108,.16);}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{color:#fff!important;font-weight:690!important;}
[data-testid="stSidebar"] [role="radiogroup"] label p{color:#e2e5f1!important;font-size:.88rem!important;font-weight:550!important;line-height:1.3!important;margin:0!important;}
/* O círculo nativo permanece acessível mas invisível; o ícone passa a indicar a página */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;opacity:0!important;pointer-events:none!important;}
[data-testid="stSidebar"] [role="radiogroup"] label::before{content:"";flex:0 0 19px;width:19px;height:19px;background-size:contain;background-position:center;background-repeat:no-repeat;opacity:.99;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(1)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(1) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJtMyAxMCA5LTcgOSA3djEwYTEgMSAwIDAgMS0xIDFoLTV2LTdIOXY3SDRhMSAxIDAgMCAxLTEtMXoiLz48L3N2Zz4=")!important;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(2)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(2) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNNyAyaDlsNSA1djE0YTEgMSAwIDAgMS0xIDFIN2ExIDEgMCAwIDEtMS0xVjNhMSAxIDAgMCAxIDEtMVoiLz48cGF0aCBkPSJNMTYgMnY2aDVNOSAxMmg4bS04IDRoOCIvPjwvc3ZnPg==")!important;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(3)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(3) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMTYgMjF2LTJhNCA0IDAgMCAwLTQtNEg2YTQgNCAwIDAgMC00IDR2MiIvPjxjaXJjbGUgY3g9IjkiIGN5PSI3IiByPSI0Ii8+PHBhdGggZD0iTTIyIDIxdi0yYTQgNCAwIDAgMC0zLTMuODdNMTYgMy4xM2E0IDQgMCAwIDEgMCA3Ljc1Ii8+PC9zdmc+")!important;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(4)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(4) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJtMTIgMyA5IDUtOSA1LTktNSA5LTVaIi8+PHBhdGggZD0iTTMgOHY5bDkgNSA5LTVWOE0xMiAxM3Y5Ii8+PC9zdmc+")!important;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(5)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(5) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48Y2lyY2xlIGN4PSIxMiIgY3k9IjciIHI9IjQiLz48cGF0aCBkPSJNNSAyMXYtM2E3IDcgMCAwIDEgMTQgMHYzIi8+PC9zdmc+")!important;}
[data-testid="stSidebar"] [role="radiogroup"] > label:nth-of-type(6)::before,
[data-testid="stSidebar"] [role="radiogroup"] > div:nth-of-type(6) label::before{background-image:url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSJub25lIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS13aWR0aD0iMS43NSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cGF0aCBkPSJNMjAgMTYuNkE0LjcgNC43IDAgMCAwIDE3IDhhNi44IDYuOCAwIDAgMC0xMyAyQTQuNSA0LjUgMCAwIDAgNSAxOWgxM2EzLjUgMy41IDAgMCAwIDItMi40WiIvPjwvc3ZnPg==")!important;}
.sx-sidebar-footer{padding:1.2rem .45rem 0;border-top:1px solid rgba(255,255,255,.07);margin-top:1.2rem;}
.sx-sidebar-mini{color:#8e98ad;font-size:.72rem;letter-spacing:.09em;text-transform:uppercase;font-weight:650;}
.sx-sidebar-health{display:flex;align-items:center;gap:8px;margin-top:9px;font-size:.77rem;color:#9ba7bb;}
.sx-sidebar-health i{display:inline-block;border-radius:50%;width:7px;height:7px;background:#38d7a0;box-shadow:0 0 9px rgba(56,215,160,.5);}
/* Controles e formulários */
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:12px!important;min-height:43px;transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease!important;background:rgba(255,255,255,.04)!important;border:1px solid rgba(217,227,255,.15)!important;color:#f8f8fd!important;}
.stButton>button:hover,.stDownloadButton>button:hover,.stFormSubmitButton>button:hover{transform:translateY(-1px);border-color:rgba(255,128,89,.48)!important;box-shadow:0 6px 20px rgba(0,0,0,.14)!important;}
.stButton>button[kind="primary"],.stFormSubmitButton>button,.stDownloadButton>button[kind="primary"]{background:linear-gradient(105deg,#ff9132 0%,#ff5849 48%,#ff276f 100%)!important;border-color:rgba(255,215,211,.22)!important;color:#fff!important;font-weight:680!important;box-shadow:0 8px 22px rgba(255,45,104,.20)!important;}
.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button:hover,.stDownloadButton>button[kind="primary"]:hover{box-shadow:0 10px 28px rgba(255,45,104,.32)!important;}
.stButton>button[kind="primary"] p,.stFormSubmitButton>button p,.stDownloadButton>button[kind="primary"] p{color:white!important;font-weight:690!important;}
.stButton>button:disabled,.stFormSubmitButton>button:disabled{opacity:.44!important;transform:none!important;}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stTextArea"] textarea,[data-baseweb="select"]>div{background:rgba(20,25,42,.90)!important;color:#f6f8ff!important;border-color:rgba(219,230,255,.15)!important;border-radius:11px!important;}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#ff697f!important;box-shadow:0 0 0 1px rgba(255,83,110,.2)!important;}
[data-testid="stWidgetLabel"] p,[data-testid="stMarkdownContainer"] label{color:#cbd1df!important;font-size:.87rem!important;}
[data-testid="stVerticalBlockBorderWrapper"]>div{background:linear-gradient(148deg,rgba(30,36,58,.72),rgba(18,23,38,.78))!important;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid var(--sx-edge)!important;border-radius:18px!important;}
[data-testid="stExpander"]{border:1px solid var(--sx-edge)!important;background:rgba(23,28,45,.72)!important;border-radius:16px!important;overflow:hidden;}
[data-testid="stExpander"] summary{min-height:55px;}
[data-testid="stDataFrame"],[data-testid="stDataEditor"]{border:1px solid var(--sx-edge)!important;border-radius:15px!important;overflow:hidden;}
[data-testid="stDataEditor"] [role="columnheader"]{background:rgba(255,255,255,.045)!important;color:#e7eaf3!important;}
[data-testid="stMetric"]{background:linear-gradient(150deg,rgba(32,38,61,.82),rgba(19,24,40,.82));padding:18px;border:1px solid rgba(221,228,255,.1);border-radius:17px;min-height:114px;}
[data-testid="stMetricValue"]{color:#fff!important;letter-spacing:-.035em;}
[data-testid="stAlert"]{border-radius:13px!important;}
[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li{line-height:1.52;}
h1,h2,h3{letter-spacing:-.027em!important;color:#fafaff!important;}
h1{font-size:2rem!important;}h2{font-size:1.4rem!important;}h3{font-size:1.12rem!important;}
hr{border-color:rgba(231,239,255,.08)!important;}
.sx-heading{font-size:1.9rem;font-weight:750;letter-spacing:-.033em;color:#fff;margin:0 0 .35rem;}
.sx-subtitle{color:#a5afc3;font-size:.91rem;margin-bottom:1.7rem;}
.sx-section{color:#f3f5fb;font-weight:710;font-size:1.08rem;margin:1.45rem 0 1.05rem;letter-spacing:-.01em;}
.sx-mini-note{font-size:.78rem;color:#a8b0c1;}
.sx-glow{color:#ffbe73;}
.sx-tag{display:inline-flex;align-items:center;padding:5px 10px;border-radius:100px;font-size:.70rem;font-weight:700;background:rgba(61,204,138,.14);color:#4de2a7;}
.sx-tag.warn{background:rgba(255,171,54,.13);color:#ffb74b;}.sx-tag.bad{background:rgba(249,66,100,.15);color:#ff7b94;}
/* KPI: respiro horizontal e vertical, ícones line brancos com brilho subtil */
[data-testid="stHorizontalBlock"]:has(.sx-kpi){column-gap:1.55rem!important;margin-bottom:1.35rem!important;align-items:stretch;}
[data-testid="stHorizontalBlock"]:has(.sx-kpi)>[data-testid="stColumn"]{min-width:0!important;}
.sx-kpi{position:relative;min-height:171px;background:linear-gradient(150deg,rgba(30,37,60,.91),rgba(17,22,39,.94));border:1px solid rgba(221,233,255,.12);border-radius:20px;padding:20px 21px 17px;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);overflow:hidden;transition:transform .17s,border-color .17s;}
.sx-kpi:hover{transform:translateY(-3px);border-color:rgba(255,158,128,.25);}
.sx-kpi::before{content:"";height:2px;position:absolute;left:20px;right:20px;bottom:0;background:linear-gradient(90deg,transparent,var(--kpi-accent),transparent);opacity:.58;}
.sx-kpi::after{content:"";position:absolute;width:152px;height:145px;background:radial-gradient(circle at center,var(--kpi-halo),transparent 71%);right:-50px;top:-56px;pointer-events:none;}
.sx-kpi-head{display:flex;justify-content:space-between;align-items:center;gap:1rem;margin-bottom:24px;}
.sx-kpi-name{color:#c8cfdf;font-size:.82rem;font-weight:620;line-height:1.35;}
.sx-icon-pill{display:inline-flex;justify-content:center;align-items:center;flex-shrink:0;width:40px;height:40px;border-radius:13px;background:var(--kpi-halo);border:1px solid rgba(255,255,255,.09);}
.sx-kpi-icon{width:21px;height:21px;stroke:#fff;stroke-width:1.75;fill:none;stroke-linecap:round;stroke-linejoin:round;}
.sx-kpi-value{font-size:1.66rem;color:#fff;letter-spacing:-.036em;font-weight:750;line-height:1.12;white-space:normal;overflow-wrap:anywhere;}
.sx-kpi-sub{font-size:.76rem;color:#9ca7bb;margin-top:11px;line-height:1.4;}
/* Gráficos SVG baseados nos dados efetivos da aplicação */
[data-testid="stHorizontalBlock"]:has(.sx-chart-card){column-gap:1.45rem!important;align-items:stretch;}
.sx-chart-card{position:relative;min-height:360px;padding:21px 22px 15px;border-radius:20px;overflow:hidden;border:1px solid rgba(216,229,255,.13);background:linear-gradient(147deg,rgba(31,38,61,.87),rgba(16,21,36,.96));box-shadow:0 12px 32px rgba(0,0,0,.12);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);}
.sx-chart-card:before{content:"";position:absolute;top:0;right:-60px;width:260px;height:160px;pointer-events:none;background:radial-gradient(circle,rgba(255,120,68,.10),transparent 72%);}
.sx-chart-head{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;margin-bottom:8px;position:relative;}
.sx-chart-heading{font-size:.95rem;color:#fff;font-weight:690;}
.sx-chart-caption{font-size:.75rem;color:#9da8bd;margin-top:5px;}
.sx-chart-accent{height:5px;width:38px;background:linear-gradient(90deg,#ff9333,#ff2874);border-radius:99px;margin-top:7px;box-shadow:0 0 16px rgba(255,68,99,.27);}
.sx-chart-body svg{width:100%;height:auto;display:block;max-height:285px;overflow:visible;}
.sx-chart-grid{stroke:rgba(208,220,251,.095);stroke-width:1;}
.sx-chart-axis{fill:#8490a7;font-size:13px;font-family:Inter,-apple-system,sans-serif;}
.sx-chart-area{opacity:.88;}
.sx-chart-note{color:#8e9bb0;font-size:.72rem;line-height:1.45;margin-top:5px;}
.sx-chart-legend{display:flex;align-items:center;gap:7px;color:#d7dce9;font-size:.74rem;white-space:nowrap;}
.sx-legend-dot{display:inline-block;width:8px;height:8px;flex-shrink:0;border-radius:50%;background:var(--legend);box-shadow:0 0 9px var(--legend);}
.sx-donut-flex{display:flex;align-items:center;justify-content:center;gap:18px;min-height:263px;}
.sx-donut-flex svg{width:54%;max-width:235px;flex:0 0 52%;}
.sx-donut-legend{display:flex;flex-direction:column;gap:12px;flex:1;min-width:0;}
.sx-donut-item{display:flex;align-items:center;justify-content:space-between;gap:8px;color:#dce2ee;font-size:.80rem;}
.sx-donut-label{display:flex;align-items:center;gap:8px;min-width:0;}
.sx-donut-count{font-size:.9rem;color:#f5f7ff;font-weight:750;}
.sx-donut-center{fill:#fff;font-size:37px;font-weight:770;text-anchor:middle;letter-spacing:-1px;}
.sx-donut-center-caption{fill:#9aa8c0;font-size:12px;text-anchor:middle;}
/* Cards de histórico em grelha (resumo informativo acima dos detalhes) */
.sx-history-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:14px 0 22px;}
.sx-history-card{background:linear-gradient(145deg,rgba(30,37,60,.88),rgba(18,23,40,.94));border:1px solid rgba(220,231,255,.12);padding:17px 18px;border-radius:17px;min-width:0;}
.sx-history-card-top{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;}
.sx-history-id{font-size:.92rem;font-weight:720;color:#fff;}
.sx-history-client{font-size:.77rem;color:#a6b0c4;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.sx-history-value{font-size:1.06rem;font-weight:760;color:#fff;white-space:nowrap;}
.sx-history-footer{display:flex;align-items:center;justify-content:space-between;margin-top:17px;gap:10px;}
.sx-history-date{font-size:.72rem;color:#8d9aaf;}
.sx-soft-card{padding:15px 18px;border-radius:16px;border:1px solid rgba(255,255,255,.10);background:rgba(255,255,255,.027);}

.sx-kpi-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin-top:6px;}
.sx-kpi-grid .sx-kpi{height:100%;margin:0!important;}
.sx-kpi.featured{background:linear-gradient(145deg,rgba(255,145,50,.22),rgba(255,39,111,.18) 74%),linear-gradient(145deg,rgba(31,38,61,.90),rgba(16,21,36,.96));border-color:rgba(255,192,148,.22);box-shadow:0 18px 40px rgba(255,78,101,.18),inset 0 1px 0 rgba(255,255,255,.06);}
.sx-kpi.featured:before{background:radial-gradient(circle at 30% 30%,rgba(255,188,99,.30),transparent 55%);opacity:1;}
.sx-kpi.featured .sx-kpi-sub{color:#fff0dc;opacity:.95;}
.sx-kpi.featured .sx-kpi-value{font-size:1.95rem;}
.sx-flow-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:4px;}
.sx-flow-tile{border-radius:18px;padding:17px 18px;border:1px solid rgba(216,229,255,.12);background:linear-gradient(145deg,rgba(27,34,57,.82),rgba(13,18,33,.94));min-height:120px;box-shadow:0 10px 30px rgba(0,0,0,.10);}
.sx-flow-name{font-size:.78rem;color:#aab4c6;font-weight:600;line-height:1.45;}
.sx-flow-value{font-size:1.5rem;font-weight:760;color:#fff;margin-top:18px;letter-spacing:-.03em;}
.sx-flow-sub{font-size:.73rem;color:#8e9cb4;line-height:1.45;margin-top:10px;}
.sx-auth-brand{display:flex;justify-content:center;align-items:center;margin:0 auto 1rem;}
.sx-auth-brand img{display:block;width:min(100%,270px);height:auto;margin:0 auto;object-fit:contain;}
.sx-auth-shell{display:flex;flex-direction:column;align-items:center;justify-content:center;}
.sx-auth-card{width:min(100%,460px);margin:0 auto;}
.sx-auth-footer{max-width:460px;margin-left:auto;margin-right:auto;}
/* Login premium */
.sx-auth-label{font-size:1.30rem;font-weight:700;text-align:center;color:#fff;margin:8px 0 3px;letter-spacing:-.02em;}
.sx-auth-desc{text-align:center;color:#a0abc1;font-size:.87rem;margin:0 0 24px;}
.sx-auth-footer{text-align:center;color:#8793a8;font-size:.74rem;margin-top:20px;}
@media(max-width:1000px){.block-container{padding-left:1.35rem!important;padding-right:1.35rem!important;}.sx-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;}.sx-flow-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;}.sx-kpi{padding:15px 14px;min-height:150px}.sx-kpi-value{font-size:1.36rem}.sx-kpi-head{margin-bottom:16px}}
@media(max-width:768px){.block-container{padding:3.8rem .8rem 4.5rem!important;}.sx-topline{height:8px;margin:4px 0 1.55rem;}.sx-heading{font-size:1.55rem;}.sx-subtitle{font-size:.82rem;margin-bottom:1.25rem;}.sx-chart-card{padding:16px 13px;min-height:0;}.sx-chart-body svg{min-height:185px;}.sx-history-grid{grid-template-columns:1fr;gap:10px;}.sx-kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;}.sx-kpi-grid .sx-kpi.featured{grid-column:1/-1;min-height:150px;}.sx-kpi-grid .sx-kpi{min-height:138px;padding:15px 14px;}.sx-kpi-name{font-size:.73rem}.sx-kpi-value{font-size:1.22rem}.sx-kpi.featured .sx-kpi-value{font-size:1.85rem}.sx-kpi-head{margin-bottom:12px}.sx-icon-pill{width:34px;height:34px}.sx-donut-flex{gap:8px;flex-direction:column;align-items:center;}.sx-donut-flex svg{width:72%;max-width:220px;flex-basis:auto;}.sx-donut-legend{width:100%;}.sx-donut-item{font-size:.72rem;}[data-testid="stSidebar"]{max-width:270px!important;}.sx-chart-body{overflow-x:auto;overflow-y:hidden;scrollbar-width:thin;scrollbar-color:rgba(255,160,97,.36) transparent;}.sx-chart-body svg{width:560px!important;min-width:560px!important;max-height:none!important;min-height:0!important;}[data-testid="stHorizontalBlock"]:has(.sx-chart-card){display:block!important;}[data-testid="stHorizontalBlock"]:has(.sx-chart-card)>div{width:100%!important;flex:1 1 100%!important;margin-bottom:14px;}.sx-flow-grid{grid-template-columns:1fr;gap:12px;}.sx-auth-brand img{width:min(100%,230px);}.sx-auth-card{width:100%;}}
@media(max-width:520px){.sx-kpi-grid{grid-template-columns:1fr;}.sx-kpi-grid .sx-kpi.featured{grid-column:auto;}.sx-kpi{min-height:132px;}.sx-auth-label{font-size:1.18rem;}.sx-auth-desc{font-size:.82rem;}.sx-auth-brand{margin-bottom:.7rem;}}
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

    if not st.session_state.get("password_correct", False):
        st.markdown('<div class="sx-topline"></div>', unsafe_allow_html=True)
        _, auth_center, _ = st.columns([1.0, 1.18, 1.0], gap="large")
        with auth_center:
            st.markdown('<div class="sx-auth-shell">', unsafe_allow_html=True)
            auth_logo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo_solarx_mono.png")
            if os.path.isfile(auth_logo):
                st.markdown(f'<div class="sx-auth-brand"><img src="{file_to_data_uri(auth_logo)}" alt="SolarX"></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="sx-auth-brand"><h2 style="margin:0;color:white;">SOLAR X</h2></div>', unsafe_allow_html=True)
            st.markdown('<div class="sx-auth-card">', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="sx-auth-label">Bem-vindo à SolarX</div>', unsafe_allow_html=True)
                st.markdown('<div class="sx-auth-desc">Gestão comercial e financeira · Acesso reservado</div>', unsafe_allow_html=True)
                with st.form("login_form"):
                    st.text_input("Palavra-passe", type="password", key="password_input", placeholder="Introduza a palavra-passe")
                    submitted = st.form_submit_button("Entrar na SolarX", use_container_width=True, type="primary")
                if submitted:
                    password_entered()
                    if st.session_state.get("password_correct"):
                        st.rerun()
                if st.session_state.get("password_correct") is False:
                    st.error("Palavra-passe incorreta. Tente novamente.")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="sx-auth-footer">SOLARX · Energia inteligente. Futuro sem limites.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
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

def file_to_data_uri(path):
    try:
        mime = "image/png" if str(path).lower().endswith(".png") else "image/jpeg"
        with open(path, "rb") as fh:
            encoded = base64.b64encode(fh.read()).decode("ascii")
        return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""


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


def kpi_card_html(label, value, detail, icon="sales", tone="", featured=False):
    palettes = {
        "approved": ("#32dca1", "rgba(50,220,161,.14)"),
        "clients": ("#62aafc", "rgba(98,170,252,.14)"),
        "solar": ("#ffae48", "rgba(255,174,72,.16)"),
        "sales": ("#ff8752", "rgba(255,135,82,.15)"),
        "tax": ("#bb91f7", "rgba(187,145,247,.15)"),
        "profit": ("#44dbaa", "rgba(68,219,170,.15)"),
    }
    accent, halo = palettes.get(icon, palettes["sales"])
    svg = f'<svg viewBox="0 0 24 24" class="sx-kpi-icon" aria-hidden="true">{ICON_SVG.get(icon, ICON_SVG["sales"])}</svg>'
    tag = (f'<span class="sx-tag {tone}">{html_escape(detail)}</span>'
           if detail.startswith(("+", "−", "-")) else f'<div class="sx-kpi-sub">{html_escape(detail)}</div>')
    classes = "sx-kpi featured" if featured else "sx-kpi"
    return (f'<article class="{classes}" style="--kpi-accent:{accent};--kpi-halo:{halo}">'
            f'<div class="sx-kpi-head"><span class="sx-kpi-name">{html_escape(label)}</span>'
            f'<span class="sx-icon-pill">{svg}</span></div>'
            f'<div class="sx-kpi-value">{html_escape(str(value))}</div>{tag}</article>')

def kpi_card(label, value, detail, icon="sales", tone="", featured=False):
    st.markdown(kpi_card_html(label, value, detail, icon=icon, tone=tone, featured=featured), unsafe_allow_html=True)

def render_kpi_grid(cards):
    st.markdown('<div class="sx-kpi-grid">' + ''.join(cards) + '</div>', unsafe_allow_html=True)

def flow_metric_html(label, value, detail=""):
    return (f'<article class="sx-flow-tile">'
            f'<div class="sx-flow-name">{html_escape(label)}</div>'
            f'<div class="sx-flow-value">{html_escape(str(value))}</div>'
            f'<div class="sx-flow-sub">{html_escape(detail)}</div></article>')

def render_flow_grid(items):
    st.markdown('<div class="sx-flow-grid">' + ''.join(items) + '</div>', unsafe_allow_html=True)


def sales_trend_card(months, revenue_by_month):
    """Gráfico SVG responsivo e legível. Dados reais; sem séries fictícias."""
    from math import ceil, log10
    values = [max(0.0, float(revenue_by_month.get(m, 0))) for m in months]
    if not months:
        months, values = [datetime.now().strftime("%Y-%m")], [0.0]
    width, height = 820, 300
    left, right, top, bottom = 62, 26, 22, 50
    inner_w = width - left - right
    baseline = height - bottom
    inner_h = baseline - top
    data_max = max(values) if values else 0
    # Escala arredondada: os intervalos mantêm-se legíveis mesmo com um único mês.
    if data_max <= 0:
        step = 1.0
    else:
        raw_step = data_max / 5
        base = 10 ** int(log10(raw_step))
        step = next((k * base for k in (1, 2, 2.5, 5, 10) if k * base >= raw_step), 10 * base)
    ceiling = step * 5
    x = [left + ((idx + .5) / len(values) * inner_w) for idx in range(len(values))]
    y = [baseline - (v / ceiling * inner_h) for v in values]
    pts = list(zip(x, y))
    def curve(points):
        if not points: return ""
        if len(points) == 1:
            return f"M {points[0][0]:.2f} {points[0][1]:.2f}"
        path = f"M {points[0][0]:.2f} {points[0][1]:.2f}"
        for i in range(len(points) - 1):
            p0 = points[max(0, i-1)]
            p1 = points[i]
            p2 = points[i+1]
            p3 = points[min(len(points)-1, i+2)]
            # Catmull–Rom -> curvas cúbicas suaves, com tensão moderada.
            c1x = p1[0]+(p2[0]-p0[0])/6
            c1y = p1[1]+(p2[1]-p0[1])/6
            c2x = p2[0]-(p3[0]-p1[0])/6
            c2y = p2[1]-(p3[1]-p1[1])/6
            # Não deixar a interpolação ultrapassar os valores reais entre dois pontos.
            lo, hi = sorted((p1[1], p2[1]))
            c1y = min(hi, max(lo, c1y))
            c2y = min(hi, max(lo, c2y))
            path += f" C {c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {p2[0]:.2f},{p2[1]:.2f}"
        return path
    line = curve(pts)
    if len(pts) == 1:
        line += f" L {width-right:.2f},{pts[0][1]:.2f}"
    area = f"{line} L {width-right:.2f},{baseline:.2f} L {left:.2f},{baseline:.2f} Z"
    def euro_axis(v):
        if v >= 1000:
            return f"{v/1000:.1f}k" if v % 1000 else f"{v/1000:.0f}k"
        return f"{v:g}"
    lines = []
    for i in range(6):
        yy = baseline-i*inner_h/5
        lines.append(f'<line class="sx-chart-grid" x1="{left}" y1="{yy:.2f}" x2="{width-right}" y2="{yy:.2f}"/>')
        lines.append(f'<text class="sx-chart-axis" x="{left-12}" y="{yy+4:.2f}" text-anchor="end">{euro_axis(step*i)} €</text>')
    labels = {'01':'jan','02':'fev','03':'mar','04':'abr','05':'mai','06':'jun','07':'jul','08':'ago','09':'set','10':'out','11':'nov','12':'dez'}
    for xx,m in zip(x,months):
        short=labels.get(m[-2:],m[-2:])
        lines.append(f'<text class="sx-chart-axis" x="{xx:.2f}" y="{baseline+27}" text-anchor="middle">{short}</text>')
    months_markup = ''.join(lines)
    points_markup=''.join(
        f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="5.3" fill="#ffb35d" stroke="#151a2c" stroke-width="2.5"><title>{html_escape(m)}: {html_escape(money_eur(v))}</title></circle>'
        for xx,yy,m,v in zip(x,y,months,values)
    )
    selected_total = money_eur(sum(values))
    html = f'''<section class="sx-chart-card" aria-label="Evolução das vendas aprovadas sem IVA">
    <div class="sx-chart-head"><div><div class="sx-chart-heading">Evolução de vendas</div>
    <div class="sx-chart-caption">Vendas aprovadas · sem IVA · {len(months)} meses</div></div>
    <div class="sx-chart-legend"><span class="sx-legend-dot" style="--legend:#ff9343"></span>Vendas</div></div>
    <div class="sx-chart-body"><svg viewBox="0 0 {width} {height}" role="img" aria-label="Gráfico de vendas mensais">
    <defs><linearGradient id="sxSalesFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ff9c39" stop-opacity=".48"/><stop offset="60%" stop-color="#ff4b73" stop-opacity=".14"/><stop offset="100%" stop-color="#ff3273" stop-opacity="0"/></linearGradient>
    <linearGradient id="sxSalesStroke" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#ff9e30"/><stop offset="65%" stop-color="#ff6a52"/><stop offset="100%" stop-color="#ff2c80"/></linearGradient>
    <filter id="sxSalesGlow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    {months_markup}<path class="sx-chart-area" d="{area}" fill="url(#sxSalesFill)"/><path d="{line}" stroke="url(#sxSalesStroke)" stroke-width="3.8" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#sxSalesGlow)"/>{points_markup}</svg></div>
    <div class="sx-chart-note">Total no gráfico: <strong style="color:#e8ecf7">{html_escape(selected_total)}</strong> · Passe o cursor sobre os pontos para consultar cada mês.</div>
    </section>'''
    st.markdown(html,unsafe_allow_html=True)


def status_donut_card(state_counts):
    """Donut de distribuição real dos estados, sem dados de exemplo."""
    from math import pi
    color_map = {"em_analise": "#ffbc56", "aprovado": "#3ada9d", "instalado": "#63acfb", "rejeitado": "#fe6683"}
    total = sum(int(state_counts.get(key, 0)) for key in STATUS_LABELS)
    radius, circumference = 76, 2*pi*76
    used, arcs, legend = 0.0, [], []
    for key in ("aprovado","em_analise","instalado","rejeitado"):
        count = int(state_counts.get(key, 0))
        color = color_map[key]
        portion = (count / total) if total else 0
        if count:
            dash = portion * circumference
            arcs.append(f'<circle cx="110" cy="110" r="{radius}" fill="none" stroke="{color}" stroke-width="19" stroke-linecap="round" transform="rotate(-90 110 110)" stroke-dasharray="{max(0,dash-5):.3f} {circumference:.3f}" stroke-dashoffset="{-used:.3f}"><title>{STATUS_LABELS[key]}: {count}</title></circle>')
        used += portion*circumference
        legend.append(f'<div class="sx-donut-item"><span class="sx-donut-label"><span class="sx-legend-dot" style="--legend:{color}"></span>{html_escape(STATUS_LABELS[key])}</span><span class="sx-donut-count">{count}</span></div>')
    markup=f'''<section class="sx-chart-card" aria-label="Distribuição dos estados dos projetos">
    <div class="sx-chart-head"><div><div class="sx-chart-heading">Estado dos projetos</div>
    <div class="sx-chart-caption">Distribuição de todo o histórico</div></div><div class="sx-chart-accent"></div></div>
    <div class="sx-donut-flex"><svg viewBox="0 0 220 220" role="img" aria-label="Distribuição dos {total} projetos">
      <circle cx="110" cy="110" r="{radius}" fill="none" stroke="rgba(255,255,255,.075)" stroke-width="19"/>{''.join(arcs)}
      <text class="sx-donut-center" x="110" y="108">{total}</text><text class="sx-donut-center-caption" x="110" y="130">projetos</text></svg>
    <div class="sx-donut-legend">{''.join(legend)}</div></div>
    <div class="sx-chart-note">Contagem por situação comercial; apenas aprovados e instalados entram nas vendas.</div>
    </section>'''
    st.markdown(markup,unsafe_allow_html=True)


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
    dashboard_cards = [
        kpi_card_html("Vendas aprovadas (sem IVA)", money_eur(sales_net), "Não são recebimentos", "sales", featured=True),
        kpi_card_html("Projetos aprovados", str(len(approved)), "Aprovados no período", "approved"),
        kpi_card_html("Clientes cadastrados", str(len(clients)), client_detail, "clients"),
        kpi_card_html("Potência fotovoltaica aprovada", f"{project_kwp:,.2f} kWp".replace(",","X").replace(".",",").replace("X","."), f"Instalados no período: {installed_kwp:.2f} kWp", "solar"),
        kpi_card_html("IVA das propostas aprovadas", money_eur(iva), "Estimativa; não é IVA a pagar", "tax"),
        kpi_card_html("Lucro bruto estimado", money_eur(profit) if profits else "—", (f"{n_unknown} proposta(s) sem custos históricos" if n_unknown else "Custos diretos deduzidos"), "profit"),
    ]
    render_kpi_grid(dashboard_cards)

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
    state_counts={status:sum(q.get("status", "em_analise")==status for q in quotes) for status in STATUS_LABELS}
    chart_left,chart_right=st.columns([1.68,1],gap="large")
    with chart_left:
        sales_trend_card(months,revenue_by_month)
    with chart_right:
        status_donut_card(state_counts)

    st.markdown('<div class="sx-section">Fluxo de caixa e execução</div>',unsafe_allow_html=True)
    paid=Decimal("0")
    if all_payments is not None:
        paid=sum((cents(p.get("amount")) for p in all_payments if in_period(p.get("received_at"))),Decimal("0"))
    billed=sum((cents(q.get("total")) for q in quotes if q.get("invoiced_at") and in_period(q.get("invoiced_at"))),Decimal("0"))
    open_balance=sum((max(Decimal("0"),cents(q.get("total"))-sum((cents(p.get("amount")) for p in (all_payments or []) if p.get("quote_id")==q["id"]),Decimal("0"))) for q in quotes if q.get("status") in ("aprovado","instalado")),Decimal("0"))
    render_flow_grid([
        flow_metric_html("Pagamentos registados no período", money_eur(paid) if all_payments is not None else "Indisponível", "Recebimentos efetivos já registados"),
        flow_metric_html("Orçamentos faturados no período", money_eur(billed), "Valores com fatura emitida"),
        flow_metric_html("Saldo por receber (projetos ativos)", money_eur(open_balance) if all_payments is not None else "Indisponível", "Diferença entre propostas ativas e pagamentos"),
    ])
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
    st.markdown('<div class="sx-sidebar-footer"><div class="sx-sidebar-mini">SOLARX · Energy Business</div>'
                + ('<div class="sx-sidebar-health"><i></i>Ligação financeira configurada</div>'
                   if SERVER_KEY else '<div class="sx-sidebar-health">Ligação financeira não configurada</div>')
                + '</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="sx-section">01 · Dados gerais</div>',unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 2], gap="large")
    
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

    st.markdown('<div class="sx-section">02 · Equipamentos e serviços <span class="sx-mini-note">· Margem automática 15%</span></div>',unsafe_allow_html=True)
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

    st.markdown('<div class="sx-section">03 · Instalação, IVA e condições</div>',unsafe_allow_html=True)
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

        if st.button("Salvar Alterações de Clientes", type="primary", disabled=bool(pending)):
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
            
            if st.form_submit_button("Guardar Cliente", type="primary"):
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
        if st.button("Salvar Alterações de Equipamentos", type="primary"):
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

            if st.form_submit_button("Guardar Equipamento", type="primary"):
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

        if st.button("Salvar Alterações de Utilizadores", type="primary"):
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
            if st.form_submit_button("Guardar Utilizador", type="primary"):
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
    if shown:
        # Uma grelha visual compacta; todos os formulários operacionais continuam
        # disponíveis nos expansores abaixo, sem duplicar widgets nem ações.
        gallery = []
        for item in shown[:8]:
            s = item.get("status") or "em_analise"
            cls = "sx-tag" if s in ("aprovado", "instalado") else ("sx-tag bad" if s == "rejeitado" else "sx-tag warn")
            who = html_escape(str((item.get("clients") or {}).get("name") or "Cliente desconhecido"))
            proposal_label = html_escape(str(item.get("proposal") or "—"))
            value = html_escape(money_eur(item.get("total")))
            when = html_escape(str(item.get("created_at") or "")[:10])
            gallery.append(
                '<div class="sx-history-card"><div class="sx-history-card-top">'
                f'<div><div class="sx-history-id">Proposta {proposal_label}</div><div class="sx-history-client">{who}</div></div>'
                f'<div class="sx-history-value">{value}</div></div><div class="sx-history-footer">'
                f'<span class="{cls}">{html_escape(STATUS_LABELS.get(s, "Em análise"))}</span>'
                f'<span class="sx-history-date">{when}</span></div></div>'
            )
        st.markdown('<div class="sx-section">Resumo dos orçamentos</div><div class="sx-history-grid">'
                    + ''.join(gallery) + '</div>', unsafe_allow_html=True)
        st.caption("Abra a proposta abaixo para editar, gerir pagamentos ou emitir a requisição.")
    st.markdown('<div class="sx-section">Detalhes e gestão</div>', unsafe_allow_html=True)
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
                submit_status=st.form_submit_button("Guardar estado do projeto", type="primary")
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
                invoice_submit=st.form_submit_button("Guardar faturação", type="primary")
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
                if st.button("Guardar custos / potência",type="primary",key=f"sx_cost_save_{qid}"):
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
                        paid_submit=st.form_submit_button("Registar recebimento", type="primary")
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
            if st.button("Gerar requisição PDF",type="primary",key=f"sx_req_make_{qid}"):
                if not selected_req:st.warning("Selecione pelo menos um artigo.")
                elif len(selected_req)>13:st.error("É permitido um máximo de 13 artigos.")
                else:
                    try:
                        req_buf=generate_requisition_pdf_buffer(q,selected_req,req_user)
                        st.download_button("Descarregar requisição",data=req_buf,
                            file_name=f"Requisicao_Material_Proposta_{proposal}.pdf",mime="application/pdf",
                            key=f"sx_req_dl_{qid}",type="primary")
                    except Exception as exc:st.error("Falha ao gerar PDF: "+str(exc))
