from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
from time import sleep_ms

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN   = 4
DC_PIN   = 5
RST_PIN  = 3

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )
tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
SCREEN_WIDTH = tft.width

tft.fill( 0 )

def rainbow( delay = 0 ):
    #red
    for y in range(0, 20):
        color = tft.color565( y * 10 + 65, 0, 0 )
        tft.fill_rect(0, y * 2, SCREEN_WIDTH, 2, color)
    
    #red-green
    for y in range(0, 20):
        color = tft.color565(  y * 10 + 65, y * 10 + 65, 0 )
        tft.fill_rect(0, y * 2 + 40, SCREEN_WIDTH, 2, color)
    
    #green
    for y in range(0, 20):
        color = tft.color565(  0, y * 10 + 65, 0 )
        tft.fill_rect(0, y* 2 + 80, SCREEN_WIDTH, 2, color)

    #green-blue
    for y in range(0, 20):
        color = tft.color565(  0, y * 10 + 65, y * 10 + 65 )
        tft.fill_rect(0, y * 2 + 120, SCREEN_WIDTH, 2, color)

    #blue
    for y in range(0, 20):
        color = tft.color565(  0, 0, y * 10 + 65 )
        tft.fill_rect(0, y * 2 + 160, SCREEN_WIDTH, 2, color)
        
    #red-blue
    for y in range(0, 20):
        color = tft.color565( y * 10 + 65, 0, y * 10 + 65 )
        tft.fill_rect(0, y * 2 + 200, SCREEN_WIDTH, 2, color)

rainbow()

for i in range(3):
    tft.scroll( 5 )