"""
extratores/extrator_ricardo.py

Extrator da Imobiliaria Ricardo (imobiliariaricardo.com.br).
Segue o contrato: expoe extrair() -> list[dict]

DESCOBERTA IMPORTANTE (26/07/2026): o site e feito em Next.js e embute
TODOS os dados dos imoveis como JSON puro dentro de uma tag
<script id="__NEXT_DATA__" type="application/json">...</script>
no proprio HTML da pagina. Isso significa:

  1. NAO precisamos de seletores CSS frageis (que quebram a cada
     redesign do site) - extraimos direto do JSON estruturado.
  2. NAO ha paginacao real nem scroll infinito de dados: o parametro
     da API "limit_imv" e 3000, e o campo "hasMore" e false para essa
     quantidade de imoveis. Ou seja, uma unica requisicao ja traz tudo.

Isso foi confirmado inspecionando o "Ver codigo-fonte" (Ctrl+U) da pagina:
https://www.imobiliariaricardo.com.br/imoveis/para-alugar/apartamento+casa+flat+sobrado/brasil?propertySubtypes=169&propertySubtypes=64&propertySubtypes=50&propertySubtypes=350&propertySubtypes=346&propertySubtypes=19&propertySubtypes=55&propertySubtypes=39&finalidade=1&order=menor_preco
que retornou "count":10,"totalPages":1,"hasMore":false.
"""

import json
import re
import requests

# URL que traz TODOS os tipos de imovel (apartamento, casa, flat, sobrado)
# para locacao de uma vez so.
LISTAGEM_URL = (
    "https://www.imobiliariaricardo.com.br/imoveis/para-alugar/"
    "apartamento+casa+flat+sobrado/brasil"
    "?propertySubtypes=169&propertySubtypes=64&propertySubtypes=50"
    "&propertySubtypes=350&propertySubtypes=346&propertySubtypes=19"
    "&propertySubtypes=55&propertySubtypes=39&finalidade=1&order=menor_preco"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjetoAcademicoUninter/1.0; "
                  "+trabalho de extensao universitaria - Ciencia de Dados)"
}


def _extrair_next_data(html):
    """Extrai e faz parse do JSON dentro da tag <script id="__NEXT_DATA__">."""
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html, re.DOTALL
    )
    if not match:
        raise ValueError(
            "Nao encontrei a tag __NEXT_DATA__ no HTML. "
            "O site pode ter mudado de framework/estrutura -- avisar Claude."
        )
    return json.loads(match.group(1))


def _item_para_dict(item):
    """Converte um item bruto de 'imoveis' do JSON no formato padrao do contrato."""
    referencia = item.get("imv_cod_gaia")
    if not referencia:
        return None  # itens como {"isBairro": true, ...} nao sao imoveis de verdade

    tipo_imovel = item.get("tipo_imovel") or {}
    endereco_rua = item.get("imv_endereco")
    numero = item.get("imv_end_numero")
    endereco = f"{endereco_rua}, {numero}" if endereco_rua else None

    return {
        "referencia": referencia,
        "tipo": tipo_imovel.get("timv_nome"),
        "finalidade": "Locacao",
        "nome": item.get("imv_titulo"),
        "bairro": item.get("imv_bairro") or "Nao informado",
        "endereco": endereco,
        "v_aluguel": item.get("imv_preco_locacao"),
        "v_condominio": item.get("imv_preco_cond"),
        "m2": item.get("imv_area_util") or item.get("imv_area_total"),
        "quartos": item.get("imv_qtd_dorm"),
        "salas": None,
        "banheiros": item.get("imv_qtd_banheiros"),
        "suite": None,
        "vagas": item.get("imv_qtd_vagas"),
        "descricao": item.get("imv_obs"),
        "url": item.get("url_amiga"),
    }


TIPOS_RESIDENCIAIS = {"casa", "apartamento", "sobrado", "flat", "kitnet", "kit-net", "sobreposta"}


def _e_residencial_e_locacao(item):
    """Filtro de seguranca: garante residencial, valor de aluguel presente
    e imovel localizado em Arapongas (nao outra cidade que a imobiliaria
    tambem atenda)."""
    tipo = (item.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_RESIDENCIAIS:
        return False
    if item.get("v_aluguel") is None:
        return False
    bairro = (item.get("bairro") or "")
    url = (item.get("url") or "").lower()
    if "arapongas" not in url and "arapongas" not in bairro.lower():
        return False
    return True


def extrair():
    """
    Busca a pagina de listagem (todos os tipos, locacao) e extrai os imoveis
    diretamente do JSON __NEXT_DATA__ embutido no HTML.
    """
    resposta = requests.get(LISTAGEM_URL, headers=HEADERS, timeout=20)
    resposta.raise_for_status()

    dados = _extrair_next_data(resposta.text)
    page_props = dados["props"]["pageProps"]

    total = page_props.get("count")
    tem_mais = page_props.get("hasMore")
    print(f"Total de imoveis reportado pelo site: {total} (hasMore={tem_mais})")

    imoveis_brutos = page_props.get("imoveis", [])
    imoveis = []
    for item in imoveis_brutos:
        convertido = _item_para_dict(item)
        if convertido:
            imoveis.append(convertido)

    imoveis = [i for i in imoveis if _e_residencial_e_locacao(i)]

    print(f"Total coletado na Imobiliaria Ricardo: {len(imoveis)} imoveis")

    if tem_mais:
        print(
            "AVISO: hasMore=true -- este filtro tem mais imoveis do que "
            "vieram numa unica pagina. Sera necessario investigar paginacao "
            "real (parametro 'page' ou similar) para esse caso."
        )

    return imoveis


if __name__ == "__main__":
    resultado = extrair()
    for imovel in resultado:
        print(imovel)