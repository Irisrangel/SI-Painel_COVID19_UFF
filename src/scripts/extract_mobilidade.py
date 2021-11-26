#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : extract_mobilidade.py
# FUNCAO                  : Realizar extracao dos dados de mobilidade urbana.
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
import time
import datetime
import traceback
import zipfile
import os
import gzip
import shutil
import uuid
import json
import pandas as pd
from zipfile import ZipFile
from utils import logger

logger.application = "EXTRACT_MOBILIDADE"
logging = logger.logger

def run():
    # Criando um nome unico para o arquivo temporario
    file_id = str(uuid.uuid4())
    tmp_downloading = '/tmp/' + file_id + '.zip'
    logging.info("Iniciando extração do covid. [{}]".format(tmp_downloading))

    # Download do arquivo compactado com todos os paises
    url = 'https://www.gstatic.com/covid19/mobility/Region_Mobility_Report_CSVs.zip'
    logging.info("Fazendo requisição do arquivo")
    r = requests.get(url, allow_redirects=True, stream = True)

    logging.info("Baixando arquivo")
    output = open(tmp_downloading, 'wb')

    try:
        for chunk in r.iter_content(chunk_size=1024000):
            output.write(chunk)

        output.close()

        mobilidade_status_diario = 'src/input/mobilidade/status.json'

        historico = {}
        with open(mobilidade_status_diario) as status_file:
            # Cada linha do arquivo é um dicionario em Json e as keys são DATA(YYYY-MM-DD)
            falhas = {}
            if(os.stat(mobilidade_status_diario).st_size != 0):
                historico = json.load(status_file)
                for dia in historico:
                    if(historico[dia]['extract_status'] != 'OK'):
                        falhas[dia] = historico[dia]

        # Leitura do arquivo baixado
        br_file_id = str(uuid.uuid4())
        br_tmp_downloading = '/tmp/' + br_file_id

        # Extraindo apenas os dados do Brasil
        with ZipFile(tmp_downloading, 'r') as report_todos_paises:
            reports_por_pais = report_todos_paises.namelist()
            for pais_report in reports_por_pais:
                if "BR_Region_Mobility_Report" in pais_report:
                    csv_brasil_path = br_tmp_downloading + "/" + pais_report
                    report_todos_paises.extract(pais_report, br_tmp_downloading)

        os.remove(tmp_downloading)

        df0 = pd.read_csv(csv_brasil_path, sep=",", engine='python')

        # Carga de todas as falhas
        for data_falha in falhas:
            try:
                start_time = time.time()
                ano, mes, dia = data_falha.split('-')

                output_path = 'src/input/mobilidade/{}/{}'.format(ano, mes)
                output_file_path = '{}/mobilidade_{}-{}-{}-{}.csv'.format( output_path, ano, mes, dia, str(uuid.uuid4()) )
                os.makedirs( output_path, exist_ok=True )

                # Pegando apenas a data que houve falha no carregamento
                df = df0[df0['date'] == data_falha]
                df.to_csv( output_file_path, encoding = 'utf8', index=False)

                logging.info("[REPROCESSING]Particionando e compactando arquivo. [{}]".format(output_file_path))
                output_compressed_file_path = output_file_path + '.gz'
                with open(output_file_path, 'rb') as f_in:
                    with gzip.open( output_compressed_file_path , 'wb' ) as f_out:
                        shutil.copyfileobj(f_in, f_out)

                if(historico.get(data_falha) is None):
                    historico[data_falha] = {}

                # Gerando linha de sucesso para o arquivo de status
                end_time = time.time()
                historico[data_falha]['extract_status'] = 'OK'
                historico[data_falha]['extract_duracao'] = round(( end_time - start_time), 4)
                historico[data_falha]['extract_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                historico[data_falha]['extract_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                historico[data_falha]['extract_arquivo'] = output_compressed_file_path
                historico[data_falha]['extract__error'] = ''
            except Exception as task_ex:
                # Gerando linha de falha para o arquivo de status
                historico[data_falha]['extract_status'] = 'FAIL'
                historico[data_falha]['extract_duracao'] = round(( end_time - start_time), 4)
                historico[data_falha]['extract_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                historico[data_falha]['extract_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                historico[data_falha]['extract_arquivo'] = ''
                historico[data_falha]['extract__error'] = str(task_ex)
                logging.error("Falha ao baixar e compactar arquivo particionado")

        # Verificando se é a primeira vez que o programa roda
        if(historico):
            # Ultima data no historico(de acordo com o arquivo de status)
            ultimo_dia_carregado = list(historico.keys())[-1]
            ts_udc = datetime.datetime.strptime(ultimo_dia_carregado, "%Y-%m-%d")
            ts_udc = ts_udc + datetime.timedelta(days=1)
        else:
            # Primeira data no dataframe
            ultimo_dia_carregado = min(df0['date'])
            ts_udc = datetime.datetime.strptime(ultimo_dia_carregado, "%Y-%m-%d")

        tem_dados = True
        # Para que na mudança de mês, não dê falso negativo em dataframe zerado yyyy-02-31 por exemplo
        evitar_bissexto = 4
        while(tem_dados):
            start_time = time.time()
            str_udc = ts_udc.strftime('%Y-%m-%d')
            df = df0[df0['date'] == str_udc]

            if(df.empty):
                evitar_bissexto -= 1
                ts_udc = ts_udc + datetime.timedelta(days=1)
                if(evitar_bissexto == 0):
                    logging.info("Evitando ano bissexto, ultima verificação dia {} ".format(str_udc))
                    tem_dados = False
            else:
                try:
                    historico[str_udc] = {'extract_status':'PENDING'}
                    evitar_bissexto = 4
                    ano, mes, dia = str_udc.split('-')

                    # Formatando a saída
                    output_path = 'src/input/mobilidade/{}/{}'.format(ano, mes)
                    output_file_path = '{}/mobilidade_{}-{}-{}-{}.csv'.format( output_path, ano, mes, dia, str(uuid.uuid4()) )
                    output_compressed_file_path = output_file_path + '.gz'
                    os.makedirs( output_path, exist_ok=True )

                    df.to_csv( output_file_path, encoding = 'utf8', index=False)
                    logging.info("Sucesso para extrair o dia {}".format( str_udc ) )

                    with open(output_file_path, 'rb') as f_in:
                        with gzip.open( output_compressed_file_path , 'wb' ) as f_out:
                            shutil.copyfileobj(f_in, f_out)

                    logging.info("Sucesso para compactar o dia {}".format(output_file_path))
                    end_time = time.time()

                    # Gerando linha de sucesso para o arquivo de status
                    historico[str_udc]['extract_status'] = 'OK'
                    historico[str_udc]['extract_duracao'] = round(( end_time - start_time), 4)
                    historico[str_udc]['extract_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                    historico[str_udc]['extract_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                    historico[str_udc]['extract_arquivo'] = output_compressed_file_path

                    # Remoção do arquivo não compactado do dia extraído
                    os.remove(output_file_path)

                    ts_udc = ts_udc + datetime.timedelta(days=1)

                except:
                    # Estudar casos de falhas desconhecido e implementar no 'status' os motivos do erro
                    logging.error("Falha para extrair o dia {}".format( str_udc.strftime('%Y-%m-%d') ) )
                    logging.error("[EXCEPTION] {}".format(task_ex))
                    logging.error("[TRACEBACK] {}".format(traceback.format_exc()))
                    end_time = time.time()

                    # Gerando linha de falha para o arquivo de status
                    historico[str_udc]['extract_status'] = 'FAIL'
                    historico[str_udc]['extract_duracao'] = round(( end_time - start_time), 4)
                    historico[str_udc]['extract_inicio'] = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                    historico[str_udc]['extract_fim'] = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                    historico[str_udc]['extract_arquivo'] = ''

                    ts_udc = ts_udc + datetime.timedelta(days=1)

        # Atualizando o arquivo de status
        with open(mobilidade_status_diario, 'w+') as status_file:
            status_file.write(json.dumps(historico))

        logging.info("Deletando arquivo temporário")
        os.remove( csv_brasil_path )
        os.removedirs( br_tmp_downloading )
        logging.info("FIM")
    except:
        logging.error("Falha ao baixar e compactar arquivo")
        logging.info("Deletando arquivo temporário")
        os.remove(tmp_downloading)
        with open(mobilidade_status_diario + ".error", 'w+') as status_file:
            status_file.write(json.dumps(historico))
        raise

if __name__ == '__main__':
    try:
        run()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))