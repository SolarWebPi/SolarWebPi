#!/usr/bin/python
# -*- coding: utf-8 -*-

import time 
import MySQLdb 
import RPi.GPIO as GPIO
#import sys
import random # para simulacion usando random.choice
import urllib2  # libreria  para reles wifi
from smbus import SMBus
#import os  # para envio de msg Telegram-cli .--OBSOLETO
#import subprocess # Uso E-mail
import Adafruit_ADS1x15 # Import the ADS1x15 module.

import telebot # Librería de la API del bot.
from telebot import types # Tipos para la API del bot.
import token

usar_telegram = 1  # poner a 0 para no usar / poner a 1 para usar

if usar_telegram == 1:
    ###### Poner Nuestro token del bot creado
    TOKEN = '' 
    bot = telebot.TeleBot(TOKEN) # Creamos el objeto de nuestro bot.
    bot.skip_pending = True # Skip the pending messages

    ###### ID de Usuario TELEGRAM
    Aut = [] 
    cid = Aut[0]

###### Direccion ip de la LAN para reles wifi
ip_lan = "http://192.168.0."

#------------------------------------------------
###### ------------------------------------------
simular = 0  # Simulacion datos FV si =1
simular_reles = 0 # Simular reles fisicos
mux = 0      # Poner a 1 si existe un multiplexor de 16 canales
sensortemperatura = 1   # Poner a 0 si no se ha instalado el DS18B20
# -----------------------------------------------
# -----------------------------------------------

bus = SMBus(1) # Bus I2C
GPIO.setmode(GPIO.BOARD)

###### Parametros Base de Datos
servidor = 'localhost' 
usuario = 'rpi' 
clave = 'fv' 
basedatos = 'control_solar'

# ------------------------------------------
######      PARAMETROS INSTALACION 
# ------------------------------------------
SHUNT1 = 500.0/50 #Shunt Ibat
SHUNT2 = 500.0/75 #Shunt Iplaca
RES0 = 14.47*25.1/10.66 # Divisor tension Vbat  
RES1 = (0.7+1)/1 # Divisor tension salida Aux FM80 (Vflot/Diver)
RES2 = 97.9/1.41 # Divisor tension Vplaca

vflotacion = 54.5 #valor por defecto de flotacion a 25ºC
vsis = 4 # Voltaje sistema - 1=12V  2=24V   4=48V

TIPO_DIVER = 'vplaca' # valores posibles 'vplaca' , 'vaux' ..... poner 'NO' para desactivar diver

AH = 1129.1 # Capacidad C20
CP = 1.096  # Indice Peukert
EC = 0.9    # Eficiencia Carga 

###### Alta ADS1115 ADC (16-bit).
  #adc con pin addr a GND
  #A0=iplaca // A1=Iplaca // // A2=Ibat // A3=ibat
adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=1)

  #adc con pin addr a 3V3
  #A0=Vbat // A1=Vflot o Diver // A2= Vplaca// A3= Mux
adc1 = Adafruit_ADS1x15.ADS1115(address=0x49, busnum=1) 

#---------------------------------------------------------------
DatosFV = {} #Creamos diccionario para los datos FV
OP = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,'id_rele2':7,'operacion':8,'parametro':9,'condicion':10,'valor':11}
OPH = {'id_rele':0,'nombre':1,'modo':2,'estado':3,'grabacion':4,'salto':5,'prioridad':6,'id_rele2':7,'parametro_h':8,'valor_h_ON':9,'valor_h_OFF':10}
NDIA = {'D':0,'L':1,'M':2,'X':3,'J':4,'V':5,'S':6}

#Inicializando las variables del programa
Grabar = 1

T_ejecucion_max = 0.0
hora3 = 5.0  
hora_m = time.time() #para calcular tiempo entre muestras real
t_muestra = 5 # Inicializo Tiempo entre muestra real...idealmente TP[0][2]

ibat = 0.0      	# Intensidad Bateria
vbat = 12.0 * vsis     	# Voltaje Bateria
iplaca = 0.0    	# Intensidad Placas (salida regulador)
vplaca = 0.0    	# Volataje Placas (valor antes del regulador)
vaux = 0.0      	# Voltaje salida auxiliar Regulador
temp = 0.0      	# temperatura baterias
vflot = 0.0     	# Voltaje asociado a estado de flotacion

nwifi_lectura = 0 #utilizado en secuenciacion lectura reles wifi

#---Variables calculo SOC --------------------------------
Ip = 0.0
Ip1 = 0.0
Ip2 = 0.0
float(CP)
float(Ip)
float(Ip1)
float(Ip2)
DS=0.0


Puerto = 0
estado = 0

hora_actual = time.strftime("%H")
tiempo = time.strftime("%Y-%m-%d %H:%M:%S")

kWh_bat = 0.0
kWhp_bat = 0.0 
kWhn_bat = 0.0

kWh_placa = 0.0
kWh_consumo = 0.0

GPIO.setup(7, GPIO.IN)  # si se usa para señal vflot

# --------------------- DEFINICION DE FUNCIONES --------------

def act_rele(adr,port,out) : # Activar Reles
    if simular_reles == 0:
        if int(adr/10) == 2: #Rele WIFI
            try:
                ip = ip_lan + str(adr) + "/R" + str(port) + "=" + str(out)
                urllib2.urlopen(ip)
            except:
                if simular != 1:
                    logBD('Error rele wifi'+str(adr)+str(port)+'='+ str(out))   

        if int(adr/10) == 3: # Rele I2C
            try:
                estado = bus.read_byte(adr)  #devuelve el valor en decimal
                if out == 100 :
                    i2c_out = estado & (2**(port-1) ^ (255))
                else :
                    i2c_out = estado | 2**(port-1)
                bus.write_byte(adr,i2c_out)
            except:
                if simular != 1:
                    logBD('Error bus I2C '+str(adr)+str(port)+ '='+ str(out))
    return

def logBD(texto) : # Incluir en tabla de Log
    try: 
        cursor.execute("""INSERT INTO log (Tiempo,log) VALUES(%s,%s)""",(tiempo,texto))
        #print tiempo,' ', texto
        db.commit()
    except:
        db.rollback()

    return

def leer_ibat(x) :  # leer ibat
    try:
        y = - round(adc.read_adc_difference(3, gain=16, data_rate=8) * 0.0078125 * SHUNT1, 2)  # A2-A3
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor ibat')
    if y < -200 or y > 200:
        logBD('lectura incoherente ibat='+str(y))
        y = x
    return y

def leer_iplaca(x) :  # leer iplaca
    try:
        y = - round(adc.read_adc_difference(0, gain=16, data_rate=8) * 0.0078125 * SHUNT2, 2)  # A0-A1
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor iplaca')
    if y > 150 or y < -1:
        logBD('lectura incoherente iplaca='+str(y))
        y = x
    if y < 0.15:
        y = 0
    return y

def leer_vbat(x) :  # leer vbat
    try:
        y = round(adc1.read_adc(0, gain=1) * 0.000125 * RES0, 2)  # A0   4,096V/32767=0.000125 
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor vbat')
    if y < 40 or y > 64:
        logBD('lectura incoherente vbat='+str(y))
        y = x
    return y

def leer_vaux(x) :  # leer vaux
    try:
        y = round(adc1.read_adc(1, gain=1) * 0.000125 * RES1, 2)  # A1   4,096V/32767=0.000125
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor vaux')
    if y < -1 or y > 14:
        logBD('lectura incoherente vaux='+str(y))
        y = x
    return y

def leer_vplaca(x) :  # leer vplaca
    try:
        y = round(adc1.read_adc(2, gain=1) * 0.000125 * RES2, 2)  # A2   4,096V/32767=0.000125
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor vplaca')
    if y < 0 or y > 140:
        logBD('lectura incoherente vplaca='+str(y))
        y = x
    return y

def leer_diver(x) :  # leer estado diversion
    if x == "vaux":
        vaux = leer_vaux(0)
        if vaux > 1:
            diver = 1
        else:
            diver = 0
    elif x == "vplaca":
        vplaca = leer_vplaca(0) # si error lectura devuelve 0
        ibat = leer_ibat(-10)    # si error lectura devuelve -10
        if vplaca > TP[0][5] and ibat > -10: 
            diver = 1
        else:
            diver = 0
    else:
        diver = 0
    return diver

def leer_temp(x) :  # leer temperatura
    try:
        ###### Actualizar 28-xxxxx segun DS18B20 instalado
        tempfile= open("/sys/bus/w1/devices/28-0516a11858ff/w1_slave")
        thetext=tempfile.read()
        tempfile.close()
        tempdata = thetext.split("\n")[1].split(" ")[9]
        y = round(float(tempdata[2:]) / 1000,2)
    except:
        y = x
        logBD('-ERROR MEDIDA FV-sensor temp')
    if y < -10 or y > 50:
        logBD('lectura incoherente temp='+str(y))
        y = x
    return y

## RECUPERAR DE LA BD ALGUNOS DATOS ##

try:

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql='SELECT DS, DATE(Tiempo) FROM datos ORDER BY id DESC limit 1'
    cursor.execute(sql)
    var=cursor.fetchone()
    DS=float(var[0])
    HOY=str(var[1])

    if HOY == time.strftime("%Y-%m-%d"):
        sql='SELECT kWhp_bat FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWhp_bat=float(var[0])

        sql='SELECT kWhn_bat FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWhn_bat=float(var[0])

        sql='SELECT kWh_placa FROM datos ORDER BY id DESC limit 1'
        cursor.execute(sql)
        var=cursor.fetchone()
        kWh_placa=float(var[0])

    else:
         kWhp_bat=0.0
         kWhn_bat=0.0
         kWh_placa=0.0
         print "Nuevo dia", time.strftime("%Y-%m-%d")

except Exception as e:
    print "Error, la base de datos no existe"

## Definir matrices Rele_Out y Rele_Out_Ant y apagar todos los reles
    
Rele_Out = [[0] * 8 for i in range(40)] # Situacion actual
Rele_Out_Ant = [[0] * 8 for i in range(40)] # Situacion anterior
TR_D = [[0] * 3 for i in range(40)]  #Para excedentes Id_rele,Control,Timestamp

##  ------ inicializamos reles apagandolos  ------------------------
sql_reles = 'SELECT * FROM reles'
nreles = cursor.execute(sql_reles)
nreles = int(nreles)  # = numero de reles
TR = cursor.fetchall()

for I in range(nreles): #apagado fisico
    Puerto = (TR[I][0] % 10) - 1
    addr = int((TR[I][0] - Puerto)/10)
    Rele_Out[addr][Puerto] = 0
    Rele_Out_Ant[addr][Puerto] = 0
    act_rele(addr,Puerto+1,0)

if nreles > 0 : # apagado en BD
    sql = "UPDATE reles SET estado = 0"
    cursor.execute(sql)

## ------------------------------------------------------------
### Calcular voltaje sistema (12,24 o 48)
#print ('ERROR LECTURA VOLTAJE BATERIA.....SISTEMA POR DEFECTO a 24V')

vbat = leer_vbat(vsis * 12) # pongo por defecto la config. del sistema
log=''
if vbat > 11 and vbat < 15.5 :
    vsis = 1
elif vbat > 22 and vbat < 31 :
    vsis = 2
elif vbat > 44 and vbat < 62 :
    vsis = 4
else :
    log='Error: Imposible reconocer el voltaje del sistema'
    #sys.exit()	# Activar modulo sys si se descomenta

vflotacion = 13.7 * vsis

print('Pulsa Ctrl-C para salir...')

log = ' Arrancando programa fv.py \nBateria = ' + str(vbat) + 'v' + log
logBD(log) # incluyo mensaje en el log
if usar_telegram == 1:
    try:
        bot.send_message( cid, log)
    except:
        logBD("Error en Msg Telegram") #incluyo mensaje en el log

# -------------------------------- BUCLE PRINCIPAL --------------------------------------

while True:

    cursor.close()
    db.close()
    
    hora1=time.time()

    ### ------------ Cargar tablas parametros, reles , reles_c, reles_h ---------------------

    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    sql_reles='SELECT * FROM parametros'
    nparametros=cursor.execute(sql_reles)
    nparametros=int(nparametros)  # = numero de filas de parametros.---- debe ser 1
    TP=cursor.fetchall()

    sql_reles='SELECT * FROM reles'
    nreles=cursor.execute(sql_reles)
    nreles=int(nreles)  # = numero de reles
    TR=cursor.fetchall()

    sql_reles='SELECT * FROM reles INNER JOIN reles_c ON reles.id_rele = reles_c.id_rele'
    ncon=cursor.execute(sql_reles)
    ncon=int(ncon)  # = numero de condiciones
    R=cursor.fetchall()

    sql_reloj='SELECT * FROM reles INNER JOIN reles_h ON reles.id_rele = reles_h.id_rele'
    hcon=cursor.execute(sql_reloj)
    hcon=int(hcon)  # = numero de condiciones horarias
    H=cursor.fetchall()

    # ------------------------ LECTURA FECHA / HORA ----------------------

    tiempo = time.strftime("%Y-%m-%d %H:%M:%S")
    diasemana = time.strftime("%w")	
    hora = time.strftime("%H:%M:%S") #No necesario .zfill() ya pone los ceros a la izquierda
    
# ------------------------ LECTURA PARAMETROS FV----------------------

    t_muestra_ant=t_muestra
    t_muestra=time.time()-hora_m
    hora_m=time.time()

    if simular==1:
        ibat=random.choice([0,12,22,33,46,56,65,78,101,
                            -10,-20,-30,-40,-50,-60,-70,-80,-90])
        iplaca=random.choice([0,10,20,30,45,57,67,77,88,99,102,110])
        vbat=random.choice([22.5,23,24,24.4,25,26,27,27.5,28,29])
        vplaca=random.choice([60,59.4,61,59.9,52,60.1,61.6,58.7,62,57.3])
        diver=random.choice([1,1,1,0,1,0,1,1])  
        temp=random.choice([10,12,14,16,18,20,22,24,26,28,30,32,34])
    else:
        ibat = leer_ibat(ibat)
        vbat = leer_vbat(vbat)
        iplaca = leer_iplaca(iplaca)
        vplaca = leer_vplaca(vplaca)
        vaux = leer_vaux(vaux)
        TIPO_DIVER = TP[0][6]
        diver = leer_diver(TIPO_DIVER)
        vflot = 0
        
        # pongo 0, 1 ,2 o 3 en vflot dependiendo de estado vplaca/salida aux
        if vaux > 1: # por ahora utilizare campo vflot para ver diver en la BD 
            vflot = 1
        if diver == 1:
            vflot = vflot + 2

        if sensortemperatura == 1:
            temp = leer_temp(temp)

    ######## VALORES DEL MULTIPLEXOR ----PCF en Direccion 39---#########
    if mux == 1: 
        ###### Asegurar que el PCF del mux esta en la direccion 39 ==> A0=A1=A2=1
        for K in range(16):
            act_rele(39,1,int(not(K%2)))       #Pin S0 74HC4067
            act_rele(39,2,int(not((K//2)%2)))  #Pin S1 74HC4067
            act_rele(39,3,int(not((K//4)%2)))  #Pin S2 74HC4067
            act_rele(39,4,int(not((K//8)%2)))  #Pin S3 74HC4067

            #print 'direcc=',int(not(K%2)),
            #print int(not((K//2)%2)),
            #print int(not((K//4)%2)),
            #print int(not((K//8)%2)),
            try:

                ###### pin del ADS1115 para mux
                mux1 = adc.read_adc(1, gain=1)
                #print ' Mux1=',mux1

            #### FALTA INCORPORAR A BD ######

            except:
                logBD('-ERROR MEDIDA MUX1-'+ str(K))

    ##################################################################

    ### CALCULO KWH_BAT y KWH_PLACA
    hora_anterior=hora_actual
    hora_actual=time.strftime("%H")

    if (hora_anterior== "23" and hora_actual=="00"): #cambio de dia
        kWh_bat = 0.0
        kWhp_bat = 0.0
        kWhn_bat = 0.0
        kWh_placa = 0.0
    else:
        if ibat < 0:
            kWhn_bat = round(kWhn_bat - (ibat * vbat * t_muestra/3600),2)
        else:
            kWhp_bat = round(kWhp_bat + (ibat * vbat * t_muestra/3600),2)

        kWh_placa = round(kWh_placa + (iplaca * vbat * t_muestra/3600),2)
        ###para kWh dividir por 1000

    ### CALCULO SOC% A C20
    if ibat < 0 :
        Ip1 = -ibat 
        Ip1 = Ip1**CP 
        Ip1 = AH*Ip1

        Ip2 = AH / 20
        Ip2 = (Ip2**CP)*20
        Ip= -Ip1/Ip2
    else :
        Ip = ibat * EC

    if (ibat>0 and ibat<1 and abs(vbat-vflotacion)<0.2) :
        DS = DS + (AH-DS)/50
    else :
        DS = DS + (Ip * t_muestra/3600)
    
    if DS > AH :
        DS = AH
    if DS < 0 :
        DS = 0

    if TP[0][4] != 0: # Actualizo SOC si en la BD es distinto de 0
        DS = AH*TP[0][4]/100
        cursor.execute("UPDATE parametros SET nuevo_soc=0 WHERE id_parametros=1")
        db.commit()                
    soc = round(DS/AH*100,2)

    ### FIN CALCULO SOC%

    #------------- Asignamos valores al diccionario para parametros condiciones ...

    DatosFV['Vbat'] = vbat
    DatosFV['Ibat'] = ibat
    DatosFV['SOC'] = soc
    DatosFV['Iplaca'] = iplaca
    DatosFV['Vflot'] = vflot
    DatosFV['Temp'] = temp
    DatosFV['Vplaca'] = vplaca
    DatosFV['Diver'] = diver

    #------------------------ ALGORITMO CONDICIONES RELES -----------------------------

    #### Cargamos los valores actuales de los reles  en Rele_Out_Ant####
    nwifi = 0
    for I in range(nreles): # Calculo Numero reles wifi y Rele_Out_Ant por defecto
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)
        Rele_Out_Ant[addr][Puerto] = Rele_Out[addr][Puerto]
        if int(addr/10) == 2:
            nwifi = nwifi + 1

    nwifi_lectura = nwifi_lectura + 1 # lectura de un unico rele wifi por ciclo
    if nwifi_lectura > nwifi:       # para evitar colapsar al NodeMCU
        nwifi_lectura = 0

    nwifi_lectura1 = 0

    if simular_reles == 0: #Captura de los valores reales que estan en los reles
        for I in range(nreles):
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            #print 'Puerto=',Puerto, addr
                
            if int(addr/10) == 3: # Reles I2C
                try:
                    estado = bus.read_byte(addr)
                    estado = bin(estado ^ 255)[2:10].zfill(8)
                    Rele_Out_Ant[addr][Puerto] = int(estado[7-Puerto]) * 100
                except:
                    logBD('Error lectura I2C en direccion/ '+str(addr)+str(Puerto))

            if int(addr/10) == 2: # Reles Wifi lectura un solo rele por ciclo
                nwifi_lectura1 = nwifi_lectura1 + 1
                if nwifi_lectura == nwifi_lectura1:
                    try:
                        ip = ip_lan + str(addr) + "/R"+str(Puerto+1) + "=?"
                        sock = urllib2.urlopen(ip,timeout=10)
                        lines = sock.readlines()
                        salida_node = lines[1]
                        if salida_node[0:7] == "PWM_R" + str(Puerto+1) + "=": 
                            Rele_Out_Ant[addr][Puerto] = int(salida_node[7:10])
                        if salida_node[0:5] == "ERROR":
                            Rele_Out_Ant[addr][Puerto] = 0 
                            logBD(' ERROR Rele ' + str(Puerto+1) + ' en NodeMCU de direccion '+str(addr))
                    except:
                        logBD('Rele ' + str(Puerto + 1) + ' en NodeMCU de direccion '+str(addr)+' NO ENCONTRADO')


    #### Apagamos virtualmente y encendemos SI condiciones FV o HORARIAS por defecto####
    
    for I in range(ncon): # enciendo reles con condiciones FV
        Puerto = (R[I][0] % 10) - 1
        addr = int((R[I][0]-Puerto) / 10)
        Rele_Out[addr][Puerto] = R[I][5] # pongo valor del salto

    for I in range(hcon): # enciendo reles con condiciones horario
        Puerto = (H[I][0] % 10)-1
        addr = int((H[I][0] - Puerto)/10)
        Rele_Out[addr][Puerto] = H[I][5] # pongo valor del salto

    for I in range(nreles): # reles diver se ponen a situacion anterior
        if TR[I][6] != 0:
            Puerto = (TR[I][0] % 10) - 1
            addr = int((TR[I][0] - Puerto) / 10)
            Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto]

 # -------------------- Bucle de condiciones de horario --------------------------

    Rele_Out_H = [[0] * 8 for i in range(40)] # Inicializo variable a 0

    for I in range(hcon):
        Puerto = (H[I][0] % 10) - 1
        addr = int((H[I][0] - Puerto) / 10) 

        diaok = 0 # variables de control para ver si esta dentro de horario
        horaok = 0
        
        if H[I][OPH['parametro_h']] == 'T': #Todos los dias de la semana
            diaok = 1
        elif str(NDIA[H[I][OPH['parametro_h']]]) == diasemana:
            diaok = 1

        if str(H[I][OPH['valor_h_ON']]).zfill(8) > str(H[I][OPH['valor_h_OFF']]).zfill(8): #True si periodo pasa por 0:00
            if (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= "23:59:59"): 
                horaok = 1                                                       
            if (hora >= "00:00:00" and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)): 
                horaok = 1

        elif (hora >= str(H[I][OPH['valor_h_ON']]).zfill(8) and hora <= str(H[I][OPH['valor_h_OFF']]).zfill(8)):
            horaok = 1

        if diaok == 1 and horaok == 1:
            Rele_Out_H[addr][Puerto]+= 1

    for I in range(hcon):
        Puerto = (H[I][0] % 10)-1
        addr = int((H[I][0] - Puerto) / 10) 
                
        if Rele_Out_H[addr][Puerto] == 0:
            Rele_Out[addr][Puerto] = 0 #apago rele
            Rele_Out_H[addr][Puerto] = -1 # para quitar posibilidad de ser rele diver en el ciclo

 # -------------------- Bucle de condiciones de parametros FV --------------------------

    for I in range(ncon):
        Puerto = (R[I][0] % 10) - 1   
        addr = int((R[I][0] - Puerto) / 10)

        if R[I][OP['condicion']] == '<':
            if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] > R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                Rele_Out[addr][Puerto] = 0
            if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] <= R[I][OP['valor']] :
                Rele_Out[addr][Puerto] = 0

        if R[I][OP['condicion']] == '>':
            if R[I][OP['operacion']] == 'ON' and DatosFV[R[I][OP['parametro']]] < R[I][OP['valor']] and Rele_Out_Ant[addr][Puerto] == 0 :
                Rele_Out[addr][Puerto] = 0
            if R[I][OP['operacion']] == 'OFF' and DatosFV[R[I][OP['parametro']]] >= R[I][OP['valor']] :
                Rele_Out[addr][Puerto] = 0

#-------------------- Bucle encendido/apagado reles ------------------------------------

    Flag_Rele_Encendido = 0

    for I in range(nreles):
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)

        ### forzado ON/OFF
        if TR[I][OP['modo']] == 'ON' :
            Rele_Out[addr][Puerto] = 100
        if TR[I][OP['modo']] == 'OFF' :
            Rele_Out[addr][Puerto] = 0

        ### dejar rele como esta     
        if Rele_Out[addr][Puerto] == 100 and Rele_Out_Ant[addr][Puerto] < 100 and Flag_Rele_Encendido == 1 : 
            Rele_Out[addr][Puerto] = Rele_Out_Ant[addr][Puerto]      #dejar rele en el estado anterior

        ### encender rele
        if Rele_Out[addr][Puerto] == 100 and Rele_Out_Ant[addr][Puerto] < 100 and Flag_Rele_Encendido == 0:
            Flag_Rele_Encendido = 1
            act_rele(addr,Puerto+1,100)

        ### apagar rele
        if Rele_Out[addr][Puerto] == 0 and Rele_Out_Ant[addr][Puerto] > 0 :
            act_rele(addr,Puerto+1,0) #apagar rele

    ### CONTROL DE EXCEDENTES -- DIVER

    ndiver = 1 # Numero de ciclos diver por muestra
    tdiver = str(diver) # Almacena secuencia diver
    while True:
        if simular == 1:
            diver = random.choice([1,0,1,0,1,0,1,0,1])
        else:
            diver = leer_diver(TIPO_DIVER)

        tdiver = tdiver + str(diver)

        if diver == 1 :  #hay excedentes
            # Pongo 1 en TR_D[P][1] en reles candidatos a diver
            # y busco prioridad_actual
            prioridad_actual = 100
            for P in range(nreles):
                Puerto = (TR[P][0] % 10) - 1
                addr = int((TR[P][0] - Puerto) / 10)

                TR_D[P][0] = TR[P][0]
                TR_D[P][1] = 0
                if TR[P][2] == 'PRG' and Rele_Out[addr][Puerto] < 100 and TR[P][6]!= 0 and Rele_Out_H[addr][Puerto] != -1:
                    TR_D[P][1] = 1
                    if TR[P][6] < prioridad_actual :
                        prioridad_actual = TR[P][6]
                    else:
                        TR_D[P][1] = 0

            if prioridad_actual != 100:
                # Pongo 2 en TR_D[P][1] si coincide prioridad actual
                # y busco rele con la marca temporal mas antigua
                timerele = 9999999999
                id_rele_diver = 0
                for P in range(nreles):
                    if TR[P][6] == prioridad_actual and TR_D[P][1] == 1 and TR_D[P][2] < timerele:
                        timerele = TR_D[P][2]
                        id_rele_diver = TR_D[P][0]

                for P in range(nreles):
                    if TR[P][0] == id_rele_diver:
                        Puerto = (TR[P][0] % 10) - 1
                        addr = int((TR[P][0] - Puerto) / 10)
                        Rele_Out[addr][Puerto] = Rele_Out[addr][Puerto] + TR[P][5]

                        if Rele_Out[addr][Puerto] > 100:
                            Rele_Out[addr][Puerto] = 100
                        act_rele(addr,Puerto+1,Rele_Out[addr][Puerto])
                        timerele = time.clock()
                        TR_D[P][2] = timerele

            break

        else:  # NO hay excedentes  diver==0
            prioridad_actual = 0
            for P in range(nreles):
                Puerto = (TR[P][0] % 10) - 1
                addr = int((TR[P][0] - Puerto) / 10)
                TR_D[P][0] = TR[P][0]
                if TR[P][2] == 'PRG' and Rele_Out[addr][Puerto] > 0 and TR[P][6]!= 0 :
                    TR_D[P][1] = 1
                    if TR[P][6] > prioridad_actual :
                        prioridad_actual = TR[P][6]
                else:
                    TR_D[P][1] = 0

            if prioridad_actual != 0:
                timerele = 9999999999
                id_rele_diver = 0
                for P in range(nreles):
                    if TR[P][6] == prioridad_actual and TR_D[P][1] == 1 and TR_D[P][2] < timerele:
                        timerele = TR_D[P][2]
                        id_rele_diver = TR_D[P][0]

                for P in range(nreles):
                    if TR[P][0] == id_rele_diver:
                        Puerto = (TR[P][0] % 10) - 1
                        addr = int((TR[P][0] - Puerto) / 10)
                        Rele_Out[addr][Puerto] = Rele_Out[addr][Puerto] - TR[P][5]

                        if Rele_Out[addr][Puerto] < 0:
                            Rele_Out[addr][Puerto] = 0
                        act_rele(addr,Puerto+1,Rele_Out[addr][Puerto])
                        timerele = time.clock()
                        TR_D[P][2] = timerele

        ndiver = ndiver + 1
        time.sleep(0.2)
        if time.time() - hora1 > TP[0][2] - 1: #Tmuestra menos 1 segundo
            break

    #if int(hora_actual) < 21 and int(hora_actual) > 8:
    #    print hora, ndiver, tdiver

    # -------------------------- Escribir en la BD Tabla Reles el Estado RELES -------------------------
    for I in range(nreles):
        Puerto = (TR[I][0] % 10) - 1
        addr = int((TR[I][0] - Puerto) / 10)
        id = TR[I][0]
        estado = Rele_Out[addr][Puerto]
        sql = "UPDATE reles SET estado =" +str(estado)+ " WHERE id_rele = " + str(id)
        sql_reles = 'SELECT id_rele,segundos_on,nconmutaciones FROM reles_segundos_on WHERE fecha='+'"'+time.strftime("%Y-%m-%d")+'" and id_rele =' + str(id)

        try:
            nreles_on = cursor.execute(sql_reles)
            nreles_on = int(nreles_on)
            if estado > 0 :
                segundos_on = TP[0][2]
                nconmutaciones = 1

                if nreles_on >= 1:
                    TS = cursor.fetchall()
                    
                    segundos_on = TS[0][1] + round((t_muestra*estado/100),2)  # calculo funcionamiento real reles PWM
                    if TR[I][3] == 0:
                        nconmutaciones = TS[0][2] + 1
                    else:
                        nconmutaciones = TS[0][2]

                    #UPDATE
                    sql_reles = ("UPDATE reles_segundos_on SET segundos_on =" +str(segundos_on)+
                                 ",nconmutaciones =" + str(nconmutaciones)+ " WHERE id_rele = " +
                                 str(id) + ' and fecha = "' + time.strftime("%Y-%m-%d") +'"')
                    cursor.execute(sql_reles)
                else :
                    #INSERT
                    cursor.execute("""INSERT INTO reles_segundos_on
                                    (id_rele,fecha,segundos_on,nconmutaciones)
                                    VALUES (%s,%s,%s,%s)""",
                                    (id,time.strftime("%Y-%m-%d"),segundos_on,1))

            if Rele_Out[addr][Puerto] != TR[I][3]:
                cursor.execute(sql)

##            db.commit()

        except:
            db.rollback()
            logBD('Error grabacion Reles_segundos_on')
            
        if TP[0][1] == "S" and Grabar == 1 and TR[I][4] == "S" and Rele_Out[addr][Puerto] != TR[I][3]:
            try:
                cursor.execute("""INSERT INTO reles_grab (Tiempo,id_rele,valor_rele)
                               VALUES(%s,%s,%s)""",(tiempo,TR[I][0],estado))
    ##            db.commit()
            except:
                db.rollback()
                logBD('tabla reles_grab NO grabados por fallo')

#------------------------Escribir en la tabla valores FV  ---------------------------

    if TP[0][0] == "S" and Grabar == 1:
        try:
            cursor.execute("""INSERT INTO datos (Tiempo,Ibat,Vbat,SOC,DS,Vflot,kWhp_bat,kWhn_bat,Iplaca,Vplaca,kWh_placa,Temp) 
               VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
               (tiempo,ibat,vbat,soc,DS,vflot,kWhp_bat,kWhn_bat,iplaca,vplaca,kWh_placa,temp))
            db.commit()

        except:
            db.rollback()
            logBD('Registro DATOS no grabado')
    else :
        db.commit()
        #print "registro DATOS NO grabado"


    Grabar = Grabar + 1
    if Grabar >= TP[0][3] + 1:
        Grabar = 1

    if t_muestra > 5:
        logBD('Tiempo muestra elevado ='+str(round(t_muestra,1))+'sg')

    hora2 = time.time()
    ###### ajuste fino tiempo bucle=0.10
    T_ejecucion = hora2 - hora1 + 0.10
    if T_ejecucion_max < T_ejecucion:
        T_ejecucion_max = T_ejecucion


    # Repetir bucle cada X segundos
    espera = TP[0][2] - T_ejecucion
    if espera > 0:
        time.sleep(espera)

