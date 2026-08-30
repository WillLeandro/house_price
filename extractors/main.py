"""
extratores/main.py

Roda um (ou todos) os extratores e sincroniza os resultados com dim_moradia.

Uso:
    python main.py            -> roda todos os extratores cadastrados
    python main.py ricardo    -> roda so o extrator da Ricardo
"""

import sys
import base
import extrator_ricardo
import extrator_solara
import extrator_linham
import extrator_panorama
import extrator_franjovi
import extractor_bnz
import extrator_almeida
import extrator_giuliano
import extractor_terra_santa

# Cada entrada: (nome_para_exibicao, fragmento_do_site_em_dim_imobiliaria, modulo_extrator)
EXTRATORES = {
    "ricardo": ("Imobiliaria Ricardo", "imobiliariaricardo.com.br", extrator_ricardo),
    "solara": ("Imobiliaria Solara", "imobiliariasolara.com.br", extrator_solara),
    "linham": ("Imobiliaria e Loteadora Linham", "imobiliarialinham.com.br", extrator_linham),
    "panorama": ("Imoveis Panorama", "imoveispanorama.com.br", extrator_panorama),
    "franjovi": ("Imobiliaria Franjovi", "imobiliariafranjovi.com.br", extrator_franjovi),
    "bnz": ("BNZ Negócios Imobiliários", "bnznegociosimobiliarios.com.br", extractor_bnz),
    "almeida": ("Imobiliaria Almeida", "almeidasilvaimoveis.com.br", extrator_almeida),
    "giuliano": ("Imobiliaria Giuliano", "imobiliariagiuliano.com.br", extrator_giuliano),
    "terra_santa": ("Imobiliaria Terra Santa", "terrasantaimoveis.com.br", extractor_terra_santa),
}


def rodar(chave):
    nome, fragmento_site, modulo = EXTRATORES[chave]
    print(f"\n=== Rodando extrator: {nome} ===")

    conn = base.conectar()
    cur = conn.cursor()
    i_id = base.obter_i_id(cur, fragmento_site)
    conn.close()

    imoveis = modulo.extrair()
    base.sincronizar(i_id, imoveis, nome_imobiliaria=nome)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        chave = sys.argv[1]
        if chave not in EXTRATORES:
            print(f"Extrator '{chave}' nao encontrado. Opcoes: {list(EXTRATORES.keys())}")
            sys.exit(1)
        rodar(chave)
    else:
        for chave in EXTRATORES:
            rodar(chave)