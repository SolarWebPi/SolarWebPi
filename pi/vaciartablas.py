#!/usr/bin/python

import MySQLdb
import time

######
servidor = 'localhost' 
usuario = 'rpi' 
clave = 'fv' 
basedatos = 'control_solar'

tiempo = time.strftime("%Y-%m-%d %H:%M:%S")


try:
    error='conexion BD'
    db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
    cursor = db.cursor()

    error='borrando tabla datos'
    sql="DELETE FROM datos WHERE Tiempo < SUBDATE(NOW(),INTERVAL 366 DAY)"
    cursor.execute(sql)

    error='borrando tabla reles_segundos_on'
    sql="DELETE FROM reles_segundos_on WHERE fecha < SUBDATE(NOW(),INTERVAL 366 DAY)"
    cursor.execute(sql)

    error='borrando tabla reles_grab'
    sql="DELETE FROM reles_grab WHERE Tiempo < SUBDATE(NOW(),INTERVAL 366 DAY)"
    cursor.execute(sql)

    error='borrando tabla log'
    sql="DELETE FROM log WHERE Tiempo < SUBDATE(NOW(),INTERVAL 30 DAY)"
    cursor.execute(sql)

    db.commit()

    print 'vaciartablas.py ejecutado correctamente'

except Exception as e:
    log='Error en vaciatablas.py'+error
    try: 
        cursor.execute("""INSERT INTO log (fecha,log) VALUES(%s,%s)""",(tiempo,log))
        print tiempo,' ', log
        db.commit()
    except:
        db.rollback()
        print "Error en vaciatablas.py, no acceso a la base de datos"
