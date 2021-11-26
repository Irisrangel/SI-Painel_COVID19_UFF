#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : stage_covid.py
# FUNCAO                  : Realizar carga em tabela STAGE dos dados de covid-19.
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
import os
import json
import datetime

import pandas as pd
import sqlalchemy as sq

from utils import logger
from utils.mysql import df_to_table

logger.application = "LOAD_STAGE_COVID"
logging = logger.logger

DATABASE = 'uff'
COVID_TABLE = 'stg_covid'
#COVID_STATUS_DIARIO = 'src/status.json'
COVID_STATUS_DIARIO = 'src/input/covid/status.json'

def historico_status():
    with open(COVID_STATUS_DIARIO) as status_file:
        historico = {}
        if(os.stat(COVID_STATUS_DIARIO).st_size != 0):
            historico = json.load(status_file)
            return historico
        else:
            logging.warning("Primeira carga")
            return []

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
    historico = historico_status()

    if(historico == []):
        logging.warning("Não há arquivos extraídos e registrados na base({}). Por favor, execute a extração".format(COVID_STATUS_DIARIO))

    # Ultimo dia
    ud = list(historico.keys())[-1]
    compare_historico = [{}, {}]
    for dia in historico:
        print(dia)
        try:
            # Caso ja tenha carregado ou não tenha o arquivo, pule o dia
            if(historico[dia].get("load_status") == "OK" or historico[dia].get("extract_status") != "OK"):
                logging.info("Dia {} ja foi previamente carregado com sucesso".format(dia))
                continue

            start_time = time.time()

            # Carga anterior e carga atual
            compare_historico = compare_historico[1].copy(), historico[dia]
            historico[dia]['load_status'] = 'PENDING'
            historico[dia]['load_start'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            # Leitura do arquivo da população
            logging.info("Leitura do arquivo {}".format(historico[dia]['extract_arquivo']))
            covid = pd.read_csv(historico[dia]['extract_arquivo'], sep=';', header=0)

            # População
            covid_columns = ['uf', 'bairro', 'cep', 'municipio_res', 'idade', 'sexo', 'dt_evento', 'dt_sintoma', 'dt_coleta_dt_notif', 'classificacao', 'evolucao', 'dt_obito', 'comorbidade', 'dias']
            covid_df = covid[covid_columns]

            # Renomear
            covid_columns[3] = 'nome_municipio_res'
            covid_df = covid_df.rename(columns={'municipio_res':'nome_municipio_res'})

            # Remoção das células que não são dados
            logging.info("Conversão dos tipos de dados da tabela")

            covid_df[covid_columns[0]] = covid_df[covid_columns[0]].astype(str).str.strip()
            covid_df[covid_columns[1]] = covid_df[covid_columns[1]].astype(str).str.strip()
            covid_df[covid_columns[2]] = covid_df[covid_columns[2]].astype(str).str.strip()[:8] # CEP
            covid_df[covid_columns[3]] = covid_df[covid_columns[3]].astype(str).str.strip()
            covid_df[covid_columns[4]] = covid_df[covid_columns[4]].fillna(0).astype(int)
            covid_df[covid_columns[5]] = covid_df[covid_columns[5]].astype(str).str.strip()
            covid_df[covid_columns[6]] = pd.to_datetime( covid_df[covid_columns[6]])
            covid_df[covid_columns[7]] = pd.to_datetime( covid_df[covid_columns[7]])
            covid_df[covid_columns[8]] = pd.to_datetime( covid_df[covid_columns[8]])
            covid_df[covid_columns[9]] = covid_df[covid_columns[9]].astype(str).str.strip() # CONFIRMADO para true
            covid_df[covid_columns[10]] = covid_df[covid_columns[10]].astype(str).str.strip() # 'obito', nan
            covid_df[covid_columns[11]] = pd.to_datetime( covid_df[covid_columns[11]])
            covid_df[covid_columns[12]] = covid_df[covid_columns[12]].astype(str).str.strip()
            covid_df[covid_columns[13]] = covid_df[covid_columns[13]].fillna(0).astype(int)

            # Inserção ao banco
            linhas_inseridas = df_to_table( covid_df, DATABASE, COVID_TABLE)
            novas_linhas = linhas_inseridas - compare_historico[0].get('load_linhas', 0)

            end_time = time.time()
            historico[dia]['load_status'] = "OK"
            historico[dia]['load_duracao'] = round(( end_time - start_time), 4)
            historico[dia]['load_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_linhas'] = linhas_inseridas
            historico[dia]['load_linhas_novas'] = novas_linhas if novas_linhas else linhas_inseridas
            historico[dia]['load_error'] = ''
        except Exception as task_ex:
            logging.error("Falha ao carregador o dia {}".format(dia))
            end_time = time.time()
            historico[dia]['load_status'] = "FAIL"
            historico[dia]['load_duracao'] = round(( end_time - start_time), 4)
            historico[dia]['load_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_error'] = str(task_ex)

            # Atualizando o arquivo de status
            with open(COVID_STATUS_DIARIO, 'w+') as status_file:
                status_file.write(json.dumps(historico))

    # Atualizando o arquivo de status
    with open(COVID_STATUS_DIARIO, 'w+') as status_file:
        status_file.write(json.dumps(historico))

    logging.info("FIM")

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))