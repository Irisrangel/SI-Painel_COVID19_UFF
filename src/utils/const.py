#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : const.py
# FUNCAO                  : Validacao de variaveis
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
from utils.logger import logger
import os
import sys
import subprocess

logging = logger

# Variáveis de ambiente obrigatórias
assert os.getenv('MYSQL_USER') is not None, logging.error('Missing environment variable MYSQL_USER')
assert os.getenv('MYSQL_PASSWORD') is not None, logging.error('Missing environment variable MYSQL_PASSWORD')
assert os.getenv('WORK_ENV') is not None, logging.error('Missing environment variable WORK_ENV(dev/prod)')

# Variáveis de ambiente de código
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
WORK_ENV = os.getenv('WORK_ENV')

# Variável opcional para caso queira forçar um host
MYSQL_HOST = os.getenv('MYSQL_HOST')

# Paths
if(WORK_ENV=='dev'):
    INPUT_PATH = os.getcwd() + '/src/input'
    if(MYSQL_HOST == None):
        mysql_docker_container_name = 'mysql-uff-covid'
        command = "docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + mysql_docker_container_name
        MYSQL_HOST = subprocess.run( command, shell=True, capture_output=True).stdout.decode().strip()
else:
    INPUT_PATH = "/app/src/input"
    MYSQL_HOST = "mysql-uff-covid"