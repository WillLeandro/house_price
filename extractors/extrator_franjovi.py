"""
extratores/extrator_franjovi.py

Extrator da Imobiliaria Franjovi (imobiliariafranjovi.com.br).
Segue o contrato: expoe extrair() -> list[dict]

HISTORICO: inicialmente tratamos este site como bloqueado por robots.txt.
Ao reexaminar o arquivo (26/07/2026), confirmamos que a regra geral e
"User-agent: * / Allow: /" -- so bots especificos por nome sao bloqueados
(crawlers de SEO, ferramentas de download em massa, alguns bots de IA).
O nosso User-Agent customizado e honesto (abaixo) NAO esta nessa lista de
bloqueio, entao o acesso automatizado e permitido.

Plataforma: Code49 (mesma da Imobiliaria Solara) -- reaproveitamos a
mesma logica de parsing de card.
"""

import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.imobiliariafranjovi.com.br"
LISTAGEM_URL_BASE = "https://www.imobiliariafranjovi.com.br/imobiliaria/locacao/apartamento-casa-sobrado/imoveis/82316"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjetoAcademicoUninter/1.0; "
                  "+trabalho de extensao universitaria - Ciencia de Dados)"
}


def _texto_para_float(texto):
    if not texto:
        return None
    numeros = re.sub(r"[^\d,.]", "", texto)
    numeros = numeros.replace(".", "").replace(",", ".")
    try:
        return float(numeros)
    except ValueError:
        return None


def _texto_para_int(texto):
    if not texto:
        return None
    match = re.search(r"\d+", texto)
    return int(match.group()) if match else None


def _extrair_bairro_do_titulo(titulo):
    """
    Fallback: quando o bloco de endereco do card nao informa o bairro
    (ex: card so mostra 'Arapongas - PR', sem bairro antes da virgula),
    tenta extrair o bairro do TITULO do anuncio, que geralmente repete
    essa informacao (ex: 'Casa para Locacao no Jardim Cultura').
    """
    if not titulo:
        return None
    match = re.search(r'-\s*Loca[cç][aã]o\s*-\s*(.+)$', titulo, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r'\bn[ao]\s+(.+?)(?:\s+de\s+Fundos)?$', titulo, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extrair_card(article):
    """Mesma logica de parsing usada na Solara (plataforma Code49 identica)."""
    id_attr = article.get("id", "")
    match_ref = re.search(r"property-(\d+)", id_attr)
    referencia = match_ref.group(1) if match_ref else None

    titulo_tag = article.select_one("h2.c49-property-card_title")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None

    tipo_tag = article.select_one(".c49-property-card_type")
    tipo = tipo_tag.get_text(strip=True) if tipo_tag else None

    endereco_tag = article.select_one(".c49-property-card_address")
    bairro = "Nao informado"
    if endereco_tag:
        texto_endereco = endereco_tag.get_text(strip=True)
        texto_endereco = texto_endereco.replace("\uf3c5", "").strip()
        partes = [p.strip() for p in texto_endereco.split(",")]
        if len(partes) > 1:
            bairro = partes[0]

    if bairro == "Nao informado" and titulo:
        bairro_do_titulo = _extrair_bairro_do_titulo(titulo)
        if bairro_do_titulo:
            bairro = bairro_do_titulo

    link_tag = article.select_one("a.c49btn-details")
    url_imovel = link_tag.get("href") if link_tag else None
    if url_imovel and not url_imovel.startswith("http"):
        url_imovel = BASE_URL + url_imovel

    descricao_tag = article.select_one(".c49-property-card_description p")
    descricao = descricao_tag.get_text(strip=True) if descricao_tag else None

    # So pegamos o valor de LOCACAO (o site tambem mostra Venda em alguns cards)
    valor_locacao = None
    for preco_div in article.select(".c49-property-card_rent-price"):
        spans = preco_div.find_all("span")
        rotulo = spans[-1].get_text(strip=True) if spans else ""
        if "loca" in rotulo.lower():
            valor_locacao = _texto_para_float(preco_div.get_text())
            break

    condominio = None
    outros_precos = article.select_one(".c49-property-card_other-prices")
    if outros_precos and "condom" in outros_precos.get_text(strip=True).lower():
        condominio = _texto_para_float(outros_precos.get_text())

    quartos = banheiros = vagas = area = None
    for wrap in article.select(".c49-property-number-wrap"):
        icone = wrap.select_one("span[class*='c49icon-']")
        valor_tag = wrap.select_one(".c49-property-number")
        if not icone or not valor_tag:
            continue
        classe_icone = " ".join(icone.get("class", []))
        valor_texto = valor_tag.get_text(strip=True)

        if "bedroom" in classe_icone:
            quartos = _texto_para_int(valor_texto)
        elif "bathroom" in classe_icone:
            banheiros = _texto_para_int(valor_texto)
        elif "garage" in classe_icone:
            vagas = _texto_para_int(valor_texto)
        elif "area" in classe_icone:
            area = _texto_para_float(valor_texto)

    suite = None
    bedroom_wrap = article.select_one(".c49-property-number-wrap:has(span[class*='bedroom'])")
    if bedroom_wrap:
        title_attr = bedroom_wrap.get("title", "")
        match_suite = re.search(r"(\d+)\s*su[íi]te", title_attr, re.IGNORECASE)
        if match_suite:
            suite = int(match_suite.group(1))

    return {
        "referencia": referencia,
        "tipo": tipo,
        "finalidade": "Locacao",
        "nome": titulo,
        "bairro": bairro,
        "endereco": None,
        "v_aluguel": valor_locacao,
        "v_condominio": condominio,
        "m2": area,
        "quartos": quartos,
        "salas": None,
        "banheiros": banheiros,
        "suite": suite,
        "vagas": vagas,
        "descricao": descricao,
        "url": url_imovel,
    }


# --- Filtro de seguranca: so residencial (Casa/Apartamento/Sobrado/Kitnet),
# so locacao de verdade (nunca venda pura), e so Arapongas (alguns sites
# atendem varias cidades e vazam resultados de fora mesmo com URL filtrada) ---
TIPOS_RESIDENCIAIS = {"casa", "apartamento", "sobrado", "kitnet", "kit-net", "sobreposta"}


def _e_residencial_e_locacao(item):
    tipo = (item.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_RESIDENCIAIS:
        return False
    if item.get("v_aluguel") is None:
        return False
    url = (item.get("url") or "").lower()
    if "/locacao-" not in url and "venda-locacao-" not in url:
        return False
    if "arapongas" not in url:
        return False
    return True


def _extrair_pagina(url, sessao):
    resposta = sessao.get(url, headers=HEADERS, timeout=20)
    resposta.raise_for_status()
    soup = BeautifulSoup(resposta.text, "html.parser")

    articles = soup.select("article.c49-property-card")
    imoveis = [_extrair_card(a) for a in articles]
    imoveis = [i for i in imoveis if i["referencia"]]
    imoveis = [i for i in imoveis if _e_residencial_e_locacao(i)]

    return imoveis


def extrair(max_paginas=20):
    sessao = requests.Session()
    todos_imoveis = []
    pagina = 1

    while pagina <= max_paginas:
        # Padrao Code49: numero de pagina no final da URL, ex: .../imoveis/66060/2
        url_pagina = f"{LISTAGEM_URL_BASE}/{pagina}" if pagina > 1 else LISTAGEM_URL_BASE
        print(f"Coletando pagina {pagina}: {url_pagina}")

        try:
            imoveis_pagina = _extrair_pagina(url_pagina, sessao)
        except requests.RequestException as erro:
            print(f"Erro ao acessar pagina {pagina}: {erro}")
            break

        if not imoveis_pagina:
            print("Nenhum imovel encontrado nesta pagina -- parando.")
            break

        todos_imoveis.extend(imoveis_pagina)

        if len(imoveis_pagina) < 10:
            break
        pagina += 1

    print(f"Total coletado na Imobiliaria Franjovi: {len(todos_imoveis)} imoveis")
    return todos_imoveis


if __name__ == "__main__":
    resultado = extrair()
    for imovel in resultado:
        print(imovel)