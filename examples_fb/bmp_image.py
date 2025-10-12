from gc9a01_spi_fb import GC9A01_SPI_FB
from machine import SPI, Pin
from time import ticks_ms # need only for test measuring

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN   = 4
DC_PIN   = 5
RST_PIN  = 3

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )
tft = GC9A01_SPI_FB( spi, CS_PIN, DC_PIN, RST_PIN )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False
    
filename = 'bird240x240.bmp'
if file_exists(filename):    
    start = ticks_ms()

    tft.draw_bmp( filename, 0, 0 )
    
    print( ( ticks_ms() - start ), 'ms' ) # 269
    
    tft.show()
