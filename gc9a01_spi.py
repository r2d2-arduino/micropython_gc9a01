"""
GC9A01_SPI v 0.3.1
Display controller driver

Displays: GC9A01
Connection: 4-line SPI
Colors: 12, 16, 18 bits
Controllers: Esp32-family, RP2-family
 
Project path: https://github.com/r2d2-arduino/micropython_gc9a01
MIT License

Author: Arthur Derkach
"""

from gc9a01_spi_base import GC9A01_SPI_BASE
from tft_draw.draw_spi_c16 import DRAW_SPI_C16

class GC9A01_SPI( GC9A01_SPI_BASE, DRAW_SPI_C16 ):
    
    def __init__( self, spi, cs_pin, dc_pin, rst_pin, blk_pin = None,
                  width = 240, height = 240, bgr = False ):
        """ Constructor
        Args
        spi  (object): SPI
        cs_pin  (int): Chip Select pin number
        dc_pin  (int): Data/Command pin number
        rst_pin (int): Reset pin number 
        blk_pin (int): Backlight pin number
        width   (int): Screen width in pixels (less)
        height  (int): Screen height in pixels
        bgr    (bool): Color order: False = RGB, True = BGR
        """ 
        super().__init__( spi, cs_pin, dc_pin, rst_pin, blk_pin,
                          width, height, bgr )
            
        DRAW_SPI_C16.__init__( self, self.spi, self.cs, self.dc,
                               self.width, self.height )
        
        self.init()   
    
    def draw_text_wrap( self, text, x, y, color, bg ):
        """ Draw text on display (fast version)
        Args
        x (int) : Start X position
        y (int) : Start Y position
        color (int): RGB color
        """
        def is_point_in_screen( x, y, cx, cy, radius ):
            """ Check is point in visibled part of screen
            Args
            x (int) : X position of point
            y (int) : Y position of point
            Return (bool): is in screen        
            """            
            return (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2
        
        
        def find_left_x( y, cx, cy, radius ):
            #print( y, cx, cy, radius )
            return round( cx - (radius**2 - (y - cy)**2)**0.5 )
        
        def find_rigth_x( y, cx, cy, radius ):
            return round( cx + (radius**2 - (y - cy)**2)**0.5 )        

        screen_height = self.height
        screen_width = self.width
        radius = screen_width // 2
        cx = screen_width // 2
        cy = screen_height // 2
        x_start = x
        left_x = find_left_x( y, cx, cy, radius )
        if x_start < left_x:
            x_start = left_x
        
        font = self.font        
        if font == None:
            print("Font not set")
            return False
        
        draw_bitmap = self.draw_bitmap
        getch = font.get_ch
        
        corr = 0
        for char in text:
            if char == "\n": # New line
                x = screen_width
                continue
            
            if char == "\t": #replace tab to space
                char = " "                
            
            glyph = getch(char)
            glyph_height = glyph[1]
            glyph_width  = glyph[2]
            
            if not is_point_in_screen( x + glyph_width, y + corr, cx, cy, radius ):
                #x = x_start
                y += glyph_height
                if y + glyph_height >= screen_height: # End of screen
                    break
                #print(y, cx, cy)

                if y > radius:
                    corr = glyph_height
                    
                x = find_left_x( y + corr, cx, cy, radius )
            #print(y, x)
            draw_bitmap(glyph, x, y, color, bg)
            x += glyph_width 
        