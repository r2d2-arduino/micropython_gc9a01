from gc9a01_spi_fb import GC9A01_SPI_FB
from pio_spi import PIO_SPI
import resources.LibreBodoni48 as bigFont
import resources.LibreBodoni24 as smallFont
from time import ticks_ms # need only for test measuring
import math

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN  = 4
DC_PIN  = 5
RST_PIN = 3
BLK_PIN = None

# standart SPI dosn't work with dma
piospi = PIO_SPI( sck = SCK_PIN, mosi = MOSI_PIN )
tft = GC9A01_SPI_FB( piospi, CS_PIN, DC_PIN, RST_PIN, BLK_PIN, bgr = True, dma = True )

tft.set_rotation(0) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

def fill_arc(start_angle, end_angle, inner_radius, angle_step):    
    color = COLOR_GREEN
    
    cx = tft.width // 2 - 1
    cy = tft.height // 2 - 1
    
    radius = tft.width // 2 - inner_radius
    
    angle = start_angle
    while angle < end_angle + 1:
        theta = math.radians( angle )
        x = int( cx + radius * math.cos(theta) ) 
        y = int( cy + radius * math.sin(theta) )
        
        diff_angle = angle - start_angle
        #print(diff_angle)
        if diff_angle > 339:
            color = tft.color565( 0, 0, 255 )
        elif diff_angle > 254:
            color = tft.color565( 510 - (diff_angle * 3), 0, 255 )
        elif diff_angle > 171:
            color = tft.color565( 255, 0, diff_angle * 3 - 513 )
        elif diff_angle > 85:
            color = tft.color565( 255, 513 - (diff_angle * 3), 0 )
        else:
            color = tft.color565( diff_angle * 3, 255, 0 )  
        
        tft.ellipse(x, y, inner_radius, inner_radius, color, True)
        angle += angle_step

COLOR_BLACK   = tft.color565( 0, 0, 0 )
COLOR_BLUE    = tft.color565( 0, 0, 255 )
COLOR_RED     = tft.color565( 255, 0, 0 )
COLOR_GREEN   = tft.color565( 0, 255, 0 )
COLOR_CYAN    = tft.color565( 0, 255, 255 )
COLOR_MAGENTA = tft.color565( 255, 0, 255 )
COLOR_YELLOW  = tft.color565( 255, 255, 0 )
COLOR_WHITE   = tft.color565( 255, 255, 255 )
COLOR_GRAY    = tft.color565( 112, 160, 112 )
COLOR_ORANGE  = tft.color565( 255, 200, 0 )

start = ticks_ms()

tft.fill( COLOR_BLACK )

tft.set_font( bigFont )
tft.draw_text("1320", 70, 100, COLOR_BLUE)

tft.set_font( smallFont )
tft.draw_text("CO2", 94, 76, COLOR_MAGENTA)
tft.draw_text("ppm", 94, 140, COLOR_RED)

fill_arc( 120, 370, 20, 4 )

tft.show()

print( ( ticks_ms() - start ), 'ms' )
#pico 78 ms
#dma  44 + 16 = 60