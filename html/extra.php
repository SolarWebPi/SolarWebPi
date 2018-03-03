<?php
$rango="MONTH";
$parametro="Produccion";

if(( $_POST["parametro"] ) && ($_POST["rango"] )) {//|| (($rango=="MONTH") && ($parametro=="Produccion")){

    require('conexion.php');

    date_default_timezone_set("UTC");

    $parametro = $_POST["parametro"];
    $rango = $_POST["rango"];
    $anno = $_POST["anno"];

    if($parametro == "Produccion") {

	$colorbar = 'rgba(100,149,237,0.8)';

	if($rango=="WEEK") {
		$sql = "SELECT Fecha, TRUNCATE(kWh_placa/1000,1) as Datos FROM diario
			WHERE WEEK(Fecha,1) = WEEK(CURDATE(),1)
			GROUP BY Fecha";

		$vartitulo = "Producción Semanal kWh";
		$anchocol = 40;

	} elseif($rango=="MONTH") {
		$sql = "SELECT Fecha, TRUNCATE(kWh_placa/1000,1) as Datos FROM diario
			WHERE MONTH(Fecha) = MONTH(CURDATE()) AND YEAR(Fecha) = YEAR(CURDATE())
			GROUP BY Fecha";

		$vartitulo = "Producción Mensual kWh";
		$anchocol= 20;

	} elseif($rango=="ASEM") {


                $sql = "SELECT Fecha, TRUNCATE(SUM(kWh_placa/1000),1) as Datos
                        FROM diario WHERE YEAR(Fecha)=$anno
                        GROUP BY WEEK(Fecha,3)";   //1 antes, con 3 funciona OK

		$vartitulo = "Producción kWh Año $anno por Semanas";
		$anchocol= 20;

	} else {

                $sql = "SELECT STR_TO_DATE(concat('1,', MONTH(Fecha), ',', YEAR(Fecha)), '%d,%m,%Y') as Fecha, TRUNCATE(SUM(kWh_placa/1000),1) as Datos
                        FROM diario WHERE YEAR(Fecha)=$anno
                        GROUP BY MONTH(Fecha)";

                $vartitulo = "Producción kWh Año $anno por Meses";
                $anchocol= 40;

	}


    } elseif($parametro == "Consumo") {

	$colorbar = 'rgba(255,0,0,0.8)';

        if($rango=="WEEK") {
                $sql = "SELECT Fecha, TRUNCATE((kWh_placa-(kWhp_bat-kWhn_bat))/1000,1) as Datos FROM diario
                        WHERE WEEK(Fecha,1) = WEEK(CURDATE(),1)
                        GROUP BY Fecha";

                $vartitulo = "Consumo kWh Semanal";
                $anchocol = 40;

        } elseif($rango=="MONTH") {
                $sql = "SELECT Fecha, TRUNCATE((kWh_placa-(kWhp_bat-kWhn_bat))/1000,1) as Datos FROM diario
                        WHERE MONTH(Fecha) = MONTH(CURDATE()) AND YEAR(Fecha) = YEAR(CURDATE())
                        GROUP BY Fecha";

                $vartitulo = "Consumo kWh Mensual";
                $anchocol= 20;

        } elseif($rango=="ASEM") {

                $sql = "SELECT Fecha, TRUNCATE(SUM(kWh_placa-(KWhp_bat-kWhn_bat))/1000,1) as Datos
                        FROM diario WHERE YEAR(Fecha)=$anno
                        GROUP BY WEEK(Fecha,3)";  // 1 antes, con 3 funciona OK


                $vartitulo = "Consumo kWh Año $anno por Semanas";
                $anchocol= 20;

        } else {

                $sql = "SELECT STR_TO_DATE(concat('1,', MONTH(Fecha), ',', YEAR(Fecha)), '%d,%m,%Y') as Fecha, TRUNCATE(SUM(kWh_placa-(KWhp_bat-kWhn_bat))/1000,1) as Datos
                        FROM diario WHERE YEAR(Fecha)=$anno
                        GROUP BY MONTH(Fecha)";

                $vartitulo = "Consumo kWh Año $anno por Meses";
                $anchocol= 40;

        }

    }

    if($result = mysqli_query($link, $sql)){

	    $i=0;
	    while($row1 = mysqli_fetch_assoc($result)) {
		    //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
		    $rawdata1[$i] = $row1;
		    $i++;
	    }

    } else{

            echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
    }


    mysqli_close($link);


    //Adaptar el tiempo grafica4
    for($i=0;$i<count($rawdata1);$i++){
        $time = $rawdata1[$i]["Fecha"];
        $date = new DateTime($time);
        $rawdata1[$i]["Fecha"]=$date->getTimestamp()*1000;
    }
}


?>

<HTML>

<body>

<meta charset="utf-8">


<script src="https://code.jquery.com/jquery.js"></script>

<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>
<script src="http://code.highcharts.com/themes/grid.js"></script>


<form action = "<?php $_PHP_SELF ?>" method = "POST">
    <select name="parametro">
        <option value=""></option>
	<option value="Produccion">Producción</option>
        <option value="Consumo">Consumo</option>
    </select>
    <select name="rango">
        <option value=""></option>
        <option value="WEEK">Semana actual</option>
        <option value="MONTH">Mes actual</option>
	<option value="ASEM">Año x Semanas</option>
	<option value="AMES">Año x Meses</option>
    </select>
    <select name="anno">
        <option value="2016" <?php if (date("Y") == 2016) echo 'selected="selected"' ?>>2016</option>
        <option value="2017" <?php if (date("Y") == 2017) echo 'selected="selected"' ?>>2017</option>
        <option value="2018" <?php if (date("Y") == 2018) echo 'selected="selected"' ?>>2018</option>
        <option value="2019" <?php if (date("Y") == 2019) echo 'selected="selected"' ?>>2019</option>
        <option value="2020" <?php if (date("Y") == 2020) echo 'selected="selected"' ?>>2020</option>
        <option value="2021" <?php if (date("Y") == 2021) echo 'selected="selected"' ?>>2021</option>
        <option value="2022" <?php if (date("Y") == 2022) echo 'selected="selected"' ?>>2022</option>
        <option value="2023" <?php if (date("Y") == 2023) echo 'selected="selected"' ?>>2023</option>
        <option value="2024" <?php if (date("Y") == 2024) echo 'selected="selected"' ?>>2024</option>
        <option value="2025" <?php if (date("Y") == 2025) echo 'selected="selected"' ?>>2025</option>
        <option value="2026" <?php if (date("Y") == 2026) echo 'selected="selected"' ?>>2026</option>
        <option value="2027" <?php if (date("Y") == 2027) echo 'selected="selected"' ?>>2027</option>
        <option value="2028" <?php if (date("Y") == 2028) echo 'selected="selected"' ?>>2028</option>
        <option value="2029" <?php if (date("Y") == 2029) echo 'selected="selected"' ?>>2029</option>
        <option value="2030" <?php if (date("Y") == 2030) echo 'selected="selected"' ?>>2030</option>
    </select>
    <input type = "submit" value = "Ver" />
</form>

<p></p>

<div id="container1" style="width: auto;height: 60vh;margin-left: 5;margin-right:5"></div>
<br>



</body>

<script>
$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: true
            },
	    lang: {
		months: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
		weekdays: ['Dom', 'Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'],
		shortMonths: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],
	        rangeSelectorFrom: "Desde",
	        rangeSelectorTo: "A",
 	        printChart: "Imprimir gráfico",
		loading: "Cargando..."
	    }
        });

        var chart1 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container1',
                zoomType: 'xy'
            },

            title: {
                text: '<?php echo $vartitulo;?>'
	    },

            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
	    xAxis: {
		dateTimeLabelFormats: {
			day: '%e %b',
			week:'%e %b',
			month: '%b',
			year: '%Y'
		},
		type: 'datetime'    //datetime
	    },
	    yAxis: {
			title: {
				text: ''
			},
			labels: {
				enabled: true
			}
	    },
	    legend: {
		enabled: false
	    },
	    tooltip: {
		valueSuffix: ' Wh',
		valueDecimals: 2
	    },

        plotOptions: {
		  column: {
		    dataLabels: {
			enabled: true,
			crop: false,
			overflow: 'none',
		    },
		    enableMouseTracking: false
		  }
	    },

	    series: [{
		name: 'Wh',
		type: 'column',
		pointWidth: '<?php echo $anchocol;?>', //Ancho fijado de las columnas
		color: '<?php echo $colorbar;?>',
		//color: Highcharts.getOptions().colors[5],
		data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata1);$i++){
		   ?>
		   data.push([<?php echo $rawdata1[$i]["Fecha"];?>,<?php echo $rawdata1[$i]["Datos"];?>]);
                   <?php } ?>
		return data;
                     })()
		}]
	});
});


</script>
</html>
