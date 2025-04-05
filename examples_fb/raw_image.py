# Set your pins here
SPI_NUM = 1
SCK_PIN  = 14 #SCL
MOSI_PIN = 15 #SDA
DC_PIN   = 5
CS_PIN   = 4
RST_PIN  = 3

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False
    
from gc9a01fb_spi import GC9A01FB_SPI
from machine import SPI, Pin
from time import ticks_ms # need only for test measuring

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )

tft = GC9A01FB_SPI( spi, CS_PIN, DC_PIN, RST_PIN )
tft.set_rotation(2) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

filename = 'vintage240x240.raw'
if file_exists(filename):    
    start = ticks_ms()

    tft.draw_raw_image( filename, 0, 0, 240, 240 )

    print( ( ticks_ms() - start ), 'ms' )
    
    tft.show()