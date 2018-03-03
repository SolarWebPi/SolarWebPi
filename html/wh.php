<?php

require('conexion.php');
date_default_timezone_set("UTC");

//Coger datos 2 grafica
$sql = "SELECT Fecha, TRUNCATE(kWhp_bat/1000,1) as kWhp_bat1, TRUNCATE(kWhn_bat/1000,1) as kWhn_bat1
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

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


//Coger datos 3 grafica
$sql = "SELECT Fecha, TRUNCATE(kWh_placa/1000,1) as kWh_placa1
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row3 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata3[$i] = $row3;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


//Coger datos 4 grafica
$sql = "SELECT Fecha,TRUNCATE((kWh_placa-(kWhp_bat-kWhn_bat))/1000,1) as kWh_consumo
		FROM diario WHERE Fecha>= SUBDATE(NOW(), INTERVAL 30 DAY)
		GROUP BY Fecha ORDER BY Fecha";

if($result = mysqli_query($link, $sql)){

        $i=0;
        while($row4 = mysqli_fetch_assoc($result)) {
                //guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
                $rawdata4[$i] = $row4;
                $i++;
        }

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}


mysqli_close($link);



//Adaptar el tiempo grafica2
for($i=0;$i<count($rawdata1);$i++){
    $time = $rawdata1[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata1[$i]["Fecha"]=$date->getTimestamp()*1000;
}

//Adaptar el tiempo grafica3
for($i=0;$i<count($rawdata3);$i++){
    $time = $rawdata3[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata3[$i]["Fecha"]=$date->getTimestamp()*1000;
}


//Adaptar el tiempo grafica4
for($i=0;$i<count($rawdata4);$i++){
    $time = $rawdata4[$i]["Fecha"];
    $date = new DateTime($time);
    $rawdata4[$i]["Fecha"]=$date->getTimestamp()*1000;
}





?>

<HTML>

<body>

<meta charset="utf-8">


<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>
<script src="js/highcharts.js"></script>
<script src="js/highcharts-more.js"></script>
<script src="js/themes/grid.js"></script>
-->
<!-- Importo el archivo Javascript directamente desde la web -->

<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/highcharts.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>


<div id="container2"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<br style="clear:both;"/>
<br>
<div id="container3"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<br style="clear:both;"/>
<br>
<div id="container4"  style="width: 100%; height: 240px; margin-left:5; float: left"></div>
<br style="clear:both;"/>
<br>

</body>

<script>
$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: true,
				//timezoneOffset: - 0 * 60 
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


	var char2 = new Highcharts.Chart ({
	    chart: {
		renderTo: 'container2',
                zoomType: 'xy'
            },

            title: {
                text: 'kWh Batería'
            },
	    subtitle: {
		text: 'Puesta a 0, cada día a las 0h'
	    },
	    credits: {
		enabled: false
	    },
            xAxis: {
		dateTimeLabelFormats: { day: '%e %b' },
		type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
		layout: 'vertical',
		backgroundColor: 'white',
		align: 'right',
		verticalAlign: 'top',
		y: 0,
		x: 0,
		borderWidth: 1,
		borderRadius: 0,
		floating: true
            },

	    plotOptions: {
		  column: {
		    grouping: true, //false para columnas una delante de otra
			dataLabels: {
			          enabled: true,
			          crop: false,
			          overflow: 'none',
			        },
			borderWidth: 1
                },
		    series: {
		       shadow: true,
		       pointPadding: 0,
		       groupPadding: 0.1 //
		     }
            },

            series: [{
                name: 'kWh in',
		type: 'column',
		pointWidth: 15,  //Ancho de la columna
		color: 'rgba(100,149,237,0.8)',  //0.4 nivel de transparecia
                //color: Highcharts.getOptions().colors[1],
                tooltip: {
                    valueSuffix: ' kWh',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata1);$i++){
                   ?>
                   data.push([<?php echo $rawdata1[$i]["Fecha"];?>,<?php echo $rawdata1[$i]["kWhp_bat1"];?>]);
                   <?php } ?>
                return data;
                     })()
	    }, {
                name: 'kWh out',
                type: 'column',
		pointWidth: 15,
		color: 'rgba(255,0,0,0.8)',
                //color: Highcharts.getOptions().colors[2],
                tooltip: {
                    valueSuffix: ' Wh',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata1);$i++){
                   ?>
                   data.push([<?php echo $rawdata1[$i]["Fecha"];?>,<?php echo $rawdata1[$i]["kWhn_bat1"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]
        });
    var char3 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container3',
                zoomType: 'xy'
            },

            title: {
                text: 'kWh Placa'
            },
            subtitle: {
                text: 'Puesta a 0, cada día a las 0h'
            },
            credits: {
                enabled: false
	    },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },

            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },
            plotOptions: {
                column: {
                    grouping: false,
					dataLabels: {
			          enabled: true,
			          crop: false,
			          overflow: 'none',
			        },
                    borderWidth: 1
                },
                series: {
                    shadow: true,
                    //pointWidth: 20,
                    //pointInterval: 0,
                    pointPadding: 0,
                    groupPadding: 0
                }
            },

            series: [{
                name: 'kWh',
                type: 'column',
		pointWidth: 20,
                color: 'rgba(100,149,237,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' kWh',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata3);$i++){
                   ?>
                   data.push([<?php echo $rawdata3[$i]["Fecha"];?>,<?php echo $rawdata3[$i]["kWh_placa1"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

	});

    var char4 = new Highcharts.Chart ({
            chart: {
                renderTo: 'container4',
                zoomType: 'xy'
            },

            title: {
                text: 'kWh Consumo diario'
            },
            subtitle: {
                text: 'Puesta a 0, cada día a las 0h'
            },
            credits: {
                enabled: false
            },
            xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
                //categories: ['Mie','Jue','Vie','Sab','Dom']
            },
            yAxis: {
                title: {
                    text: null
                }
            },

            legend: {
                enabled: true,
                layout: 'vertical',
                backgroundColor: 'white',
                align: 'right',
                verticalAlign: 'top',
                y: 0,
                x: 0,
                borderWidth: 1,
                borderRadius: 0,
                floating: true
            },

            plotOptions: {
                column: {
                    grouping: false,
					dataLabels: {
			          enabled: true,
			          crop: false,
			          overflow: 'none',
			        },
                    borderWidth: 1
                },
                series: {
                    shadow: true,
                    //pointWidth: 20,
                    //pointInterval: 0,
                    pointPadding: 0,
                    groupPadding: 0
                }
            },
            series: [{
                name: 'kWh',
                type: 'column',
		pointWidth: 20,
                color: 'rgba(255,0,0,0.8)',
                //color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' kWh',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata4);$i++){
                   ?>
                   data.push([<?php echo $rawdata4[$i]["Fecha"];?>,<?php echo $rawdata4[$i]["kWh_consumo"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

        });

});
</script>
</html>
