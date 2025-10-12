from gc9a01_spi import GC9A01_SPI
from machine import SPI, Pin
import math
from time import ticks_ms, ticks_diff, sleep_ms

# Set your pins here
SPI_NUM = 0
SCK_PIN  = 6
MOSI_PIN = 7

CS_PIN   = 4
DC_PIN   = 5
RST_PIN  = 3

spi = SPI( SPI_NUM, baudrate = 40_000_000, sck = Pin(SCK_PIN), mosi = Pin(MOSI_PIN) )
tft = GC9A01_SPI( spi, CS_PIN, DC_PIN, RST_PIN )

tft.set_rotation(2) # 0 = 0 degrees, 1 = 90 degrees, 2 = 180 degrees, 3 = 270 degrees

COLOR_BLACK   = tft.color565( 0, 0, 0 )
COLOR_BLUE    = tft.color565( 0, 0, 255 )
COLOR_RED     = tft.color565( 255, 0, 0 )
COLOR_GREEN   = tft.color565( 0, 255, 0 )
COLOR_CYAN    = tft.color565( 0, 255, 255 )
COLOR_MAGENTA = tft.color565( 255, 0, 255 )
COLOR_YELLOW  = tft.color565( 255, 255, 0 )
COLOR_WHITE   = tft.color565( 255, 255, 255 )
COLOR_GRAY    = tft.color565( 112, 160, 112 )

filename = 'vintage240x240.raw'

def file_exists(filename):
    import os
    try:
        os.stat(filename)
        return True
    except OSError:
        print("File not found:", filename)
        return False
    
if file_exists(filename):    
    tft.draw_raw_image( filename, 0, 0, 240, 240 )

def draw_watch_second( angle, length, color ):
    center_x = tft.width  // 2
    center_y = tft.height // 2
    
    rad = math.radians(angle)
    
    end_x = int( center_x + length * math.sin(rad) )
    end_y = int( center_y - length * math.cos(rad) )
    
    tft.draw_line(center_x, center_y, end_x, end_y, color)    

def draw_watch_hand( angle, length, color, think ):
    step = length // 8
    
    center_x = tft.width  // 2
    center_y = tft.height // 2
    
    rad = math.radians(angle)
    
    length1 = length

    while length1 > step:
        end_x = int( center_x + length1 * math.sin(rad) )
        end_y = int( center_y - length1 * math.cos(rad) )
        
        rad2 = math.radians(angle - think)
        
        center_x2 = int( end_x - length1 * math.sin(rad2) )
        center_y2 = int( end_y + length1 * math.cos(rad2) )

        tft.draw_line(center_x2, center_y2, end_x, end_y, color)
        
        rad3 = math.radians(angle + think)
        
        center_x3 = int( end_x - length1 * math.sin(rad3) )
        center_y3 = int( end_y + length1 * math.cos(rad3) )

        tft.draw_line(center_x3, center_y3, end_x, end_y, color)
        
        length1 -= step


def draw_analog_watch( hours, minutes, seconds ):
    # second
    draw_watch_second( seconds * 6, 100, COLOR_RED )
    #minutes
    draw_watch_hand( minutes * 6 + seconds // 10, 90, COLOR_BLACK, 5 )
    #hours
    draw_watch_hand( hours * 30 + minutes // 2, 60, COLOR_BLACK, 7 )
    #circle
    tft.fill_circle(120, 120, 10, COLOR_BLACK)
    
hours = 16
minutes = 37
seconds = 45

draw_analog_watch( hours, minutes, seconds )

while 1:
    start = ticks_ms()
    
    tft.draw_raw_image( filename, 0, 0, 240, 240 )
    draw_analog_watch( hours, minutes, seconds )
    
    seconds += 1
    
    if seconds == 60:
        seconds = 0
        minutes += 1
        
    if minutes == 60:
        minutes = 0
        hours += 1
        
    if hours == 24:
        hours = 0
    
    diff = ticks_diff( ticks_ms(), start )

    print(diff, 'ms')
    sleep_ms( 1000 - diff )
