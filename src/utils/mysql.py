#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : mysql.py
# FUNCAO                  : Procedures para o banco de dados.
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
import sqlalchemy as sq
from utils.const import MYSQL_USER, MYSQL_HOST, MYSQL_PASSWORD
from utils import logger
from utils.tables import create_table

logging = logger.logger

def connect(database, table):
    try:
        # Conexão ao banco
        logging.info("Criando conexão com o banco de host [{}] e a base {}.{}".format(MYSQL_HOST, database, table))
        conn_str = "mysql+pymysql://{user}:{pw}@{hs}/{db}".format(user=MYSQL_USER,pw=MYSQL_PASSWORD,hs=MYSQL_HOST, db=database)
        engine = sq.create_engine(conn_str)
        return engine.connect()
    except:
        logging.error("Falha ao conectar na base de dados")
        raise

def delete_from_table(database, table, where_clause):
    conn = connect(database, table)

    try:
        logging.info("Removendo dados {} da tabela {}.{}".format(where_clause, database, table))
        conn.execute("DELETE FROM {}.{} WHERE {}".format(database, table, where_clause))
        logging.info("SUCESSO")
        conn.close()
    except Exception as task_ex:
        logging.error("[EXCEPTION] {}".format(task_ex))
        logging.error("[TRACEBACK] {}".format(traceback.format_exc()))
        if ( task_ex.code == 'f405' ):
            logging.warn("Tabela não existente. Criando tabela")
            conn.execute(create_table[table])
            conn.close()
        else:
            raise

def truncate_table(database, table):
    conn = connect(database, table)

    try:
        logging.info("Limpando tabela {}.{}".format(database, table))
        conn.execute("TRUNCATE TABLE {}.{}".format(database, table))
        conn.close()
    except Exception as task_ex:
        if ( task_ex.code == 'f405' ):
            logging.warn("Tabela não existente. Criando tabela")
            conn.execute(create_table[table])
            conn.close()
        else:
            raise

def insert_into(df, database, table):
    conn = connect(database, table)
    try:
        # Inserção ao banco
        logging.info("Inserindo informações na tabela {}.{}".format(database, table))
        df.to_sql(table, conn ,index=False, if_exists='append')
        logging.info("{} linhas inseridas em {}.{} com sucesso!".format( df.shape[0] , database, table))
        logging.info("Fechando conexão!")
        conn.close()
    except:
        # TODO: Processo para recuperação da tabela
        logging.error("Falha ao inserir os dados na tabela")
        raise

def df_to_table(df, database, table):
    conn = connect(database, table)
    #truncate_table(database, table)
    insert_into(df, database, table)

def select_max(database, table, col, where_clause = None):
    try:
        # Conexão ao banco
        logging.info("Criando conexão com o banco de host [{}] e a base {}.{}".format(MYSQL_HOST, database, table))
        conn_str = "mysql+pymysql://{user}:{pw}@{hs}/{db}".format(user=MYSQL_USER,pw=MYSQL_PASSWORD,hs=MYSQL_HOST, db=database)
        engine = sq.create_engine(conn_str)
        conn = engine.connect()
        try:
            logging.info("Buscando informacao no banco")
            if(where_clause):
                query = "SELECT MAX({}) FROM {}.{} WHERE {}".format( col, database, table, where_clause )
                max_value = conn.execute(query).fetchall()
                conn.close()
                return max_value[0][0]
            else:
                query = "SELECT MAX({}) FROM {}.{}".format( col, database, table)
                max_value = conn.execute(query).fetchall()
                conn.close()
                return max_value[0][0]
        except Exception as task_ex:
            if ( task_ex.code == 'f405' ):
                logging.warn("Tabela não existente. Criando tabela")
            else:
                raise
            error_dict = {
                'database': database, 
                'table': table,
                'query': query
            }
            logging.info("Falha ao requisitar dados. {}".format( error_dict ))
            logging.error("[EXCEPTION] {}".format(task_ex))
            logging.error("[TRACEBACK] {}".format(traceback.format_exc()))
            conn.close()
    except:
        raise
