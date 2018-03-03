#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import time # Librería para hacer que el programa que controla el bot no se acabe.
import random
import datetime
import token
import os
import commands

import MySQLdb
import sys

###### Poner Nuestro token del bot creado
TOKEN = 'XXXXXXXX' 
bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
bot.skip_pending=True # Skip the pending messages

###### ID de Usuarios que autorizo a cambiar valores en TELEGRAM
Aut=[xxx,yyyy,zzzz]

###### Acceso BD
servidor = 'localhost'
usuario = 'rpi'
clave = 'fv'
basedatos = 'control_solar'



#markup=types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=True,resize_keyboard=True)

#############################################
#Listener
def listener(messages): #definimos función 'listener', recibe como parámetro 'messages'.
    try:
        for m in messages: # Por cada dato 'm' en el dato 'messages'
            cid = m.chat.id # Almacenaremos el ID de la conversación.

            tg_to=cid
            tg_to_u=str(m.chat.first_name)
            tg_from=cid

            if m.content_type == 'text':
               
                #print m
                
                print " Mensaje de [" + str(cid) + "]: " + m.text # Y haremos que imprima algo parecido a esto -> [52033876]: /start
                
                if m.text[0]=='#':
                    tg_orden=str(m.text[1:])

                    orden_autorizada=1

                    #bot.send_message( cid, "Orden introducida "+tg_orden)
                    bot.send_chat_action(cid,'typing')
                    
                    tipo_orden= tg_orden[0].upper() # H, I, R, P,

                    print 'Orden introducida ',tg_orden, ' tipo=',tipo_orden
                    

                    #------------------ ORDEN RELES -----------------------
                    if tipo_orden=='R':
                        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                        cursor = db.cursor()
                        try:
                            objeto_orden= tg_orden[1:4]
                            orden= tg_orden[4:].upper()
                        except:
                            objeto_orden=''
                            orden=''
                        try:
                            orden1=orden[0]
                        except:
                            orden1=''
                        
                        try:
                            orden2=orden[1:]
                        except:
                            orden2=''   

                        # -------- Sub_Orden ON/OFF/PRG ---------    
                        if (orden=='ON' or orden=='OFF' or orden=='PRG'):
                            if orden_autorizada==1:
                                try:
                                    sql = "UPDATE reles SET modo='"+orden+ "' WHERE id_rele="+objeto_orden
                                    cursor.execute(sql)
                                    db.commit()
                                                                        
                                    msg='Rele Nº'+objeto_orden+' puesto a '+ orden + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)
                                    
                                except:
                                    msg='No se puede actualizar la tabla reles con la orden recibida   '+sql
                                    bot.send_message( cid, msg)
                                                                        
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)
                                
                                
                        # -------- Sub_Orden Cambio Nombre Rele ---------    
                        elif orden1=='N':
                            if orden_autorizada==1:
                                try:
                                    sql = "UPDATE reles SET nombre='"+orden2+ "' WHERE id_rele="+objeto_orden
                                    cursor.execute(sql)
                                    db.commit()
                                    msg='Nombre Rele Nº'+objeto_orden+' ='+ orden2 + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)
                                    
                                except:
                                    msg='No se puede actualizar la tabla reles con la orden recibida   '+sql
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden Creacion Rele ---------    
                        elif orden1=='C':
                            if orden_autorizada==1:
                                try:
                                    orden2=orden2[1:]
                                    cursor.execute("""INSERT INTO reles
                                                   (id_rele,nombre,modo,estado,grabacion)
                                                   VALUES (%s,%s,%s,%s,%s)""",
                                                        (objeto_orden,orden2,'OFF',0,'N'))

                                    db.commit()
                                    msg='Creado Rele Nº'+objeto_orden+' ='+ orden2 + ' por ' +tg_to_u
                                    bot.send_message( cid, msg)

                                except:
                                    msg='No se puede crear rele con la orden recibida   '
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden Borrado Rele ---------    
                        elif orden1=='B':
                            if orden_autorizada==1:
                                try:
                                    sql = "DELETE FROM reles  WHERE id_rele="+objeto_orden
                                    cursor.execute(sql)
                                    db.commit()
                                    msg='Borrado Rele Nº'+objeto_orden+' por ' +tg_to_u
                                    bot.send_message( cid, msg)

                                except:
                                    msg='No se puede crear rele con la orden recibida   '
                                    bot.send_message( cid, msg)
                            else:
                                msg=tg_from+' NO tiene permiso para esta orden'
                                bot.send_message( cid, msg)

                        # -------- Sub_Orden informacion Reles ---------
                        elif orden=='':
                            try:
                                sql = "SELECT id_rele,nombre,modo,estado,grabacion FROM reles"
                                cursor.execute(sql)
                                nreles=cursor.execute(sql)
                                nreles=int(nreles)  # = numero de reles
                                TR=cursor.fetchall()
                                msg=' ----- ESTADO RELES -----'+ '\n'
                                msg=msg+'_id_|_S_|Mod|Gr| Nombre'+ '\n'
                                for I in range(nreles):
                                    msg=msg+str(TR[I][0])+'|_'+ str(TR[I][3])+'_|'+TR[I][2].ljust(3)+'|'+ TR[I][4]
                                    msg=msg+ ' | '+TR[I][1] +'\n'
                                    #msg=msg+str(TR[I])+ '\n'
                                    
                                msg=msg + '----------------------------------------------------------'+ '\n'
                                msg=msg + '  EJEMPLOS COMANDOS RELES '+ '\n'
                                msg=msg + '----------------------------------------------------------'+ '\n'
                                msg=msg + ' #R201ON  activa rele 201'+ '\n'
                                msg=msg + ' #R201OFF  apaga rele 201'+ '\n'
                                msg=msg + ' #R201PRG  rele 201 programado'+ '\n'
                                msg=msg + ' #R201N=XX cambia nombre a XX'+ '\n'
                                msg=msg + ' #R201C=XX crea rele 201 N=XX-OFF'+ '\n'
                                msg=msg + ' #R201B borra rele 201'+ '\n'
                                            
                                msg=msg + ' #R  Muestra este mensaje'
                                
                                bot.send_message( cid, msg)

                            except:
                                msg= 'Error al acceder a la tabla reles'
                                bot.send_message( cid, msg) 
                        else:
                            msg='No interpreto correctamente la orden recibida'
                            bot.send_message( cid, msg)
                        cursor.close()
                        db.close()

                    #------------------ ORDEN INFORMACION -----------------------
                    elif tipo_orden=='I':
                        try:
                            
                            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                            cursor = db.cursor()

                            sql_reles='SELECT * FROM reles'
                            nreles=cursor.execute(sql_reles)
                            nreles=int(nreles)  # = numero de reles
                            TR=cursor.fetchall()

                            sql_datos=('SELECT Tiempo,Ibat,Vbat,SOC,Vflot,kWhp_bat,kWhn_bat,Iplaca,kWh_placa,Temp'
                                      ' FROM datos ORDER BY Tiempo DESC LIMIT 1')
                            #print sql_datos

                            ndatos=cursor.execute(sql_datos)
                            TD=cursor.fetchone()
                            cursor.close()
                            db.close()

                            fecha=TD[0]
                            ibat=TD[1]
                            vbat=TD[2]
                            soc=TD[3]
                            vflot=TD[4]
                            kWhp_bat=TD[5]
                            kWhn_bat=TD[6]
                            iplaca=TD[7]
                            kWh_placa=TD[8]
                            temp=TD[9]

                            L1='SOC='+str(round(soc,1))+'% -- Vbat='
                            L1=L1+str(round(vbat,1))+'v -- Flot='
                            L1=L1+str(int(round(vflot,0)))

                            L2='Iplaca='+str(round(iplaca,1))+'A -- Ibat='
                            L2=L2+str(round(ibat,1))+'A -- T='
                            L2=L2+str(round(temp,1))+'ºC'

                            L3='Kwh_placa='+str(round(kWh_placa/1000,1))+' -- kWh_bat='
                            L3=L3+str(round((kWhp_bat-kWhn_bat)/1000,1))

                            L4='RELES('
                            
                            for I in range(nreles): # Reles wifi
                                Puerto=(TR[I][0]%10)-1
                                addr=int((TR[I][0]-Puerto)/10)
                                if int(addr/10)== 2:
                                    valor=int(TR[I][3]/10)
                                    if valor==10:
                                        texto="X"
                                    else:
                                        texto=str(valor)
                                    L4=L4+texto

                            L4=L4+') ('

                            for I in range(nreles): # Reles i2C
                                Puerto=(TR[I][0]%10)-1
                                addr=int((TR[I][0]-Puerto)/10)
                                if int(addr/10)== 3:
                                    valor=int(TR[I][3]/10)
                                    if valor==10:
                                        texto="X"
                                    else:
                                        texto=str(valor)
                                    L4=L4+texto

                            L4=L4+')'

                            temp_cpu = commands.getoutput('sudo /opt/vc/bin/vcgencmd measure_temp')
                            temp_cpu=temp_cpu[0:len(temp_cpu)-2]
                            L5='Temp='+str(round(temp,1))+'ºC -- CPU='+temp_cpu[5:] +'ºC'   
                            L6=str(fecha)
    
                            msg=L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5+'\n'+L6
                            bot.send_message(cid, msg)

                        except:
                            msg= 'No se puede leer la tabla datos con la orden recibida'
                            bot.send_message( cid, msg)

                    #------------------ ORDEN PARAMETROS -----------------------
                    elif tipo_orden=='P':
                        try:
                            objeto_orden= tg_orden[1]
                        except:
                            objeto_orden=''
                        try:    
                            orden= tg_orden[3:].upper()
                        except:
                            orden=''
                                                                       
                        if objeto_orden=='':
                            L1='Tabla de parametros de la BD'
                            L2='P1..Grabar datos---S/N..ejm #P1=S'
                            L3='P2..Grabar reles---S/N..ejm #P2=S'
                            L4='P3..T_muestras en sg..ejm #P3=5'
                            L5='P4..N_muestras para grabar..ejm #P4=1'
                            L6='P5..Actualizar SOC..ejm #P5=95.7'
                            msg=L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5+'\n'+L6
                            bot.send_message( cid, msg)
                            
                        # -------- Sub_Orden P5 SOC ---------
                        elif objeto_orden=='5' and orden_autorizada==1:
                            try:
                                if float(orden)>100 or float(orden)<0:
                                    raise
                                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                                cursor = db.cursor()

                                sql = "UPDATE parametros SET nuevo_soc='"+orden+ "'"
                                cursor.execute(sql)
                                db.commit()
                                msg='SOC puesto a '+ orden
                                bot.send_message( cid, msg)

                            except:
                                msg='No se puede actualizar el SOC con la orden recibida   '+sql
                                bot.send_message( cid, msg)

                    #------------------ ORDEN AYUDA -----------------------
                    elif (tipo_orden=='H') or (tipo_orden=='?'):
                        L1='--- ORDENES ACEPTADAS ---'
                        L2=''#reiniciar..reinicia la RPi'
                        L3=''#teamviewer..reinicia teamviewer'
                        L4='#h o #?..Muestra esta ayuda'
                        L5='#i..Informacion resumida FV'
                        L6='#p..Ayuda para comandos parametros'
                        L7='#r..Ayuda para comandos reles'
                        
                        msg=L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5+'\n'+L6+'\n'+L7
                        bot.send_message( cid, msg)

                    #------------------ ORDEN INCORRECTA -------------------
                    else:
                        msg='Orden incorrecta .. #'
                        bot.send_message( cid, msg)


    except:
        print 'Fallo'
        
bot.set_update_listener(listener) # decimos al bot que como escuchadora la función 'listener'.

#############################################
#Funciones

# -------- Funcion Help ------------
@bot.message_handler(commands=['h','?','start']) 
def command_ayuda(m): 
    global markup

    cid = m.chat.id
   
##Botones para seleccion ordenes 
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)
    #itembtn1 = types.KeyboardButton('Reiniciar RPi')
    itembtn1 = types.KeyboardButton('/i Informacion FV\n')
    itembtn2 = types.KeyboardButton('')
    
    itembtn3 = types.KeyboardButton('/teamviewer_restart')
    itembtn4 = types.KeyboardButton('/teamviewer_stop')
    
    itembtn5 = types.KeyboardButton('/p Actualizar parametros BD')
    itembtn6 = types.KeyboardButton('/r Actualizar Reles')

    

    #itembtn6 = types.KeyboardButton('/s Salir')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
     
    msg=bot.send_message(cid, "Elige COMANDO:", reply_markup=markup)
    
#    hideBoard=types.ReplyKeyboardHide()
    
    
#------------- TEAMVIEWER ---------------------------
@bot.message_handler(commands=['teamviewer_restart'])
def command_teamviewer_r(m):
    cid = m.chat.id
    if cid in Aut:
        os.system('sudo teamviewer --daemon restart')
        bot.send_message(cid, "Teamviewer reiniciado")

@bot.message_handler(commands=['teamviewer_stop'])
def command_teamviewer_s(m):
    cid = m.chat.id 
    if cid in Aut:
        os.system('sudo teamviewer --daemon stop')
        bot.send_message(cid, "Teamviewer parado")

#------------- INFORMACION ---------------------------
@bot.message_handler(commands=['i'])
def command_i(m):
    cid = m.chat.id

    bot.send_chat_action(cid,'typing')

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql_reles='SELECT * FROM reles'
    nreles=cursor.execute(sql_reles)
    nreles=int(nreles)  # = numero de reles
    TR=cursor.fetchall()

    sql_datos=('SELECT Tiempo,Ibat,Vbat,SOC,Vflot,kWhp_bat,kWhn_bat,Iplaca,kWh_placa,Temp'
              ' FROM datos ORDER BY Tiempo DESC LIMIT 1')
    #print sql_datos

    ndatos=cursor.execute(sql_datos)
    TD=cursor.fetchone()
    cursor.close()
    db.close()

    fecha=TD[0]
    ibat=TD[1]
    vbat=TD[2]
    soc=TD[3]
    vflot=TD[4]
    kWhp_bat=TD[5]
    kWhn_bat=TD[6]
    iplaca=TD[7]
    kWh_placa=TD[8]
    temp=TD[9]

    L1='SOC='+str(round(soc,1))+'% -- Vbat='
    L1=L1+str(round(vbat,1))+'v -- Flot='
    L1=L1+str(int(round(vflot,0)))

    L2='Iplaca='+str(round(iplaca,1))+'A -- Ibat='
    L2=L2+str(round(ibat,1))+'A'
    

    L3='Kwh_placa='+str(round(kWh_placa/1000,1))+' -- kWh_bat='
    L3=L3+str(round((kWhp_bat-kWhn_bat)/1000,1))

    L4='RELES('

    for I in range(nreles): # Reles wifi
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 2:
            valor=int(TR[I][3]/10)
            if valor==10:
                texto="X"
            else:
                texto=str(valor)
            L4=L4+texto

    L4=L4+') ('

    for I in range(nreles): # Reles i2C
        Puerto=(TR[I][0]%10)-1
        addr=int((TR[I][0]-Puerto)/10)
        if int(addr/10)== 3:
            valor=int(TR[I][3]/10)
            if valor==10:
                texto="X"
            else:
                texto=str(valor)
            L4=L4+texto

    L4=L4+')'

    temp_cpu = commands.getoutput('sudo /opt/vc/bin/vcgencmd measure_temp')
    
    temp_cpu=temp_cpu[0:len(temp_cpu)-2]
    L5='Temp='+str(round(temp,1))+'ºC -- CPU='+temp_cpu[5:] +'ºC'   
    L6=str(fecha)
    
    tg_msg=L1+'\n'+L2+'\n'+L3+'\n'+L4+'\n'+L5+'\n'+L6
    #print tg_msg
    bot.send_message(cid, tg_msg)

    
# -------- Funcion Tabla Parametros BD ------------
@bot.message_handler(commands=['p'])
def command_p(m):
    global markup

    cid = m.chat.id
    
    bot.send_chat_action(cid,'typing')

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql_reles='SELECT * FROM parametros'
    nparametros=cursor.execute(sql_reles)
    TP=cursor.fetchone()
    cursor.close()
    db.close()
    
    msg=('PARAMETROS\nGrabar Datos= '+TP[0]+'\n'+'Grabar Reles= '+TP[1]+'\n'+
         'Tiempo Muestra= '+str(TP[2])+'\n'+ 'Num Muestras entre registros BD= '+str(TP[3])
         +'\n'+'SOC= '+str(TP[4])+'%')
    bot.send_message(cid, msg)
    

##Botones para seleccion campo de la tabla parametros 
    markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)

    #markup = types.ForceReply(force_replay)
    
    itembtn1 = types.KeyboardButton('/GD Grabar datos FV en BD')
    itembtn2 = types.KeyboardButton('/GR Grabar reles en BD')
    itembtn3 = types.KeyboardButton('/TM T_muestra en segundos')
    itembtn4 = types.KeyboardButton('/NM N_muestras para guardar')
    itembtn5 = types.KeyboardButton('/SOC Actualizar SOC')
    itembtn6 = types.KeyboardButton('/h Volver Menu Principal')

    markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)
     
    msg=bot.send_message(cid, "Elige parametro:", reply_markup=markup)

# ---------------- GD -----------------------
@bot.message_handler(commands=['GD'])
def GD(message):
    cid=message.chat.id
       
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Grabar datos S/N = ",reply_markup=FR)
    bot.register_next_step_handler(msg,GD_upgrade)
    
def GD_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            print 'Usuario autorizado',cid
            m=message.text.upper()
            if m!='S' and m!='N':
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET grabar_datos='"+m+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro grabar_datos modificado a "+m,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)
    except:
        bot.send_message(cid, "No se puede modificar grabar_datos\n Vuelve a intentarlo")

# ---------------- GR -----------------------
@bot.message_handler(commands=['GR'])
def GR(message):
    cid=message.chat.id

    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Grabar reles S/N = ",reply_markup=FR)

    bot.register_next_step_handler(msg,GR_upgrade)

def GR_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            m=message.text.upper()
            if m!='S' and m!='N':
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET grabar_reles='"+m+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro grabar_reles modificado a "+m,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar grabar_reles\n Vuelve a intentarlo",reply_markup=markup)
    
   
# ---------------- TM -----------------------
@bot.message_handler(commands=['TM'])
def TM(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Tiempo muestra en segundos = ",reply_markup=FR)
    bot.register_next_step_handler(msg,TM_upgrade)

def TM_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET t_muestra='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro t_muestra modificado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar t_muestra\n Vuelve a intentarlo",reply_markup=markup)

# ---------------- NM -----------------------
@bot.message_handler(commands=['NM'])
def NM(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Numero de muestras = ",reply_markup=FR)
    bot.register_next_step_handler(msg,NM_upgrade)

def NM_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        if cid in Aut:
            if float(message.text)<1:
                bot.send_message(cid, "Ha de ser mayor que 0")
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET n_muestras_grab='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"Parametro n_muestras modificado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)

    except:
        bot.send_message(cid, "No se puede modificar n_muestras\n Vuelve a intentarlo",reply_markup=markup)


# ---------------- SOC -----------------------
@bot.message_handler(commands=['SOC'])
def SOC(message):
    cid=message.chat.id
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "Introduce nuevo SOC:",reply_markup=FR)
    bot.register_next_step_handler(msg,SOC_upgrade)

def SOC_upgrade(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    #bot.send_message(cid, "Nuevo SOC = "+message.text)
    try:
        if cid in Aut:
            if float(message.text)>100 or float(message.text)<0:
                raise
            db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
            cursor = db.cursor()

            sql = "UPDATE parametros SET nuevo_soc='"+message.text+ "'"
            cursor.execute(sql)
            db.commit()
            bot.send_message(cid,"SOC cambiado a "+message.text,reply_markup=markup)
            cursor.close()
            db.close()
        else:
            bot.send_message(cid,"Sin autorizacion para cambiar este dato",reply_markup=markup)
 
    except:
        bot.send_message(cid, "No se puede actualizar el nuevo SOC\n Vuelve a intentarlo",reply_markup=markup)
    
# ----------------------- RELES  ---------------------------------------
@bot.message_handler(commands=['r'])
def reles(message):
    cid=message.chat.id
    bot.send_chat_action(cid,'typing')
    try:
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        
        sql = "SELECT id_rele,nombre,modo,estado,grabacion,salto,prioridad FROM reles"
        cursor.execute(sql)
        nreles=cursor.execute(sql)
        nreles=int(nreles)  # = numero de reles
        TR=cursor.fetchall()
        cursor.close()
        db.close()
                
        msg=' ----- ESTADO RELES -----'+ '\n'
        msg=msg+'_id_|_S_|Mod|Gr|Salto|Prio| Nombre'+ '\n'
        for I in range(nreles):
            valor=int(TR[I][3]/10)
            if valor==10:
                texto="X"
            else:
                texto=str(valor)
            valor=int(TR[I][5])
            if valor==100:
                texto1="X"
            else:
                texto1=str(valor)

            
            msg=msg+str(TR[I][0])+'|_'+ texto+'_|'+TR[I][2].ljust(3)+'|'+ TR[I][4]+'_|_'+ texto1+'__|___'+ str(TR[I][6])
            msg=msg+ '_| '+TR[I][1] +'\n'
                        
        
        bot.send_message(cid, msg)
    

##Botones reles 
        markup = types.ReplyKeyboardMarkup(row_width=2,one_time_keyboard=False,resize_keyboard=True)

        #markup = types.ForceReply(force_replay)
        
        itembtn1 = types.KeyboardButton('/ON Poner Rele a ON')
        itembtn2 = types.KeyboardButton('/OFF Poner Rele a OFF')
        itembtn3 = types.KeyboardButton('/PRG Poner Rele a PRG')
        itembtn4 = types.KeyboardButton('/Crear_Rele')
        itembtn5 = types.KeyboardButton('/Borrar_Rele')
        itembtn6 = types.KeyboardButton('/h Volver Menu Principal')

        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn6)

        msg=bot.send_message(cid, "Elige parametro:", reply_markup=markup)

    except:
        msg= 'Error al acceder a la tabla reles'
        bot.send_message(cid, msg)

# ---------------- RELE ON -----------------------
@bot.message_handler(commands=['ON'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_on_upgrade)

def rele_on_upgrade(message):
    cid=message.chat.id
    print message.text
    orden='ON'
    rele_upgrade(orden,message.text,cid)
    
# ---------------- RELE OFF -----------------------
@bot.message_handler(commands=['OFF'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_off_upgrade)

def rele_off_upgrade(message):
    cid=message.chat.id
    print message.text
    orden='OFF'
    rele_upgrade(orden,message.text,cid)

# ---------------- RELE PRG -----------------------
@bot.message_handler(commands=['PRG'])
def rele_on(message):
    cid=message.chat.id
    
    FR=types.ForceReply(True)
    msg=bot.send_message(cid, "introduce Nº Rele= ",reply_markup=FR)
    
    bot.register_next_step_handler(msg,rele_prg_upgrade)

def rele_prg_upgrade(message):
    cid=message.chat.id
    print message.text
    orden='PRG'
    rele_upgrade(orden,message.text,cid)

# ---------------- RELE CAMBIO MODO ----------------------- 
def rele_upgrade(orden,nrele,cid):    
    try:
        sql = "UPDATE reles SET modo='"+orden+"' WHERE id_rele=" + nrele
        
        db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
        cursor = db.cursor()
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()

        msg='Rele '+ nrele + ' puesto a '+ orden
               
        bot.send_message(cid, msg, reply_markup=markup)
    except:
        msg='No se puede actualizar la tabla reles con la orden recibida   '
        bot.send_message(cid, msg, reply_markup=markup)


        bot.send_message(cid, saludo)
            
           
#############################################
#Polling
def telegram_polling():
    try:
        bot.polling(none_stop=True)#,interval=10, timeout=60) #constantly get messages from Telegram
    except:
        print time.strftime("%c"), 'Error polling C'
        bot.stop_polling()
        time.sleep(10)
        telegram_polling()


telegram_polling()
    
