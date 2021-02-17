# https://github.com/benevpi/pico_python_ws2812b/tree/main/examples
import time
from ws2812b import ws2812b

num_leds = 60
pixels = ws2812b(num_leds, 0,0, delay=0)

pixels.fill(10,10,10)
pixels.show()

while True:
    for i in range(num_leds):
        for j in range(num_leds):
            pixels.set_pixel(j,abs(i+j)%10,abs(i-(j+3))%10,abs(i-(j+6))%10)          
        pixels.show()
        time.sleep(0.05)