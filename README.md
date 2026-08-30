# Recomendador de Imóveis por Custo-Benefício - Arapongas/PR

Sistema que recomenda imóveis para locação em Arapongas-PR cruzando orçamento,
distância até o trabalho e infraestrutura do bairro (saúde, educação,
alimentação e lazer). O objetivo é ajudar o futuro inquilino a escolher o
bairro com melhor custo-benefício para o seu perfil.

Projeto desenvolvido para a disciplina Atividade Extensionista II: Tecnologia
Aplicada à Inclusão Digital (UNINTER, CST em Ciência de Dados), alinhado aos
Objetivos de Desenvolvimento Sustentável ODS 10 (Redução das Desigualdades) e
ODS 11 (Cidades e Comunidades Sustentáveis).

Arapongas é conhecida como a Capital Nacional do Móvel. Essa identidade
inspirou o visual do aplicativo: tons de madeira, tipografia com caráter de
marcenaria e um indicador de progresso em forma de régua/fita métrica.

## Funcionalidades

- Web scraping automatizado de 9 imobiliárias de Arapongas, cada uma com seu
  próprio extrator, já que a cidade não tem um portal único de imóveis.
- Sincronização incremental: cada nova coleta insere imóveis novos, atualiza
  os que já existiam e marca como inativo quem saiu do ar, sem duplicar ou
  perder o histórico.
- Base de contexto do bairro com saúde, educação, alimentação/mercado e
  lazer, coletados via Google Places e fontes públicas.
- Filtro eliminatório pela Regra dos 30%: aluguel mais condomínio não pode
  passar de 30% da renda bruta informada.
- Score de custo-benefício ponderado, calculado a partir de 6 critérios
  (distância do trabalho, preço, saúde, educação, lazer, alimentação), com
  pesos que o próprio usuário calibra.
- Interface Streamlit em 3 etapas: renda e local de trabalho, prioridades,
  ranking dos 10 melhores imóveis.

## Estrutura do projeto

```
house_price/
├── app.py                     Interface Streamlit (etapas 1, 2 e 3)
├── requirements.txt
├── db/
│   └── arapongas.db            Banco SQLite com schema e dados coletados
├── extractors/                 Web scrapers, um por imobiliária
│   ├── base.py                 Motor comum de sincronização incremental
│   ├── main.py                 Executa um ou todos os extratores
│   └── extrator_*.py           9 extratores (Ricardo, Solara, Linham,
│                                Panorama, Franjovi, BNZ, Almeida Silva,
│                                Giuliano, Terra Santa)
├── pop/                        Scripts de criação e população do banco
│   ├── create_db.py            Cria o schema (7 tabelas dim_*)
│   ├── pop_dim_saude.py
│   ├── pop_dim_educacao.py
│   ├── pop_dim_alimentacao.py
│   ├── pop_dim_lazer.py
│   ├── pop_dim_imobiliaria.py
│   ├── geocodificador.py       Preenche latitude/longitude de dim_bairro
│   └── rodar_tudo.py           Roda create_db e todos os pop_* em sequência
└── docs/
    └── imobiliarias.txt        Notas sobre as imobiliárias mapeadas
```

### Modelo de dados (SQLite)

| Tabela | O que guarda |
|---|---|
| dim_bairro | Bairros de Arapongas, com coordenadas geográficas |
| dim_imobiliaria | Cadastro das imobiliárias (endereço, telefone, site) |
| dim_moradia | Imóveis para locação, o núcleo do projeto, com status Ativo ou Inativo |
| dim_saude | UBS, hospitais, clínicas, laboratórios |
| dim_educacao | Escolas, CMEIs, faculdades |
| dim_alimentacao | Mercados, mercearias, conveniências |
| dim_lazer | Praças, parques, clubes, academias, cinema |

## Como rodar

### 1. Clonar e instalar dependências

```bash
git clone <url-do-repositorio>
cd house_price
python -m venv env
source env/bin/activate
# no Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 2. Criar e popular o banco de dados

```bash
cd pop
python rodar_tudo.py
python geocodificador.py
```

O rodar_tudo.py cria o schema e popula saúde, educação, alimentação, lazer e
imobiliária. O geocodificador.py precisa rodar depois de qualquer recriação
do banco do zero, porque nenhum script de população preenche a coordenada
dos bairros sozinho. Sem esse passo, os cálculos de distância ficam todos
errados.

### 3. Rodar os extratores de imóveis

```bash
cd ../extractors
python main.py
```

Isso roda as 9 imobiliárias de uma vez. Também dá pra rodar uma por vez, por
exemplo python main.py ricardo.

### 4. Rodar o aplicativo

```bash
cd ..
streamlit run app.py
```

## Tecnologias

- Python 3
- SQLite
- BeautifulSoup4 e Requests, para o web scraping
- Pandas, para manipulação de dados
- Streamlit, para a interface web
- Google Places, para geocodificação e coleta de pontos de interesse (saúde,
  educação, alimentação, lazer)

## Limitações conhecidas

Granularidade por bairro, não por endereço exato. A distância até o trabalho
é calculada entre o centróide do bairro do imóvel e o centróide do bairro de
trabalho informado, não entre endereços exatos. Dois imóveis no mesmo bairro
sempre têm a mesma distância calculada.

3 imobiliárias ficaram fora do escopo: Bertoni, Shamar e Vale Verde. As duas
últimas usam aplicações Angular do tipo SPA e a Bertoni carrega os dados via
JavaScript no navegador, sem API pública localizada. Nos três casos seria
necessário Selenium ou outro navegador headless, o que não foi implementado
nesta versão.

Coordenadas de alguns bairros são aproximadas (coluna
b_geocodificacao_incerta na tabela dim_bairro), nos casos em que não havia
correspondência exata no Google Places para Arapongas especificamente.

## Autor

Leandro Alves de Souza, RU 2136383
CST em Ciência de Dados, Centro Universitário Internacional UNINTER
