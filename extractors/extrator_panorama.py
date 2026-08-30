"""
extratores/extrator_panorama.py

Extrator da Imoveis Panorama (imoveispanorama.com.br).
Segue o contrato: expoe extrair() -> list[dict]

Plataforma: sistema customizado (rodape "Desenvolvido por Sistemas Cordon").

LIMITACAO IMPORTANTE: a pagina de LISTAGEM nao mostra quartos, suites,
banheiros nem vagas -- esses campos aparecem em branco no HTML (ex:
"<b></b> Dorm."). Esses dados só existem na pagina de DETALHE de cada
imovel, que exigiria uma requisicao extra por imovel. Por ora deixamos
esses campos como None; se quiser esses dados no futuro, dá pra evoluir
o extrator para visitar cada pagina de detalhe.

PAGINACAO: nao ha parametro de pagina visivel no HTML (o site parece
mostrar tudo de uma vez por tipo). Por isso, percorremos os TIPOS de
imovel disponiveis nas "Buscas Rapidas - Locacao" (apartamento, casa,
sala, sobrado, barracao) e juntamos os resultados, removendo duplicatas
pela referencia.
"""


import re
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.imoveispanorama.com.br"

# Tipos disponiveis na secao "Busca Rapida - Locacao" do site
# Tipos residenciais disponiveis na secao "Busca Rapida - Locacao" do site.
# Removidos "sala" e "barracao" -- sao comerciais, nao residenciais.
TIPOS_LOCACAO = ["apartamento", "casa", "sobrado"]

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


def _extrair_card(card_div, tipo_busca):
    # Coluna da direita (col-md-7) tem todos os dados textuais
    coluna_info = card_div.select_one(".col-sm-12.col-md-7")
    if not coluna_info:
        return None

    # Bairro/cidade: primeiro <span style="font-size: 20px..."> com <br> separando
    span_local = coluna_info.select_one("span[style*='font-size: 20px']")
    bairro = "Nao informado"
    cidade = "Arapongas"
    if span_local:
        # o conteudo vem como "Centro <br> Arapongas/PR" -- pegamos via get_text
        # com separador de linha, e usamos a 1a linha como bairro
        linhas = [l.strip() for l in span_local.get_text(separator="\n").split("\n") if l.strip()]
        if linhas:
            bairro = linhas[0]
        if len(linhas) > 1 and "/" in linhas[1]:
            cidade = linhas[1].split("/")[0].strip()

    # Referencia e tipo: dentro de <small><b>Ref: 711</b> - Apartamento</small>
    small_tag = coluna_info.select_one("small")
    referencia = None
    tipo = tipo_busca.capitalize()
    if small_tag:
        texto_small = small_tag.get_text(" ", strip=True)
        match_ref = re.search(r"Ref:\s*(\d+)", texto_small)
        if match_ref:
            referencia = match_ref.group(1)
        match_tipo = re.search(r"-\s*(.+)$", texto_small)
        if match_tipo:
            tipo = match_tipo.group(1).strip()

    # Valor: dentro do <span><b>Valor:</b> R$ 2.000,00</span>
    valor = None
    for span in coluna_info.select("span"):
        if span.find("b") and "valor" in span.find("b").get_text(strip=True).lower():
            valor = _texto_para_float(span.get_text())
            break

    # URL: link "Ver detalhes do imovel"
    link_tag = coluna_info.select_one("a.btn-dark")
    url_imovel = link_tag.get("href") if link_tag else None

    if not referencia:
        return None

    return {
        "referencia": referencia,
        "tipo": tipo,
        "finalidade": "Locacao",
        "nome": None,  # site nao da um titulo proprio ao anuncio
        "bairro": bairro,
        "endereco": None,  # nao aparece na listagem
        "v_aluguel": valor,
        "v_condominio": None,  # nao aparece na listagem
        "m2": None,
        "quartos": None,   # so aparece na pagina de detalhe (branco na listagem)
        "salas": None,
        "banheiros": None,  # idem
        "suite": None,       # idem
        "vagas": None,       # idem
        "descricao": None,
        "url": url_imovel,
    }


TIPOS_RESIDENCIAIS_VALIDOS = {"apartamento", "casa", "sobrado"}


def _extrair_por_tipo(tipo, sessao):
    url = f"{BASE_URL}/busca_rapida?finalidade=locacao&tipo={tipo}"
    print(f"Coletando tipo '{tipo}': {url}")

    resposta = sessao.get(url, headers=HEADERS, timeout=20)
    resposta.raise_for_status()
    soup = BeautifulSoup(resposta.text, "html.parser")

    # Cada card de imovel e um .row.mb-3 com fundo cinza claro, dentro da secao de imoveis
    cards = soup.select("section#imoveis .row.mb-3[style*='background-color']")

    imoveis = []
    for card in cards:
        imovel = _extrair_card(card, tipo)
        if not imovel:
            continue
        # Filtro de seguranca: tipo real (nao a busca) precisa ser residencial
        tipo_real = (imovel.get("tipo") or "").strip().lower()
        if not (any(t in tipo_real for t in TIPOS_RESIDENCIAIS_VALIDOS) and "comercial" not in tipo_real):
            continue
        # Filtro de seguranca: so Arapongas (a URL do imovel traz a cidade)
        if "arapongas" not in (imovel.get("url") or "").lower():
            continue
        imoveis.append(imovel)

    return imoveis


def extrair():
    sessao = requests.Session()
    vistos = set()
    todos_imoveis = []

    for tipo in TIPOS_LOCACAO:
        try:
            imoveis_tipo = _extrair_por_tipo(tipo, sessao)
        except requests.RequestException as erro:
            print(f"Erro ao acessar tipo '{tipo}': {erro}")
            continue

        for imovel in imoveis_tipo:
            if imovel["referencia"] not in vistos:
                vistos.add(imovel["referencia"])
                todos_imoveis.append(imovel)

    print(f"Total coletado na Imoveis Panorama: {len(todos_imoveis)} imoveis")
    return todos_imoveis


if __name__ == "__main__":
    resultado = extrair()
    for imovel in resultado:
        print(imovel)