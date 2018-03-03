# SolarWebPi

Control de instalación fotovoltáica con Raspberry Pi

**Qué necesitas:**
- 1 raspberry pi con fuente de alimentación y una tarjeta microsd 8GB.
- 1 Protoboard o una placa PV CONTROL+ diseñada por @MLeon para soldar los componentes, que actualmente se encuentra en la versión - 1.2, encontraras su diseño en formato .... aquí.
- 2 Shuhnts de ..... /....
- 1 ADS1115
- 1 PCF8574
- 1 PCF8574
- 1 MUX74HC4067
- 1 DS18B20
- Conectores enchufables

**Indice de conenidos:**

#1 Instalación HW inicial.

2 Instalación Sistema Operativo.

3 Activar Wifi.

4 Configuración Inicial RPi.

5 Cargamos las utilidades y librerías Python.

6 Acceso remoto

    6.1 Tipo terminal por SSH
  
    6.2 Escritorio remoto
  
    6.3 Controlar RPi por web con webmin (no es necesario…solo para usuarios un poco avanzados)

7 Instalar Apache/PHP/MariaDB

    7.1 Controlar Mysql por web
  
8 Instalar Programa Control Fotovoltaico

    8.1 Copiar programa e Instalar BD
  
    8.2 Paginas web
  
    8.3 Cambiar archivos de configuración
 
    8.4 TELEGRAM
  
    8.5 Probando Programa principal
  
    8.6 Creando servicios y tareas periódicas
  
    8.7 Creando tareas al arrancar
  
    8.8 Creando tareas periódicas
  
9 Instalando Opciones

    9.1 Sensor de Temperatura DS18B20
  
    9.2 TEAMVIEWER
  
    9.3 Reinicio Router en remoto


   **1  Instalación HW inicial**
Utilizaremos una tarjeta microSD de 8GB
Utilizar la entrada HDMI de la TV  para ver la pantalla
Utilizar un teclado /ratón inalámbrico con dongle USB que tenia
Así conecto la RPI por HDMI a la TV  y desde en “sofá” del salón uso el teclado/ratón
Una vez configurada inicialmente lo normal será acceder a la RPi desde cualquier PC
  
  **2  Instalación Sistema Operativo**
En mi caso he instalado Raspbian con Desktop desde aquí https://www.raspberrypi.org/downloads/raspbian/
  
  **3  Activar Wifi**
Se hace desde el interfaz grafico bastante intuitivamente....
No obstante hay tutoriales explicándolo...
http://bot-boss.com/configuracion-wifi-bluetooth-raspberry-pi-3/

   **4  Configuración Inicial RPi**
Abrimos Preferencias/Configuración de Raspberry Pi

    • Pestaña System 
        ◦  Hostname a rpi  u otro nombre
        ◦ Cambiar clave de raspberry a otra (por ejm Solarweb@123 o la que se quiera)
        ◦ Cambiar resolución de pantalla a lo que se quiera  o dejarlo como esta
    • En Pestaña Interfaces  Activamos
        ◦  SSH: Conexión segura por Terminal (no activar si no se va a usar)
        ◦  VNC:  Escritorio remoto  (no activar si no se va a usar)
        ◦  I2C: Control de los ADS1115 y PCF8574
        ◦ 1 Wire : Para el sensor de temperatura DS18B20 (no activar si no se va a usar)
    • Pestaña Localization: 
        ◦ Locale …. Lenguaje: es ( Spanish)
        ◦ Country….ES (spain) 
        ◦ Character Set….UTF-8
        ◦ Timezone Europe/Madrid
        ◦ Keyboard: Spain /Spanish
        ◦ Wifi Country: ES Spain  

Ahora toca poner la IP de la RPI fija…..la hemos puesto en la 10….luego en una red 192.168.1.X seria:
Botón ratón derecho sobre símbolo wifi (esquina superior derecha) ..Network Preferences

   **5  Cargamos las utilidades y librerías Python**
Abrir Terminal
Teclear:
   ``` • sudo apt-get install -y i2c-tools
       • sudo pip install adafruit-ads1x15
       • sudo i2cdetect -y 1 ..... nos debería dar algo parecido a esto
 ```  
 Reiniciamos la Raspberry
 
   **6 Acceso remoto**
Una vez que ya tenemos conectividad y una primera configuración,  por eso de no usar la TV , vamos a configurar varias formas de acceso remoto

   **6.1 Tipo terminal por SSH**
Yo utilizo PuttyPortable pero se puede utilizar cualquier programa tipo hiperterminal, etc
Es bastante autoexplicativo sabiendo el usuario y clave

Abrir el puerto SSH tiene riesgos de que “los malos” te intenten entrar desde fuera dependiendo de cómo tengas configurado el router etc
Si no se va a usar mejor no activarlo…en mi caso  antes he puesto un firewall un poco bestia inicialmente usando hosts.deny (ALL:ALL) y hosts.allow (ALL:192.168.*.*)

   **6.2 Escritorio remoto**
Nos instalamos en un PC el VNC viewer, ya tenemos acceso al escritorio remoto desde un pc
https://www.realvnc.com/download/viewer/
Es un método recomendable si no estás habituado a Linux y quieres moverte con el interfaz grafico
Yo además uso Teamviewer para controlar remotamente todos los ordenadores que tengo 
Con esto ya podemos dejar la TV “libre” y seguir desde el PC configurando

   **6.3 Controlar RPi por web con webmin (no es necesario…solo para usuarios un poco avanzados)**
Este tutorial  vale pero poniendo  “sudo” si no entras como root…..se queda unpacking un buen rato……..
http://www.deacosta.com/instala-webmin-y-administra-tu-raspberry-pi-desde-una-consola-web/

Web oficial
http://www.webmin.com/deb.html

Using the Webmin APT repository
If you like to install and update Webmin via APT, edit the `/etc/apt/sources.list` file on your system and add the line: 
`deb http://download.webmin.com/download/repository sarge contrib`
You should also fetch and install my GPG key with which the repository is signed, with the commands :cd /root
`wget http://www.webmin.com/jcameron-key.asc`
`apt-key add jcameron-key.asc` You will now be able to install with the commands :apt-get update
`apt-get install webmin` All dependencies should be resolved automatically.

   **7 Instalar Apache/PHP/MariaDB**
https://librematica.es/blogs/como-instalar-servidor-lamp-debian-9-stretch
```
sudo apt-get install mariadb-client mariadb-server
sudo apt-get install php7.0 php7.0-mysql
sudo apt-get install apache2 apache2-mod-php7.0
```
Recordar que el usuario de MariaDB  por defecto es root y no tiene clave

Para probar la base de datos podemos teclear:
`sudo mysql -u root –p`
teclear `exit` para salir de la BD

Parece lógico asegurar con una clave el acceso a la BD…para ello tecleamos:
 `sudo mysql_secure_installation`
y seguimos el proceso 
Guardar la clave para entrar en la Base de datos

Ahora instalamos una librería para acceder a la BD desde el programa en Python:
`sudo apt-get install python-mysqldb`

   **7.1 Controlar Mysql por web**
Tutorial http://visystem.ddns.net:7442/instalacion-phpmyadmin-raspberrypi/
Para instalar phpmyadmin: `sudo apt-get install phpmyadmin`

   **8 Instalar Programa Control Fotovoltaico**
Para copiar archivos específicos del programa a la RPi, yo uso Winscp para poder copiar los archivos entre el PC y la RPI, hay mas formas de copiar archivos, luego para gustos, los colores
https://winscp.net/eng/download.php

   **8.1 Copiar programa e Instalar BD**
    • Copiar contenido de la carpeta /home/pi
    • Dar permisos de ejecución desde el terminal de la RPi
        ◦ chmod u+x install_BD.sh
        ◦ chmod u+x cortafuegos
        ◦ chmod u+x fv.py
        ◦ chmod u+x fvbot.py
        ◦ chmod u+x gestionbd.sh
        ◦ chmod u+x diario.sh
    • Ejecutar el script cortafuegos con `sudo ./cortafuegos`  (atento que lleva punto al principio)
    • Instala la Base de Datos con `sudo ./install_BD.sh`   
Darle nombre a:
    • la Base de Datos----por ejm control_solar
    • usuario: por ejm rpi
    • clave: por ejm  fv
Ahora ya podemos entrar en la base de datos recién creada con phpmyadmin
Para ello tecleamos en el navegador web 
http://192.168.1.10/phpmyadmin/ 
y deberemos ver algo parecido a esto:

   **8.2 Paginas web**
Por facilidad de modificación yo he cambiado el propietario de la carpeta/var/www/html de root a pi, para hacer esto desde terminal seria:
        `sudo chown pi.pi -R  /var/www/html`
        `rm  /var/www/html/ index.html`     (Borra archivo por defecto index.html)
Copiar en `/var/www/html` todo el contenido de la carpeta html, con esto ya deberíamos ver las páginas web (sin datos aun) en la dirección IP de la Raspberry…por ejm desde el navegador con 192.168.1.10

   **8.3 Cambiar archivos de configuración**
Se aconseja dejar la  IP 192.168.1.10, en caso contrario hay que cambiar todas las referencias a esa IP (servidor web, cortafuegos, etc). En caso de cambiarusuario/clave de la BD hay que actualizar en `/home/pi` los siguientes archivos:
-fv.py
-diario.py
-diario_ayer.py
-fvbot_msg.py
-vaciartablas.py
-fvbot.py
-gestionbd.sh

También tendrá que cambiar el user/pass elegido en el archivo /var/www/html/conexion.php. Para ello desde terminal con `sudo  nano /var/www/html/conexion.php`

   **8.4 TELEGRAM**
Instalamos la librería del bot para python con `sudo pip install pyTelegramBotAPI`
Lo lógico es que ahora se cree, si no se tiene ya, un BOT en Telegram hay muchos tutoriales por la web
Lo normal es que se instale en el PC o en el móvil (o en ambos) el programa Telegram y, usando BotFather crearse un bot propio
El objetivo es tener nuestro TOKEN (te lo dan al crear el Bot) y es lo que tenemos que poner en el programa para que nos mande los mensajes, etc.
Si lo has creado y ya tienes el TOKEN, por ejm entra en el IDLE de Python 2 y abre el archivo fvbot_msg.py
Poner en TOKEN el valor del bot creado
Si ejecutamos el programa……. Run – Run Module ( o pulsar F5)  ya deberíamos recibir en el móvil o PC un msg (sin datos validos lógicamente)

   **8.5 Probando Programa principal**
Entramos en el IDLE de Python 2.7 y cargamos el archivo fv.py
Chequear líneas cercanas a la que tiene 6 # es decir  ######, para adaptarlo a nuestra instalación en particular (valor shunt, etc)

Por defecto esta en modo simulación y así podemos probar que el SW va OK sin tener nada conectado 
Si lo ejecutamos (F5) ya se debería ver en la web como cambian los valores

Toca crear relés y ponerles condiciones etc para ir viendo cómo funciona
En mi caso esta carga inicial por rapidez la he realizado por web con phpmyadmin….poniendo en el navegador 192.168.1.10/phpmyadmin e introduciendo los registros en las tablas:
    • reles:  Id, Nombre de los reles….
    • reles_c: condiciones de ON y OFF
    • reles_h: condiciones de horario

 Una vez dados de alta los relés y sus condiciones por ejm se puede probar desde el Telegram del móvil o PC, que el  programa fvbot.py va OK dándole unas pocas ordenes

   **8.6 Creando servicios y tareas periódicas**
Para asegurar que el programa principal fv.py está siempre activo, lo mejor es ejecutarlo como servicio, por lo que debemos crear dicho servicio desde terminal:
    `cd /etc/systemd/system`       pasamos al directorio /etc/systemd/system       
    `sudo nano fv.service`             Creamos un archivo de texto llamado fv.service
Introducimos este texto:
```
[Unit]
Description=Control Fotovoltaico
After=mysql.service

[Service]
ExecStart=/home/pi/fv.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```
Guardamos y salimos con Crtl+X
    `sudo systemctl enable fv.service`     habilitamos servicio(puede omitirse .service)

Con esto ya estaría listo para arrancarse en el próximo reinicio…algunos comandos útiles para manejo de servicios:

    `sudo systemctl start fv.service`             arranca servicio 
    `sudo systemctl stop fv.service`             para servicio
    `sudo systemctl disable fv.service`        deshabilita servicio, no arranca al iniciar
    `sudo journalctl -u fv.service`                  información de log
    `sudo systemctl is-enabled fv.service`   
mas información en 
https://www.digitalocean.com/community/tutorials/how-to-use-systemctl-to-manage-systemd-services-and-units

Si vamos a utilizar el bot de Telegram hacemos lo mismo para crear el servicio fvbot.py
    `cd /etc/systemd/system`       pasamos al directorio /etc/systemd/system       
    `sudo nano fvbot.service`           Creamos un archivo de texto llamado fvbot.service
Introducimos este texto:
```
[Unit]
Description=FV Telegram bot
After=mysql.service

[Service]
ExecStart=/home/pi/fvbot.py
Restart=always
RestartSec=600

[Install]
WantedBy=multi-user.target
```
Guardamos y salimos con Crtl+X

    `sudo systemctl enable fvbot.service`     habilitamos servicio

Con esto ya estaría listo para arrancarse en el próximo reinicio

   **8.7 Creando tareas al arrancar**
Ponemos en   `/etc/rc.local`  lo que queremos que se inicie al arrancar (por ahora solo el cortafuegos)
    `sudo nano /etc/rc.local`
```
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"

sudo /home/pi/cortafuegos
exit 0
fi
```
Guardamos y salimos (crtl+X)

   **8.8 Creando tareas periódicas**
Utilizaremos crontab para activar las tareas periódicas..(copia de seguridad cada dia, envio de mensajes de telegram cada 30 minutos y creación del registro diario)
    • sudo nano /etc/crontab
```
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
10 0    * * *   root    /home/pi/gestionbd.sh
25 *    * * *   root    /home/pi/diario.sh
55 *    * * *   root    /home/pi/diario.sh
00 *    * * *   root    python /home/pi/fvbot_msg.py
30 *    * * *   root    python /home/pi/fvbot_msg.py
```
Como se ve he puesto que mande un mensaje de Telegram cada 30 minutos (a X:00 y a X:30) , si solo queremos cada hora quitar la última línea 
Guardamos y salimos (crtl+X)
Con esto ya tendríamos una configuración operativa hay algunas opciones que dependerán de si se instalan cosas (sensor temperatura u otras preferencias) 

**9 Instalando Opciones**
  **9.1 Sensor de Temperatura DS18B20**
Aunque es para Python3 este tutorial es bueno
http://bigl.es/ds18b20-temperature-sensor-with-python-raspberry-pi/
Asegurad que en el apartado Configuración Inicial RPi hemos habilitado 1-wire
    `sudo pip install w1thermsensor`
En la carpeta `/home/pi` hay un programa en Python denominado TEST_DS18B20.py que se puede utilizar para ver si va bien el sensor
Recordad cambiar en el programa de python la referencia concreta del DS18B20 instalado (28-xxxxx) según lo que aparezca en      `/sys/devices/w1_bus_master1`

  **9.2 TEAMVIEWER**
Descarga el programa  para Raspberry  y copialo en la carpeta pi
https://pages.teamviewer.com/published/raspberrypi/
Instala el paquete teamviewer-host_11.0.63329_armhf.deb (en entorno gráfico…botón derecho sobre el fichero ….Instalar paquete)
Se tirara un ratillo instalando
Con esto ya tendríamos instalado Teamviewer, en mi caso tengo creada una cuenta y por tanto puedo acceder a todos mis dispositivos que tienen este programa de forma mas cómoda

   **9.3 Reinicio Router en remoto**
En mi caso tengo la instalación en remoto con un router 3G, por lo que debo asegurar en la medida de lo posible que exista conectividad de datos
Una forma es reiniciando el router automáticamente si dicha conectividad se pierde por un periodo de tiempo, para ello instalamos los siguientes programas
```
    • sudo apt-get install telnet
    • sudo apt-get install expect
```
Editamos el archivo router.sh que hemos incluido en /home/pi  modificando los valores de user (admin es lo habitual), password e IP para nuestro router
```
set username "YYYYYYY"
set password "XXXXXXX"
set ip "192.168.1.1"
```
Ya se podría utilizar el programa, por ejm desde el terminal de la RPi:
`./router.sh help`		muestra comandos disponibles
`./router.sh reboot`     	reinicia el router
En mi caso he modificado fvbot_msg.py para que si falla en el envío 10 veces reinicie el router

 
Menciones especiales para :+1: @Nikkito y :+1: @MLeon
