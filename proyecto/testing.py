from machine import Pin
from time import sleep

# Configurar el pin 2 como salida
led = Pin(2, Pin.OUT)

# Bucle infinito para parpadear el LED
while True:
    led.on()      # Encender LED
    sleep(0.5)    # Esperar 0.5 segundos
    led.off()     # Apagar LED
    sleep(0.5)    # Esperar 0.5 segundos
