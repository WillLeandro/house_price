"""
Popula dim_lazer com pracas/parques, cinema/teatro, boliche, SESC/SESI,
clubes recreativos e academias de Arapongas-PR.

Fonte: Google Places (via places_search), coletado em 25/07/2026.
Enderecos e coordenadas sao os reais do Google Maps.
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# cada item: (nome, tipo, endereco, bairro, cep, lat, lon)
lazer = [
    # ---------------- Pracas e parques ----------------
    ("Praca da Saudade", "Praca", "Av. Arapongas, 119", "Centro", "86720-000", -23.4033664, -51.4476912),
    ("Praca Carlos Gomes", "Praca", "Rod. Melo Peixoto, 1660", "Zona Rural", None, -23.4957705, -51.425278),
    ("Parque Municipal dos Passaros", "Parque", "R. Tico Tico, 716-952", "Vila Natal", "86707-020", -23.4183178, -51.43588),
    ("Praca Maua", "Praca", "Av. Arapongas, 35", "Centro", "86701-378", -23.4150481, -51.4302551),
    ("Praca Maria Aguiar", "Praca", "R. Andorinhas, 39", "Centro", "86701-190", -23.4110064, -51.4305746),
    ("Parque das Nacoes", "Parque", "R. Suindara, 66", "Jardim Sao Cristovao", "86709-250", -23.4098509, -51.4508968),
    ("Praca Luis Treglia Junior", "Praca", "Ac. Luis Treglia Junior, 112", "Centro", "86701-360", -23.4046926, -51.4463849),

    # ---------------- Cultura / Cinema ----------------
    ("Cine Teatro Maua", "Cinema/Teatro", "R. Uirapuru, 55", "Centro", "86701-010", -23.4158831, -51.4309541),
    ("Cine Gracher (Havan Arapongas)", "Cinema/Teatro", "BR-369, s/n", "Parque Industrial IV", "86706-430", -23.4329259, -51.4215267),

    # ---------------- Boliche ----------------
    ("Go Strike Boliche", "Boliche", "R. Ibis, 440", "Centro", "86700-195", -23.4074698, -51.4406448),

    # ---------------- SESC / SESI (esporte e lazer) ----------------
    ("Sesc Arapongas", "SESC", "R. Tico Tico Rei, 41", "Jardim Caravelle", "86702-666", -23.3920716, -51.4420874),
    ("Sesi Arapongas - Ginasio Poliesportivo", "SESI", "Av. Maracana, 3260", "Vila Araponguinha", "86705-582", -23.4037928, -51.4278896),

    # ---------------- Clubes recreativos ----------------
    ("Clube Comercial Arapongas", "Clube", "R. Condor, 1100", "Centro", "86701-210", -23.4104739, -51.4335627),
    ("Clube Campestre Arapongas", "Clube", "R. Iratauá, 1216", "Conjunto Flamingos", "86703-300", -23.4014685, -51.4236596),
    ("Clube Comercial de Arapongas (Sede de Campo)", "Clube", None, "Conjunto Tropical", None, -23.3712165, -51.4659842),
    ("Clube Society Arapongas", "Clube", "R. Sovi, 146", "Parque Industrial", "86706-570", -23.434366, -51.4229786),
    ("Souza Racquet Club", "Clube", "R. Pavao, 1543", "Centro", "86708-556", -23.4150894, -51.4482372),
    ("Quadra Recanto Futsal e Volei", "Clube", "R. Uirapuru, 1790", "Centro", "86701-010", -23.4057545, -51.445058),
    ("Arena Farm - Beach Tennis", "Clube", "R. Tacha do Sul, 50", "Santa Alice", "86701-838", -23.3893717, -51.4353399),

    # ---------------- Academias ----------------
    ("Bodyfit", "Academia", "Av. Arapongas, 1399", "Centro", "86700-140", -23.4073463, -51.4421558),
    ("Iron Life", "Academia", "R. Perdizes, 399", "Centro", "86701-420", -23.4077213, -51.4332139),
    ("MR Studio Arapongas", "Academia", "R. Tucanos, 65, Sl 3", "Centro", "86700-070", -23.417262, -51.432093),
    ("Academia MegaFit Prime Arapongas", "Academia", "R. Uirapuru, 913", "Centro", "86700-130", -23.4106601, -51.4388095),
    ("Atom Ltda", "Academia", "R. Tangara, 893", "Jardim Vale das Perobas II", "86709-000", -23.4060661, -51.4572498),
    ("MVB Fit Academia", "Academia", "R. Tucanos, 1959", "Centro", "86701-020", -23.4049238, -51.4469818),
    ("Pink Academia de Ginastica", "Academia", "R. Harpia, 810", "Centro", "86701-260", -23.4101642, -51.4411812),
    ("Academia Ph.D Sports Arapongas", "Academia", "Av. Arapongas, 1332", "Centro", "86700-140", -23.4073541, -51.4413457),
]

# --- 1) Garantir que todos os bairros existam em dim_bairro ---
bairros_unicos = sorted(set(b for (_, _, _, b, _, _, _) in lazer))
cur.executemany(
    "INSERT OR IGNORE INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, 'Arapongas', 'PR')",
    [(b,) for b in bairros_unicos]
)
conn.commit()

cur.execute("SELECT b_id, b_nome FROM dim_bairro")
bairro_map = {nome: bid for bid, nome in cur.fetchall()}

# --- 2) Popular dim_lazer ---
rows = []
for nome, tipo, endereco, bairro, cep, lat, lon in lazer:
    rows.append((bairro_map[bairro], tipo, nome, endereco, cep, lat, lon))

cur.executemany("""
    INSERT INTO dim_lazer (
        b_id, l_tipo, l_nome, l_endereco, l_cep, l_latitude, l_longitude
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_lazer")
print("Total em dim_lazer:", cur.fetchone()[0])

cur.execute("SELECT COUNT(DISTINCT b_id) FROM dim_lazer")
print("Bairros distintos cobertos:", cur.fetchone()[0])

cur.execute("SELECT l_tipo, COUNT(*) FROM dim_lazer GROUP BY l_tipo ORDER BY 2 DESC")
print("\nPor tipo:")
for row in cur.fetchall():
    print(" ", row)

conn.close()