"""
Script de criação do schema do banco de dados
Projeto: Recomendação de bairros por custo-benefício - Arapongas/PR

Estrutura "hub and spoke": dim_bairro é a tabela central, referenciada
por saude, educacao, alimentacao, lazer, imobiliaria e moradia.
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

cur.executescript("""
-- =========================================================
-- Limpeza (permite rodar o script de novo do zero)
-- =========================================================
DROP TABLE IF EXISTS dim_moradia;
DROP TABLE IF EXISTS dim_imobiliaria;
DROP TABLE IF EXISTS dim_lazer;
DROP TABLE IF EXISTS dim_alimentacao;
DROP TABLE IF EXISTS dim_educacao;
DROP TABLE IF EXISTS dim_saude;
DROP TABLE IF EXISTS dim_bairro;

-- =========================================================
-- dim_bairro (tabela central / hub)
-- =========================================================
CREATE TABLE dim_bairro (
    b_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    b_nome      TEXT NOT NULL,
    b_cidade    TEXT NOT NULL DEFAULT 'Arapongas',
    b_estado    TEXT NOT NULL DEFAULT 'PR',
    b_latitude  REAL,
    b_longitude REAL,
    UNIQUE (b_nome, b_cidade)
);

-- =========================================================
-- dim_saude
-- =========================================================
CREATE TABLE dim_saude (
    s_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    b_id        INTEGER NOT NULL,
    s_tipo      TEXT,     -- Hospital, UBS, Clínica, Farmácia...
    s_nome      TEXT NOT NULL,
    s_endereco  TEXT,
    s_cep       TEXT,
    s_latitude  REAL,
    s_longitude REAL,
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id)
);
CREATE INDEX idx_saude_bairro ON dim_saude(b_id);

-- =========================================================
-- dim_educacao
-- =========================================================
CREATE TABLE dim_educacao (
    e_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    b_id        INTEGER NOT NULL,
    e_tipo      TEXT,     -- Creche, Escola Municipal, Estadual, Faculdade...
    e_nome      TEXT NOT NULL,
    e_endereco  TEXT,
    e_cep       TEXT,
    e_latitude  REAL,
    e_longitude REAL,
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id)
);
CREATE INDEX idx_educacao_bairro ON dim_educacao(b_id);

-- =========================================================
-- dim_alimentacao
-- =========================================================
CREATE TABLE dim_alimentacao (
    a_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    b_id        INTEGER NOT NULL,
    a_tipo      TEXT,     -- Mercado, Padaria, Restaurante, Feira...
    a_nome      TEXT NOT NULL,
    a_endereco  TEXT,
    a_cep       TEXT,
    a_latitude  REAL,
    a_longitude REAL,
    a_tamanho   TEXT CHECK (a_tamanho IN ('Pequeno', 'Medio', 'Grande')),
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id)
);
CREATE INDEX idx_alimentacao_bairro ON dim_alimentacao(b_id);

-- =========================================================
-- dim_lazer
-- =========================================================
CREATE TABLE dim_lazer (
    l_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    b_id        INTEGER NOT NULL,
    l_tipo      TEXT,     -- Praça, Parque, Academia, Clube...
    l_nome      TEXT NOT NULL,
    l_endereco  TEXT,
    l_cep       TEXT,
    l_latitude  REAL,
    l_longitude REAL,
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id)
);
CREATE INDEX idx_lazer_bairro ON dim_lazer(b_id);

-- =========================================================
-- dim_imobiliaria (cadastro da empresa: endereço, telefone, site)
-- =========================================================
CREATE TABLE dim_imobiliaria (
    i_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    b_id            INTEGER,             -- bairro onde fica a sede (pode ser NULL se desconhecido)
    i_nome          TEXT NOT NULL,
    i_endereco      TEXT,
    i_cep           TEXT,
    i_telefone      TEXT,
    i_whatsapp      TEXT,
    i_site          TEXT NOT NULL,
    i_creci         TEXT,
    i_latitude      REAL,
    i_longitude     REAL,
    i_permite_scraping INTEGER DEFAULT 1,  -- 1 = robots.txt libera, 0 = bloqueado
    i_observacao    TEXT,
    UNIQUE (i_site),
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id)
);
CREATE INDEX idx_imobiliaria_bairro ON dim_imobiliaria(b_id);

-- =========================================================
-- dim_moradia (imóveis anunciados para locação)
-- =========================================================
CREATE TABLE dim_moradia (
    m_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    i_id              INTEGER NOT NULL,   -- imobiliária que anuncia
    b_id              INTEGER NOT NULL,   -- bairro do imóvel
    m_referencia      TEXT,               -- código/ref do anúncio no site de origem
    m_tipo            TEXT,               -- Casa, Apartamento, Sobrado...
    m_finalidade      TEXT DEFAULT 'Locacao',
    m_nome            TEXT,               -- título do anúncio
    m_endereco        TEXT,
    m_v_aluguel       REAL,
    m_v_condominio    REAL,
    m_m2              REAL,
    m_quartos         INTEGER,
    m_salas           INTEGER,
    m_banheiros       INTEGER,
    m_suite           INTEGER,
    m_vagas           INTEGER,
    m_descricao       TEXT,
    m_url             TEXT,
    m_data_coleta     TEXT,
    m_latitude        REAL,
    m_longitude       REAL,
    m_status              TEXT DEFAULT 'Ativo',  -- 'Ativo' ou 'Inativo' (saiu do ar / alugado)
    m_primeira_coleta     TEXT,                  -- data em que o anuncio foi visto pela 1a vez
    m_ultima_verificacao  TEXT,                  -- data da ultima confirmacao de que segue ativo
    FOREIGN KEY (i_id) REFERENCES dim_imobiliaria(i_id),
    FOREIGN KEY (b_id) REFERENCES dim_bairro(b_id),
    UNIQUE (i_id, m_referencia)
);
CREATE INDEX idx_moradia_bairro ON dim_moradia(b_id);
CREATE INDEX idx_moradia_imobiliaria ON dim_moradia(i_id);
""")

conn.commit()

# Conferir tabelas criadas
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
print("Tabelas criadas:")
for (nome,) in cur.fetchall():
    print(" -", nome)

conn.close()
print(f"\nBanco criado em: {DB_PATH}")