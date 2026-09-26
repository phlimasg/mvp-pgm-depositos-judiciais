## 1. Contexto de Negócio e Perguntas (Etapa 2 e 4.1)

### Contexto

A Procuradoria Geral do Município do Rio de Janeiro acompanha diariamente, via scraping automatizado do Banco do Brasil, os depósitos judiciais vinculados a processos em que o Município é parte. Diariamente, às 8h, são baixados 5 arquivos do BB, cada um representando um tipo de movimentação financeira relacionada a esses depósitos. Os dados passam por uma API (FastAPI) que identifica, trata e armazena as informações no banco PostgreSQL do sistema **PGMConnect**, e também são importados no ERP jurídico **PAV**. Em seguida, o Airbyte replica essas tabelas para o BigQuery, onde uma pipeline agendada geram duas tabelas consolidadas, otimizada para consulta, que alimenta um BI (Looker Studio/Data Studio) usado pelos gestores.

Até hoje, esse BI é majoritariamente operacional (foto do dia). Este MVP organiza e documenta essa pipeline segundo os princípios de Engenharia de Dados (arquitetura em camadas, catálogo, qualidade), e aprofunda a análise histórica desses dados — algo que o BI evolutivo atual pouco explora.

### Problema

Consolidar e monitorar a posição financeira da Procuradoria referente a valores a receber, a pagar e o saldo acumulado de depósitos judiciais na conta vinculada ao Banco do Brasil, garantindo que todos os depósitos estejam corretamente vinculados a um processo no sistema PAV.

### Perguntas de negócio

1. Qual o saldo diário consolidado (Resgates a Favor do Governo − Resgates Contra o Governo) da Procuradoria?
2. Como evolui o valor acumulado em Convênio de Repasse de Depósitos (aguardando decisão judicial) mês a mês — está crescendo, estável ou caindo?
3. Qual o volume (quantidade e valor) de Depósitos Acolhidos por dia, e há algum padrão de sazonalidade?
4. Quantos processos e qual valor total estão sem vínculo com o sistema PAV?
5. Existe concentração de valores por Especializada ou Classe Processual que mereça atenção da gestão?

### Dados brutos: origem e estrutura

Os dados têm origem no extrato diário do Banco do Brasil, obtido via scraping automatizado e classificados em 4 tipos de movimentação (um 5º arquivo, o snapshot/extrato consolidado, é descartado do pipeline analítico por ser redundante em relação aos demais):

| Código `tipo_arquivo` | Nome oficial (BB)                              | Significado no negócio                                 |
| --------------------- | ---------------------------------------------- | ------------------------------------------------------ |
| 1                     | Convênio de Repasse de Depósitos - Lei Federal | Depósitos acumulados, aguardando resolução do processo |
| 2                     | Resgates Contra o Governo                      | Valores a pagar — o Município perdeu a causa           |
| 3                     | Depósitos Acolhidos                            | Novo depósito judicial recebido no dia                 |
| 4                     | Resgates a Favor do Governo                    | Valores a receber — o Município ganhou a causa         |

Após passar pela FastAPI e serem armazenados no PGMConnect (Postgres), os dados chegam ao BigQuery para serem estruturados em duas tabelas principais:

- **`dados_djo`**: dimensão completa de processos identificados no Diário da Justiça Oficial, com as partes envolvidas.
- **`dados_djo_sem_pav`**: subconjunto de `dados_djo` referente aos registros **sem vínculo** com número de processo no sistema PAV, já com os valores financeiros do depósito judicial.

### Licença de uso dos dados

Dados administrativos de órgão público municipal, sujeitos à Lei de Acesso à Informação (LAI) e à LGPD. Campos de identificação pessoal (`autor`, `cpf_cnpj_autor`, `reu`, `cpf_cnpj_reu`) são anonimizados antes de qualquer publicação externa — método de anonimização documentado na seção 5 (Qualidade de Dados). Prints do BI usados como evidência neste documento têm essas colunas ocultadas/borradas.

---

## 2. Carga dos Dados (Etapa 4.2)

O processo de coleta e carga acontece em múltiplas etapas:

1. **Scraping diário (8h)**: robô acessa o portal do Banco do Brasil e baixa 5 arquivos, um por tipo de movimentação e move para um diretório especifico para serem importados pelo ERP.
2. **Processamento via API (FastAPI)**: os arquivos são enviados a uma API que identifica o tipo de arquivo, realiza o primeiro tratamento (parsing, tipagem) e grava os dados no banco PostgreSQL do sistema PGMConnect.
3. **Replicação para a nuvem (Airbyte)**: A cada hora o Airbyte replica as tabelas do PGMConnect (Postgres) para o BigQuery, mantendo uma cópia incremental atualizada.
4. **Transformação agendada no BigQuery**: uma consulta agendada (scheduled query) processa as réplicas do PGMConnect e gera a tabela final (`dados_djo_sem_pav` + `dados_djo`), com estrutura otimizada para consulta, dado o volume (~7GB).

Essa etapa 2 (tratamento na FastAPI, antes mesmo da chegada ao BigQuery) é o motivo pelo qual grande parte da limpeza/padronização já acontece fora do BigQuery — isso é abordado com mais detalhe na Qualidade de Dados (seção 5).

Referência aos scripts:
[Backend FastApi](./fastapi/) - [WebScrapping](./scraping/) - [Consultas Agendadas BQ](./bigquery/sql/)

**Evidência (screenshot):**

![Estrutura Inicial e Tamanho das Tabelas](./screenshots/pgdjo.png)
![AirByte - Conexão](./screenshots/air1.png)
![AirByte - Execução](./screenshots/air2.png)
![GCP - Consultas Agendadas](./screenshots/gcp.png)
![GCP - Tabelas Criadas](./screenshots/gcp2.png)

---

## 3. Modelagem e Catálogo de Dados (Etapa 4.3)

### Modelo adotado

Esquema Estrela simplificado: uma tabela fato de movimentações judiciais, uma dimensão de processo e uma dimensão categórica de tipo de movimentação.

- **`fato_deposito_judicial`** (baseada em `dados_djo_sem_pav`)
- **`dim_processo`** (baseada em `dados_djo`)
- **`dim_tipo_movimentacao`** (derivada da coluna `tipo_arquivo`)

### Catálogo de Dados

#### Tabela `dados_djo` (dimensão de processos)

| Campo                | Tipo    | Descrição                            | Domínio / Observação            |
| -------------------- | ------- | ------------------------------------ | ------------------------------- |
| `id`                 | INTEGER | Identificador único do registro      | Chave primária                  |
| `num_processo`       | STRING  | Número do processo judicial          | Formato CNJ                     |
| `cod_agencia`        | STRING  | Código da agência bancária vinculada | —                               |
| `unidade_judiciaria` | STRING  | Vara/unidade judiciária responsável  | Categórico                      |
| `autor`              | STRING  | Nome da parte autora                 | Anonimizado antes da publicação |
| `cpf_cnpj_autor`     | STRING  | CPF/CNPJ da parte autora             | Anonimizado (hash)              |
| `reu`                | STRING  | Nome da parte ré                     | Anonimizado antes da publicação |
| `cpf_cnpj_reu`       | STRING  | CPF/CNPJ da parte ré                 | Anonimizado (hash)              |

#### Tabela `dados_djo_sem_pav` (fato — registros sem vínculo PAV)

| Campo                      | Tipo     | Descrição                                               | Domínio / Observação     |
| -------------------------- | -------- | ------------------------------------------------------- | ------------------------ |
| `id`                       | INTEGER  | Identificador único                                     | Chave primária           |
| `num_processo`             | STRING   | Número do processo                                      | Referência a `dados_djo` |
| `cod_agencia`              | STRING   | Código da agência                                       | —                        |
| `unidade_judiciaria`       | STRING   | Vara/unidade judiciária                                 | Categórico               |
| `autor` / `cpf_cnpj_autor` | STRING   | Parte autora                                            | Anonimizado              |
| `reu` / `cpf_cnpj_reu`     | STRING   | Parte ré                                                | Anonimizado              |
| `conta`                    | STRING   | Conta bancária do depósito judicial                     | —                        |
| `valor_principal`          | NUMERIC  | Valor principal depositado                              | Mín: 0                   |
| `juros`                    | NUMERIC  | Juros acumulados                                        | Mín: 0                   |
| `correcao`                 | NUMERIC  | Correção monetária                                      | Mín: 0                   |
| `valor_atualizado`         | NUMERIC  | Valor total atualizado                                  | ≥ `valor_principal`      |
| `valor_resgatado`          | NUMERIC  | Valor já resgatado                                      | ≤ `valor_atualizado`     |
| `data_deposito`            | DATETIME | Data do depósito                                        | —                        |
| `parcela`                  | STRING   | Identificador de parcela, se houver                     | —                        |
| `especializada`            | STRING   | Vara especializada (ex: Fazenda Pública)                | Categórico               |
| `sigla`                    | STRING   | Sigla do tribunal/órgão                                 | Categórico               |
| `classeProcessual`         | STRING   | Classe processual (tipo de ação)                        | Categórico               |
| `data_djo`                 | DATETIME | Data de publicação no Diário da Justiça                 | —                        |
| `tipo_arquivo`             | STRING   | Tipo de movimentação (ver tabela de códigos na seção 1) | 1, 2, 3 ou 4             |

**Linhagem:** ambas as tabelas têm origem no scraping diário do Banco do Brasil → tratamento na API FastAPI → PostgreSQL (PGMConnect) → replicação via Airbyte → consulta agendada no BigQuery.
Os campos de CPF/CNPJ e nome sofrem anonimização por ofuscação antes da publicação de qualquer material externo.

**Evidência (screenshot):**
![GCP - Data Studio](./screenshots/ds1.png)
![GCP - Data Studio](./screenshots/ds2.png)

---

## 4. Pipeline de Dados (Etapa 4.4)

O pipeline é dividido em estágios que atravessam diferentes ferramentas, refletindo a arquitetura Medalhão mesmo sem estar tudo dentro de uma única plataforma:

![Fluxo de Funcionamento](./Fluxo%20dos%20dados.gif)

| Camada                | Onde acontece                            | O que faz                                                                                                                                                                                                          |
| --------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Bronze**            | PostgreSQL (PGMConnect), via API FastAPI | Recebe os 5 arquivos brutos do BB, identifica o tipo de arquivo, faz parsing e tipagem inicial                                                                                                                     |
| **Bronze → BigQuery** | Airbyte                                  | Replica as tabelas do PGMConnect para o BigQuery, mantendo histórico incremental                                                                                                                                   |
| **Silver/Gold**       | Consulta agendada no BigQuery            | Transforma as réplicas em `dados_djo` e `dados_djo_sem_pav`, já otimizadas para consulta (dado o volume de ~7GB), e realiza o cruzamento entre depósitos e processos do PAV para identificar registros sem vínculo |
| **Consumo**           | Looker Studio (Data Studio)              | Painel com filtros por processo, réu, autor, unidade judiciária, valor, etc.                                                                                                                                       |

Documentação da transformação principal:

> "A consulta agendada no BigQuery cruza os registros de depósitos judiciais (réplica do PGMConnect) com a base de processos do sistema PAV pelo campo `num_processo`, classificando cada depósito como vinculado ou não vinculado. Os registros sem vínculo alimentam a tabela `dados_djo_sem_pav`, junto com os valores financeiros (`valor_principal`, `juros`, `correcao`, `valor_atualizado`, `valor_resgatado`)."

Referência aos scripts: [Consulta Agendada - dados_djo](./bigquery/sql/gera_dados_djo.sql) - [Consulta Agendada - dados_djo_sem_pav](./bigquery/sql/gera_dados_djo_sem_pav.sql.sql)

**Evidência (screenshot):**
![Agendamentos](./screenshots/gcp.png)
![GCP - Dados](./screenshots/gcp2.png)
![GCP - Dados DJO](./screenshots/dados_djo.png)
![GCP - Dados DJO Sem pavs vinculados](./screenshots/sem_pav.png)

---

## 5. Qualidade de Dados (Etapa 4.5)

| Verificação  | O que foi avaliado                                                       | Resultado                                                                                 |
| ------------ | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| Completude   | Presença de `num_processo` vinculado ao PAV                              | 49.788 processos identificados sem vínculo, totalizando R$2,7 bilhões em valor atualizado |
| Consistência | Formato de `num_processo` (padrão CNJ vs. formatos legados)              | Uma média de 10% está fora do padrão CNJ, que inside em processos anteriores a 1998       |
| Unicidade    | Duplicidade de registros (mesmo processo, mesma conta, mesmo depósito)   | Não foram identificadas duplicidades e sim depósitos complementares                       |
| Acurácia     | `valor_resgatado` não pode exceder `valor_atualizado`; valores negativos | N/A                                                                                       |
| Outliers     | Depósitos com valor muito acima da média da mesma classe processual      | `[preencher]`                                                                             |

**Achado principal:** o cruzamento entre depósitos judiciais e o sistema PAV, que hoje já roda em produção como parte da pipeline, identificou historicamente processos sem número vinculado que resultaram na recuperação de mais de R$2 bilhões para o Município — evidenciando o impacto direto de um problema de qualidade de dados (falta de vínculo) sobre o resultado financeiro do órgão. Esse achado é a evidência central deste MVP de que verificação de qualidade de dados gera valor de negócio mensurável, não apenas conformidade técnica.

**Evidência (screenshot):**
![Imagem](./screenshots/ds2.png)
Hoje o valor disponível é menor que R$ 2bi, pois já foi recuperado pelo municipio, restando apenas uma média de 350mi em processos sem identificação.

**Vídeo de Apresentação na AB2L 2026**
[![Apresentação do projeto na AB2L de 2026 - Youtube](https://img.youtube.com/vi/8Yt811dYNUY/0.jpg)](https://www.youtube.com/watch?v=8Yt811dYNUY)

---

## 6. Análise de Dados

**Pergunta 1 — Saldo diário consolidado (a receber − a pagar):**

Consulta:
[Sql](./bigquery/sql/consolidado.sql)

Resultado:
Resultado (últimos 12 meses, posição de [data da consulta]):

| qtd_dias_com_movimentacao | saldo_acumulado_periodo | saldo_medio_diario | dias_com_saldo_positivo | dias_com_saldo_negativo | maior_saldo_positivo_dia | maior_saldo_negativo_dia |
| ------------------------- | ----------------------- | ------------------ | ----------------------- | ----------------------- | ------------------------ | ------------------------ |
| 230                       | -342653420.82           | -1489797.48        | 55                      | 175                     | 22472036                 | -55076181.99             |

Ao longo dos últimos 12 meses, o Município apresentou saldo diário negativo em 76% dos dias com movimentação (175 de 230), resultando em um saldo acumulado de -R$342,6 milhões no período — ou seja, o valor total resgatado contra o governo (processos perdidos) superou em muito o valor resgatado a favor do governo (processos ganhos). Isso confirma que, no recorte analisado, o Município tende a ter mais perdas do que ganhos nos processos vinculados a depósitos judiciais, com uma média de -R$1,49 milhão por dia de movimentação.

Vale destacar que essa distribuição não é uniforme: um único dia concentrou uma perda de R$55 milhões, valor muito acima do padrão diário observado — esse ponto foi tratado na seção de Qualidade de Dados como outlier a ser investigado, já que pode representar tanto uma decisão judicial legítima de alto valor quanto uma inconsistência no dado que merece verificação adicional antes de ser usada isoladamente em decisões orçamentárias.

Esse resultado reforça a relevância da Pergunta 4 (processos sem vínculo PAV): parte do valor que hoje é registrado como "a pagar" pode estar represado ou mal contabilizado por falta de vínculo processual correto, o que pode distorcer ainda mais esse saldo já desfavorável ao Município.

**Pergunta 2 — Volume médio e valor diário de Depósitos Acolhidos**

Consulta [SQL](./bigquery/sql/media_valor_dia.sql)
| media_periodo | valor_ultimo_dia | data_maxima |
|------------------|------------------|---------------------|
| R$1.077.125,48 | R$70.193,58 | 2026-09-18T00:00:00 |

A analise reve que os depósitos diários, sempre são baixos e que há um período especifico do ano que temos o pico de depósitos.

**Pergunta 3 — Processos sem vínculo PAV: quantidade e impacto financeiro:**
Com base no BI atual (posição de 18/09/2026), foram identificados 10757 processos sem vínculo com o sistema PAV, totalizando R$350mi em valor atualizado. ![BI](./screenshots/ds2.png)

**Discussão geral:** `[conectar as respostas ao problema original — ex: o quanto a falta de vínculo processual represa recursos que poderiam ser rapidamente resolvidos, e o que isso sugere para a gestão da Procuradoria]`

---

## 7. Autoavaliação

`[Discussão sobre quais perguntas foram totalmente respondidas, quais não foram e por quê, dificuldades técnicas encontradas — ex: integração entre FastAPI/Postgres/Airbyte/BigQuery, volume de dados (~7GB), anonimização de dados sensíveis — e trabalhos futuros, como aprofundar o BI evolutivo hoje pouco utilizado.]`

---

## Estrutura do repositório

```
mvp-pgm-depositos-judiciais/
├── scraping/          # robô de coleta diária no Banco do Brasil
├── fastapi/           # API de identificação e tratamento (Bronze)
├── airbyte/           # configs de replicação PGMConnect → BigQuery
├── bigquery/
│   └── sql/            # consulta agendada (Silver/Gold) e queries de análise
├── docs/
│   └── catalogo_dados.xlsx
├── screenshots/        # evidências (com dados sensíveis ocultados)
└── README.md
```
