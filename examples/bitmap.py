# Set your pins here
SPI_NUM = 1
SCK_PIN  = 14 #SCL
MOSI_PIN = 15 #SDA
DC_PIN   = 5
CS_PIN   = 4
RST_PIN  = 3
    
from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
from bitmaps import rain

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )

tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )
tft.set_rotation(2) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

tft.fill( COLOR_BLACK )

colors = [COLOR_WHITE, COLOR_CYAN, COLOR_MAGENTA, COLOR_RED, COLOR_GREEN, COLOR_BLUE, COLOR_YELLOW]

size = 16

for i in range( len(colors) ):
    color = colors[i]
    for y in range(15):
        for x in range(15):
            tft.draw_bitmap(rain, x * size, y * size, color, COLOR_BLACK)



