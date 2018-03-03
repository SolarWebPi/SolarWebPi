**FVControl: Activar/desactivar relés mandando mensajes de voz desde Telegram**

Mandar un mensaje de voz desde Telegram no es ningún misterio, pero hay que saber que su contenedor o formato
de archivo de audio es Ogg (códec OPUS).
Nuestro reconocimiento de voz funciona con formato de audio WAV, con lo que es necesario convertir el archivo de OGG a WAV. 

Primero voy a pegar aquí la modificación que he hecho a fvbot.py para después comentar cada paso y por último 
realizar la instalación del software necesario.


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
                subprocess.check_call("pocketsphinx_continuous -lm /home/pi/3988.lm \
                                                   -dict /home/pi/3988.dic \
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

Las modificaciones incorporadas al programa van desde/hasta los textos marcados con fondo rojo.

La primera parte (desde el IF inicial hasta new_file.write) sirve para identificar que el mensaje 
enviado por Telegram es de voz y en tal caso guardarlo en /home/pi con el nombre de voice.ogg

El siguiente comando lo que hace es convertir el archivo voice.ogg a voice.wav con una tasa de 
muestreo (sample rate) de 16000 Hz.
El siguiente comando ejecuta el programa de reconocimiento de voz, guardando la salida (texto)
en el archivo /home/pi/text
* Los archivos 3988.lm y 3988.dic pueden cambiar el nombre pero no la extensión. Luego veremos como crearlos.

A continuación lo que hacemos es leer el contenido del archivo text y si se corresponde con alguna de las 
condiciones (IF), actualizará el 'modo' del relé en cuestión, en la base de datos. Luego ya fv.py se ocupará 
de encender/apagar el relé. Se puede también incluir el modo PRG (Ejemplo: 'DEPURADORA PROG\n' y orden = 'PRG') 

** Es posible activar/desactivar GPIOs de la Raspberry directamente. Aquí, ya la imaginación de cada uno.


SOFTWARE necesario:

Convertidor de Ogg a Wav

$ sudo apt-get install opus-tools

Instalar algunas posibles dependencias

$ sudo apt-get install bison libasound2-dev swig


Reconocimiento de voz (son dos programas, descargar y compilar)

SPHINXBASE

cd ~/
wget http://sourceforge.net/projects/cmusphinx/files/sphinxbase/5prealpha/sphinxbase-5prealpha.tar.gz
tar -zxvf ./sphinxbase-5prealpha.tar.gz
cd ./sphinxbase-5prealpha
./configure --enable-fixed
make clean all
make check
sudo make install 

POCKETSPHINX

cd ~/
wget http://sourceforge.net/projects/cmusphinx/files/pocketsphinx/5prealpha/pocketsphinx-5prealpha.tar.gz
tar -zxvf pocketsphinx-5prealpha.tar.gz
cd ./pocketsphinx-5prealpha
./configure
make clean all
make check
sudo make install 
 

Ahora ya toca liarnos con los archivos 3988.lm (modelo de lenguaje) y 3988.dic (diccionario).

Lo que vamos a hacer, es crear un documento de texto 'corpus.txt'. Podemos hacerlo desde Windows. 
Y dentro escribiremos los mensajes que podemos/queramos mandar. Ejemplo:

corpus.txt
DEPURADORA ON
DEPURADORA OFF
RIEGO ON
RIEGO OFF
ENCENDER LUZ EXTERIOR
APAGAR LUZ EXTERIOR
PROGRAMAR LUZ EXTERIOR

Creo que se entiende la idea. Una vez creado, vamos a subirlo a esta web:

http://www.speech.cs.cmu.edu/tools/lmtool-new.html

y le damos al botón COMPILE KNOWLEDGE BASE.

Se abrirá una nueva página web con varios archivos. Nos interesan los enlaces de los .lm y .dic

Desde la raspberry los bajamos con:

$ wget URL_del_lm 
y
$ wget URL_del_dic

Ya sólo nos queda cambiar los nombres a estos dos archivos por 3988.lm y 3988.dic o entrar dentro 
de fvbot.py y cambiar el nombre allí.
