#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : carga_tb_municipios.py
# FUNCAO                  : Realizar carga da tabela de municipios segundo codigos do IBGE.
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
import traceback
import time
import argparse
import os
import json
import datetime

import pandas as pd
import sqlalchemy as sq

from utils import logger
from utils.mysql import df_to_table

logger.application = "LOAD_CARGA_MUNICIPIOS"
logging = logger.logger

DATABASE = 'uff'
TABLE = 'tb_municipios'


# Renomea as colunas do Dataframe
def dfColumnsRename(df, df_new_columns):
    # Reconhecimento das colunas
    df_raw_column = [i for i in list(df)]
    #
    # Renomeação para as colunas
    columns_rename_list_dict = [{df_raw_column[i]:df_new_columns[i]} for i in range(len(df_new_columns))]
    columns_rename_dict = {k: v for d in columns_rename_list_dict for k, v in d.items()}
    #
    logging.info("Conversão do arquivo em tabela. Header encontrado no arquivo : {}".format(df_raw_column))
    return df[df_raw_column].rename(columns=columns_rename_dict)[df_new_columns]

def run():
    logging.info("INICIO")

    start_time = time.time()

    # Leitura do arquivo de municipios
    logging.info("Leitura do arquivo {}".format('Municipios_RJ_cod_IBGE.csv'))
    municipios_df = pd.read_csv('src/input/municipios/Municipios_RJ_cod_IBGE.csv', sep=';', header=0)

    # Renomear colunas
    municipios_df.columns = ['cod_municipio', 'cod_uf', 'uf', 'nome_municipio']

    # Inserção ao banco
    linhas_inseridas = df_to_table(municipios_df, DATABASE, TABLE)

    end_time = time.time()

    logging.info("FIM")

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))