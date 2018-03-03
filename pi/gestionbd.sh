#!/bin/bash

######
usuario="rpi"
password="fv"
basedatos="control_solar"

DATE=`date +%Y-%m-%d`
SQLFILE=$basedatos-${DATE}.sql

### creamos copia de la base de datos
mysqldump -u $usuario -p$password $basedatos > /home/pi/backBD/$SQLFILE 
gzip /home/pi/backBD/$SQLFILE

### eliminamos las copias de seguridad con mas de 10 dias de antiguedad
find /home/pi/backBD/$basedatos* -mtime +10 -exec rm {} \;

### vaciar contenido tablas datos, reles_grab y reles_segundos_on con antiguedad superior a 366 dias y log con 30 dias
python /home/pi/vaciartablas.py

### crear registro en tabla diario del dia anterior
python /home/pi/diario_ayer.py

### creamos copia de la base de datos solo de datos de ayer
mysqldump -u$usuario -p$password $basedatos log -w"DATE(Tiempo) >= SUBDATE(NOW(),INTERVAL 2 DAY)" > /home/pi/backBD/log_ayer.sql
gzip /home/pi/backBD/log_ayer.sql

mysqldump -u$usuario -p$password $basedatos datos -w"DATE(Tiempo) >= SUBDATE(NOW(),INTERVAL 2 DAY)" > /home/pi/backBD/datos_ayer.sql
gzip /home/pi/backBD/datos_ayer.sql

mysqldump -u$usuario -p$password $basedatos diario -w"DATE(Fecha) >= SUBDATE(NOW(),INTERVAL 2 DAY)" > /home/pi/backBD/diario_ayer.sql
gzip /home/pi/backBD/diario_ayer.sql

