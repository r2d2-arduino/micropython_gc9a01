# Set your pins here
SPI_NUM = 1
SCK_PIN  = 14 #SCL
MOSI_PIN = 15 #SDA
DC_PIN   = 5
CS_PIN   = 4
RST_PIN  = 3
    
from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
import LibreBodoni24 as smallFont
from time import ticks_ms # need only for test measuring

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.\n Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )

tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )
tft.set_rotation(2) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees
tft.set_font( smallFont )

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

start = ticks_ms()

tft.draw_text_wrap(text, 0, 0, COLOR_WHITE, COLOR_BLACK)
tft.draw_text("Simple text", 70, 110, COLOR_BLUE, COLOR_GREEN)

print( ( ticks_ms() - start ), 'ms' )

