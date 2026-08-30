"""
extrators/base.py

Modulo comum a todos os extratores de imobiliarias.
Define o contrato que cada extrator deve seguir e a logica de
sincronizacao incremental com a dim_moradia.

CONTRATO: cada extrator (extrator_xxx.py) deve expor uma funcao:

    def extrair() -> list[dict]

Cada dict da lista deve ter as chaves (todas em minusculo):
    referencia   (str, obrigatorio - codigo/ref do anuncio no site de origem)
    tipo         (str) - Casa, Apartamento, Sobrado...
    finalidade   (str) - Locacao / Venda
    nome         (str ou None) - titulo do anuncio
    bairro       (str, obrigatorio) - nome do bairro (sera resolvido para b_id)
    endereco     (str ou None)
    v_aluguel    (float ou None)
    v_condominio (float ou None)
    m2           (float ou None)
    quartos      (int ou None)
    salas        (int ou None)
    banheiros    (int ou None)
    suite        (int ou None)
    vagas        (int ou None)
    descricao    (str ou None)
    url          (str, obrigatorio)
"""

import sqlite3
from datetime import date

DB_PATH = "./db/arapongas.db"


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def obter_ou_criar_bairro(cur, nome_bairro, cidade="Arapongas", estado="PR"):
    """Retorna o b_id do bairro, criando-o em dim_bairro se necessario."""
    cur.execute(
        "SELECT b_id FROM dim_bairro WHERE b_nome = ? AND b_cidade = ?",
        (nome_bairro, cidade),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, ?, ?)",
        (nome_bairro, cidade, estado),
    )
    return cur.lastrowid


def obter_i_id(cur, site_url_fragmento):
    """
    Busca o i_id da imobiliaria pelo pedaco de URL do site
    (ex: 'imobiliariaricardo.com.br').
    """
    cur.execute(
        "SELECT i_id FROM dim_imobiliaria WHERE i_site LIKE ?",
        (f"%{site_url_fragmento}%",),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(
            f"Imobiliaria com site contendo '{site_url_fragmento}' nao encontrada "
            f"em dim_imobiliaria. Confira se ela foi cadastrada antes de rodar o extrator."
        )
    return row[0]


def sincronizar(i_id, imoveis_coletados, nome_imobiliaria="(sem nome)"):
    """
    Sincroniza os imoveis coletados de UMA imobiliaria com a dim_moradia.

    - Novo (referencia nao existe para essa imobiliaria) -> INSERE, status='Ativo'
    - Ja existe -> ATUALIZA dados, mantem status='Ativo', atualiza m_ultima_verificacao
    - Existia no banco mas NAO veio na coleta desta vez -> marca status='Inativo'

    Retorna um dict com contadores: {'novos': N, 'atualizados': N, 'inativados': N}
    """
    conn = conectar()
    cur = conn.cursor()
    hoje = date.today().isoformat()

    referencias_coletadas = set()
    novos = 0
    atualizados = 0

    for item in imoveis_coletados:
        referencia = item["referencia"]
        referencias_coletadas.add(referencia)

        b_id = obter_ou_criar_bairro(cur, item["bairro"])

        cur.execute(
            "SELECT m_id FROM dim_moradia WHERE i_id = ? AND m_referencia = ?",
            (i_id, referencia),
        )
        existente = cur.fetchone()

        # Campos comuns aos dois casos (INSERT e UPDATE), na mesma ordem
        campos_comuns = (
            b_id, item.get("tipo"), item.get("finalidade", "Locacao"),
            item.get("nome"), item.get("endereco"), item.get("v_aluguel"),
            item.get("v_condominio"), item.get("m2"), item.get("quartos"),
            item.get("salas"), item.get("banheiros"), item.get("suite"),
            item.get("vagas"), item.get("descricao"), item["url"],
        )

        if existente:
            m_id = existente[0]
            cur.execute("""
                UPDATE dim_moradia SET
                    b_id=?, m_tipo=?, m_finalidade=?, m_nome=?, m_endereco=?,
                    m_v_aluguel=?, m_v_condominio=?, m_m2=?, m_quartos=?,
                    m_salas=?, m_banheiros=?, m_suite=?, m_vagas=?, m_descricao=?,
                    m_url=?, m_ultima_verificacao=?, m_status='Ativo'
                WHERE m_id=?
            """, campos_comuns + (hoje, m_id))
            atualizados += 1
        else:
            cur.execute("""
                INSERT INTO dim_moradia (
                    i_id, m_referencia, b_id, m_tipo, m_finalidade, m_nome,
                    m_endereco, m_v_aluguel, m_v_condominio, m_m2, m_quartos,
                    m_salas, m_banheiros, m_suite, m_vagas, m_descricao, m_url,
                    m_data_coleta, m_ultima_verificacao, m_status, m_primeira_coleta
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Ativo', ?)
            """, (i_id, referencia) + campos_comuns + (hoje, hoje, hoje))
            novos += 1

    # Marca como inativo qualquer anuncio dessa imobiliaria que estava no banco
    # mas nao apareceu na coleta de agora
    cur.execute(
        "SELECT m_referencia FROM dim_moradia WHERE i_id = ? AND m_status = 'Ativo'",
        (i_id,),
    )
    referencias_no_banco = {row[0] for row in cur.fetchall()}
    referencias_sumidas = referencias_no_banco - referencias_coletadas

    inativados = 0
    for ref in referencias_sumidas:
        cur.execute(
            "UPDATE dim_moradia SET m_status='Inativo' WHERE i_id=? AND m_referencia=?",
            (i_id, ref),
        )
        inativados += 1

    conn.commit()
    conn.close()

    resultado = {"novos": novos, "atualizados": atualizados, "inativados": inativados}
    print(f"[{nome_imobiliaria}] novos={novos} atualizados={atualizados} inativados={inativados}")
    return resultado

