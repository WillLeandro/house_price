import html
import math
import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title='Recomendador de Imóveis Arapongas',
    page_icon='🏠',
    layout='wide',
)

# ============================================================
# SISTEMA DE DESIGN
# Identidade visual inspirada em Arapongas-PR, a "Capital Nacional
# do Móvel": tons de madeira/nogueira, tipografia com caráter de
# marcenaria, e um indicador de etapas em forma de régua/fita
# métrica -- o app "mede" se o imóvel serve pra sua vida.
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --bg: #1B140F;
        --surface: #2A2119;
        --surface-alt: #241C16;
        --border: #46392C;
        --text: #F2E8DB;
        --text-muted: #B4A18D;
        --accent: #D9A653;
        --accent-dark: #A97C36;
        --score-high: #7E9B6C;
        --score-mid: #D9A653;
        --score-low: #B2593F;
    }

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    .block-container {
        max-width: 960px;
        margin-left: auto;
        margin-right: auto;
        padding-top: 2.5rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Fraunces', serif !important;
        color: var(--text) !important;
        letter-spacing: -0.01em;
    }

    p, span, label, .stMarkdown, div {
        color: var(--text);
    }

    /* ---------- Hero / cabecalho ---------- */
    .hero-eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.4rem;
    }
    .hero-title {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 2.4rem;
        line-height: 1.15;
        color: var(--text);
        margin: 0 0 0.35rem 0;
    }
    .hero-caption {
        font-family: 'IBM Plex Sans', sans-serif;
        color: var(--text-muted);
        font-size: 0.98rem;
        margin-bottom: 1.6rem;
    }

    /* ---------- Indicador de etapas (regua/fita metrica) ---------- */
    .ruler {
        display: flex;
        align-items: flex-start;
        margin: 0.5rem 0 2.2rem 0;
    }
    .ruler-step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    .ruler-connector {
        position: absolute;
        top: 15px;
        left: -50%;
        width: 100%;
        height: 2px;
        background: var(--border);
        z-index: 0;
    }
    .ruler-connector.filled { background: var(--accent); }
    .ruler-step:first-child .ruler-connector { display: none; }
    .ruler-badge {
        position: relative;
        z-index: 1;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        margin: 0 auto 0.5rem auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        font-weight: 600;
        background: var(--surface-alt);
        border: 2px solid var(--border);
        color: var(--text-muted);
    }
    .ruler-step.done .ruler-badge {
        background: var(--accent);
        border-color: var(--accent);
        color: var(--bg);
    }
    .ruler-step.active .ruler-badge {
        background: var(--bg);
        border-color: var(--accent);
        color: var(--accent);
        box-shadow: 0 0 0 4px rgba(217, 166, 83, 0.18);
    }
    .ruler-label {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.78rem;
        color: var(--text-muted);
    }
    .ruler-step.active .ruler-label {
        color: var(--text);
        font-weight: 600;
    }

    /* ---------- Widgets nativos do Streamlit ---------- */
    [data-testid="stWidgetLabel"] p {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 500;
        color: var(--text) !important;
    }
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: var(--surface-alt) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
        font-family: 'IBM Plex Mono', monospace;
    }
    [data-testid="stAlert"] {
        background-color: var(--surface) !important;
        border: 1px solid var(--border);
        border-left: 4px solid var(--accent);
        border-radius: 6px;
    }
    [data-testid="stAlert"] p { color: var(--text) !important; }

    .stButton > button, .stLinkButton > a {
        font-family: 'IBM Plex Sans', sans-serif;
        font-weight: 600;
        border-radius: 6px;
        border: 1px solid var(--border);
    }
    /* Centraliza os botoes dentro do espaco disponivel, em vez de
       ficarem grudados na esquerda (que e o padrao do Streamlit). */
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton > button {
        width: auto;
        padding-left: 1.7rem;
        padding-right: 1.7rem;
    }
    .stButton > button[kind="primary"] {
        background-color: var(--accent);
        border-color: var(--accent);
        color: var(--bg);
    }
    .stButton > button[kind="primary"]:hover {
        background-color: var(--accent-dark);
        border-color: var(--accent-dark);
    }
    .stButton > button[kind="secondary"] {
        background-color: transparent;
        color: var(--text-muted);
    }
    .stLinkButton > a {
        background-color: transparent;
        border: 1px solid var(--accent);
        color: var(--accent) !important;
    }
    .stLinkButton > a:hover {
        background-color: var(--accent);
        color: var(--bg) !important;
    }

    /* ---------- Cards de imovel (etiqueta com furo) ---------- */
    [data-testid="stVerticalBlockBorderWrapper"]:has(.property-tag-marker) {
        background-color: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: 10px;
        position: relative;
        overflow: visible !important;
        margin-bottom: 1.4rem;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:has(.property-tag-marker)::before {
        content: '';
        position: absolute;
        top: 22px;
        left: -8px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: var(--bg);
        border: 1px solid var(--border);
        z-index: 2;
    }

    .rank-badge {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.85rem;
        color: var(--text-muted);
        letter-spacing: 0.05em;
    }
    .property-title {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 1.35rem;
        color: var(--text);
        margin: 0.1rem 0 0.5rem 0;
    }
    .property-meta {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.92rem;
        color: var(--text-muted);
    }
    .property-meta b { color: var(--text); font-weight: 600; }

    .score-block { text-align: right; }
    .score-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
    }
    .score-value {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        font-size: 2.1rem;
        line-height: 1.1;
    }
    .score-value .score-max {
        font-size: 1.1rem;
        color: var(--text-muted);
        font-weight: 400;
    }

    .stat-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
        margin-bottom: 0.15rem;
    }
    .stat-value {
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 600;
        font-size: 1.3rem;
        color: var(--text);
    }

    .section-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--accent);
        margin-bottom: 0.4rem;
    }
    .infra-line {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.92rem;
        color: var(--text-muted);
        line-height: 1.85;
    }
    .infra-line b { color: var(--text); font-family: 'IBM Plex Mono', monospace; }
    .description-text {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 0.92rem;
        color: var(--text-muted);
        line-height: 1.6;
        white-space: pre-line;
    }

    hr { border-color: var(--border) !important; }

    .app-footer {
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.03em;
        color: var(--text-muted);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- CONEXÃO E CARGA DE DADOS COM CAMINHO ABSOLUTO ---
@st.cache_data
def carregar_dados():
  # Garante que o banco seja aberto na mesma pasta onde o app.py está
  db_path = Path(__file__).resolve().parent / './db/arapongas.db'

  if not db_path.exists():
    raise FileNotFoundError(
        f'Arquivo do banco de dados não encontrado em: {db_path}'
    )

  conn = sqlite3.connect(db_path)

  query_bairros = (
      'SELECT b_id, b_nome, b_latitude, b_longitude FROM dim_bairro ORDER BY'
      ' b_nome'
  )
  df_bairros = pd.read_sql_query(query_bairros, conn)

  query_imoveis = """
    SELECT 
        m.m_id,
        m.m_referencia,
        m.m_nome,
        m.m_tipo,
        m.m_v_aluguel,
        m.m_v_condominio,
        (COALESCE(m.m_v_aluguel, 0) + COALESCE(m.m_v_condominio, 0)) AS custo_total,
        m.m_quartos,
        m.m_banheiros,
        m.m_vagas,
        m.m_m2,
        m.m_descricao,
        m.m_url,
        b.b_id,
        b.b_nome AS bairro_imovel,
        b.b_latitude AS lat_imovel,
        b.b_longitude AS lon_imovel,
        i.i_nome AS imobiliaria,
        COALESCE(s.qtd_saude, 0) AS qtd_saude,
        COALESCE(e.qtd_educacao, 0) AS qtd_educacao,
        COALESCE(l.qtd_lazer, 0) AS qtd_lazer,
        COALESCE(a.qtd_alimentacao, 0) AS qtd_alimentacao
    FROM dim_moradia m
    JOIN dim_bairro b ON m.b_id = b.b_id
    JOIN dim_imobiliaria i ON m.i_id = i.i_id
    LEFT JOIN (SELECT b_id, COUNT(*) AS qtd_saude FROM dim_saude GROUP BY b_id) s ON b.b_id = s.b_id
    LEFT JOIN (SELECT b_id, COUNT(*) AS qtd_educacao FROM dim_educacao GROUP BY b_id) e ON b.b_id = e.b_id
    LEFT JOIN (SELECT b_id, COUNT(*) AS qtd_lazer FROM dim_lazer GROUP BY b_id) l ON b.b_id = l.b_id
    LEFT JOIN (SELECT b_id, COUNT(*) AS qtd_alimentacao FROM dim_alimentacao GROUP BY b_id) a ON b.b_id = a.b_id
    WHERE m.m_status = 'Ativo';
    """
  df_imoveis = pd.read_sql_query(query_imoveis, conn)
  conn.close()
  return df_bairros, df_imoveis


df_bairros, df_imoveis_raw = carregar_dados()


# --- FUNÇÕES UTILITÁRIAS PARA EVITAR ERROS DE NaN ---
def safe_int(val):
  if pd.isna(val) or val is None:
    return 0
  try:
    return int(val)
  except (ValueError, TypeError):
    return 0


def formatar_titulo(tipo, nome):
  if pd.isna(nome) or str(nome).strip().lower() in ('nan', 'none', ''):
    return f'{tipo} para Locação'
  return f'{tipo}: {nome}'


def montar_descricao_completa(imovel):
  """
  Monta o texto da descricao combinando:
  - Caracteristicas do imovel (quartos/banheiros/vagas), SO as que o
    anuncio original informou (nao mostra "0" quando o dado e ausente).
  - O texto de descricao original do anuncio, se houver.
  Se nao houver NENHUM dos dois, retorna uma mensagem padrao explicando
  que a imobiliaria nao informou esses dados.
  """
  partes = []

  pedacos_caracteristicas = []
  if pd.notna(imovel['m_quartos']):
    pedacos_caracteristicas.append(f" {safe_int(imovel['m_quartos'])} quarto(s)")
  if pd.notna(imovel['m_banheiros']):
    pedacos_caracteristicas.append(f" {safe_int(imovel['m_banheiros'])} banheiro(s)")
  if pd.notna(imovel['m_vagas']):
    pedacos_caracteristicas.append(f" {safe_int(imovel['m_vagas'])} vaga(s)")
  if pd.notna(imovel['m_m2']):
    pedacos_caracteristicas.append(f" {imovel['m_m2']:.0f} m²")

  if pedacos_caracteristicas:
    partes.append(' | '.join(pedacos_caracteristicas))

  tem_descricao_original = pd.notna(imovel['m_descricao']) and str(
      imovel['m_descricao']
  ).strip() not in ('nan', '')
  if tem_descricao_original:
    partes.append(str(imovel['m_descricao']).strip())

  if not partes:
    return 'Dados não informados no anúncio da imobiliária.'

  return '\n\n'.join(partes)


def formatar_distancia(bairro_imovel, bairro_trabalho, distancia_km):
  """
  Evita a confusao de mostrar '0.00 km' quando o imovel esta no mesmo
  bairro informado como local de trabalho -- nesse caso, deixa explicito
  em texto em vez de um numero que pode parecer estranho/erro pro usuario.
  """
  if str(bairro_imovel).strip().lower() == str(bairro_trabalho).strip().lower():
    return 'Bairro do trabalho'
  return f'{distancia_km:.2f} km'


# --- FUNÇÕES DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
  if None in (lat1, lon1, lat2, lon2):
    return 999.0
  r = 6371.0
  phi1, phi2 = math.radians(lat1), math.radians(lat2)
  dphi = math.radians(lat2 - lat1)
  dlambda = math.radians(lon2 - lon1)
  a = (
      math.sin(dphi / 2) ** 2
      + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
  )
  return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def calcular_ranking(df_filtrado, lat_trab, lon_trab, teto_orcamento, pesos):
  df = df_filtrado.copy()
  soma_pesos = sum(pesos.values())
  w = (
      {k: v / soma_pesos for k, v in pesos.items()}
      if soma_pesos > 0
      else {k: 1 / len(pesos) for k in pesos}
  )

  # 1. Distância ao trabalho (km) e Score (0 a 100)
  df['distancia_km'] = df.apply(
      lambda row: haversine(
          row['lat_imovel'], row['lon_imovel'], lat_trab, lon_trab
      ),
      axis=1,
  )
  df['s_dist'] = df['distancia_km'].apply(
      lambda d: max(0.0, 100.0 * (1.0 - (d / 12.0)))
  )

  # 2. Score Financeiro (folga orçamentária até os 30%)
  df['s_preco'] = (
      100.0 * (1.0 - (df['custo_total'] / teto_orcamento))
  ).clip(0, 100)

  # 3. Scores de Infraestrutura Local (normalização por saturação de 4 POIs)
  df['s_saude'] = (df['qtd_saude'] / 4.0 * 100.0).clip(0, 100)
  df['s_educ'] = (df['qtd_educacao'] / 4.0 * 100.0).clip(0, 100)
  df['s_lazer'] = (df['qtd_lazer'] / 4.0 * 100.0).clip(0, 100)
  df['s_alim'] = (df['qtd_alimentacao'] / 4.0 * 100.0).clip(0, 100)

  # 4. Score Final Ponderado
  df['score_final'] = (
      w['dist'] * df['s_dist']
      + w['preco'] * df['s_preco']
      + w['saude'] * df['s_saude']
      + w['educ'] * df['s_educ']
      + w['lazer'] * df['s_lazer']
      + w['alim'] * df['s_alim']
  )

  return df.sort_values(by='score_final', ascending=False)


def cor_score(valor):
  """Retorna a cor semantica do score: alto=verde-salvia, medio=ambar, baixo=terracota."""
  if valor >= 70:
    return '#7E9B6C'
  if valor >= 45:
    return '#D9A653'
  return '#B2593F'


def renderizar_regua_etapas(etapa_atual):
  """
  Indicador de progresso em forma de regua/fita metrica (assinatura visual
  do app, referenciando a industria moveleira de Arapongas -- o app
  'mede' o encaixe entre imovel e estilo de vida).
  """
  etapas = [
      ('01', 'Renda & Local'),
      ('02', 'Prioridades'),
      ('03', 'Resultado'),
  ]
  html = '<div class="ruler">'
  for i, (numero, label) in enumerate(etapas, start=1):
    estado = 'done' if i < etapa_atual else ('active' if i == etapa_atual else '')
    conector = 'filled' if i <= etapa_atual else ''
    html += (
        f'<div class="ruler-step {estado}">'
        f'<div class="ruler-connector {conector}"></div>'
        f'<div class="ruler-badge">{numero}</div>'
        f'<div class="ruler-label">{label}</div>'
        f'</div>'
    )
  html += '</div>'
  st.markdown(html, unsafe_allow_html=True)


# --- GERENCIAMENTO DE ESTADO (ETAPAS) ---
if 'etapa' not in st.session_state:
  st.session_state.etapa = 1

st.markdown(
    """
    <div class="hero-title">Recomendador de Imóveis</div>
    <div class="hero-caption">
        Cruza distância do trabalho, infraestrutura do bairro e orçamento pra recomendar os imóveis 
        com melhor custo-benefício em Arapongas-PR, usando até 30% da sua renda bruta como teto seguro de aluguel."
    </div>
    """,
    unsafe_allow_html=True,
)
renderizar_regua_etapas(st.session_state.etapa)

# ==========================================
# ETAPA 1: DADOS DO USUÁRIO
# ==========================================
if st.session_state.etapa == 1:
  st.markdown('<div class="section-label">Etapa 01</div>', unsafe_allow_html=True)
  st.subheader('Renda e local de trabalho')

  renda = st.number_input(
      'Renda Familiar ou Pessoal Bruta (R$):',
      min_value=1000.0,
      value=st.session_state.get('renda', 5000.0),
      step=200.0,
  )
  teto_30 = renda * 0.30
  st.info(
      f'💡 Seu teto orçamentário seguro (30% da renda) é de **R$'
      f' {teto_30:,.2f}**.'
  )

  lista_bairros = df_bairros['b_nome'].tolist()
  bairro_padrao = st.session_state.get('bairro_trab', 'Centro')
  bairro_trab = st.selectbox(
      'Bairro onde você trabalha:',
      options=lista_bairros,
      index=lista_bairros.index(bairro_padrao)
      if bairro_padrao in lista_bairros
      else 0,
  )

  if st.button('Continuar', type='primary'):
    # Checa ANTES de avancar se existe algum imovel dentro do orcamento --
    # essa checagem so depende da renda (nao dos pesos da Etapa 2), entao
    # faz sentido barrar aqui mesmo, sem fazer o usuario preencher a
    # calibracao de prioridades a toa.
    existe_imovel_no_orcamento = (
        (df_imoveis_raw['custo_total'] > 0)
        & (df_imoveis_raw['custo_total'] <= teto_30)
    ).any()

    if not existe_imovel_no_orcamento:
      st.warning(
          'Nenhum imóvel disponível com valor válido encontrado dentro do'
          f' limite de R$ {teto_30:,.2f}. Tente aumentar o valor da renda.'
      )
    else:
      st.session_state.renda = renda
      st.session_state.teto_30 = teto_30
      st.session_state.bairro_trab = bairro_trab
      st.session_state.etapa = 2
      st.rerun()

# ==========================================
# ETAPA 2: CALIBRAÇÃO DE PESOS
# ==========================================
elif st.session_state.etapa == 2:
  st.markdown('<div class="section-label">Etapa 02</div>', unsafe_allow_html=True)
  st.subheader('Calibre o que é mais importante pra você')
  st.write('Defina o peso de 1 (Pouco Importante) a 5 (Muito Importante):')

  # Peso da Proximidade do Trabalho é fixo: é o próprio objetivo central do
  # app (recomendar o bairro mais próximo do trabalho), então não faz
  # sentido o usuário "desligar" esse critério.
  PESO_DIST_FIXO = 4

  # Recupera pesos ja escolhidos (se o usuario esta voltando pra recalibrar)
  pesos_anteriores = st.session_state.get('pesos', {})

  col1, col2 = st.columns(2)
  with col1:
    p_preco = st.slider(
        'Economia / Menor Preço de Aluguel:', 1, 5,
        pesos_anteriores.get('preco', 4),
    )
    p_saude = st.slider(
        'Presença de Serviços de Saúde (UBS, Clínicas):', 1, 5,
        pesos_anteriores.get('saude', 3),
    )
    p_educ = st.slider(
        'Presença de Escolas / Creches:', 1, 5,
        pesos_anteriores.get('educ', 3),
    )
  with col2:
    p_lazer = st.slider(
        'Opções de Lazer (Praças, Parques, Clubes):', 1, 5,
        pesos_anteriores.get('lazer', 2),
    )
    p_alim = st.slider(
        'Mercados e Alimentação no Bairro:', 1, 5,
        pesos_anteriores.get('alim', 3),
    )

  st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

  pad_l, c_voltar, c_avancar, pad_r = st.columns([2, 1, 1.4, 2])
  with c_voltar:
    if st.button('⬅️ Voltar'):
      st.session_state.etapa = 1
      st.rerun()
  with c_avancar:
    if st.button('Ver top 10 Imóveis', type='primary'):
      st.session_state.pesos = {
          'dist': PESO_DIST_FIXO,
          'preco': p_preco,
          'saude': p_saude,
          'educ': p_educ,
          'lazer': p_lazer,
          'alim': p_alim,
      }
      st.session_state.etapa = 3
      st.rerun()

# ==========================================
# ETAPA 3: RANKING FINAL DE RECOMENDAÇÕES
# ==========================================
if st.session_state.etapa == 3:
  st.markdown('<div class="section-label">Etapa 03</div>', unsafe_allow_html=True)
  st.subheader('Os 10 imóveis com melhor custo-benefício')

  # Recupera dados do bairro de trabalho
  dados_bairro_trab = df_bairros[
      df_bairros['b_nome'] == st.session_state.bairro_trab
  ].iloc[0]

  # Se a latitude do bairro for NaN, usa o centro de Arapongas como padrão
  lat_trab = (
      dados_bairro_trab['b_latitude']
      if pd.notna(dados_bairro_trab['b_latitude'])
      else -23.4140
  )
  lon_trab = (
      dados_bairro_trab['b_longitude']
      if pd.notna(dados_bairro_trab['b_longitude'])
      else -51.4286
  )

  # 1. Filtro rígido: Apenas imóveis com aluguel válido (> 0) e dentro dos 30% da renda
  df_elegiveis = df_imoveis_raw[
      (df_imoveis_raw['custo_total'] > 0)
      & (df_imoveis_raw['custo_total'] <= st.session_state.teto_30)
  ]

  if df_elegiveis.empty:
    st.warning(
        'Nenhum imóvel disponível com valor válido encontrado dentro do limite'
        f' de R$ {st.session_state.teto_30:,.2f}. Tente aumentar o valor da'
        ' renda.'
    )
  else:
    df_ranking = calcular_ranking(
        df_elegiveis,
        lat_trab,
        lon_trab,
        st.session_state.teto_30,
        st.session_state.pesos,
    )
    top_10 = df_ranking.head(10)

    st.success(
        f'Foram analisados **{len(df_elegiveis)}** imóveis elegíveis para o seu'
        ' perfil orçamentário e Prioridades.'
    )

    for idx, (_, imovel) in enumerate(top_10.iterrows(), start=1):
      with st.container(border=True):
        st.markdown(
            '<span class="property-tag-marker" style="display:none;"></span>',
            unsafe_allow_html=True,
        )

        c_tit, c_score = st.columns([3, 1])
        with c_tit:
          titulo_limpo = html.escape(
              formatar_titulo(imovel['m_tipo'], imovel['m_nome'])
          )
          bairro_seguro = html.escape(str(imovel['bairro_imovel']))
          imobiliaria_segura = html.escape(str(imovel['imobiliaria']))
          st.markdown(
              f'<div class="rank-badge">#{idx:02d}</div>'
              f'<div class="property-title">{titulo_limpo}</div>'
              f'<div class="property-meta">📍 <b>Bairro:</b> {bairro_seguro}'
              f' &nbsp;|&nbsp; 🏢 <b>Imobiliária:</b> {imobiliaria_segura}</div>',
              unsafe_allow_html=True,
          )
        with c_score:
          cor = cor_score(imovel['score_final'])
          st.markdown(
              f'<div class="score-block">'
              f'<div class="score-label">Custo-Benefício</div>'
              f'<div class="score-value" style="color:{cor};">'
              f'{imovel["score_final"]:.1f}<span class="score-max">/100</span>'
              f'</div></div>',
              unsafe_allow_html=True,
          )

        st.markdown('<div style="height:0.9rem;"></div>', unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
          st.markdown(
              '<div class="stat-label">Valor Aluguel</div>'
              f'<div class="stat-value">R$ {imovel["custo_total"]:,.2f}</div>',
              unsafe_allow_html=True,
          )
        with m2:
          st.markdown(
              '<div class="stat-label">Distância do Trabalho</div>'
              f'<div class="stat-value">'
              f'{formatar_distancia(imovel["bairro_imovel"], st.session_state.bairro_trab, imovel["distancia_km"])}'
              f'</div>',
              unsafe_allow_html=True,
          )

        st.markdown('<div style="height:1.2rem;"></div>', unsafe_allow_html=True)

        c_infra, c_descricao = st.columns([1, 2])
        with c_infra:
            st.markdown(
                '<div class="section-label">🏘️ Infraestrutura</div>'
                '<div class="infra-line">'
                f' Saúde: <b>{safe_int(imovel["qtd_saude"])}</b><br>'
                f' Educação: <b>{safe_int(imovel["qtd_educacao"])}</b><br>'
                f' Lazer: <b>{safe_int(imovel["qtd_lazer"])}</b><br>'
                f' Alimentação: <b>{safe_int(imovel["qtd_alimentacao"])}</b>'
                '</div>',
                unsafe_allow_html=True,
            )
        with c_descricao:
            st.markdown('<div class="section-label">📝 Descrição</div>', unsafe_allow_html=True)
            descricao_segura = html.escape(montar_descricao_completa(imovel))
            st.markdown(
                f'<div class="description-text">{descricao_segura}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:1rem;"></div>', unsafe_allow_html=True)

        if (
            pd.notna(imovel['m_url'])
            and str(imovel['m_url']).startswith('http')
        ):
          st.link_button('🔗 Acessar Anúncio do Imóvel', imovel['m_url'])

  st.divider()

  if df_elegiveis.empty:
    # Recalibrar pesos nao resolve o problema (e orcamento, nao prioridade)
    # -- so faz sentido oferecer uma nova consulta com outra renda.
    pad_l, c_nova3, pad_r = st.columns([2, 1.6, 2])
    with c_nova3:
      if st.button('Nova Consulta'):
        for chave in ('renda', 'teto_30', 'bairro_trab', 'pesos'):
          st.session_state.pop(chave, None)
        st.session_state.etapa = 1
        st.rerun()
  else:
    pad_l, c_voltar3, c_nova3, pad_r = st.columns([2, 1.3, 1.6, 2])
    with c_voltar3:
      if st.button('Recalibrar'):
        # Mantem renda, bairro e pesos ja escolhidos -- so volta pra ajustar
        st.session_state.etapa = 2
        st.rerun()
    with c_nova3:
      if st.button('Nova Consulta'):
        # Nova consulta de verdade: limpa os valores anteriores, senão a
        # Etapa 1 reapareceria pre-preenchida com a consulta antiga.
        for chave in ('renda', 'teto_30', 'bairro_trab', 'pesos'):
          st.session_state.pop(chave, None)
        st.session_state.etapa = 1
        st.rerun()
# ==========================================
# RODAPE (aparece em todas as etapas)
# ==========================================
st.markdown(
    '<div class="app-footer">'
    'Curso Superior Tecnólogo em Ciência de Dados · '
    'Leandro Alves de Souza, RU 2136383 · UNINTER'
    '</div>',
    unsafe_allow_html=True,
)