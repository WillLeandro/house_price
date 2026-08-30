"""
Script maestro: recria o banco do zero e popula todas as dimensoes de
contexto (saude, educacao, alimentacao, lazer, imobiliaria), na ordem
certa. NAO roda os extratores de moradia (isso continua sendo feito
separadamente com "python main.py", depois deste script).

Uso:
    python rodar_tudo.py

Se algum passo falhar, o script para e mostra o erro -- assim voce sabe
exatamente onde precisa corrigir antes de continuar.
"""

import os
import subprocess
import sys

# Pasta onde este proprio script (rodar_tudo.py) esta localizado -- assim
# ele acha os outros scripts nao importa de onde voce rode "python rodar_tudo.py"
# (raiz do projeto, dentro da pasta pop/, etc).
PASTA_SCRIPT = os.path.dirname(os.path.abspath(__file__))

# Raiz do projeto = pasta pai de onde este script esta (ex: se este script
# esta em house_price/pop/rodar_tudo.py, a raiz e house_price/). E la que
# fica a pasta db/, entao os scripts precisam rodar com essa pasta como
# diretorio de trabalho para o "./db/arapongas.db" deles funcionar certo.
RAIZ_PROJETO = os.path.dirname(PASTA_SCRIPT)

# Ordem de execucao. dim_bairro nao tem script proprio -- ela e alimentada
# de forma incremental pelos proprios scripts de pop (cada um cria os
# bairros que precisar via INSERT OR IGNORE).
PASSOS = [
    ("Criar schema do banco", "create_db.py"),
    ("Popular dim_saude", "pop_dim_saude.py"),
    ("Popular dim_educacao", "pop_dim_educacao.py"),
    ("Popular dim_alimentacao", "pop_dim_alimentacao.py"),
    ("Popular dim_lazer", "pop_dim_lazer.py"),
    ("Popular dim_imobiliaria", "pop_dim_imobiliaria.py"),
]


def rodar_passo(descricao, script):
    print("=" * 60)
    print(f"PASSO: {descricao}  ({script})")
    print("=" * 60)

    caminho_script = os.path.join(PASTA_SCRIPT, script)

    resultado = subprocess.run(
        [sys.executable, caminho_script],
        capture_output=True,
        text=True,
        cwd=RAIZ_PROJETO,
    )

    print(resultado.stdout)
    if resultado.returncode != 0:
        print(f"\n!!! ERRO no passo '{descricao}' !!!")
        print(resultado.stderr)
        print(f"\nParando aqui. Corrija o erro acima e rode novamente.")
        sys.exit(1)

    print(f"--> OK: {descricao}\n")


def main():
    os.makedirs(os.path.join(RAIZ_PROJETO, "db"), exist_ok=True)

    for descricao, script in PASSOS:
        rodar_passo(descricao, script)

    print("=" * 60)
    print("TUDO CONCLUIDO COM SUCESSO!")
    print("=" * 60)
    print(
        "\nProximo passo: rode 'python main.py' (dentro da pasta dos "
        "extratores) para popular a dim_moradia com os imoveis das "
        "imobiliarias."
    )


if __name__ == "__main__":
    main()