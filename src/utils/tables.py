#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#==============================================================
# SCRIPT                  : tables.py
# FUNCAO                  : Criar tabelas on banco de dados.
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
stg_censo_populacao ="""CREATE TABLE IF NOT EXISTS stg_censo_populacao(
    uf VARCHAR(2), 
    cod_uf VARCHAR(2) COMMENT 'Codigo do estado', 
    cod_municipio VARCHAR(6), 
    nome_municipio VARCHAR(50), 
    populacao_estimada INT
) comment='Dados sobre a população estimada de cada municipio';
"""

stg_censo_populacao_idosa = """CREATE TABLE IF NOT EXISTS stg_censo_populacao_idosa(
    cod_uf VARCHAR(2) COMMENT 'Codigo do estado',
    cod_municipio VARCHAR(6),
    nome_municipio VARCHAR(50),
    populacao_total INT COMMENT 'Populacao sem restrição de idade',
    populacao INT COMMENT 'Populacao idosa',
    populacao_homem INT COMMENT 'Populacao de homens idosos',
    populacao_mulher INT COMMENT 'Populacao de mulheres idosas'
) comment='Dados sobre a população idosa estimada de cada municipio';
"""

stg_covid = """CREATE TABLE IF NOT EXISTS stg_covid(
    uf VARCHAR(2) COMMENT 'Sigla do estado',
    bairro VARCHAR(50),
    cep VARCHAR(8),
    nome_municipio_res VARCHAR(50),
    idade INT,
    sexo VARCHAR(2),
    dt_evento DATETIME,
    dt_sintoma DATETIME,
    dt_coleta_dt_notif DATETIME,
    classificacao VARCHAR(20),
    evolucao VARCHAR(20),
    dt_obito DATETIME,
    comorbidade VARCHAR(100),
    dias INT
) comment='Estado do invididuo em relação à enfermidade';"""

stg_mobilidade = """CREATE TABLE IF NOT EXISTS stg_mobilidade(
    country_region_code VARCHAR(2) COMMENT 'Sigla pais',
    country_region VARCHAR(20) COMMENT 'Nome pais',
    sub_region_1 VARCHAR(50) COMMENT 'Estado',
    sub_region_2 VARCHAR(50) COMMENT 'Cidade',
    metro_area FLOAT COMMENT 'Desconhecida',
    iso_3166_2_code VARCHAR(5) COMMENT 'Sigla pais e estado concatenada',
    census_fips_code FLOAT COMMENT 'Desconhecida',
    date DATETIME COMMENT 'Data do report',
    retail_and_recreation_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de lugares como restaurantes, cafes, shopping centers, parques tematicos, museus, bibliotecas e cinemas',
    grocery_and_pharmacy_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de lugares como mercados, armazens de alimentos, feiras, lojas especializadas em alimentos, drogarias e farmacias',
    parks_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de lugares como parques locais e nacionais, praias públicas, marinas, parques para cães, praças e jardins públicos',
    transit_stations_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de lugares como terminais de transporte público, tipo estações de metrô, ônibus e trem',
    workplaces_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de locais de trabalho',
    residential_percent_change_from_baseline INT COMMENT 'Tendencias de mobilidade de areas residenciais'
) COMMENT='Os dados mostram como visitas a lugares como supermercados e parques estão mudando em cada região geografica';"""






create_table = {}

create_table['stg_censo_populacao'] = stg_censo_populacao
create_table['stg_censo_populacao_idosa'] = stg_censo_populacao_idosa
create_table['stg_covid'] = stg_covid
create_table['stg_mobilidade'] = stg_mobilidade