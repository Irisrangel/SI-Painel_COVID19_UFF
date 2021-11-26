#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : extract_covid.py
# FUNCAO                  : Realizar extracao dos dados de covid-19.
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
import requests
from datetime import datetime
import traceback
import zipfile
import os
import gzip
import shutil
import uuid
from utils import logger

logger.application = "EXTRACT_COVID"
logging = logger.logger

def run():
    data_extracao = datetime.today()
    ano, mes, dia = datetime.today().year, datetime.today().month, datetime.today().day

    file_id = str(uuid.uuid4())
    tmp_downloading = '/tmp/' + file_id + '.csv'
    logging.info("Iniciando extração do covid. [{}]".format(tmp_downloading))

    url = 'http://painel.saude.rj.gov.br/arquivos/COVID.CSV'
    logging.info("Fazendo requisição do arquivo")
    r = requests.get(url, allow_redirects=True, stream = True)

    logging.info("Baixando arquivo")
    output = open(tmp_downloading, 'wb')

    try:
        for chunk in r.iter_content(chunk_size=1024):
            output.write(chunk)

        output.close()

        output_path = 'src/input/covid/{}/{}/{}'.format(ano, mes, dia)
        output_file_path = '{}/covid_{}-{}-{}-{}'.format(output_path, ano, mes, dia, file_id)
        os.makedirs( output_path, exist_ok=True )

        logging.info("Particionando e compactando arquivo. [{}]".format(output_file_path))
        with open(tmp_downloading, 'rb') as f_in:
            with gzip.open(output_file_path + '.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        logging.info("Deletando arquivo temporário")
        os.remove(tmp_downloading)
    except:
        logging.error("Falha ao baixar e compactar arquivo")
        logging.info("Deletando arquivo temporário")
        os.remove(tmp_downloading)
        raise

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))