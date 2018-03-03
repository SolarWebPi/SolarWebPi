<?php

require('conexion.php');

//Coger datos grafica historico general
//$sql = "SELECT Tiempo, SOC as SOCavg, Ibat as Ibatavg, Iplaca as Iplacaavg, Vbat as Vbatavg, Vflot*10 as Vflotavg
//        FROM datos WHERE DATE(Tiempo) >= SUBDATE(NOW(), INTERVAL 7 DAY)
//        ORDER BY Tiempo";

$sql = "SELECT Tiempo, AVG(SOC) as SOCavg, AVG(Ibat) as Ibatavg, AVG(Iplaca) as Iplacaavg, AVG(Vbat) as Vbatavg, AVG(Vflot)*10 as Vflotavg
        FROM datos WHERE DATE(Tiempo) >= SUBDATE(NOW(), INTERVAL 7 DAY)
        GROUP BY DAY(Tiempo),((60/1)*HOUR(TIME(Tiempo))+FLOOR(MINUTE(TIME(Tiempo))/1)) ORDER BY Tiempo";

if($result = mysqli_query($link, $sql)){

	$i=0;
	while($row = mysqli_fetch_assoc($result)) {
    		//guardamos en rawdata todos los vectores/filas que nos devuelve la consulta
    		$rawdata[$i] = $row;
    		$i++;
	}

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

//Adaptar el tiempo grafica historico general
for($i=0;$i<count($rawdata);$i++){
    $time = $rawdata[$i]["Tiempo"];
    $date = new DateTime($time);
    $rawdata[$i]["Tiempo"]=$date->getTimestamp()*1000;
}

?>


<HTML>

<body>

<meta charset="utf-8">


<!-- Importo el archivo Javascript de Highcharts directamente desde la RPi 
<script src="js/jquery.js"></script>
<script src="js/stock/highstock.js"></script>
<script src="js/highcharts-more.js"></script>

<script src="js/themes/grid.js"></script>
-->

<!-- Importo el archivo Javascript directamente desde la webr -->
<!--
-->
<script src="https://code.jquery.com/jquery.js"></script>
<script src="http://code.highcharts.com/stock/highstock.js"></script>
<script src="http://code.highcharts.com/highcharts-more.js"></script>

<script src="http://code.highcharts.com/themes/grid.js"></script>



<div id="container12" style="width: auto; height: 600px; margin-left: 5;margin-right:5"></div>
<br>

</body>

<script>
$(function () {

	Highcharts.setOptions({
            global: {
                useUTC: false
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

        var char = new Highcharts.StockChart ({
            chart: {
                renderTo: 'container12',
                zoomType: 'xy',
				panning: true,
                panKey: 'shift'
            },

            title: {
                text: 'Promedio SOC, Iplaca/Ibat y Vbat'
            },
            subtitle: {
                //text: 'Permite Zoom XY'
            },
            credits: {
                enabled: false
            },
            yAxis: [{
		        opposite: false,
				min: -150,
		        max: 150 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                }
             },{
                opposite: false,
				min: 24,
		        max: 35 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 28.8,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vabs'
		             }
		            }, {
		            value: 27.6,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: 'Vflot'
		              }
		          }]
	
             },{
                opposite: true,
				min: 20,
		        max: 100 ,
		        labels: {
                    //align: 'left',
                    y: 5
            	},
                title: {
                    text: null
                },
				plotLines: [{
		            value: 100,
		            width: 2,
		            color: 'green',
		            dashStyle: 'shortdash',
		            label: {
			            text: '100%'
		             }
		            }, {
		            value: 80,
		            width: 2,
		            color: 'red',
		            dashStyle: 'shortdash',
		            label: {
			            text: '80%'
		              }
		          }]
	
	
			 }],
			
			xAxis: {
                dateTimeLabelFormats: { day: '%e %b' },
                type: 'datetime'
             },
            legend: {
                enabled: true
             },

            rangeSelector: {
                buttons: [{
                    type: 'day',
                    count: 1,
                    text: '1día'
                }, {
                    type: 'day',
                    count: 7,
                    text: '7días'
                }, {
                    type: 'day',
                    count: 15,
                    text: '15días'
                }, {
                    type: 'all',
                    text: 'Todo'
                }],
                selected: 1
             },
            tooltip: {
                crosshairs: true,
                shared: true,
                valueDecimals: 2
             },

            series: [{
                name: 'Avg SOC',
                type: 'spline',
				yAxis: 2,
                color: Highcharts.getOptions().colors[1],
                tooltip: {
                    valueSuffix: ' %',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["SOCavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Avg Vbat',
                type: 'spline',
				yAxis: 1,
                color: Highcharts.getOptions().colors[0],
                tooltip: {
                    valueSuffix: ' V',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vbatavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Avg Ibat',
                type: 'spline',
                color: Highcharts.getOptions().colors[2],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Ibatavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Avg Iplaca',
                type: 'spline',
                color: Highcharts.getOptions().colors[3],
                tooltip: {
                    valueSuffix: ' A',
                    valueDecimals: 2,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Iplacaavg"];?>]);
                   <?php } ?>
                return data;
                     })()
              }, {
                name: 'Avg Vflot',
                type: 'spline',
                color: Highcharts.getOptions().colors[4],
                tooltip: {
                    valueSuffix: ' ',
                    valueDecimals: 0,
                },
                data: (function() {
                   var data = [];
                   <?php
                       for($i = 0 ;$i<count($rawdata);$i++){
                   ?>
                   data.push([<?php echo $rawdata[$i]["Tiempo"];?>,<?php echo $rawdata[$i]["Vflotavg"];?>]);
                   <?php } ?>
                return data;
                     })()
            }]

        });

});
</script>
</html>
