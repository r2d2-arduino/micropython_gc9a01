# Set your pins here
SPI_NUM = 1
SCK_PIN  = 14 #SCL
MOSI_PIN = 15 #SDA
DC_PIN   = 5
CS_PIN   = 4
RST_PIN  = 3

from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
import LibreBodoni48 as bigFont
import LibreBodoni24 as smallFont
from time import ticks_ms # need only for test measuring
import math

def fill_arc(start_angle, end_angle, inner_radius, angle_step):
    cx = tft.width // 2 - 1
    cy = tft.height // 2 - 1
    
    color = COLOR_GREEN
    
    radius = tft.width // 2 - inner_radius
    
    angle = start_angle
    while angle < end_angle + 1:
        theta = math.radians( angle )
        x = int( cx + radius * math.cos(theta) ) 
        y = int( cy + radius * math.sin(theta) )
        
        if angle > 320:
            color = COLOR_ORANGE
        elif angle > 270:
            color = COLOR_YELLOW        
        
        tft.fill_circle( x, y, inner_radius, color)
        angle += angle_step

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
COLOR_ORANGE  = tft.rgb( 255, 200, 0 )

tft.fill( COLOR_BLACK )

start = ticks_ms()

tft.set_font( bigFont )
tft.draw_text("1320", 70, 100, COLOR_BLUE, COLOR_BLACK)

tft.set_font( smallFont )
tft.draw_text("CO2", 94, 76, COLOR_MAGENTA, COLOR_BLACK)
tft.draw_text("ppm", 94, 140, COLOR_RED, COLOR_BLACK)


fill_arc(120, 350, 20, 4)


print( ( ticks_ms() - start ), 'ms' )


