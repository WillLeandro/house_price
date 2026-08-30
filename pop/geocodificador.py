"""
Geocodifica os bairros de dim_bairro que tem imoveis (dim_moradia),
preenchendo b_latitude/b_longitude. Fonte: Google Places, coletado em
27/07/2026.

IMPORTANTE - 2 casos sem resolucao confiavel:
  - "Jardim Paraiso": o Google Places so retornou um bairro de mesmo nome
    em APUCARANA, nao em Arapongas. Usamos as coordenadas do Centro como
    fallback aproximado (b_geocodificacao_incerta=1 -- ver nota abaixo).
  - "Nao informado": bairro nao identificado no imovel de origem, nao da
    pra geocodificar por definicao. Fica sem coordenada (NULL), e o
    calculo de distancia vai pular esses imoveis.

Alguns bairros usaram como proxy a coordenada de um estabelecimento
comercial de mesmo nome (ex: "Grupo Santa Alice" para o bairro
"Jardim Santa Alice") quando o Google nao trouxe o poligono do bairro
em si -- sao aproximacoes razoaveis, mas nao sao o centroide exato.

Rode este script UMA VEZ, depois de rodar main.py (extratores de moradia),
para poder calcular distancias no indice de custo-beneficio.
"""

import os
import sqlite3

DB_PATH = "db/arapongas.db"  # ajuste o caminho se necessario

if not os.path.exists(DB_PATH):
    raise SystemExit(
        f"ERRO: nao encontrei o banco em '{DB_PATH}' (rodando a partir de "
        f"'{os.getcwd()}').\n"
        f"Confira se voce esta rodando este script da RAIZ do projeto "
        f"(onde fica a pasta db/), e se o create_db.py + os pop_dim_*.py "
        f"ja foram rodados antes deste."
    )

# (nome_bairro, latitude, longitude, incerto)
# incerto=1 significa que a coordenada e uma aproximacao grosseira, nao
# o centroide real do bairro -- usar com cautela no indice.
COORDENADAS_BAIRROS = [
    ("Centro", -23.4090905, -51.4375207, 0),
    ("Cidade Jardim", -23.4195296, -51.4770496, 1),
    ("Conjunto Aguias", -23.3815371, -51.4073385, 0),
    ("Conjunto Centauro", -23.4082233, -51.4539298, 0),
    ("Conjunto Novo Centauro", -23.4211824, -51.4532734, 0),
    ("Conjunto Ulisses Guimarães", -23.4187723, -51.4191473, 0),
    ("Hermínio Maria", -23.4321582, -51.4412884, 1),
    ("Jardim Aeroporto", -23.3821962, -51.4440838, 0),
    ("Jardim Arapongas", -23.3995652, -51.4499912, 0),
    ("Jardim Bandeirantes", -23.3960219, -51.4270210, 0),
    ("Jardim Casa Branca", -23.4323178, -51.4483135, 1),
    ("Jardim Morumbi", -23.4197100, -51.4460529, 0),
    ("Jardim Mônaco", -23.3943928, -51.4558992, 0),
    ("Jardim Mônaco II", -23.3943928, -51.4558992, 1),  # proxy: mesmo que Jardim Monaco
    ("Jardim Panorama", -23.4121424, -51.4480220, 0),
    ("Jardim Paraná", -23.3786470, -51.4439139, 1),
    ("Jardim Paraíso", -23.4282967, -51.4394831, 1),  # media de 2 ruas reais do bairro (Rua Tururim + Rua Melro Mineiro), via enderecos dos imoveis
    ("Jardim Portal das Flores", -23.4008146, -51.4348956, 0),
    ("Jardim Primavera", -23.3988568, -51.4453965, 0),
    ("Jardim Santa Alice", -23.3920020, -51.4236615, 1),
    ("Jardim Santo Antônio", -23.4141996, -51.4184912, 0),
    ("Jardim Vale Das Perobas", -23.4089326, -51.4660752, 1),
    ("Parque Veneza", -23.4005986, -51.4427711, 0),
    ("Residencial Bem Viver", -23.3944480, -51.4807689, 0),
    ("Vila Nova", -23.4208489, -51.4348956, 0),
    ("Vila Passos", -23.4114532, -51.4235761, 0),
    ("Vila Sampaio", -23.4136041, -51.4250525, 0),
    ("Vila Triângulo", -23.3998381, -51.4703430, 0),
    # --- Adicionados em 27/07/2026 (apareceram em uma nova rodada do banco) ---
    ("Bem Viver", -23.394448, -51.4807689, 0),  # mesmo local de "Residencial Bem Viver"
    ("Conjunto Residencial Piacenza", -23.4446552, -51.4383187, 1),  # proxy: oficina Piacenza (mais proxima)
    ("Jardim Caravelle", -23.3913975, -51.4434275, 0),
    ("Jardim Columbia 3", -23.439249, -51.4335831, 1),  # proxy: Jardim Columbia IV (mais proximo)
    ("Jardim Mônaco I", -23.3943928, -51.4558992, 1),  # proxy: mesmo que Jardim Monaco
    ("Jardim Paulista", -23.4272431, -51.4299738, 0),
    ("Vila Bernardes", -23.4164898, -51.4263648, 0),
    ("Vila Natal", -23.4164932, -51.4339112, 0),
    ("Vila São João", -23.4176381, -51.4378488, 0),
    ("Nao informado", -23.4090905, -51.4375207, 1),  # fallback: centro da cidade
]

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dim_bairro';")
if cur.fetchone() is None:
    conn.close()
    raise SystemExit(
        f"ERRO: o arquivo '{DB_PATH}' existe, mas nao tem a tabela "
        f"dim_bairro. Rode create_db.py (schema) e os pop_dim_*.py "
        f"antes de rodar este script."
    )

# Adiciona a coluna de incerteza, se ainda nao existir
cur.execute("PRAGMA table_info(dim_bairro);")
colunas = {row[1] for row in cur.fetchall()}
if "b_geocodificacao_incerta" not in colunas:
    cur.execute("ALTER TABLE dim_bairro ADD COLUMN b_geocodificacao_incerta INTEGER DEFAULT 0;")
    print("Coluna b_geocodificacao_incerta adicionada.")

atualizados = 0
nao_encontrados = []

for nome, lat, lon, incerto in COORDENADAS_BAIRROS:
    cur.execute(
        "UPDATE dim_bairro SET b_latitude=?, b_longitude=?, b_geocodificacao_incerta=? "
        "WHERE b_nome=? AND b_cidade='Arapongas'",
        (lat, lon, incerto, nome),
    )
    if cur.rowcount == 0:
        nao_encontrados.append(nome)
    else:
        atualizados += cur.rowcount

conn.commit()

print(f"Bairros atualizados com coordenadas: {atualizados}")
if nao_encontrados:
    print(f"AVISO: nao encontrei estes nomes exatos em dim_bairro (conferir grafia): {nao_encontrados}")

# Conferencia: quantos bairros COM IMOVEL ainda ficaram sem coordenada
cur.execute("""
    SELECT DISTINCT b.b_nome
    FROM dim_moradia m
    JOIN dim_bairro b ON b.b_id = m.b_id
    WHERE b.b_latitude IS NULL
""")
sem_coordenada = [r[0] for r in cur.fetchall()]
print(f"\nBairros com imovel mas AINDA sem coordenada: {sem_coordenada}")

conn.close()