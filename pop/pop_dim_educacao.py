"""
Popula dim_educacao com escolas municipais, colegios estaduais, CMEIs
(creches municipais), faculdades/universidades e escolas particulares
de Arapongas-PR.

Fonte: Google Places (via places_search), coletado em 25/07/2026.
Enderecos e coordenadas sao os reais do Google Maps.
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# cada item: (nome, tipo, endereco, bairro, cep, lat, lon)
escolas = [
    # ---------------- Escolas Municipais (Ensino Fundamental I) ----------------
    ("Escola Municipal Dr. Maria Hercilia Horacio Stawinski", "Escola Municipal", "R. Formigueiro Estrelado, 141", "Conjunto Padre Bernardo Merckel", "86706-260", -23.4497533, -51.4268521),
    ("Escola Municipal Professora Antonica G. Franciosi", "Escola Municipal", "R. Pavao, 26", "Centro", "86701-290", -23.403318, -51.4404917),
    ("Escola Municipal Professora Alzira Horvatich", "Escola Municipal", "R. Garca Branca, 325", "Conjunto Del Condor", "86703-370", -23.3934939, -51.4184661),
    ("Escola Municipal Professora Aleydah Costa Santos", "Escola Municipal", "R. Bigua Una, 215", "Jardim Monte Carlo", "86704-200", -23.3816356, -51.4147262),
    ("Escola Municipal Professora Nereide de Souza Camargo", "Escola Municipal", "R. Bico de Veludo, S/N", "Conjunto Centauro", "86709-320", -23.408825, -51.4516021),
    ("Escola Municipal Jose Bernardo dos Santos", "Escola Municipal", "R. Tetraz, 550", "Vila Industrial", "86706-050", -23.4185725, -51.4248727),
    ("Escola Municipal Albor Pimpao Ferreira", "Escola Municipal", "R. Codornix, 290", "Jardim Lorena", "86707-260", -23.4224205, -51.4280014),
    ("Escola Municipal Julio Savieto", "Escola Municipal", "R. Arataiacu, 729", "Centro", "86707-005", -23.4175313, -51.4337523),
    ("Escola Municipal Desembargador Clotario Portugal", "Escola Municipal", "R. Tuim, 217", "Vila Triangulo", "86709-380", -23.4059844, -51.4508411),
    ("Escola Municipal Padre Germano Mayer", "Escola Municipal", "R. Ave Lira, 140", "Vila Nova", "86707-060", -23.4195908, -51.4319022),

    # ---------------- Colegios Estaduais (Ensino Fundamental II / Medio) ----------------
    ("Colegio Estadual Profa. Ivanilde de Noronha", "Colegio Estadual", "R. Rouxinol, 2008", "Vila Aparecida", "86706-198", -23.4284352, -51.4264058),
    ("Colegio Estadual Emilio de Menezes", "Colegio Estadual", "R. Quiscalo, 185", "Centro", "86700-445", -23.4204218, -51.429623),
    ("Colegio Estadual Unidade Polo", "Colegio Estadual", "R. Pavao, 831", "Centro", "86700-215", -23.4097176, -51.4451088),
    ("Colegio Estadual Civico Militar Marques de Caravelas", "Colegio Estadual", "R. Uirapuru, 295", "Centro", "86700-060", -23.414043, -51.433881),
    ("Colegio Estadual Irondi Mantovani Pugliesi", "Colegio Estadual", "R. Uru do Campo, 50", "Casa Familia Arapongas I", "86706-370", -23.4545218, -51.4311545),
    ("Julia Wanderley - E E Profa-Ef", "Colegio Estadual", "R. das Pombas, 1443", "Centro", "86701-410", -23.4031797, -51.442476),
    ("Colegio Estadual Nadir Mendes Montanha", "Colegio Estadual", "R. Macuru, 199", "Conjunto Flamingos", "86703-440", -23.3954991, -51.419136),
    ("Escola Estadual Profa. Regina Celia Alves dos Santos Domit", "Colegio Estadual", "R. Codornix, 290", "Jardim Lorena", "86707-260", -23.4225807, -51.4278984),
    ("Antonio G Novaes - C E-Ef M Profis", "Colegio Estadual", "R. Perdizes, 910", "Centro", "86701-420", -23.4049604, -51.4365801),
    ("Antonio Racanello Sampaio - C E-Ef M", "Colegio Estadual", "R. Guacuru, 190", "Vila Araponguinha", "86705-600", -23.4044618, -51.4239836),

    # ---------------- CMEIs (Creches municipais) ----------------
    ("CMEI Primeiros Passos", "CMEI", "R. Tico Tico Rei, 79", "Jardim Caravelle", "86702-666", -23.3917204, -51.4421796),
    ("CMEI Helena Garanhani Escobal", "CMEI", "R. Eurilemos, 1159", "Centro", "86708-250", -23.4146813, -51.439517),
    ("CMEI Maria Aparecida Fernandes Weiss", "CMEI", "R. Albatroz Real, 111", "Conjunto Del Condor", "86703-341", -23.3929374, -51.4208446),
    ("CMEI Ismenia Antoniolli Grassano", "CMEI", "R. Juriti Safira, s/n", "Casa Familia Arapongas IV", "86709-820", -23.4183211, -51.4584617),
    ("CMEI Padre Bernardo Merckel", "CMEI", "R. Mergulhador, 720", "Jardim Bandeirantes", "86703-055", -23.3964038, -51.4306628),
    ("CMEI Maria Hilda Santiago Grassano", "CMEI", "R. Maitaca Roxa", "Conjunto Flamingos III", "86703-650", -23.3957262, -51.4127028),
    ("CMEI Sao Miguel Arcanjo", "CMEI", "R. Bem-Te-Vi-Cinza, 100", "Centro", "86702-191", -23.3952164, -51.4531263),
    ("CMEI Izaura dos Santos Vieira", "CMEI", "R. Perdizes Branca, 115", "Jardim Alto da Boa Vista", "86706-790", -23.4570821, -51.4295503),
    ("CMEI Dolores Lazaro Martins - Tia Nena", "CMEI", "R. Quetzal, 150", "Vila Bernardes", "86705-062", -23.4142947, -51.4235303),
    ("CMEI Professora Sonia Saikawa Koga", "CMEI", "R. Tesoura, 43", "Jardim Bandeirantes", "86703-040", -23.4043937, -51.4294352),

    # ---------------- Faculdades / Universidades ----------------
    ("Unopar", "Universidade", "Rodovia PR 218, Km 01, S/N", "Jardim Universitario", "86702-670", -23.3883705, -51.4499208),
    ("IFPR Campus Avancado Arapongas", "Instituto Federal", "R. Surucua Acu, 321", "Vila Araponguinha", "86705-590", -23.4035137, -51.4261489),
    ("EAD UniCesumar - Arapongas", "Universidade", "R. Falcao, 768", "Centro", "86700-005", -23.4092098, -51.437381),
    ("Unopar e Anhanguera - Polo Pombas", "Universidade", "R. das Pombas, 144, sala 05", "Centro", "86700-020", -23.4099431, -51.4315356),
    ("Faculdade Estacio - Polo EAD Arapongas", "Universidade", "R. das Rolinhas, 1304", "Centro", "86701-030", -23.4081129, -51.4460734),
    ("Faculdade UNINA Sao Braz Arapongas", "Universidade", "R. Condor, 359, Sl 08", "Vila Cascata", "86701-472", -23.4048626, -51.4289528),
    ("Faculdade HONPAR", "Faculdade", "PR-218, Km 01", "Jardim Aeroporto", "86702-420", -23.3895795, -51.4487037),
    ("Unifatecie Arapongas", "Universidade", "Av. Arapongas, 88", "Centro", "86700-050", -23.4145335, -51.4301994),
    ("UNINTER Arapongas", "Universidade", "R. das Rolinhas, 10", "Centro", "86701-030", -23.4151457, -51.4356515),
    ("Faculdade Rhema", "Faculdade", "R. Macucos, 200", "Centro", "86701-110", -23.418979, -51.4307531),

    # ---------------- Escolas Particulares ----------------
    ("Colegio Olimpus", "Escola Particular", "R. Lori, 1440", "Jardim Panorama", "86701-300", -23.4137514, -51.4491009),
    ("Colegio Prisma", "Escola Particular", "R. Macucos, 176", "Centro", "86701-110", -23.4185539, -51.4310402),
    ("Bom Jesus Mother of Divine Love", "Escola Particular", "R. Eurilemos, 1190", "Centro", "86708-970", -23.4146668, -51.4402733),
    ("Escola Piemont", "Escola Particular", "R. Pica Pau, 259", "Centro", "86700-082", -23.4155193, -51.4363638),
    ("Escola Pequeno Marujo", "Escola Particular", "R. Irauna, 180", "Parque Veneza", "86701-630", -23.3981646, -51.44515),
    ("Centro de Recreacao Cores Primarias", "Escola Particular", "R. Cabure Canela, 595", "Jardim San Rafael", "86703-492", -23.3944624, -51.4132709),
    ("Escola Genius", "Escola Particular", "R. Eurilemos, 1076", "Centro", "86700-155", -23.4136117, -51.4391828),
    ("Escola Infantil Risque e Rabisque", "Escola Particular", "R. Cap. do Mato, 06", "Jardim Aeroporto", "86702-010", -23.3937587, -51.4476205),
]

# --- 1) Garantir que todos os bairros existam em dim_bairro ---
bairros_unicos = sorted(set(b for (_, _, _, b, _, _, _) in escolas))
cur.executemany(
    "INSERT OR IGNORE INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, 'Arapongas', 'PR')",
    [(b,) for b in bairros_unicos]
)
conn.commit()

cur.execute("SELECT b_id, b_nome FROM dim_bairro")
bairro_map = {nome: bid for bid, nome in cur.fetchall()}

# --- 2) Popular dim_educacao ---
rows = []
for nome, tipo, endereco, bairro, cep, lat, lon in escolas:
    rows.append((bairro_map[bairro], tipo, nome, endereco, cep, lat, lon))

cur.executemany("""
    INSERT INTO dim_educacao (
        b_id, e_tipo, e_nome, e_endereco, e_cep, e_latitude, e_longitude
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_educacao")
print("Total em dim_educacao:", cur.fetchone()[0])

cur.execute("SELECT COUNT(DISTINCT b_id) FROM dim_educacao")
print("Bairros distintos cobertos:", cur.fetchone()[0])

cur.execute("SELECT e_tipo, COUNT(*) FROM dim_educacao GROUP BY e_tipo ORDER BY 2 DESC")
print("\nPor tipo:")
for row in cur.fetchall():
    print(" ", row)

conn.close()