from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
from resources.bitmaps import rain

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN  = 4
DC_PIN  = 5
RST_PIN = 3
BLK_PIN = None # Set to None if the display doesn't have a backlight pin

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )
tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN, BLK_PIN, bgr = True )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

COLOR_BLACK   = tft.color565( 0, 0, 0 )
COLOR_BLUE    = tft.color565( 0, 0, 255 )
COLOR_RED     = tft.color565( 255, 0, 0 )
COLOR_GREEN   = tft.color565( 0, 255, 0 )
COLOR_CYAN    = tft.color565( 0, 255, 255 )
COLOR_MAGENTA = tft.color565( 255, 0, 255 )
COLOR_YELLOW  = tft.color565( 255, 255, 0 )
COLOR_WHITE   = tft.color565( 255, 255, 255 )
COLOR_GRAY    = tft.color565( 112, 160, 112 )

tft.fill( COLOR_BLACK )

colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]

size = 16

for i in range( len(colors) ):
    color = colors[i]
    for y in range(15):
        for x in range(15):
            tft.draw_bitmap(rain, x * size, y * size, color, COLOR_BLACK)
