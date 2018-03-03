#!/usr/bin/python
# -*- coding: utf-8 -*-

import time 

temp1 = 0
temp2 = 0

###### Actualizar 28-xxxxx segun DS18B20 instalados
sensor1="28-xxxxxxxxx"  # sensor PCB
sensor2="28-yyyyyyyyy"  # sensor Externo



# --------------------- DEFINICION DE FUNCIONES --------------

def leer_temp(sensor,x) :  # leer temperatura
    try:
        
        tempfile= open("/sys/bus/w1/devices/" + sensor + "/w1_slave")
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


# -------------------------------- BUCLE PRINCIPAL --------------------------------------

print "empìezo"

while True:
    temp1= leer_temp(sensor1,temp1)
    temp2= leer_temp(sensor2,temp2)
    
    print time.strftime("%Y-%m-%d %H:%M:%S"),temp1, temp2
    #time.sleep(1)
