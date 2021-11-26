#!/bin/bash

MAX_BKP_NUMBER=6

last_month=$(date -d "-30 days" '+%Y_%m')
persist_log="log_$last_month.txt"
mv src/log.txt src/$persist_log
gzip src/$persist_log

echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S.%3N') [ROTAGE_LOGS]: START" >> src/log.txt

log_count="$(find src/log_*.txt.gz -maxdepth 1 -type f | wc -l)"
bkp_file="$(ls -Art src/log_*.txt.gz | head -n 1 | tail ${i})"
extra_backups="$(expr $log_count - $MAX_BKP_NUMBER)"

if [ $extra_backups -gt 0 ]
    then
        # Remoção de todos os backups extras do mais antigo para o mais novo
        for i in $(seq 1 1 ${extra_backups});     
            do  
                oldest_bkp="$(ls -Art src/log_*.txt.gz | head -n 1)"
                rm $oldest_bkp
                echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S.%3N') [ROTAGE_LOGS]: Removendo o backup ${oldest_bkp}" >> src/log.txt
        done
    else
        echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S.%3N') [ROTAGE_LOGS]: Não há backups extras à serem removidos" >> src/log.txt
fi

echo "[INFO] $(date '+%Y-%m-%d %H:%M:%S.%3N') [ROTAGE_LOGS]: END" >> src/log.txt