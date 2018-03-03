#Listener
def listener(messages): #definimos función 'listener', recibe como parámetro 'messages'.
    try:
        for m in messages: # Por cada dato 'm' en el dato 'messages'
            cid = m.chat.id # Almacenaremos el ID de la conversación.

            if cid in Aut:
                orden_autorizada = 1
            else:
                orden_autorizada = 0

            tg_to=cid
            tg_to_u=str(m.chat.first_name)
            tg_from=cid


            if m.content_type == 'voice':
                #bot.send_message( cid, 'voice')
                fileID = m.voice.file_id
                #bot.send_message( cid, fileID)
                file = bot.get_file(fileID)
                #bot.send_message( cid, file.file_path)

                downloaded_file = bot.download_file(file.file_path)

                with open('/home/pi/voice.ogg', 'wb') as new_file:
                    new_file.write(downloaded_file)

                # convertir ogg a wav
                subprocess.check_call("opusdec --rate 16000 /home/pi/voice.ogg /home/pi/voice.wav", shell=True)
                # reconocimiento de voz y convertir a texto
                subprocess.check_call("pocketsphinx_continuous -lm /home/pi/3988.lm -dict /home/pi/3988.dic \
                                      -infile /home/pi/voice.wav > /home/pi/text", shell=True)

                # leer contenido de text
                fichero = open("/home/pi/text")
                contenido = fichero.read()
                fichero.close()
                # mandar a telegram un mensaje con el contenido
                #bot.send_message( cid, contenido)
                #print contenido

                db = MySQLdb.connect(host = servidor, user = usuario, passwd = clave, db = basedatos)
                cursor = db.cursor()

                if contenido == 'DEPURADORA ON\n':
                    x = '321'
                    orden = 'ON'
                elif contenido == 'DEPURADORA OFF\n':
                    x = '321'
                    orden = 'OFF'
                elif contenido == 'RIEGO ON\n':
                    x = '202'
                    orden = 'ON'
                elif contenido == 'RIEGO OFF\n':
                    x = '202'
                    orden = 'OFF'
                else:
                    pass

                try:
                    sql = "UPDATE reles SET modo='"+orden+"' WHERE id_rele="+x
                    cursor.execute(sql)
                    db.commit()
                    bot.send_message( cid, contenido)
                except:
                    msg='No se puede actualizar la tabla reles con la orden recibida.'
                    bot.send_message(cid, msg)

                cursor.close()
                db.close()


            elif m.content_type == 'text':

                #print m
                ...
                ...
