#!/bin/bash
#
#==============================================================
# SCRIPT                  : stage_covid.py
# FUNCAO                  : Script shell para executar a extracao do covid-19.
# DATA CRIADO             : 25/01/2021
# AUTOR                   : Arthur Egide
# VERSAO                  : 1.0
# 
# LOG ALTERACOES:
# VER          DATA                AUTOR               COMENTARIOS
# ==============================================================
#  1.0         20/01/2021          Arthur Egide        Versao inicial.
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
    python3 src/extract_covid.py
else
    echo "[PROD]"
    docker-compose -f docker-compose.python-covid-uff.yml run --rm python-covid-uff python3 src/extract_covid.py