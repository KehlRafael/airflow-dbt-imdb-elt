# ELT com Airflow e dbt Core no Postgres

Esta é uma versão modificada do [Docker Compose Oficial do Apache Airflow 3.0.6](https://airflow.apache.org/docs/apache-airflow/3.0.6/howto/docker-compose/index.html) para incluir `pgAdmin` e um data warehouse dedicado usando `pgduckdb` (Postgres com extensão DuckDB) para permitir que o usuário execute os DAGs do projeto, bem como consulte o data warehouse para inspecionar os dados gerados pelo processo ELT sem depender de qualquer outro software instalado na máquina.

Esta não é uma imagem de container pronta para produção. Ela tem muitos problemas, como credenciais padrão e não criptografadas. O objetivo deste projeto é fornecer um ponto de partida para aqueles que desejam aprender mais sobre dbt e Airflow.

## O Que Este Projeto Faz

Este projeto é um **pipeline ELT (Extract, Load, Transform) completo** que analisa avaliações de episódios de séries de TV do IMDb. Você construirá um pipeline de dados funcional que:

1. **Extrai** - Baixa conjuntos de dados reais do IMDb (informações de títulos, detalhes de episódios e avaliações)
2. **Carrega** - Ingere dados brutos em um data warehouse PostgreSQL
3. **Transforma** - Usa dbt para limpar e estruturar os dados em tabelas prontas para análise
4. **Orquestra** - Automatiza tudo com Apache Airflow

Ao final, você terá um data warehouse com camadas organizadas:
- **Camada de staging** (`stg_*`): Dados limpos de séries de TV e episódios
- **Tabelas de fatos** (`fact_*`): Avaliações de episódios e séries com contagens de votos
- **Tabelas de dimensão** (`dim_*`): Melhores e piores episódios pré-calculados para cada série

### Exemplos de Perguntas Que Você Pode Responder

Uma vez que o pipeline seja executado com sucesso, você pode consultar o data warehouse para descobrir:
- "Qual é o episódio mais bem avaliado de Breaking Bad?"
- "Quais séries de TV têm as quedas de qualidade mais dramáticas entre os melhores e piores episódios?"
- "Quais são os 10 episódios de TV mais bem avaliados de todos os tempos?"
- "Quantos votos cada episódio tem e quão confiáveis são as avaliações?"

## Tecnologias Utilizadas

Este projeto combina várias ferramentas modernas de engenharia de dados. Veja o que cada uma faz:

### Tecnologias Principais

- **[Apache Airflow](https://airflow.apache.org/)** - Plataforma de orquestração de fluxo de trabalho que agenda, monitora e gerencia pipelines de dados. Pense nisso como um agendador de tarefas sofisticado que pode executar código Python, comandos bash e lidar com dependências entre tarefas.

- **[dbt (data build tool)](https://docs.getdbt.com/)** - Framework de transformação baseado em SQL para análises.

- **[PostgreSQL](https://www.postgresql.org/)** - Banco de dados relacional de código aberto servindo como nosso data warehouse. Usamos a versão 16 com extensões especiais:
  - **[pg_duckdb](https://github.com/duckdb/pg_duckdb)** - Integra o motor de consulta analítica rápida do DuckDB no PostgreSQL, permitindo até mesmo leitura de arquivos

- **[Docker](https://www.docker.com/)** - Plataforma de containerização que empacota todo o software e dependências para que tudo seja executado de forma consistente em qualquer máquina sem instalação manual.

### Ferramentas de Suporte

- **[pgAdmin](https://www.pgadmin.org/)** - Ferramenta de gerenciamento de banco de dados baseada na web para consultar e explorar seu data warehouse visualmente.

- **[uv](https://docs.astral.sh/uv/)** - Gerenciador de pacotes Python rápido para instalar dbt e suas dependências localmente.

- **[Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/)** - Biblioteca que fornece integração nativa de dbt no Airflow, transformando cada modelo dbt em uma tarefa do Airflow para melhor observabilidade.

### Por Que ELT?

**ELT (Extract, Load, Transform)** carrega dados brutos no warehouse primeiro e então os transforma usando SQL. Isso difere do **ETL (Extract, Transform, Load)** tradicional que transforma dados antes de carregá-los. ELT é popular em data warehouses modernos porque:
- Aproveita o poder de computação do warehouse para transformações
- Dados brutos são preservados para auditoria e reprocessamento
- Carregamento inicial de dados mais rápido
- Mais flexível para análise iterativa

## Pré-requisitos
Este projeto requer Docker e `uv` para executar os [DAGs ELT](airflow/dags) e o [projeto dbt](dbt).

Para instalar o Docker, consulte o [guia de instalação oficial](https://docs.docker.com/get-docker/). Você pode consultar os guias de instalação específicos do sistema abaixo:
- macOS: [Instalar Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
- Linux/Ubuntu: [Instalar Docker Desktop](https://docs.docker.com/desktop/install/linux-install/) ou [Instalar Docker Engine](https://docs.docker.com/engine/install/)
- Windows: [Instalar Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)

Para instalar `uv`, consulte o [guia de instalação oficial](https://docs.astral.sh/uv/getting-started/installation/). Alternativamente, você pode instalar e criar o ambiente virtual `dbt` usando seu gerenciador de pacotes de escolha, mas esse não é o foco deste projeto.

Com ambos instalados, você está pronto para começar!

## Começando
Primeiro clone o repositório em sua máquina local:
```
git clone https://github.com/KehlRafael/airflow-dbt-imdb-elt.git
cd airflow-dbt-imdb-elt
```

Um passo opcional, caso você queira servir (acessar via uma página web) a documentação do `dbt`, é instalar as dependências do projeto em um ambiente virtual. Para fazer isso, use `uv` para criar o ambiente virtual do projeto e então ativá-lo:
```
uv sync
source .venv/bin/activate
```

Isso permitirá que você use comandos `dbt` localmente, não apenas de dentro de seus DAGs.

### Configuração
Antes de executar os containers, você pode personalizar o ambiente editando o arquivo [.env](.env). As principais opções de configuração incluem:

- **Credenciais do Airflow**: Altere `_AIRFLOW_WWW_USER_USERNAME` e `_AIRFLOW_WWW_USER_PASSWORD` para login personalizado na UI do Airflow
- **Porta do data warehouse**: Altere `WAREHOUSE_PORT` se você tiver a porta 5432 em uso (padrão: 5432)
- **Credenciais do banco de dados**: Modifique `WAREHOUSE_POSTGRES_USER`, `WAREHOUSE_POSTGRES_PASSWORD`, etc. para credenciais personalizadas do banco de dados
- **Credenciais do pgAdmin**: Atualize `PGADMIN_DEFAULT_EMAIL` e `PGADMIN_DEFAULT_PASSWORD` para acesso personalizado ao pgAdmin

**Importante**: Se você alterar as credenciais do banco de dados, também deve atualizar:
- [dbt/imdb_ratings/profiles.yml](dbt/imdb_ratings/profiles.yml)
- [postgres/pgpass](postgres/pgpass)
- [postgres/servers.json](postgres/servers.json)

### Executando os Containers
Para executar os containers especificados no arquivo [docker-compose.yml](docker-compose.yml), você pode simplesmente executar:
```
docker compose -p imdb_ratings up -d
```
Este comando construirá automaticamente as imagens Docker personalizadas (Airflow com dbt/Cosmos e PostgreSQL com extensões) na primeira execução e então iniciará todos os serviços. Todos os containers serão listados sob o projeto `imdb_ratings`.

### Acessando a UI
Para acessar a UI do Airflow, você deve:
- Abrir a UI do Airflow em [http://localhost:8080/](http://localhost:8080/)
- Nome de usuário: airflow
- Senha: airflow

Estes são os valores padrão no [docker-compose.yml](docker-compose.yml). Eles podem ser alterados atualizando as variáveis listadas acima no arquivo [.env](.env).

Para acessar a UI do `pgAdmin`, você deve:
- Abrir a UI do `pgAdmin` em [http://localhost:8888/](http://localhost:8888/)
- Email: admin@admin.com
- Senha: admin

Estes são os valores padrão no [docker-compose.yml](docker-compose.yml). Eles podem ser alterados atualizando as variáveis listadas acima no arquivo [.env](.env).

### Conectando ao Data Warehouse

Os detalhes de conexão padrão do data warehouse (`pgduckdb_warehouse`) são:
- **Host**: localhost
- **Porta**: 5432
- **Banco de dados**: dwh
- **Nome de usuário**: postgres
- **Senha**: postgres

Você pode se conectar usando pgAdmin (veja a seção [Acessando a UI](#acessando-a-ui) acima) ou qualquer outro cliente de banco de dados. Os arquivos [postgres/pgpass](postgres/pgpass) e [postgres/servers.json](postgres/servers.json) contêm formatos de string de conexão para várias ferramentas. Todos os valores padrão são configuráveis no arquivo [.env](.env).

### Extraindo e Carregando os Conjuntos de Dados do IMDb

Antes de executar qualquer transformação, você precisa extrair e carregar os dados brutos do IMDb usando o DAG [extract_and_load_datasets](./airflow/dags/extract_and_load_datasets.py). Este DAG realiza as seguintes etapas:

1. **Baixa os conjuntos de dados do IMDb** de [https://datasets.imdbws.com/](https://datasets.imdbws.com/)
   - `title.basics.tsv.gz` - Informações básicas sobre títulos (filmes, programas de TV, etc.)
   - `title.episode.tsv.gz` - Informações de episódios para séries de TV
   - `title.ratings.tsv.gz` - Avaliações do IMDb e contagens de votos
2. **Descompacta os conjuntos de dados** e remove os arquivos compactados
3. **Configura as tabelas do banco de dados** usando [sql/setup_imdb_tables.sql](./sql/setup_imdb_tables.sql)
4. **Ingere os dados** no data warehouse usando [sql/ingest_imdb_tables.sql](./sql/ingest_imdb_tables.sql)

Este DAG aceita dois parâmetros opcionais que podem ser configurados ao acioná-lo manualmente na UI do Airflow:

- **`rewrite_files`** (booleano, padrão: `false`)
  - Defina como `true` para baixar novamente os conjuntos de dados mesmo que eles já existam na pasta `/data`
  - Defina como `false` (padrão) para pular o download se os arquivos já estiverem presentes
  - Útil quando você deseja atualizar os dados com os conjuntos de dados mais recentes do IMDb

- **`db_conn_var`** (string, padrão: `AIRFLOW_CONN_PGDUCKDB_WAREHOUSE`)
  - O nome da variável de ambiente contendo a string de conexão do banco de dados
  - O padrão aponta para o data warehouse configurado no docker-compose.yml
  - Altere isso somente se quiser usar uma conexão de banco de dados diferente

### Executando Transformações dbt

Este projeto fornece duas opções de DAG para executar transformações dbt, ambas localizadas em [airflow/dags](./airflow/dags):

1. **`run_imdb_ratings_dbt_bash.py`** - Abordagem tradicional usando BashOperator para executar comandos dbt. Isso lhe dá controle total sobre os comandos CLI do dbt e é útil para aprender como os comandos dbt funcionam, mas não tem tratamento de erros ou alertas.

2. **`run_imdb_ratings_dbt_cosmos.py`** - Abordagem moderna e recomendada usando [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/) (versão 1.11.2), que fornece integração nativa de dbt no Airflow. Isso gera automaticamente tarefas do Airflow para cada modelo dbt, permitindo melhor observabilidade, tentativas em nível de tarefa e execução paralela de modelos independentes.

Ambos os DAGs realizam o mesmo objetivo - transformar os dados brutos do IMDb em tabelas prontas para análise. Escolha aquele que melhor se adapta aos seus objetivos de aprendizado ou necessidades operacionais. Você pode habilitar um ou ambos os DAGs na UI do Airflow.

### Disponibilizando a Documentação dbt

Certifique-se de que os DAGs [extract_and_load_datasets](./airflow/dags/extract_and_load_datasets.py) e [run_imdb_ratings_bash](./airflow/dags/run_imdb_ratings_dbt_bash.py) ou [run_imdb_ratings_cosmos](./airflow/dags/run_imdb_ratings_dbt_cosmos.py) já foram executados com sucesso no Airflow. Depois disso, execute os seguintes comandos a partir da raiz deste projeto:
```
cd ./dbt/imdb_ratings
uv run dbt docs serve --port 8001 --profiles-dir .
```
Com isso, a documentação estará disponível em [http://localhost:8001/](http://localhost:8001/).

### Parando e Removendo Imagens
Para parar os containers, execute:
```
docker compose -p imdb_ratings stop
```
Para desmontar o ambiente, execute:
```
docker compose -p imdb_ratings down
```
Você pode adicionar as flags `-v` e `--rmi local` no final para também remover volumes e imagens, respectivamente, que estão associados ao projeto.

### Contato
Se você tiver alguma dúvida, preocupação ou quiser sugerir melhorias, entre em contato através das informações de contato disponíveis no meu perfil do GitHub, [kehlrafael](https://github.com/kehlrafael).

### Licença
Veja o arquivo [LICENSE](LICENSE).
