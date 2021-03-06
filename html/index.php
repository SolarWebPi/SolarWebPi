<?php

require('conexion.php');

//FLOTACION/DIVER
$sql = "SELECT Vflot FROM datos WHERE DATE(Tiempo)= CURDATE() AND id=(SELECT max(id) FROM datos)";

if($result = mysqli_query($link, $sql)){

        $row=mysqli_fetch_row($result);
	$row = number_format((float)$row[0], 0, '.', '');

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>


<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="es-ES" lang="es-ES">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<link href="img/favicon.ico" rel="shortcut icon" type="image/x-icon" />
<link href="css/index.css" rel="stylesheet" type="text/css" media="screen" />
<title>RPi: Control sistema fotovoltaico</title>
</head>

<body>

<div id="contenedor">
    <div id="cabecera">
	<a id="logo-header" href="index.php">
		<span class="site-name">RPi: Control Sistema Fotovoltaico</span>  <!-- No incrementar longitud del texto -->

		<span class="site-desc">
		    <?php
			if($row == 1)
        			print "<font size = 4 color = yellow><b>EXCEDENTES ON</b></font>";
    			else
        			print "<font size = 4 color = red><b>EXCEDENTES OFF</b></font>";
    		    ?>
		</span>

	</a> <!-- / #logo-header -->


	<?php
    	$recibe_pagina=$_GET['pagina'];
    	?>

	<nav>
		<ul>

            <li><a href="index.php?pagina=boton1"
		     	title="Inicio"><img src="img/Home.png" width="20" height="20"> Inicio</a>
			</li>
			<li><a href="#"
			    title="Gráficas"><img src="img/Graph.png" width="20" height="20"> Gráficas</a>
			    <ul>
				    <li><a href="index.php?pagina=boton2"
				        title="Wh Batería, Producción y Consumo">kWh</a>
				    </li>
                    <li><a href="index.php?pagina=boton3"
				        title="Promedios 30 días">Promedios</a>
                    </li>
				    <li><a href="index.php?pagina=boton4b"
				        title="Histórico 3 días">Hist_3</a>
				    </li>
					<li><a href="index.php?pagina=boton4"
				        title="Histórico Mes">Hist_Mes</a>
				    </li>
					<li><a href="index.php?pagina=boton7"
                        title="Gráficas Producción y Consumo">Extra</a>
                    </li>
                    <li><a href="index.php?pagina=boton8"
                        title="Tabla valores importantes">Diario</a>
                    </li>
                    <li><a href="index.php?pagina=boton9"
                        title="Logs del sistema">Log</a>
                    </li>
			    </ul>
			</li>
			<li><a href="#"
			    title="Relés"><img src="img/Target.png" width="20" height="20"> Relés</a>
			    <ul>
				    <li><a href="index.php?pagina=boton5"
				        title="Tabla relés">T.Relés</a>
				    </li>
				    <li><a href="index.php?pagina=boton6"
				        title="Horas funcionamiento">H.Relés</a>
				    </li>
			    </ul>
			</li>
		</ul>
	</nav>

    </div>

   <div id="contenido">
	<br>
 	<?php
	    switch ($recibe_pagina){
	    case "boton1":
		include ("inicio.php");
		break;
            case "boton2":
                include ("wh.php");
                break;
	    case "boton3":
		include ("prom_30.php");
		break;
            case "boton4":
                include ("historico_mes.php");
                break;
			case "boton4b":
                include ("historico3.php");
                break;	
            case "boton5":
                include ("reles.php");
                break;
            case "boton6":
                include ("horas_reles.php");
                break;
            case "boton7":
                include ("grafica_elige.php");
                break;
            case "boton8":
                include ("diario.php");
                break;
            case "boton9":
                include ("log.php");
                break;

	    default:
		include ("inicio.php");
	    }
 	?>

	<br>
    </div>

    <div id="pie">

	<h3>&copy; 2016 by mleon y nikitto  </h3>

    </div>



</div>
</body>
</html>
