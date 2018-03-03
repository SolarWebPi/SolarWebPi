wifi.sta.autoconnect(1)
print('Configurando wifi')  
wifi.setmode(wifi.STATION)  
-- wifi config start
wifi.sta.config("NOMBRE_WIFI","XXXXXXXX")

wifi.sta.connect()
wifi.sta.setip({ip="192.168.1.20",netmask="255.255.255.0",gateway="192.168.1.1"})

-- wifi config end

print('Wifi Status=',wifi.sta.status())
local ip_asignada = wifi.sta.getip()
print('IP asignada: ' .. ip_asignada)

-- Asignacion de Salidas a pin HW
M={1,2,5,6,7}
N={"D1","D2","D5","D6","D7"}


-- Inicializo valores salida PWM--
P={0,0,0,0,0}

print ('--- Mapeo ---')
print ('Salida PWM =  PIN ')
for v,i in pairs(M) do
  pwm.setup(i, 5, 1023-math.floor(P[v]*10.23))
  pwm.start(i)
  print(v,'   =',N[v])
end

tmr.softwd(3600) -- inicializo watchdog

-- inicializo servidor http
print ('Configurando el servidor')

s=net.createServer(net.TCP)
s:listen(80,function(c)
 c:on("receive",function(c,pl)
   tmr.softwd(120) -- watchdog por si no recibe  apagar reles
   --print("pp")   
   salida=99
   for v,w in pairs (M) do
     if string.find(pl,"/R"..v.."=") then 
       salida=1
       i,j=string.find(pl,"/R"..v.."=")
       if string.sub(pl,j+1,j+1) =="?" then salida=2 end
       
       if salida==1 then -- cojo valor despues del =
         if string.sub(pl,j+3,j+3)=="H" then
           nvalor=tonumber(string.sub(pl,j+1,j+2)) 
          else
           nvalor=tonumber(string.sub(pl,j+1,j+3))
         end  
         if nvalor>100 then nvalor=100 end
         if nvalor<0 then nvalor=0 end
         P[v]=nvalor 
         --print(v,"=",nvalor)
         
         pwm.setduty(w,1023-math.floor(nvalor*10.23))      
         c:send("\nPWM_R"..v.."="..P[v].."\n")
         c:send("\n ")
         c:send("\n   MAPEO PINES")
         c:send("\nPWM  VALOR = PIN D")
         for v1,w1 in pairs(M) do
           c:send("\n R"..v1.." = "..P[v1].."% /"..(1023-pwm.getduty(w1)).." duty en pin "..N[v1])
         end       
       end

       if salida==2 then 
         c:send("\nPWM_R"..v.."="..P[v].."\n")
         c:send("\n ")
         c:send("\n   MAPEO PINES  (activacion con nivel bajo)")
         c:send("\nPWM    VALOR      = PIN D")
         for v1,w1 in pairs(M) do
           c:send("\n R"..v1.." = "..P[v1].."% /"..(1023-pwm.getduty(w1)).." duty en pin "..N[v1])
         end       
       end
       
       c:on("sent",function(c) c:close() end)
     end
   end
   if salida==99 then
     c:send("\nERROR orden desconocida")
   end  
   c:send("\nTMR:"..tmr.now().." / "..string.sub(pl,1,19))
   c:on("sent",function(c) c:close() end)
 
 end)
 
end)

print ('Valor por http://192.168.1.20/Rx=y') 
print ('x cualquier valor valido de Rele (1,2,3,4,5)')
print ('y cualquier valor entre 0 y 100')
  

