#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : stage_censo.py
# FUNCAO                  : Realizar carga em tabela STAGE dos dados censitarios.
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
import traceback
import time
import argparse

import pandas as pd
import sqlalchemy as sq

from utils import logger
from utils.mysql import df_to_table
from utils.const import INPUT_PATH

logger.application = "LOAD_STAGE_CENSO"
logging = logger.logger

DATABASE = 'uff'
POPULACAO_TABLE = 'stg_censo_populacao'
POPULACAO_IDOSA_TABLE = 'stg_censo_populacao_idosa'

# Get input variables
parser = argparse.ArgumentParser()
parser.add_argument('--populacao_path', required=True, help='Path do arquivo ".xlsx" da população residente. Partindo de "input"')
parser.add_argument('--populacao_idosa_path', required=True, help='Path do arquivo ".xls" da população idosa residente, com distinção de gênero. Partindo de "input"')
args = parser.parse_args()

files_path = INPUT_PATH
populacao_path = "/".join([files_path, args.populacao_path])
populacao_idosa_path = "/".join([files_path, args.populacao_idosa_path])

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

def removeNegativeValues(df):
    return df[(df != -1).all(1)]

def run():
    # Leitura do arquivo da população
    logging.info("Leitura do arquivo {}".format(populacao_path))
    populacao = pd.read_excel(populacao_path, "Municípios", header = 1)

    # População
    pop_columns = ['uf', 'cod_uf', 'cod_municipio', 'nome_municipio', 'populacao_estimada']
    pop_df = dfColumnsRename(populacao, pop_columns)

    # Remoção dos marcadores de footer do arquivo
    regex = "\(([0-9]+)\)"
    pop_df = pop_df.replace({pop_columns[4]: regex}, {pop_columns[4]: ''}, regex=True)

    # Remoção das células que não são dados
    logging.info("Conversão dos tipos de dados da tabela")
    pop_df.fillna(-1)
    pop_df[pop_columns[0]] = pop_df[pop_columns[0]].astype(str)
    pop_df[pop_columns[1]] = pop_df[pop_columns[1]].fillna(-1).astype(int)
    pop_df[pop_columns[2]] = pop_df[pop_columns[2]].fillna(-1).astype(int)
    pop_df[pop_columns[3]] = pop_df[pop_columns[3]].astype(str)
    pop_df[pop_columns[4]] = pop_df[pop_columns[4]].fillna(-1).astype(int)

    # Remoção das linhas contendo o valor "-1"
    pop_df = removeNegativeValues(pop_df)

    # Inserção ao banco
    df_to_table( pop_df, DATABASE, POPULACAO_TABLE)

    # Leitura das arquivo da população idosa
    logging.info("Leitura do arquivo {}".format(populacao_idosa_path))
    populacao_idosa_absoluto = pd.read_excel(populacao_idosa_path, "tab1a", header = 2)
    populacao_idosa_homem = pd.read_excel(populacao_idosa_path, "tab1b", header = 2)
    populacao_idosa_mulher = pd.read_excel(populacao_idosa_path, "tab1c", header = 2)

    # População idosa
    pop_idosa_absoluta_columns = ['cod_uf', 'cod_municipio', 'nome_municipio', 'populacao_total', 'populacao']
    pop_idosa_absoluta_df = dfColumnsRename(populacao_idosa_absoluto, pop_idosa_absoluta_columns)

    # População idosa masculina
    pop_idosa_homem_columns = ['cod_uf', 'cod_municipio', 'nome_municipio', 'populacao_total', 'populacao_homem']
    pop_idosa_homem_df = dfColumnsRename(populacao_idosa_homem, pop_idosa_homem_columns)

    # População idosa feminina
    pop_idosa_mulher_columns = ['cod_uf', 'cod_municipio', 'nome_municipio', 'populacao_total', 'populacao_mulher']
    pop_idosa_mulher_df = dfColumnsRename(populacao_idosa_mulher, pop_idosa_mulher_columns)

    # União dos DFs
    pop_idosa_absoluta_df['populacao_homem'] = pop_idosa_homem_df['populacao_homem']
    pop_idosa_absoluta_df['populacao_mulher'] = pop_idosa_mulher_df['populacao_mulher']

    logging.info("Conversão dos tipos de dados da tabela")

    # Remoção das ultimas 2 linhas(que são um footer). Ponto de atenção! Regra fraca
    pop_idosa_absoluta_df = pop_idosa_absoluta_df[1:-2]

    pop_idosa_absoluta_df[pop_idosa_absoluta_columns[0]] = pop_idosa_absoluta_df[pop_idosa_absoluta_columns[0]].fillna(-1).astype(int)
    pop_idosa_absoluta_df[pop_idosa_absoluta_columns[1]] = pop_idosa_absoluta_df[pop_idosa_absoluta_columns[1]].fillna(-1).astype(int)
    pop_idosa_absoluta_df[pop_idosa_absoluta_columns[2]] = pop_idosa_absoluta_df[pop_idosa_absoluta_columns[2]].astype(str)
    pop_idosa_absoluta_df[pop_idosa_absoluta_columns[3]] = pop_idosa_absoluta_df[pop_idosa_absoluta_columns[3]].fillna(-1).astype(int)
    pop_idosa_absoluta_df[pop_idosa_absoluta_columns[4]] = pop_idosa_absoluta_df[pop_idosa_absoluta_columns[4]].fillna(-1).astype(int)

    # Remoção das linhas contendo o valor "-1"
    pop_idosa_absoluta_df = removeNegativeValues(pop_idosa_absoluta_df)

    # Inserção ao banco
    df_to_table( pop_idosa_absoluta_df, DATABASE, POPULACAO_IDOSA_TABLE)

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))