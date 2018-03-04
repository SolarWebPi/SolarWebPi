**1. Instalación software en PC**

Usaremos Windows y básicamente 2 programas: “Esplorer” y “nodemcu-Flasher-master”
Enlace a Esplorer: https://esp8266.ru/esplorer/
Enlace a Flasher: https://github.com/nodemcu/nodemcu-flasher

**2. Carga firmware en NodeMCU**

Usaremos nodemcu-flasher-master primero. Hay 2 versiones, la de 32 y 64 bits. Usar en función del SO que tengamos, que normalmente será 64.

    -a) Usaremos este programa para meter el firmware al nodeMCU. 
    -b) Conectaremos con un cable USB el nodeMCU al ordenador.
    -c) Ejecutamos ESP8266Flasher.exe (la versión que toque)
    -d) El fichero a cargar lo encontraremos dentro de Resources\Binaries y se llama nodemcu_float_0.9……
    -e) En “advanced” hay que configurar el baudrate a 115200
    -f) En “config” abriremos la primera rueda de engranage y seleccionaremos el archivo mencionado previamente.
    -g) Ir a “Operation” y darle a Flash (F)
    -h) Si todo va bien, veremos en una barra de progreso que todo va rulando bien………

Con esto, ya tenemos el FIRMWARE, Sistema operativo instalado en nuestro nodeMCU :-p

**3. Carga de programas en NodeMCU**

Abriremos Esplorer y navegaremos por las carpetas hasta encontrar dentro de “excedentes” los ficheros “init.lua” y 
“Excedentes.lua”. El primero es un loader del segundo. Para ejecutar Esplorer.jar, hay te tener previamente instalado JAVA. 
Usaremos Notepad++ o un editor de texto plano para editar el fichero “Excedentes.lua”

    -a) En la línea wifi.sta.config………pondremos SSID de la Wifi y el password.
    -b) En “setip” pondremos la ip que queramos (en mi caso me he decantado por 192.168.0.20), máscara, gateway….
    -c) Al final del fichero también hay que tunear la IP……..
    -d) Ahora abrimos el .JAR (Asumimos que el nodeMCU sigue conectado vía USB ;-)
    -e) Le damos al botón open del programa
    -f) Le damos al botón RESET (RST) del nodeMCU
    -g) En la ventana izquierda, apretamos en open y cargamos “init.lua
    -h) Le damos al botón “Save to ESP
    -i) Enla ventana izquierda, cerramos “init.lua” y abrimos “Excedentes.lua”
    -j) Le damos al botón”Save to ESP”
    -k) Le damos a CLOSE para cerrar el puerto
    -l) Cerramos Esplorer
    -m) Sin desconectar el navegador (ojo que el explorer a mi no me iba…..) conectarse a: http://192.168.0.20/R1=?
    -n) Debería de salir algo así…….
