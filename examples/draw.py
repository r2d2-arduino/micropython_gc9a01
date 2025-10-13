from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
from time import ticks_ms # need only for test measuring

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN  = 4
DC_PIN  = 5
RST_PIN = 3
BLK_PIN = None # Set to None if the display doesn't have a backlight pin

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )
tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN, BLK_PIN )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

SCREEN_WIDTH  = tft.width
SCREEN_HEIGHT = tft.height

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

start = ticks_ms()

tft.draw_rect(35, 35, 80, 80, COLOR_RED, 2)

tft.fill_rect(35, 125, 80, 80, COLOR_MAGENTA)

tft.fill_circle(180, 125, 60, COLOR_YELLOW)

tft.draw_circle(120, 120, 120, COLOR_BLUE, 2)

for y in range(SCREEN_HEIGHT // 8):
    tft.draw_line(0, 0, SCREEN_WIDTH, y * 8 , COLOR_GREEN)


print( ( ticks_ms() - start ), 'ms' ) # 929