#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : logger.py
# FUNCAO                  : Gerar logs.
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
import logging.handlers
import os
import socket
import time
import json


class __Formatter(logging.Formatter):
    converter = time.gmtime   # Force UTC timestamp

    def format(self, record):
        global application

        record.application = application
        return super().format(record)


application = None
log_format = "[%(levelname)s] %(asctime)s [%(application)s]: %(message)s"

# Removing existing handlers
logger = logging.getLogger()
if logger.handlers:
    for handler in logger.handlers:
        logger.removeHandler(handler)

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logger.setLevel(logging.getLevelName(LOG_LEVEL))

# Logger stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(__Formatter(log_format))

file_handler = logging.FileHandler('src/log.txt')
file_handler.setFormatter(__Formatter(log_format))

logger.addHandler(file_handler)
logger.addHandler(stream_handler)
