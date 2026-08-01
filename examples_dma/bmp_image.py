from gc9a01_spi_fb import GC9A01_SPI_FB
from pio_spi import PIO_SPI
from time import ticks_ms # need only for test measuring

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN  = 4
DC_PIN  = 5
RST_PIN = 3
BLK_PIN = None # Set to None if the display doesn't have a backlight pin

# standart SPI dosn't work with dma
piospi = PIO_SPI( sck = SCK_PIN, mosi = MOSI_PIN )
tft = GC9A01_SPI_FB( piospi, CS_PIN, DC_PIN, RST_PIN, BLK_PIN, bgr = True, dma = True )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False
    
filename = 'resources/bird240x240.bmp'
if file_exists(filename):    
    start = ticks_ms()

    tft.draw_bmp( filename, 0, 0 )
    
    tft.show()
    
    print( ( ticks_ms() - start ), 'ms' ) 
#pico 317 ms
#dma  283 + 16 = 299
