# SIG-Painel_COVID19_UFF

Objetivo: 
Desenvolvimento de Sistema de Informação (ETL) para Alimentar o Painel de Visualização de Dados COVID-19 UFF

## Dados utilizados

* Casos confirmados do COVID-19 - Secretaria de Saúde do Rio de Janeiro - [Painel CORONAVIRUS Covid-19](https://painel.saude.rj.gov.br/monitoramento/covid19.html#)
* Dados de mobilidade urbana - [Relatórios de Mobilidade do Google](https://www.google.com/covid19/mobility/)
* Dados censitários - [IBGE](https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html)
* Códigos de municípios - [IBGE](https://www.ibge.gov.br/explica/codigos-dos-municipios.php)

# Setup

* Python 3.x
* Docker
* git

## Ambiente de desenvolvimento

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Criar o 'variables.env' em base ao 'variables.env_example' 
