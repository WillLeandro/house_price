"""
Popula dim_bairro (bairros necessários) e dim_imobiliaria
Dados coletados via busca (CNPJ público, redes sociais e sites das empresas)
em 25/07/2026.
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# =========================================================
# 1) Bairros necessários para as sedes das imobiliárias
# =========================================================
bairros = [
    ("Centro", "Arapongas", "PR"),
    ("Jardim Primavera", "Arapongas", "PR"),
]

cur.executemany(
    "INSERT OR IGNORE INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, ?, ?)",
    bairros
)
conn.commit()

cur.execute("SELECT b_id, b_nome FROM dim_bairro")
bairro_map = {nome: bid for bid, nome in cur.fetchall()}

# =========================================================
# 2) Imobiliárias
# =========================================================
# permite_scraping: 1 = robots.txt libera, 0 = bloqueado
imobiliarias = [
    dict(
        nome="Terra Santa Empreendimentos Imobiliários", bairro="Centro",
        endereco="Rua Noitibo, 195, Sala 01", cep="86701-310",
        telefone="(43) 3274-7261", whatsapp="(43) 98404-2416",
        site="https://www.terrasantaimoveis.com.br", creci="11401-J",
        permite_scraping=0,
        observacao="robots.txt bloqueia Disallow: /"
    ),
    dict(
        nome="Imobiliária Bertoni", bairro="Centro",
        endereco="Rua Pombas, 189", cep="86700-020",
        telefone="(43) 3172-3655", whatsapp=None,
        site="https://www.imobiliariabertoni.com.br", creci="3916-J",
        permite_scraping=0,
        observacao="robots.txt bloqueia; e-mail bertoni@imobiliariabertoni.com.br"
    ),
    dict(
        nome="Imobiliária Franjovi", bairro="Centro",
        endereco="Avenida Arapongas, 1551", cep="86700-140",
        telefone="(43) 3252-1033", whatsapp=None,
        site="https://www.imobiliariafranjovi.com.br", creci=None,
        permite_scraping=0,
        observacao="robots.txt bloqueia"
    ),
    dict(
        nome="Imobiliária Solara", bairro="Jardim Primavera",
        endereco="Rua Gaturamo, 486", cep=None,
        telefone="(43) 3312-3002", whatsapp="(43) 99861-3647",
        site="https://www.imobiliariasolara.com.br", creci="J-6621",
        permite_scraping=1,
        observacao="Scraping liberado, HTML server-side"
    ),
    dict(
        nome="BNZ Negócios Imobiliários", bairro="Centro",
        endereco="Rua Uirapuru, 685, Loja 07", cep="86700-060",
        telefone=None, whatsapp="(43) 99285-2094",
        site="https://www.bnznegociosimobiliarios.com.br", creci="7622-J",
        permite_scraping=0,
        observacao="robots.txt bloqueia"
    ),
    dict(
        nome="Imobiliária Shamar", bairro="Centro",
        endereco="Rua das Pombas, 1137", cep=None,
        telefone="(43) 3152-3459", whatsapp=None,
        site="https://www.imobiliariashamar.com.br", creci=None,
        permite_scraping=1,
        observacao="Liberado no robots.txt, mas site é SPA (JS) - precisa Selenium"
    ),
    dict(
        nome="Imobiliária Vale Verde", bairro="Centro",
        endereco="Rua Eurilemos, 944", cep="86701-230",
        telefone="(43) 3252-0403", whatsapp="(43) 99121-0403",
        site="https://www.imobiliariavaleverde.com.br", creci=None,
        permite_scraping=1,
        observacao="Liberado no robots.txt, mas site é SPA (JS) - precisa Selenium"
    ),
    dict(
        nome="Almeida Silva Imóveis", bairro=None,
        endereco=None, cep=None,
        telefone="(43) 99960-0029", whatsapp="(43) 99960-0029",
        site="https://www.almeidasilvaimoveis.com.br", creci="17873-F",
        permite_scraping=0,
        observacao="robots.txt bloqueia; endereço físico não localizado (corretor: Rogério Almeida Silva)"
    ),
    dict(
        nome="Imóveis Panorama", bairro="Centro",
        endereco="Rua Condor, 1539", cep="86700-135",
        telefone="(43) 3055-3711", whatsapp="(43) 99920-9924",
        site="https://www.imoveispanorama.com.br", creci="9774-J",
        permite_scraping=1,
        observacao="Scraping liberado, HTML server-side"
    ),
    dict(
        nome="Imobiliária Giuliano", bairro="Centro",
        endereco="Rua Drongo, 1007", cep="86701-220",
        telefone="(43) 3252-0114", whatsapp="(43) 9642-0225",
        site="https://www.imobiliariagiuliano.com.br", creci=None,
        permite_scraping=0,
        observacao="robots.txt bloqueia; e-mail giulianoimoveis@hotmail.com"
    ),
    dict(
        nome="Imobiliária Ricardo", bairro="Centro",
        endereco="Rua Marabu, 157", cep=None,
        telefone="(43) 3252-5107", whatsapp="(43) 99973-1040",
        site="https://www.imobiliariaricardo.com.br", creci="04827-J",
        permite_scraping=1,
        observacao="Scraping liberado, HTML server-side, dados ricos"
    ),
    dict(
        nome="Imobiliária e Loteadora Linham", bairro="Centro",
        endereco="Rua Tico-Tico, 136", cep="86701-180",
        telefone="(43) 3055-3233", whatsapp="(43) 99125-5510",
        site="https://www.imobiliarialinham.com.br", creci="J2975",
        permite_scraping=1,
        observacao="Scraping liberado, HTML server-side"
    ),
]

rows = []
for i in imobiliarias:
    b_id = bairro_map.get(i["bairro"]) if i["bairro"] else None
    rows.append((
        b_id, i["nome"], i["endereco"], i["cep"], i["telefone"], i["whatsapp"],
        i["site"], i["creci"], i["permite_scraping"], i["observacao"]
    ))

cur.executemany("""
    INSERT INTO dim_imobiliaria (
        b_id, i_nome, i_endereco, i_cep, i_telefone, i_whatsapp,
        i_site, i_creci, i_permite_scraping, i_observacao
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_imobiliaria")
total = cur.fetchone()[0]
print(f"dim_imobiliaria populada com {total} registros.")

cur.execute("""
    SELECT i.i_nome, b.b_nome, i.i_endereco, i.i_telefone, i.i_creci, i.i_permite_scraping
    FROM dim_imobiliaria i
    LEFT JOIN dim_bairro b ON b.b_id = i.b_id
    ORDER BY i.i_nome
""")
for row in cur.fetchall():
    print(row)

conn.close()