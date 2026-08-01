"""
GC9A01_SPI_FB v 0.3.1
Display controller driver (with Framebuffer)

Displays: GC9A01
Connection: 4-line SPI
Colors: 12, 16, 18-bit
Controllers: Esp32-family
 
Project path: https://github.com/r2d2-arduino/micropython_gc9a01
MIT License

Author: Arthur Derkach
"""
from gc9a01_spi_base import GC9A01_SPI_BASE
from tft_draw.draw_fb_c16 import DRAW_FB_C16

class GC9A01_SPI_FB( GC9A01_SPI_BASE, DRAW_FB_C16 ):  
    
    def __init__( self, spi, cs_pin, dc_pin, rst_pin, blk_pin = None,
                  width = 240, height = 240, bgr = False, dma = False ):
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
        dma    (bool): Enable DMA ( for pico only )
        """ 
        super().__init__( spi, cs_pin, dc_pin, rst_pin, blk_pin,
                          width, height, bgr )
        
        # DMA section
        self.dma_enabled = False
        self.dma_is_running = False
        
        if dma:
            if self.controller_name == 'RP2':
                self.dma_enabled = True
                self.init_dma()
            else:
                print('DMA is supported only for RP2')
                
        DRAW_FB_C16.__init__( self, self.width, self.height )        

        self.init()
    
    def write_command( self, cmd ):
        """ Sending a command to the display
        Args
        cmd (int): Command number, example: 0x2E
        """
        self.wait_dma()        
        super().write_command( cmd )

    def write_data( self, data ):
        """ Sending data to the display
        Args
        data (int): Data byte, example: 0xF8
        """
        self.wait_dma()        
        super().write_data( data )
    
    
    @micropython.viper
    def set_window( self, x0:int, y0:int, x1:int, y1:int ):
        """ Sets the starting position and the area of drawing on the display
        Args
        x0 (int): Start X position  ________
        y0 (int): Start Y position  |s---> |
        x1 (int): End X position    ||     |    
        y1 (int): End Y position    |v____e|  
        """        
        dc  = self.dc
        spi = self.spi
        
        dc.value(0) # command mode
        spi.write(b'\x2a')
        dc.value(1) # data mode
        spi.write(bytearray([(x0 >> 8) & 0xff, x0 & 0xff, (x1 >> 8) & 0xff, x1 & 0xff]))
        
        dc.value(0) # command mode
        spi.write(b'\x2b')
        dc.value(1) # data mode
        spi.write(bytearray([(y0 >> 8) & 0xff, y0 & 0xff, (y1 >> 8) & 0xff, y1 & 0xff]))
        
        dc.value(0) # command mode
        spi.write(b'\x2c')
        dc.value(1)    

    def draw_text_wrap( self, text, x, y, color ):
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
        
        drawb = self.draw_bitmap
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
            
            if not is_point_in_screen( x + glyph_width, y + corr, cx, cy, radius):
                #x = x_start
                y += glyph_height
                if y + glyph_height >= screen_height: # End of screen
                    break
                #print(y, cx, cy)

                if y > radius:
                    corr = glyph_height
                    
                x = find_left_x( y + corr, cx, cy, radius )
            #print(y, x)
            drawb(glyph, x, y, color)
            x += glyph_width        
  
    def init_dma( self ):
        ''' Create DMA'''
        from rp2 import DMA
        from machine import mem32
        
        mem32[0x50000000 + 0x464] = (
            0x1  # aborting the channel seems to help restart DMA without a full power cycle
        )
        
        while mem32[0x50000000 + 0x464] != 0:
            continue
        
        self.dma = DMA()
        self.dma_ctrl = self.dma.pack_ctrl(
            size = 0,
            inc_write = False,
            irq_quiet = False,
            treq_sel = 0,
            bswap = True,
        )
        
        self.dma.active(0)
    
    def wait_dma(self):
        """ Blocks execution until the DMA has finished transmitting the current frame """
        if self.dma_is_running:
            while self.dma.active():
                pass
            
            self.cs.value(1)
            self.dma_is_running = False

    def show( self ):
        ''' Displays the contents of the buffer on the screen '''
        if self.dma_enabled:
            self.show_dma()
        else:
            self.show_fb()
        
    def show_fb( self ):
        ''' Displays the contents of the buffer on the screen '''
        self.cs.value(0)
        
        self.set_window( 0, 0, self.width - 1, self.height - 1)
        self.spi.write( self.buffer )
        
        self.cs.value(1)        
        
    def show_dma(self):
        """ Sending a buffer via DMA without blocking the processor """
        self.wait_dma() #Make sure the bus is free
        
        self.cs.value(0)
        self.set_window(0, 0, self.width - 1, self.height - 1)
        
        # Configuring DMA
        self.dma.config(
            read = self.buffer,
            write = self.spi.display_machine,
            count = self.buffsize,
            ctrl = self.dma_ctrl,
            trigger=True,
        )

        # Starting background transfer
        self.dma_is_running = True
        self.dma.active(1)
