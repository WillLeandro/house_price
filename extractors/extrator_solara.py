"""
extratores/extrator_solara.py

Extrator da Imobiliaria Solara (imobiliariasolara.com.br).
Segue o contrato: expoe extrair() -> list[dict]

Plataforma: Code49 (identificada pelas classes "c49-*" e rodape
"Desenvolvido por CODE 49"). Diferente da Ricardo (Next.js/Arbo), aqui
NAO ha JSON embutido -- o HTML e renderizado no servidor com classes CSS
claras e estaveis, entao usamos BeautifulSoup com seletores especificos.

PAGINACAO: a URL tem o formato .../imoveis/{busca_id}/{pagina}, ex:
.../imoveis/7114/1. O atributo data-num_reg_pages="10" no HTML indica
10 resultados por pagina. Percorremos incrementando o numero da pagina
ate uma pagina vir vazia (sem nenhum <article class="c49-property-card">).
"""

import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.imobiliariasolara.com.br"
# URL de locacao (apartamento + casa), busca 7114, comeca na pagina 1
LISTAGEM_URL_BASE = "https://www.imobiliariasolara.com.br/imobiliaria/locacao/apartamento-casa/imoveis/7114"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjetoAcademicoUninter/1.0; "
                  "+trabalho de extensao universitaria - Ciencia de Dados)"
}


def _texto_para_float(texto):
    """Converte 'R$ 1.205,00' em float. Retorna None se nao achar numero."""
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
    # Referencia = numero apos "property-" no id do <article>
    id_attr = article.get("id", "")
    match_ref = re.search(r"property-(\d+)", id_attr)
    referencia = match_ref.group(1) if match_ref else None

    # Titulo
    titulo_tag = article.select_one("h2.c49-property-card_title")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None

    # Tipo (badge)
    tipo_tag = article.select_one(".c49-property-card_type")
    tipo = tipo_tag.get_text(strip=True) if tipo_tag else None

    # Endereco/bairro: "Bairro, Cidade - UF" ou so "Cidade - UF"
    endereco_tag = article.select_one(".c49-property-card_address")
    bairro = "Nao informado"
    if endereco_tag:
        texto_endereco = endereco_tag.get_text(strip=True)
        # remove o icone de mapa se veio junto como texto
        texto_endereco = texto_endereco.replace("\uf3c5", "").strip()
        partes = [p.strip() for p in texto_endereco.split(",")]
        if len(partes) > 1:
            bairro = partes[0]
        # se so tem "Cidade - UF", nao ha bairro explicito -> mantem "Nao informado"

    if bairro == "Nao informado" and titulo:
        bairro_do_titulo = _extrair_bairro_do_titulo(titulo)
        if bairro_do_titulo:
            bairro = bairro_do_titulo

    # URL do imovel: pega do link "Mais detalhes"
    link_tag = article.select_one("a.c49btn-details")
    url_imovel = link_tag.get("href") if link_tag else None
    if url_imovel and not url_imovel.startswith("http"):
        url_imovel = BASE_URL + url_imovel

    # Descricao
    descricao_tag = article.select_one(".c49-property-card_description p")
    descricao = descricao_tag.get_text(strip=True) if descricao_tag else None

    # Valor de locacao: existe um ou mais ".c49-property-card_rent-price";
    # cada um tem um <span> final dizendo "Locação" ou "Venda". Pegamos so o de Locacao.
    valor_locacao = None
    for preco_div in article.select(".c49-property-card_rent-price"):
        spans = preco_div.find_all("span")
        rotulo = spans[-1].get_text(strip=True) if spans else ""
        if "loca" in rotulo.lower():
            valor_locacao = _texto_para_float(preco_div.get_text())
            break

    # Condominio: dentro de ".c49-property-card_other-prices", se tiver o texto "Condom"
    condominio = None
    outros_precos = article.select_one(".c49-property-card_other-prices")
    if outros_precos and "condom" in outros_precos.get_text(strip=True).lower():
        condominio = _texto_para_float(outros_precos.get_text())

    # Caracteristicas: quartos, banheiros, vagas, area -- via classe do icone
    quartos = banheiros = vagas = area = None
    suite = None
    for wrap in article.select(".c49-property-number-wrap"):
        icone = wrap.select_one("span[class*='c49icon-']")
        valor_tag = wrap.select_one(".c49-property-number")
        if not icone or not valor_tag:
            continue
        classe_icone = " ".join(icone.get("class", []))
        valor_texto = valor_tag.get_text(strip=True)

        if "bedroom" in classe_icone:
            quartos = _texto_para_int(valor_texto)
            # o atributo title do wrap pode conter "sendo 1 suíte"
            title_attr = wrap.get("title", "") or wrap.parent.get("title", "")
            match_suite = re.search(r"(\d+)\s*su[íi]te", title_attr, re.IGNORECASE)
            if match_suite:
                suite = int(match_suite.group(1))
        elif "bathroom" in classe_icone:
            banheiros = _texto_para_int(valor_texto)
        elif "garage" in classe_icone:
            vagas = _texto_para_int(valor_texto)
        elif "area" in classe_icone:
            area = _texto_para_float(valor_texto)

    return {
        "referencia": referencia,
        "tipo": tipo,
        "finalidade": "Locacao",
        "nome": titulo,
        "bairro": bairro,
        "endereco": None,  # site nao mostra rua/numero na listagem
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
        url_pagina = f"{LISTAGEM_URL_BASE}/{pagina}"
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
            # menos que o tamanho de pagina (10) = ultima pagina
            break
        pagina += 1

    print(f"Total coletado na Imobiliaria Solara: {len(todos_imoveis)} imoveis")
    return todos_imoveis


if __name__ == "__main__":
    resultado = extrair()
    for imovel in resultado:
        print(imovel)