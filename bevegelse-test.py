from machine import Pin
import utime

inbuiltLed = 25
#Led = 0
led = Pin(inbuiltLed, Pin.OUT)
#led = Pin(Led, Pint.OUT)

pir = Pin(16, Pin.IN, Pin.PULL_DOWN)
n = 0

#led.low()
print("Startar opp bevegelsessensor.")
utime.sleep(3)

while True:
    #print(pir.value())
    #utime.sleep(0.2)
    if pir.value() == 1:
        n = n+1
        print("Bevegelse!",n)
        led.toggle()
        utime.sleep(5)
    utime.sleep(1)