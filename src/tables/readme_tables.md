# Tabelas
Arquivo para guardar informações sobre todas as tabelas criadas no MySQL. Tais como a descrição de cada uma e o SQL utilizado para criação. Também serão guardados os diagramas sobre as relações das tabelas.

## Censo População Raw
Dados sobre a população estimada de cada municipio
```
CREATE TABLE IF NOT EXISTS stg_censo_populacao(
    uf VARCHAR(2),
    cod_uf VARCHAR(2),
    cod_municipio VARCHAR(6),
    nome_municipio VARCHAR(50),
    populacao_estimada INT
);
```

## Censo População Idosa Raw
Dados sobre a população idosa estimada de cada municipio
```
CREATE TABLE IF NOT EXISTS stg_censo_populacao_idosa(
    cod_uf VARCHAR(2),
    cod_municipio VARCHAR(6),
    nome_municipio VARCHAR(50),
    populacao_total INT,
    populacao INT,
    populacao_homem INT,
    populacao_mulher INT
);
```

## Informações epidemiologicas de COVID-19 Raw
Dados de saúde - Estado do invididuo em relação à enfermidade
```
CREATE TABLE IF NOT EXISTS stg_covid(
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
);
```

## Informações de mobilidade urbana Raw
Os dados mostram como deslocamento a lugares como supermercados e parques estão mudando em cada região geografica
```
CREATE TABLE IF NOT EXISTS stg_mobilidade(
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
);
```

## Tabela de Municipios Raw
Codigo de cada municipio segundo IBGE
```
CREATE TABLE IF NOT EXISTS tb_municipios(
    cod_municipio VARCHAR(7) NOT NULL
    ,cod_uf VARCHAR(2) COMMENT 'Codigo do estado' NOT NULL
    ,uf VARCHAR(2) NOT NULL
    ,nome_municipio VARCHAR(50) NOT NULL
	,PRIMARY KEY (cod_municipio)
) comment='Codigo de cada municipio segundo IBGE';
```