#!/bin/bash
#
#==============================================================
# SCRIPT                  : stage_covid.py
# FUNCAO                  : Script shell para executar a extracao da mobilidade.
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

MOBILIDADE_PATH=src/input/mobilidade
if [ ! -d "$MOBILIDADE_PATH" ]; then
    mkdir $MOBILIDADE_PATH
fi

STATUS_FILE=src/input/mobilidade/status.json
if ! test -f "$STATUS_FILE"; then
    touch $STATUS_FILE
fi

if [ $WORK_ENV == "dev" ]
then
    echo "[DEV]"
    export MYSQL_PASSWORD=$MYSQL_PASSWORD
    export MYSQL_USER=$MYSQL_USER
    source venv/bin/activate
    python3 src/extract_mobilidade.py
else
    echo "[PROD]"
    /usr/bin/docker-compose -f docker-compose.python-covid-uff.yml run --rm python-covid-uff python3 src/extract_mobilidade.py
fi