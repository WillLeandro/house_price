"""
Popula dim_saude com os estabelecimentos de saude institucionais de Arapongas
(UBS, Hospital, UPA, CAPS, Policlinica, SADT, Clinica) coletados via
guia.agendarconsulta.com/parana/arapongas (dados publicos, filtrados por tipo).

Nao inclui "Consultorio" (244 registros) pois a paginacao do site quebra
apos os primeiros 50 resultados.
"""

import sqlite3

DB_PATH = "./db/arapongas.db"

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON;")
cur = conn.cursor()

# cada item: (nome, tipo, rede, rua, bairro, referencia)
estabelecimentos = [
    # ---------------- UBS (31) ----------------
    ("SESI ARAPONGAS", "UBS", "Privado", "Surucua Acu", "Vila Araponguinha", "7949685"),
    ("Unidade Basica de Saude Aguias", "UBS", "Publico", "Bigua Una", "Jardim Monte Carlo I", "2571587"),
    ("Unidade Basica de Saude Araucaria", "UBS", "Publico", "Saira Dourada", "Residencial Araucaria", "7735219"),
    ("Unidade Basica de Saude Aricanduva", "UBS", "Publico", "Rua Caiapo", "Aricanduva", "2573644"),
    ("Unidade Basica de Saude Bandeirantes", "UBS", "Publico", "Rua Mergulhador", "Jardim Bandeirantes", "2573555"),
    ("Unidade Basica de Saude Baroneza", "UBS", "Publico", "Rua Tetraz", "Vila Industrial", "5122023"),
    ("Unidade Basica de Saude Bem Viver", "UBS", "Publico", "Papa Formiga de Escamas", "Conjunto Bem Viver", "8109567"),
    ("Unidade Basica de Saude Caic", "UBS", "Publico", "Codornix", "Jardim Lorena", "2573636"),
    ("Unidade Basica de Saude Campinho", "UBS", "Publico", "Alegrinho do Sertao", "Campinho", "2573547"),
    ("Unidade Basica de Saude Centauro", "UBS", "Publico", "Rua Mutum Poranga", "Conjunto Centauro", "2573601"),
    ("Unidade Basica de Saude Colonia Esperanca", "UBS", "Publico", "Corrupiao", "Vila Industrial", "2573679"),
    ("Unidade Basica de Saude Columbia", "UBS", "Publico", "Rua Pato Bravo", "Jardim Columbia I", "2571552"),
    ("Unidade Basica de Saude Del Condor", "UBS", "Publico", "Jacuguacu", "Conjunto Del Condor", "2571595"),
    ("Unidade Basica de Saude Guadalupe", "UBS", "Publico", "Rua Gaviao Pomba Azulada", "Jardim Aeroporto", "2730979"),
    ("Unidade Basica de Saude Lori", "UBS", "Publico", "Tucanos", "Centro", "2571579"),
    ("Unidade Basica de Saude Padre Chico", "UBS", "Publico", "Aguias", "Jardim Paulista", "2573563"),
    ("Unidade Basica de Saude Palmares", "UBS", "Publico", "Rua Quete", "Conjunto Bussadori", "2573628"),
    ("Unidade Basica de Saude Panorama", "UBS", "Publico", "Rua Carrancho", "Jardim Panorama", "3024156"),
    ("Unidade Basica de Saude Petropolis", "UBS", "Publico", "Rua Garrincha do Mato Grosso", "Jardim Vale das Perobas", "2573733"),
    ("Unidade Basica de Saude Pombas", "UBS", "Publico", "Rua Harpia", "Centro", "2571617"),
    ("Unidade Basica de Saude Primavera", "UBS", "Publico", "Rua Vanaquia", "Jardim Primavera", "2573598"),
    ("Unidade Basica de Saude Sampaio", "UBS", "Publico", "Rua Ema", "Vila Sampaio", "2571668"),
    ("Unidade Basica de Saude San Raphael", "UBS", "Publico", "Rua Maitaca Roxa", "Jardim San Raphael I", "2571633"),
    ("Unidade Basica de Saude Santo Antonio", "UBS", "Publico", "Rua Batuquira", "Jardim Santo Antonio", "2571609"),
    ("Unidade Basica de Saude Sao Bento", "UBS", "Publico", "R Macuquinho Serrano esq Cabure Ferrugem", "Jardim Alto da Boa Vista", "7204280"),
    ("Unidade Basica de Saude Sao Joao", "UBS", "Publico", "Rua Condor", "Vila Sao Joao", "2571625"),
    ("Unidade Basica de Saude Sao Vicente", "UBS", "Publico", "Rua Tico Tico", "Centro", "5114314"),
    ("Unidade Basica de Saude Triangulo", "UBS", "Publico", "Rua Perdizes", "Jardim Arapongas", "2571641"),
    ("Unidade Basica de Saude Tropical", "UBS", "Publico", "Rua Dancarino", "Conjunto Tropical", "2573512"),
    ("Unidade Basica de Saude Ulisses Guimaraes", "UBS", "Publico", "Andarilho", "Jardim Nova Baroneza", "2571560"),
    ("Unidade Basica de Saude Vila Araponguinha", "UBS", "Publico", "Rua Irataua", "Vila Araponguinha", "2573571"),

    # ---------------- Hospital (4) ----------------
    ("Honpar Hospital Norte Paranaense", "Hospital", "Privado", "Avenida Gaturamo", "Jardim Primavera", "2576341"),
    ("Hospital Nossa Senhora de Fatima", "Hospital", "Privado", "Flamingos", "Centro", "5911354"),
    ("Hospital Santa Rita", "Hospital", "Privado", "Rua Flamingos", "Centro", "2576171"),
    ("Irmandade Santa Casa de Arapongas", "Hospital", "Privado", "Rua Calu", "Centro", "2576198"),

    # ---------------- UPA (6) ----------------
    ("Pronto Atendimento 18 Horas Antonio J Marques Palmares", "UPA", "Publico", "Rua Tanatau", "Jardim Sao Bento", "7989520"),
    ("Pronto Atendimento 18 Horas Luiz Beffa Petropolis", "UPA", "Publico", "Rua Pato Mergulhador", "Jardim Petropolis", "7989261"),
    ("Pronto Atendimento 18 Horas Osvaldo Fila Jr Flamingos", "UPA", "Publico", "Rua Irataua", "Conjunto Flamingos", "2573385"),
    ("Pronto Atendimento 24 Hrs Alberto Esper Kallas", "UPA", "Publico", "Bonito do Campo", "Vila Industrial", "9836861"),
    ("Pronto Atendimento Alberto Esper Kallas", "UPA", "Publico", "Bonito do Campo", "Vila Industrial", "0178977"),
    ("UPA Unidade de Pronto Atendimento", "UPA", "Publico", "Tico Tico Rei", "Jardim Caravelle", "7317719"),

    # ---------------- CAPS (3) ----------------
    ("CAPS AD Raimundo Ferreira Passos Tamandua", "CAPS", "Publico", "Marabu", "Centro", "7352859"),
    ("CAPS II Centro Atencao Psicossocial Dr Abelardo de Moreira", "CAPS", "Publico", "Tucanos", "Centro", "7352824"),
    ("CAPS Infanto Juvenil Dr Walter Buzalaf", "CAPS", "Publico", "Rua Cabure Lote 01D em Frente a Rua Japu", "Jardim Lorena", "4923901"),

    # ---------------- Policlinica (12) ----------------
    ("Centro de Saude Jaime de Lima", "Policlinica", "Publico", "Juriti", "Vila Industrial", "2573369"),
    ("Centro Medico Unidade Arapongas", "Policlinica", "Privado", "Falcao", "Centro", "4989473"),
    ("CISAM Centro Integrado de Saude da Mulher", "Policlinica", "Publico", "Avenida Gaturamo", "Jardim Aeroporto", "5407281"),
    ("Clinica das Acacias", "Policlinica", "Privado", "Rua Garcas", "Centro", "7337647"),
    ("Espaco Fisio Clinica de Fisioterapia e Saude", "Policlinica", "Privado", "Uirapuru", "Centro", "2935139"),
    ("Espaco Fisio Clinica de Fisioterapia e Saude", "Policlinica", "Privado", "Flamingos", "Centro", "6048471"),
    ("Exapmed", "Policlinica", "Privado", "Mesia", "Jardim Aeroporto", "7466528"),
    ("Lab Imagem Medicina Diagnostica", "Policlinica", "Privado", "Uirapuru", "Centro", "2982978"),
    ("Loris Centro Geriatrico", "Policlinica", "Privado", "Falcao", "Centro", "4260392"),
    ("Med Sport", "Policlinica", "Privado", "Beija Flor", "Centro", "6153003"),
    ("Policlin Servicos Medicos Ltda", "Policlinica", "Privado", "Harpia", "Centro", "7544383"),
    ("Seprev Arapongas", "Policlinica", "Privado", "Uirapuru", "Centro", "7342373"),

    # ---------------- SADT (22) ----------------
    ("CDL Centro Diagnostico Laboratorial", "SADT", "Privado", "Rua Noitibo", "Centro", "2727307"),
    ("Clinica Mag", "SADT", "Privado", "Pombas", "Centro", "0293628"),
    ("Fast Lab", "SADT", "Privado", "Flamingos", "Centro", "3323749"),
    ("Incell", "SADT", "Privado", "Rua Flamingos", "Centro", "2576031"),
    ("Labclin Analises Clinicas", "SADT", "Privado", "Rua Flamingos", "Centro", "2575663"),
    ("Labora Laboratorio de Analises Clinicas Ltda", "SADT", "Privado", "Rua Calu", "Centro", "7090277"),
    ("Laboratorio Dom Bosco", "SADT", "Privado", "Rua Flamingos", "Centro", "2576228"),
    ("Laboratorio Joao Adroaldo", "SADT", "Privado", "Albatroz Real", "Conjunto Del Condor", "9466770"),
    ("Laboratorio Logos", "SADT", "Privado", "Rua Tucanos", "Centro", "5074835"),
    ("Laboratorio Municipal de Analises Clinicas", "SADT", "Publico", "Atingau", "Gleba Patrimonio Ara", "9114793"),
    ("Laboratorio Santa Terezinha", "SADT", "Privado", "Rouxinol", "Vila Aparecida", "9858105"),
    ("Laboratorio Santana", "SADT", "Privado", "Beija Flor", "Centro", "2576104"),
    ("Laboratorio Sao Francisco", "SADT", "Privado", "Rua Flamingos", "Centro", "5890101"),
    ("Laboratorio Sao Lucas", "SADT", "Privado", "Rua Flamingos", "Centro", "2576252"),
    ("Laboratorio Sao Marcos", "SADT", "Privado", "Avestruz", "Centro", "5657571"),
    ("Lasy Laboratorio Clinico", "SADT", "Privado", "Gaturamo", "Jardim Primavera", "2729849"),
    ("SESI", "SADT", "Privado", "Avenida Maracana", "Vila Araponguinha", "2576082"),
    ("SIM Sistema Integrado de Imagem em Medicina", "SADT", "Privado", "Calu", "Centro", "3024121"),
    ("Ultra Reabilitacao e Saude", "SADT", "Privado", "Condor", "Centro", "0153516"),
    ("Ultramed Arapongas Fil", "SADT", "Privado", "Pombas", "Centro", "9351175"),
    ("Unirad", "SADT", "Privado", "Pepira de Crista Amarela", "Vila Coelho", "3406172"),
    ("Unirad", "SADT", "Privado", "Avestruz", "Centro", "4228987"),

    # ---------------- Clinica (30) ----------------
    ("APAE de Arapongas", "Clinica", "Privado", "Harpia", "Centro", "3337154"),
    ("Auditivcentro de Pesquisas e Exames Audiologicos", "Clinica", "Privado", "Rua Pavao", "Jd Portal das Flores", "3411974"),
    ("Baioni Protese Dentaria", "Clinica", "Privado", "Acurana", "Jardim Santo Antonio", "7681135"),
    ("Ben Clinic", "Clinica", "Privado", "Rua Caure", "Jardim Aeroporto", "6020224"),
    ("Cardiologia Angiologia e Cirurgia Vascular", "Clinica", "Privado", "Rua Perdizes", "Parque Veneza", "2576058"),
    ("Clinica Angios", "Clinica", "Privado", "Rua Flamingos", "Centro", "3505588"),
    ("Clinica Cuore", "Clinica", "Privado", "Pombas", "Centro", "5482917"),
    ("Clinica de Fisiot Sao Judas Tadeu", "Clinica", "Privado", "Rua Pintassilgo", "Vila Aratimbo", "2576066"),
    ("Clinica de Ortopedia e Traumatologia COT", "Clinica", "Privado", "Rua Pavao", "Centro", "2575981"),
    ("Clinica Higia", "Clinica", "Privado", "Suiriri", "Centro", "3439003"),
    ("Clinica Medica Dr Alberto Cesar Schell de Morais", "Clinica", "Privado", "Rua Marabu", "Centro", "2576090"),
    ("Clinica Municipal de Fisioterapia", "Clinica", "Publico", "Rua Garcas", "Centro", "9605134"),
    ("Clinica Vida Imagem e Medicina", "Clinica", "Privado", "Drongo", "Centro", "6051251"),
    ("Clinika", "Clinica", "Privado", "Rua Perdizes", "Centro", "2576007"),
    ("Crescer Centro Clinico", "Clinica", "Privado", "Rua Condor", "Vila Cascata", "6050255"),
    ("Davita Brasil Participacoes e Servicos de Nefrologia Ltda", "Clinica", "Privado", "Anu Branco", "Jd Portal das Flores", "2576155"),
    ("Fisio Forma", "Clinica", "Privado", "Pombas", "Centro", "0153478"),
    ("Fisioclinica", "Clinica", "Privado", "Marabu", "Centro", "2575647"),
    ("Fisiomed", "Clinica", "Privado", "PR 218 Km 1", "Jardim Universitario", "5114381"),
    ("Gastromed", "Clinica", "Privado", "Rua Flamingos", "Centro", "3546098"),
    ("HFB Neuro Imagem", "Clinica", "Privado", "PR 218 Km 01", "Jd Universitario", "6276733"),
    ("HOA", "Clinica", "Privado", "Flamingos", "Centro", "3303195"),
    ("Instituto do Coracao e Cirurgia Vascular", "Clinica", "Privado", "Rua Perdizes", "Parque Veneza", "2575949"),
    ("Interfisio", "Clinica", "Privado", "Rua Pavao", "Centro", "6516424"),
    ("Litoclinica de Arapongas", "Clinica", "Privado", "PR 218", "Jd Universitario", "5878306"),
    ("Nefroclin Clinica Medica de Nefrologia Ltda", "Clinica", "Privado", "Rua Anu Branco", "Jd Portal das Flores", "9142029"),
    ("RL Fisioterapia e Ergonomia do Trabalho", "Clinica", "Privado", "Harpia", "Centro", "7130961"),
    ("Servico Hemodinamica Joao de Freitas", "Clinica", "Privado", "PR 218", "Jardim Universitario", "2730685"),
    ("Ultec Diagnosticos", "Clinica", "Privado", "Marabu", "Centro", "2575337"),
    ("Ultrarad", "Clinica", "Privado", "Noitibo", "Centro", "5502330"),
]

# --- 1) Garantir que todos os bairros existam em dim_bairro ---
bairros_unicos = sorted(set(b for (_, _, _, _, b, _) in estabelecimentos))
cur.executemany(
    "INSERT OR IGNORE INTO dim_bairro (b_nome, b_cidade, b_estado) VALUES (?, 'Arapongas', 'PR')",
    [(b,) for b in bairros_unicos]
)
conn.commit()

cur.execute("SELECT b_id, b_nome FROM dim_bairro")
bairro_map = {nome: bid for bid, nome in cur.fetchall()}

# --- 2) Popular dim_saude ---
rows = []
for nome, tipo, rede, rua, bairro, ref in estabelecimentos:
    s_tipo = f"{tipo} ({rede})"
    rows.append((bairro_map[bairro], s_tipo, nome, rua, None))

cur.executemany("""
    INSERT INTO dim_saude (b_id, s_tipo, s_nome, s_endereco, s_cep)
    VALUES (?, ?, ?, ?, ?)
""", rows)

conn.commit()

cur.execute("SELECT COUNT(*) FROM dim_saude")
print("Total em dim_saude:", cur.fetchone()[0])

cur.execute("SELECT COUNT(DISTINCT b_id) FROM dim_saude")
print("Bairros distintos cobertos:", cur.fetchone()[0])

cur.execute("""
    SELECT s.s_tipo, COUNT(*) FROM dim_saude s GROUP BY s.s_tipo ORDER BY 2 DESC LIMIT 10
""")
print("\nAmostra por tipo:")
for row in cur.fetchall():
    print(" ", row)

conn.close()
