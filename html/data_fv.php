<?php

require('conexion.php');

$sql = "SELECT Ibat,Vbat,SOC,Iplaca,Vplaca,Temp,Vflot FROM datos WHERE DATE(Tiempo)= CURDATE() AND id=(SELECT max(id) FROM datos)";

$temperatura = shell_exec('cat /sys/class/thermal/thermal_zone0/temp');
$cpu=$temperatura/1000;

if($result = mysqli_query($link, $sql)){

        $row=mysqli_fetch_row($result);
        $row[7]=$cpu;
        header("Content-type: text/json");
        print json_encode($row, JSON_NUMERIC_CHECK);

} else{

        echo "ERROR: Could not able to execute $sql. " . mysqli_error($link);
}

mysqli_close($link);

?>

