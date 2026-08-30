"""
extratores/extrator_linham.py

Extrator da Imobiliaria e Loteadora Linham (imobiliarialinham.com.br).
Segue o contrato: expoe extrair() -> list[dict]

Plataforma: Imonov / Si9Sistemas (Webflow + sistema proprio, ver rodape
"Desenvolvido por Imonov & Si9sistemas"). Sem JSON embutido -- usamos
BeautifulSoup com seletores CSS.

VALOR DE ALUGUEL: o site mostra 3 valores por imovel:
  - "Valor do Aluguel" (base)
  - "Desconto de pontualidade"
  - "Valor do aluguel com desconto" (o que o inquilino de fato paga
    pagando em dia -- mesmo padrao "bonificado" visto nas outras
    imobiliarias). Usamos esse ultimo como v_aluguel.

PAGINACAO: URL no formato .../filtro/list/locacao/{categorias}/{cidade}/
{bairro}/{faixa_valor}/{codigo}/{pagina}. O numero da pagina fica no
ultimo segmento da URL. O rodape "Paginas" mostra os links das paginas
disponiveis.
"""

import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.imobiliarialinham.com.br"
LISTAGEM_URL_BASE = (
    "https://www.imobiliarialinham.com.br/filtro/list/locacao/"
    "sobrado---casa---apartamento/arapongas/todos/0-10000000/todos"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjetoAcademicoUninter/1.0; "
                  "+trabalho de extensao universitaria - Ciencia de Dados)"
}

# Mapeia o texto do "feature-escrita" para o campo correspondente
ESCRITA_PARA_CAMPO = {
    "quarto": "quartos",
    "banheiro": "banheiros",
    "vaga": "vagas",
    "suite": "suite",
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


def _extrair_card(link_tag):
    url_imovel = link_tag.get("href")
    if url_imovel and not url_imovel.startswith("http"):
        url_imovel = BASE_URL + url_imovel

    # Referencia = ultimo segmento numerico da URL
    match_ref = re.search(r"/(\d+)$", url_imovel or "")
    referencia = match_ref.group(1) if match_ref else None

    # Tipo: 3o segmento do path /imovel/locacao/{tipo}/...
    match_tipo = re.search(r"/imovel/locacao/([a-z\-]+)/", url_imovel or "")
    tipo = match_tipo.group(1).replace("-", " ").title() if match_tipo else None

    # Titulo
    titulo_tag = link_tag.select_one(".heading-4")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else None

    # Bairro: "Bairro, CIDADE - UF"
    bairro_tag = link_tag.select_one(".text-block-15")
    bairro = "Nao informado"
    if bairro_tag:
        texto_bairro = bairro_tag.get_text(strip=True)
        partes = [p.strip() for p in texto_bairro.split(",")]
        if len(partes) > 1:
            bairro = partes[0].title()

    # Valores: dentro de .div-block-14, pares rotulo/valor em .text-block-11
    valores_divs = link_tag.select(".div-block-14 .text-block-11")
    valor_aluguel = None
    valor_condominio = None
    rotulo_atual = None
    for div in valores_divs:
        classes = div.get("class", [])
        texto = div.get_text(strip=True)
        if "descontopontualidade" in classes:
            rotulo_atual = texto.lower()
        else:
            if rotulo_atual and "com desconto" in rotulo_atual:
                valor_aluguel = _texto_para_float(texto)
            elif rotulo_atual and "condom" in rotulo_atual:
                valor_condominio = _texto_para_float(texto)
            rotulo_atual = None

    # Caracteristicas: .feature > (numero, svg, span.feature-escrita)
    caracteristicas = {"quartos": None, "banheiros": None, "vagas": None, "suite": None}
    for feature in link_tag.select(".feature"):
        numero_tag = feature.select_one("div")
        escrita_tag = feature.select_one(".feature-escrita")
        if not numero_tag or not escrita_tag:
            continue
        escrita = escrita_tag.get_text(strip=True).lower()
        numero = _texto_para_int(numero_tag.get_text(strip=True))
        for chave, campo in ESCRITA_PARA_CAMPO.items():
            if chave in escrita:
                caracteristicas[campo] = numero
                break

    return {
        "referencia": referencia,
        "tipo": tipo,
        "finalidade": "Locacao",
        "nome": titulo,
        "bairro": bairro,
        "endereco": None,  # site nao mostra rua/numero na listagem
        "v_aluguel": valor_aluguel,
        "v_condominio": valor_condominio,
        "m2": None,
        "quartos": caracteristicas["quartos"],
        "salas": None,
        "banheiros": caracteristicas["banheiros"],
        "suite": caracteristicas["suite"],
        "vagas": caracteristicas["vagas"],
        "descricao": None,  # nao aparece na listagem, so no card
        "url": url_imovel,
    }


TIPOS_RESIDENCIAIS = {"casa", "apartamento", "sobrado", "kitnet", "kit-net", "sobreposta"}


def _e_residencial_e_locacao(item):
    """Filtro de seguranca: garante residencial, valor de aluguel presente
    e imovel localizado em Arapongas."""
    tipo = (item.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_RESIDENCIAIS:
        return False
    if item.get("v_aluguel") is None:
        return False
    url = (item.get("url") or "").lower()
    if "arapongas" not in url:
        return False
    return True


def _extrair_pagina(url, sessao):
    resposta = sessao.get(url, headers=HEADERS, timeout=20)
    resposta.raise_for_status()
    soup = BeautifulSoup(resposta.text, "html.parser")

    # Cada imovel e um <a class="div-block-11 w-inline-block" href=".../imovel/locacao/...">
    links = soup.select("a.div-block-11[href*='/imovel/']")
    imoveis = [_extrair_card(a) for a in links]
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

        # Evita loop infinito: se a pagina 2 trouxer os mesmos imoveis da 1
        # (site sem paginacao real), para por aqui.
        referencias_novas = {i["referencia"] for i in imoveis_pagina}
        referencias_ja_vistas = {i["referencia"] for i in todos_imoveis}
        if referencias_novas and referencias_novas.issubset(referencias_ja_vistas):
            print("Pagina repetida (mesmos imoveis da anterior) -- parando.")
            break

        todos_imoveis.extend(imoveis_pagina)
        pagina += 1

    print(f"Total coletado na Imobiliaria Linham: {len(todos_imoveis)} imoveis")
    return todos_imoveis


if __name__ == "__main__":
    resultado = extrair()
    for imovel in resultado:
        print(imovel)