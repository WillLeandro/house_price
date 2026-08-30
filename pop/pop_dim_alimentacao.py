"""
Popula dim_alimentacao com supermercados, mercados de bairro, mini mercados
e lojas de conveniencia de Arapongas-PR.

Fonte: Google Places (via places_search), coletado em 25/07/2026.
Coordenadas e enderecos sao os reais do Google Maps -- NAO estimados/mockados
(diferente da tentativa anterior feita com IA generativa, que continha
numeros e CEPs incorretos).
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# cada item: (nome, tipo, endereco, bairro, cep, lat, lon, tamanho)
mercados = [
    # ---------------- Grandes redes / Atacarejo ----------------
    ("Verona Supermercados - Loja Centro", "Supermercado", "Av. Arapongas, 1369", "Centro", "86700-140", -23.407725, -51.44184, "Grande"),
    ("Verona Supermercados - Loja Flamingos", "Supermercado", "R. Irataua, 2307", "Conjunto Flamingos", "86703-300", -23.3918064, -51.4210562, "Grande"),
    ("Amigao Supermercados - Arapongas", "Supermercado", "R. Dancarino Rosado, 556", "Parque Veneza", "86701-660", -23.3990331, -51.4463859, "Grande"),
    ("Molicenter Supermercados - Loja 1", "Supermercado", "Av. Arapongas, 117", "Centro", "86701-010", -23.414275, -51.4314075, "Grande"),
    ("Box Atacadista", "Atacarejo", "R. Pinta Roxa, 10", "Vila Cascata", "86701-210", -23.4069877, -51.4301743, "Grande"),
    ("Max Atacadista Arapongas", "Atacarejo", "R. Tinguacu, 763", "Vila Industrial", "86706-176", -23.4187396, -51.4271442, "Grande"),

    # ---------------- Medio porte ----------------
    ("Rocha Supermercados - Rouxinol", "Supermercado", "R. Rouxinol, 1691", "Vila Aparecida", "86706-190", -23.4257143, -51.4258839, "Medio"),
    ("Rocha Supermercados - Santa Alice", "Supermercado", "R. Tico Tico Rei, 220", "Jardim Caravelle", "86702-666", -23.3907714, -51.4405039, "Medio"),
    ("Supermercado Vila Real", "Supermercado", "Av. Arapongas, 963", "Centro", "86700-140", -23.4097441, -51.4384231, "Medio"),
    ("Supermercado Centauro", "Supermercado", "R. Surucua, 163", "Conjunto Centauro", "86708-280", -23.4079908, -51.4517377, "Medio"),
    ("Veneza Supermercados - Jardim Cultura", "Supermercado", "R. Aguias, 1502", "Jardim Cultura", "86707-615", -23.4296316, -51.439616, "Medio"),
    ("Supermercado Veneza - Vila Aparecida", "Supermercado", "R. Caninde, 48", "Vila Aparecida", "86707-590", -23.4298054, -51.4266420, "Medio"),
    ("Supermercado Veneza - Jardim Caravelle", "Supermercado", "R. Sabia Poca, 170", "Jardim Caravelle", "86702-250", -23.3881473, -51.4420738, "Medio"),
    ("Supermercado Veneza - Jardim Petropolis", "Supermercado", "R. Cisne Negro, 1224", "Jardim Petropolis", "86709-678", -23.4140511, -51.4612604, "Medio"),
    ("Mercado Veneza - Jardim Bandeirantes", "Supermercado", "R. Japim, 207", "Jardim Bandeirantes", "86703-090", -23.401383, -51.4301788, "Medio"),
    ("Supermercado Flamingos", "Supermercado", "R. Loro Verde, 355", "Conjunto Del Condor", "86703-380", -23.391472, -51.4175723, "Medio"),
    ("Supermarket Too Good", "Supermercado", "R. Taperacu, 195", "Vila Sampaio", "86705-540", -23.4096456, -51.4238477, "Medio"),
    ("Mercado Municipal de Arapongas", "Mercado Municipal", "Av. Arapongas, 785", "Centro", "86700-050", -23.4108933, -51.4365967, "Medio"),

    # ---------------- Pequeno porte / mercado de bairro ----------------
    ("Mercado Aeroporto", "Mercado de Bairro", "R. Cuitelao, 206", "Jardim Aeroporto", "86702-100", -23.3892921, -51.4463491, "Pequeno"),
    ("Mercado Tropical", "Mercado de Bairro", "R. Garrincha, 345", "Conjunto Tropical", "86702-330", -23.3776766, -51.4623924, "Pequeno"),
    ("Market St. Anthony", "Mercado de Bairro", "R. Japuira, 295", "Conjunto Tropical", "86702-305", -23.3777448, -51.4595283, "Pequeno"),
    ("Mercado Bom Preco", "Mercado de Bairro", "R. Tico Tico do Bico Amarelo, 542", "Jardim Universitario", "86702-690", -23.3929555, -51.4542183, "Pequeno"),
    ("Mercado Lopes", "Mercado de Bairro", "R. Gaturamo Rei, 961", "Conjunto Flamingos III", "86703-482", -23.3933566, -51.4090576, "Pequeno"),
    ("Mini Mercado Vida Nova", "Mini Mercado", "R. Juriti Piranga, 503", "Conjunto Flamingos III", "86703-480", -23.3917976, -51.4091622, "Pequeno"),
    ("Mini Market Lopes", "Mini Mercado", "R. Tiribinha, 177", "Jardim dos Passaros", "86702-790", -23.3957915, -51.4538671, "Pequeno"),
    ("Mini Mercado Gardini", "Mini Mercado", "R. Caiapo, 49", "Aricanduva", "86719-000", -23.4932638, -51.4275813, "Pequeno"),
    ("Supermercado Sem Limite", "Mini Mercado", "R. Azulao da Serra, 105", "Conjunto Flamingos", "86703-350", -23.3946029, -51.4199841, "Pequeno"),
    ("MR Desconto - Petropolis", "Mini Mercado", "R. Cisne Negro, 1020", "Jardim Petropolis", "86709-010", -23.412279, -51.4615907, "Pequeno"),

    # ---------------- Conveniencia / mercearia ----------------
    ("Mercearia e Conveniencia 134", "Conveniencia", "R. Flamingo Chileno", "Familia", "86710-245", -23.418233, -51.4597339, "Pequeno"),
    ("Kim Conveniencia e Casa de Carnes", "Conveniencia", "R. Uirapuru, 1857", "Centro", "86703-380", -23.4052194, -51.4456148, "Pequeno"),
    ("Kim Conveniencia Flamingos", "Conveniencia", "R. Loro Verde, 375", "Conjunto Del Condor", "86703-380", -23.3918711, -51.4174092, "Pequeno"),
    ("Boss Conveniencia", "Conveniencia", "R. Rouxinol, 18", "Centro", "86700-075", -23.4097095, -51.4301388, "Pequeno"),
    ("On Beer Conveniencia", "Conveniencia", "R. Perdizes, 873", "Centro", "86700-180", -23.4050323, -51.4371749, "Pequeno"),
    ("Emporio - Tabacaria e Conveniencia", "Conveniencia", "Av. Arapongas, 1003", "Centro", "86700-140", -23.4092402, -51.438974, "Pequeno"),
    ("Coliseu Conveniencia e Tabacaria", "Conveniencia", "Av. Siriema, 420", "Parque Siomara", "86705-500", -23.4065153, -51.4227803, "Pequeno"),
    ("Bb Imports Conveniencia", "Conveniencia", "R. Tangara, 227", "Triangulo", "86709-224", -23.4051072, -51.4505451, "Pequeno"),
    ("La Casa da Beer Conveniencia", "Conveniencia", "R. Aguias, 820", "Jardim Cultura", "86707-615", -23.4251484, -51.4353089, "Pequeno"),
    ("Texas Beer Conveniencia e Tabacaria", "Conveniencia", "R. Rouxinol", "Jardim Planalto", "86706-302", -23.4472907, -51.4253536, "Pequeno"),
    ("JD Beer Conveniencia", "Conveniencia", "R. Albatroz Real, 15", "Conjunto Del Condor", "86703-341", -23.3934561, -51.4213098, "Pequeno"),
    ("Galpao Beer Conveniencia e Tabacaria", "Conveniencia", "R. Tangara, 1090", "Jardim Petropolis", "86709-000", -23.4059258, -51.4594543, "Pequeno"),
    ("ZS Conveniencia e Tabacaria", "Conveniencia", "R. Quete, 725", "Centro", "86706-405", -23.4544443, -51.4316526, "Pequeno"),

    # ---------------- Emporio / hortifruti ----------------
    ("Emporio Sabor da Serra", "Emporio", "R. Tucanos, 585", "Centro", "86700-070", -23.4137988, -51.4361273, "Pequeno"),
    ("Oba Mais Sabor Hortifruti", "Hortifruti", "R. Corruira", "Jardim Sao Cristovao", "86709-430", -23.4064046, -51.4469744, "Pequeno"),
]

# --- 1) Garantir que todos os bairros existam em dim_bairro ---
bairros_unicos = sorted(set(b for (_, _, _, b, _, _, _, _) in mercados))
cur.executemany(
    "INSERT OR IGNORE INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, 'Arapongas', 'PR')",
    [(b,) for b in bairros_unicos]
)
conn.commit()

cur.execute("SELECT b_id, b_nome FROM dim_bairro")
bairro_map = {nome: bid for bid, nome in cur.fetchall()}

# --- 2) Popular dim_alimentacao ---
rows = []
for nome, tipo, endereco, bairro, cep, lat, lon, tamanho in mercados:
    rows.append((bairro_map[bairro], tipo, nome, endereco, cep, lat, lon, tamanho))

cur.executemany("""
    INSERT INTO dim_alimentacao (
        b_id, a_tipo, a_nome, a_endereco, a_cep, a_latitude, a_longitude, a_tamanho
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_alimentacao")
print("Total em dim_alimentacao:", cur.fetchone()[0])

cur.execute("SELECT COUNT(DISTINCT b_id) FROM dim_alimentacao")
print("Bairros distintos cobertos:", cur.fetchone()[0])

cur.execute("SELECT a_tamanho, COUNT(*) FROM dim_alimentacao GROUP BY a_tamanho")
print("\nPor tamanho:")
for row in cur.fetchall():
    print(" ", row)

cur.execute("SELECT a_tipo, COUNT(*) FROM dim_alimentacao GROUP BY a_tipo ORDER BY 2 DESC")
print("\nPor tipo:")
for row in cur.fetchall():
    print(" ", row)

conn.close()