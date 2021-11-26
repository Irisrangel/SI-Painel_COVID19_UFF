import traceback
import time
import argparse
import os
import json

import pandas as pd
import sqlalchemy as sq

from utils import logger
from utils.mysql import df_to_table, select_max, insert_into, delete_from_table
from utils.const import INPUT_PATH
import datetime

logger.application = "LOAD_STAGE_MOBILIDADE"
logging = logger.logger

DATABASE = 'uff'
TABLE = 'stg_mobilidade'

def run():
    logging.info("INICIO")
    # Buscando todos os dias não carregados

    mobilidade_status_diario = 'src/input/mobilidade/status.json'
    with open(mobilidade_status_diario) as status_file:
        # Cada linha do arquivo é um dicionario em Json e as keys são DATA(YYYY-MM-DD)
        falhas = {}
        historico = {}
        if(os.stat(mobilidade_status_diario).st_size != 0):
            historico = json.load(status_file)
        else:
            logging.warning("Não há arquivos extraídos")
            logging.info("FIM")
            exit()

    dias_nao_ok = 0
    for dia in historico:
        try:
            start_time = time.time()
            extracao_ok = historico[dia]['extract_status'] == 'OK'
            ingestao = historico[dia].get('load_status')

            if(ingestao == "OK"):
                continue

            if(ingestao == 'FAIL' or ingestao == 'PENDING'):
                delete_from_table(DATABASE, TABLE, 'date = "{}"'.format(dia))

            historico[dia]['load_status'] = "PENDING"
            dias_nao_ok += 1
            # Leitura do arquivo da população
            logging.info("Leitura do arquivo {}".format(historico[dia]['extract_arquivo']))
            df = pd.read_csv(historico[dia]['extract_arquivo'], sep=",", engine='python')

            # Remoção das células que não são dados
            logging.info("Conversão dos tipos de dados da tabela")
            df[df.columns[0]] = df[df.columns[0]].astype(str).str.strip()
            df[df.columns[1]] = df[df.columns[1]].astype(str).str.strip()
            df[df.columns[2]] = df[df.columns[2]].astype(str).str.strip()
            df[df.columns[3]] = df[df.columns[3]].astype(str).str.strip()
            df[df.columns[4]] = df[df.columns[4]].fillna(0).astype(float)
            df[df.columns[5]] = df[df.columns[5]].astype(str).str.strip()
            df[df.columns[6]] = df[df.columns[6]].fillna(0).astype(float)
            df[df.columns[7]] = pd.to_datetime(df[df.columns[7]])

            insert_into( df, DATABASE, TABLE)
            end_time = time.time()
            historico[dia]['load_status'] = "OK"
            historico[dia]['load_duracao'] = round(( end_time - start_time), 4)
            historico[dia]['load_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_error'] = ''

        except Exception as task_ex:

            end_time = time.time()
            historico[dia]['load_status'] = "FAIL"
            historico[dia]['load_duracao'] = round(( end_time - start_time), 4)
            historico[dia]['load_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
            historico[dia]['load_error'] = str(task_ex)

    if(dias_nao_ok == 0 ):
        logging.info("Não há novos arquivos à serem ingeridos.")

    # Atualizando o arquivo de status
    with open(mobilidade_status_diario, 'w+') as status_file:
        status_file.write(json.dumps(historico))

    logging.info("FIM")

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))