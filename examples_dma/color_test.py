from gc9a01_spi_fb import GC9A01_SPI_FB
from pio_spi import PIO_SPI
import resources.LibreBodoni24 as bigFont
from time import ticks_ms

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

#tft.invert_display( True )

COLOR_BLACK   = tft.rgb( 0, 0, 0 )
COLOR_BLUE    = tft.rgb( 0, 0, 255 )
COLOR_RED     = tft.rgb( 255, 0, 0 )
COLOR_GREEN   = tft.rgb( 0, 255, 0 )
COLOR_CYAN    = tft.rgb( 0, 255, 255 )
COLOR_MAGENTA = tft.rgb( 255, 0, 255 )
COLOR_YELLOW  = tft.rgb( 255, 255, 0 )
COLOR_WHITE   = tft.rgb( 255, 255, 255 )
COLOR_GRAY    = tft.rgb( 112, 160, 112 )

tft.set_font(bigFont)
tft.set_rotation(0) # 0..3 - Rotates the screen

tft.fill(COLOR_BLACK) # Fill the screen with black color

row = 24

tft.draw_text('RED', 50, row * 1, COLOR_RED)
tft.draw_text('GREEN', 50, row * 2, COLOR_GREEN)
tft.draw_text('BLUE', 50, row * 3, COLOR_BLUE)
tft.draw_text('CYAN', 50, row * 4, COLOR_CYAN)
tft.draw_text('MAGENTA', 50, row * 5, COLOR_MAGENTA)
tft.draw_text('YELLOW', 50, row * 6, COLOR_YELLOW)
tft.draw_text('WHITE', 50, row * 7, COLOR_WHITE)
tft.draw_text('GRAY', 50, row * 8, COLOR_GRAY)
tft.draw_text('BLACK', 50, row * 9, COLOR_BLACK)

start = ticks_ms()

tft.show()
while tft.dma.active():
    pass
print('DMA speed:', (ticks_ms()-start), 'ms')



