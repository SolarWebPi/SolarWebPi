#!/bin/bash

######
usuario="rpi"
password="fv"
basedatos="control_solar"



### creamos copia de la base de datos solo de datos de hoy
mysqldump -u$usuario -p$password $basedatos log -w"DATE(Tiempo) >= SUBDATE(NOW(),INTERVAL 1 DAY)" > /home/pi/backBD/log_hoy.sql
gzip /home/pi/backBD/log_hoy.sql

mysqldump -u$usuario -p$password $basedatos datos -w"DATE(Tiempo) >= SUBDATE(NOW(),INTERVAL 1 DAY)" > /home/pi/backBD/datos_hoy.sql
gzip /home/pi/backBD/datos_hoy.sql

mysqldump -u$usuario -p$password $basedatos diario -w"DATE(Fecha) >= SUBDATE(NOW(),INTERVAL 1 DAY)" > /home/pi/backBD/diario_hoy.sql
gzip /home/pi/backBD/diario_hoy.sql

