#!/bin/bash

clear

unset password
unset password1
unset rootpass

echo
echo "Bienvenido al programa de instalación de la BD y tablas,"
echo "para: RPi: Control Sistema Fotovoltaico"
echo
#usuario
echo -n "Introduce nombre de usuario: "
read usuario

echo
PROMPT="Introduce contraseña: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    password+="$char"
done
echo

echo
PROMPT="Vuelve a introducir la contraseña: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    password1+="$char"
done
echo

if [ "$password" != "$password1" ]; then
	echo
        echo "Error, la contraseña no coincide. Vuelve a empezar."
        exit 0

fi
echo


#base de datos
echo -n "Introduce nombre de la base de datos: "
read basedatos
echo


echo
PROMPT="Introduzca contraseña de root: "
while IFS= read -p "$PROMPT" -r -s -n 1 char; do
    if [[ $char == $'\0' ]]; then
        break
    fi
    PROMPT='*'
    rootpass+="$char"
done
echo


#crear base de datos

echo "Creando base de datos y otorgando permisos a $usuario..."
mysql -h localhost -u root -p$rootpass -e "CREATE DATABASE $basedatos CHARACTER SET latin1 COLLATE latin1_spanish_ci"
#creamos usuario para conectar al servidor desde localhost con su contraseña
mysql -h localhost -u root -p$rootpass -e "GRANT USAGE ON *.* to $usuario@localhost identified by '$password'"
#otorgamos todos los privilegios al usuario para la base de datos
mysql -h localhost -u root -p$rootpass -e "GRANT ALL PRIVILEGES on $basedatos.* to $usuario@localhost"
echo

echo "Creando tablas necesarias...un momento..."
#creamos tabla datos con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE datos (
id INT(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
Tiempo DATETIME,
Ibat FLOAT,
Vbat FLOAT,
SOC FLOAT,
DS FLOAT,
Vflot TINYINT(1) UNSIGNED,
kWhp_bat FLOAT,
kWhn_bat FLOAT,
Iplaca FLOAT,
Vplaca FLOAT,
kWh_placa FLOAT,
Temp FLOAT
)"

datetouse=$(date +'%F %T')
#voltaje sistema
echo -n "Introduce voltaje sistema: "
read voltios
#SOC
echo -n "Introduce valor aproximado del SOC: "
read SOC
#DS
echo -n "Introduce DS (previamente calculado, mirar foro): "
read DS
#introducimos algunos datos en la tabla para que no de error fv.py
mysql -h localhost -u $usuario -p$password $basedatos -e "INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Vflot,kWhp_bat,KWhn_bat,Iplaca,Vplaca,KWh_placa,Temp) VALUES ('$datetouse',0,'$voltios','$SOC','$DS',0,0,0,0,0,0,25)"

echo "tabla parametros"
#creamos tabla parametros con el $usuario y valores por defecto
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE parametros (
grabar_datos VARCHAR(1) NOT NULL,
grabar_reles VARCHAR(1) NOT NULL,
t_muestra FLOAT NOT NULL,
n_muestras_grab TINYINT(3) NOT NULL,
nuevo_soc FLOAT NOT NULL DEFAULT '0',
vplaca_diver FLOAT NOT NULL DEFAULT '70',
tipo_diver VARCHAR(6) NOT NULL DEFAULT 'vaux',
id_parametros TINYINT(3) NOT NULL DEFAULT '1' PRIMARY KEY
)"
#introducimos valores en la tabla parametros
mysql -h localhost -u $usuario -p$password $basedatos -e "INSERT INTO parametros (grabar_datos,grabar_reles,t_muestra,n_muestras_grab,id_parametros) VALUES ('S','N',5,1,1)"

echo "tabla reles"
#creamos tabla reles con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE reles (
id_rele SMALLINT(3) UNSIGNED PRIMARY KEY,
nombre TEXT NOT NULL,
modo VARCHAR(3) NOT NULL DEFAULT 'PRG',
estado TINYINT(3)  UNSIGNED NOT NULL DEFAULT '0',
grabacion VARCHAR(1) NOT NULL DEFAULT 'N',
salto TINYINT(3) UNSIGNED NOT NULL DEFAULT '100',
prioridad TINYINT(3) UNSIGNED NOT NULL DEFAULT '0'
)"

echo "tabla reles_c"
#creamos tabla reles_c con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE reles_c (
id_rele SMALLINT(3) UNSIGNED,
operacion VARCHAR(3) NOT NULL DEFAULT 'ON',
parametro VARCHAR(10) NOT NULL,
condicion VARCHAR(1) NOT NULL DEFAULT '>',
valor FLOAT NOT NULL DEFAULT '0',
id_reles_c SMALLINT(4) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
)"

echo "tabla reles_grab"
#creamos tabla reles_grab con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE reles_grab (
Tiempo DATETIME,
id_rele SMALLINT(3) UNSIGNED,
valor_rele TINYINT(3) UNSIGNED,
id_reles_grab INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
)"

echo "tabla reles_h"
#creamos tabla reles_h con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE reles_h (
id_rele SMALLINT(3) UNSIGNED,
parametro_h VARCHAR(1) DEFAULT 'T',
valor_h_ON TIME,
valor_h_OFF TIME,
id_reles_h SMALLINT(5) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
)"

echo "tabla reles_segundos_on"
#creamos tabla reles_segundos_on con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE reles_segundos_on (
id_rele SMALLINT(3) UNSIGNED,
fecha DATE,
segundos_on FLOAT NOT NULL,
nconmutaciones MEDIUMINT(5) UNSIGNED DEFAULT '0',
id_reles_segundos_on INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY
)"

echo "tabla diario"
#creamos tabla diario con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE diario (
Fecha date NOT NULL PRIMARY KEY,
maxVbat float NOT NULL,
minVbat float NOT NULL,
avgVbat float NOT NULL,
maxSOC float NOT NULL,
minSOC float NOT NULL,
avgSOC float NOT NULL,
maxIbat float NOT NULL,
minIbat float NOT NULL,
avgIbat float NOT NULL,
maxIplaca float NOT NULL,
avgIplaca float NOT NULL,
kWh_placa float NOT NULL,
KWhp_bat float NOT NULL,
KWhn_bat float NOT NULL,
kWh_consumo float NOT NULL,
maxTemp float NOT NULL,
minTemp float NOT NULL,
avgTemp float NOT NULL
)"

echo "tabla log"
#creamos tabla log con el $usuario
mysql -h localhost -u $usuario -p$password $basedatos -e "CREATE TABLE log (
id_log INT(11) UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
Tiempo DATETIME NOT NULL,
log VARCHAR(50) NOT NULL
)"

echo
echo "Hecho"
