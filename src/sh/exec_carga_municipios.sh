#!/bin/bash
#
#==============================================================
# SCRIPT                  : carga_tb_municipios.py
# FUNCAO                  : Script shell para executar a carga da tabela de municipios segundo codigos do IBGE.
# DATA CRIADO             : 25/10/2021
# AUTOR                   : Iris Rangel
# VERSAO                  : 1.0
# 
# LOG ALTERACOES:
# VER          DATA                AUTOR               COMENTARIOS
# ==============================================================
#  1.0         25/10/2021          Iris Rangel         Versao inicial.
# ==============================================================
#
#
# ==============================================================
# Definicao de Variaveis Base
# ==============================================================
#
#
source variables.env
export WORK_ENV=$WORK_ENV

if [ $WORK_ENV == "dev" ]
then
    echo "[DEV]"
    export MYSQL_PASSWORD=$MYSQL_PASSWORD
    export MYSQL_USER=$MYSQL_USER
    source venv/bin/activate
    python3 src/carga_tb_municipios.py --arquivo_path Municipios_RJ_cod_IBGE.csv
else
    echo "[PROD]"
    docker-compose -f docker-compose.python-covid-uff.yml run --rm python-covid-uff python3 /app/src/carga_tb_municipios.py --arquivo_path Municipios_RJ_cod_IBGE.csv
fi