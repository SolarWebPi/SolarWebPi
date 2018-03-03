#!/usr/bin/python
# -*- coding: utf-8 -*-

import time 
import MySQLdb 
import os  #para reinico router
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token

###### FV_Diario es un grupo que he creado en Telegram para envio cada hora
###### de un mensaje con la situacion FV
###### Poner Nuestro token del bot creado
TOKEN = 'XXXXXXXXXXXX' 
bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

###### ID de Usuarios de TELEGRAM
Aut=[-XXXXX,YYYYYY,-ZZZZZZZ] #   
cid=Aut[0] # poner el usuario donde queremos mandar el msg 

###### Parametros Base de Datos
servidor = 'localhost' 
usuario = 'rpi' 
clave = 'fv' 
basedatos = 'control_solar'

# --------------------- DEFINICION DE FUNCIONES --------------

def logBD(texto) : # Incluir en tabla de Log
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        #print tiempo,' ', texto
        db.commit()
    except:
        db.rollback()
    
    return

## RECUPERAR ULTIMO REGISTRO DE LA BD y SITUACION RELES ##

try:

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

   #DATOS FV
    sql='SELECT Tiempo,SOC,Vbat,Vflot,Ibat,Iplaca,Vplaca,kWhp_bat,kWhn_bat,kWh_placa,Temp FROM datos ORDER BY id DESC limit 1'
    cursor.execute(sql)
    var=cursor.fetchone()
    Hora_BD=str(var[0])
    SOC=float(var[1])
    Vbat=float(var[2])
    Vflot=float(var[3])
    Ibat=float(var[4])
    Iplaca=float(var[5])
    Vplaca=float(var[6])
    kWhp_bat=float(var[7])
    kWhn_bat=float(var[8])
    kWh_placa=float(var[9])
    Temp=float(var[10])

   # RELES
    sql_reles='SELECT * FROM reles'
    nreles=cursor.execute(sql_reles)
    nreles=int(nreles)  # = numero de reles
    TR=cursor.fetchall()
    
except Exception as e:

    
    Hora_BD='Error BD'
    SOC=0
    Vbat=0
    Vflot=0
    Ibat=0
    Iplaca=0
    Vplaca=0
    kWhp_bat=0
    kWhn_bat=0
    kWh_placa=0
    Temp=0

    nreles=0

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

# -------------------------------- BUCLE PRINCIPAL --------------------------------------

salir=False
N=1
Nmax=28
               
while salir!=True and N<Nmax:

    #print salir,N
    
    # ------------------------ LECTURA FECHA / HORA ----------------------

    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    diasemana = time.strftime("%w")	
    hora = time.strftime("%H:%M:%S")
    
    # ----------- MSG TELEGRAM ------------------------

    L1='SOC='+str(round(SOC,1))+'% -- Vbat='
    L1=L1+str(round(Vbat,1))+'v -- Exc='
    L1=L1+str(int(round(Vflot,0)))

    L2='Iplaca='+str(round(Iplaca,1))+'A -- Ibat='
    L2=L2+str(round(Ibat,1))+'A - Vpl='
    L2=L2+str(round(Vplaca,1))


    L3='Kwh: Placa='+str(round(kWh_placa/1000,1))+' - Bat='
    L3=L3+str(round(kWhp_bat/1000,1))+'-'+str(round(kWhn_bat/1000,2))+'='+str(round((kWhp_bat-kWhn_bat)/1000,1))
            
    L4='RELES('
   
    for I in range(nreles): # Reles wifi
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 2:
            valor=int(TR[I][3]/10)
            if valor ==10:
                texto='X'
            else:
                texto=str(valor)
            L4=L4+texto
    L4=L4+') ('

    for I in range(nreles): # Reles i2C
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 3:
            valor=int(TR[I][3]/10)
            if valor ==10:
                texto='X'
            else:
                texto=str(valor)
            L4=L4+texto
            
    L4 = L4 + ')'
    L5 =  Hora_BD + ' - T=' + str(round(Temp,1))+'ºC'
    
   ###Usando BOT
    tg_msg = L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5 

    try:               
        bot.send_message( cid, tg_msg)
        salir=True
    except:
        salir=False
        time.sleep(60)
        N=N+1
        
           
#--------------------------------------------------

if N>=Nmax: 
    logBD(' Msg Telegram no enviado en '+str(N)+' intentos') # incluyo mensaje en el log

cursor.close()
db.close()
  
